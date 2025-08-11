# OCR FastAPI Backend (PaddleOCR 3.1.0, CUDA 12.9)

이 저장소는 PaddleOCR 3.1.0 기반의 FastAPI 백엔드 서버를 GPU 환경(ECS/EC2)에서 운영하기 위한 참조 구현입니다. 인프라(Terraform) → 애플리케이션(Docker/Poetry) → 배포(ECR/ECS/ALB) → 모니터링(CloudWatch)까지 일관된 파이프라인을 제공합니다. Amplify Gen2 Next.js 프론트엔드와 연동을 고려합니다.

## 구성 요약

- 언어/런타임: Python 3.10, FastAPI 0.100+, Uvicorn
- OCR: PaddleOCR 3.1.0, PaddlePaddle GPU 3.1 (CUDA 12.9)
- 컨테이너: `nvidia/cuda:12.9.0-runtime-ubuntu22.04`
- 인프라: AWS VPC, ECS(EC2 GPU g4dn.xlarge), ALB, ECR, CloudWatch
- IaC/CI: Terraform, GitHub Actions

디렉터리

- `app/`: FastAPI 앱 소스
- `docker/Dockerfile`: CUDA 12.9 베이스 Dockerfile
- `infra/terraform/`: Terraform 모듈(네트워크/ECS/ALB/ASG/모니터링)
- `docs/`: 상세 가이드 및 설계 문서
- `scripts/`: GPU 검증 등 유틸 스크립트
- `tasks/`: 태스크/체크리스트

## 빠른 배포 튜토리얼

- 처음 배포하신다면 루트에 있는 튜토리얼을 따라 하세요: [TUTORIAL-DEPLOY.md](TUTORIAL-DEPLOY.md)

## 사전 준비

1. 로컬 개발용

- Python 3.10 (venv 권장), Poetry 설치
- Docker Desktop + NVIDIA Container Toolkit(GPU 테스트 시)

2. AWS 자격

- AWS 계정 및 IAM 권한, S3/DynamoDB(원격 상태), ECR, ECS, ALB 사용 가능

3. 환경 변수(배포/테스트)

- API Key 모드 시: `API_KEY`
- Cognito 모드 시: `AUTH_MODE=cognito`, `COGNITO_ISSUER`, `COGNITO_AUDIENCE`

## 애플리케이션 빌드/로컬 실행

Poetry 설치

```bash
poetry install
pytest -q
```

Docker 이미지 빌드/실행

```bash
# 개발 이미지
make docker-build
make docker-run   # 8080
make smoke-health
make smoke-ocr
make docker-stop

# GPU 이미지 (휠 인덱스/런체크 포함)
make docker-build-gpu PADDLE_WHEEL_INDEX=https://www.paddlepaddle.org.cn/whl/linux/gpu
# GPU 러닝(호스트에 NVIDIA toolkit 필요)
make docker-run-gpu
```

배치/파싱/추출 스모크

```bash
make smoke-structure
make smoke-extraction
make smoke-batch
```

## 인프라 프로비저닝(Terraform)

변수 설정(`infra/terraform/variables.tf` 참고)

- `aws_region` 기본 `ap-northeast-2`
- `project_name` 기본 `ocr-fastapi`
- `ecr_image`에 ECR 이미지 URI 설정 필요(예: `<acct>.dkr.ecr.<region>.amazonaws.com/ocr-fastapi:latest`)

원격 상태 구성(`infra/terraform/backend.tf`)

```hcl
terraform {
  backend "s3" {}
}
```

사용 전 `terraform init -backend-config` 플래그로 S3/DynamoDB 구성 지정

```bash
cd infra/terraform
terraform init \
  -backend-config="bucket=<STATE_BUCKET>" \
  -backend-config="key=ocr-fastapi/terraform.tfstate" \
  -backend-config="region=<REGION>" \
  -backend-config="dynamodb_table=<LOCK_TABLE>"
terraform plan -var="ecr_image=<ECR_URI>"
terraform apply -auto-approve -var="ecr_image=<ECR_URI>"
```

출력 확인

```bash
terraform output
# vpc_id, public_subnets, private_subnets, ecr_repository_url, ecs_cluster_name, asg_gpu_name
```

## 컨테이너 이미지 빌드/푸시(ECR)

ECR 로그인/푸시

```bash
aws ecr get-login-password --region <REGION> | docker login --username AWS --password-stdin <acct>.dkr.ecr.<region>.amazonaws.com
# 태깅 후 푸시
docker tag ocr-fastapi:gpu <ECR_URI>
docker push <ECR_URI>
```

`infra/terraform/variables.tf`의 `ecr_image`에 동일 URI 설정 후 `terraform apply`로 서비스 반영

## ECS 서비스 배포/확인

- ALB 리스너/타깃 그룹 구성은 Terraform에 포함됨
- 서비스가 실행되면 ALB DNS로 `/health` 호출

```bash
curl http://<ALB_DNS>/health
```

- 인증 모드가 api-key인 경우 헤더 추가

```bash
curl -H "x-api-key: $API_KEY" http://<ALB_DNS>/ocr -F file=@sample.png
```

## GPU 검증(13.x)

로컬 또는 GPU가 장착된 호스트에서

```bash
# 이미지 빌드와 빌드 시 run_check 시도
make docker-build-gpu PADDLE_WHEEL_INDEX=https://www.paddlepaddle.org.cn/whl/linux/gpu
# 컨테이너 구동/검증(인증 필요)
API_KEY=<키> make gpu-verify
```

확인 포인트

- `/health.version.compiled_with_cuda == true`
- `/debug/paddle.run_check == true`

## 모니터링/알람

Terraform에 기본 대시보드/알람 포함(`infra/terraform/monitoring.tf`)

- ALB TargetResponseTime p95
- Target 5xx
- GPU Utilization(CWAgent 전제)
  대시보드: `<project>-dashboard`

## Amplify 연동(요약)

- Amplify Gen2 Next.js에서 API 도메인 및 인증 헤더 설정(CORS 허용은 `ALLOWED_ORIGINS`)
- 업로드는 `form-data`(`file`)로 `/ocr`/`/structure`/`/extraction` 호출
- 상세는 `docs/amplify-integration.md` 참고

## 설정(환경 변수)

- `AUTH_MODE` = `api-key`(기본) | `cognito`
- `API_KEY` (api-key 모드)
- `COGNITO_ISSUER`, `COGNITO_AUDIENCE` (cognito 모드)
- `ALLOWED_ORIGINS` (콤마 구분)
- `PRELOAD_MODELS` (True/False)
- `CHATOCR_ENABLED`, `CHATOCR_API_TOKEN` (실험적)

## 주의 사항

- 로컬 GPU 실행에는 NVIDIA Container Toolkit 필수
- 실제 GPU 메트릭 알람은 CWAgent 또는 DCGM Exporter 전제
- ChatOCR 경로는 PoC 토글로 안전 폴백 유지

## 문서 링크

- `docs/README.md`, `docs/infra-terraform.md`, `docs/docker.md`, `docs/health.md`, `docs/monitoring.md`, `docs/amplify-integration.md`
