## 서버 배포 튜토리얼 (OCR FastAPI)

이 문서는 프로젝트를 서버에 배포하고 운영하는 방법을 단계별로 안내합니다. 로컬/단일 서버(온프레미스)와 AWS ECS(EC2 GPU) 배포 두 경로를 제공합니다.

### 1) 공통 준비

- 필수 소프트웨어
  - Docker 24+
  - NVIDIA Container Toolkit(GPU 서버인 경우)
- 네트워크/포트
  - 컨테이너 내부 `8080` 포트를 서비스 포트로 사용합니다.
- 환경 변수(예시)
  - `AUTH_MODE=api-key` (기본 인증 모드)
  - `API_KEY=<원하는키>` (api-key 모드에서 필수)
  - `ALLOWED_ORIGINS=https://your-frontend.example.com,https://admin.example.com`
  - 선택: `PRELOAD_MODELS=true` (기동 시 모델 프리로드, 콜드스타트 감소)

### 2) 로컬/단일 서버 배포(온프레미스)

1. 저장소 가져오기

   ```bash
   git clone <repo-url>
   cd ocr-fastapi
   ```

2. Docker 이미지 빌드

   - CPU 실행(개발용 기본 이미지)
     ```bash
     make docker-build
     ```
   - GPU 실행(NVIDIA Toolkit 필요)
     ```bash
     make docker-build-gpu
     # 또는 인덱스 변경
     make docker-build-gpu PADDLE_WHEEL_INDEX=https://www.paddlepaddle.org.cn/whl/linux/gpu
     ```

3. 컨테이너 실행

   - CPU
     ```bash
     docker run --rm -p 8080:8080 --name ocr-api ocr-fastapi:dev \
       sh -c "uvicorn app.main:app --host 0.0.0.0 --port 8080"
     ```
   - GPU
     ```bash
     docker run --rm --gpus all -e API_KEY=$API_KEY -p 8080:8080 --name ocr-api ocr-fastapi:gpu \
       sh -c "uvicorn app.main:app --host 0.0.0.0 --port 8080"
     ```

4. 동작 확인

   - 헬스체크
     ```bash
     curl -sS http://localhost:8080/health | jq .
     ```
   - OCR 호출(인증 필요 시 `x-api-key` 헤더)
     ```bash
     curl -sS -H "x-api-key: $API_KEY" http://localhost:8080/ocr -F file=@/etc/hosts | jq .
     ```

5. 운영화(선택)
   - `docker run`을 systemd 서비스에 등록하거나, `docker compose`로 관리하면 재기동/로그 관리가 편리합니다.

### 3) AWS ECS(EC2 GPU) 배포

1. 사전 준비

   - ECR 리포지토리 생성 및 AWS CLI 로그인
   - Terraform 원격 상태(S3/DynamoDB) 구성
   - VPC, Subnet, SG, ALB 등은 Terraform 모듈로 생성

2. 이미지 빌드/푸시

   ```bash
   # 로컬에서 GPU 이미지 빌드
   make docker-build-gpu

   # ECR 로그인
   aws ecr get-login-password --region <REGION> | \
     docker login --username AWS --password-stdin <acct>.dkr.ecr.<region>.amazonaws.com

   # 태깅/푸시
   docker tag ocr-fastapi:gpu <ECR_URI>
   docker push <ECR_URI>
   ```

3. Terraform 배포

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

4. 태스크 정의/서비스 환경 변수(예시)

   - `AUTH_MODE=api-key`
   - `API_KEY=<키>`
   - `ALLOWED_ORIGINS=https://your-frontend.example.com`
   - 선택: `PRELOAD_MODELS=true`
   - 포트 매핑: 컨테이너 8080 → ALB TargetGroup 8080

5. 배포 확인
   ```bash
   # ALB DNS 확인 후 호출
   curl -sS http://<ALB_DNS>/health | jq .
   curl -sS -H "x-api-key: $API_KEY" http://<ALB_DNS>/ocr -F file=@/etc/hosts | jq .
   ```

### 4) 운영 팁

- 성능/콜드스타트
  - GPU 서버는 `--gpus all` 필수
  - `PRELOAD_MODELS=true`로 모델 프리로드하여 초기 응답 지연을 줄입니다.
- 보안
  - 기본은 `api-key` 헤더 인증(`x-api-key`). 필요 시 Cognito 모드(`AUTH_MODE=cognito`, `COGNITO_ISSUER`, `COGNITO_AUDIENCE`).
- 관찰성
  - `/health`에서 CUDA 컴파일 여부(`version.compiled_with_cuda`) 확인
  - 디버그 라우트(`/debug/paddle`)로 Paddle 동작 점검
  - CloudWatch 대시보드는 Terraform 모듈에 포함([docs/monitoring.md](docs/monitoring.md))

### 5) 트러블슈팅

- 빌드 실패(127, Makefile)
  - `docker-build-gpu`에서 기본값은 Makefile 상단 `PADDLE_WHEEL_INDEX ?= ...`로 지정되어 있습니다. 필요 시 커맨드에서 덮어쓰세요.
- CUDA/드라이버 이슈
  - 호스트 드라이버와 컨테이너 런타임 버전 매칭 확인, `nvidia-smi` 실행 확인
- 401 Unauthorized
  - `AUTH_MODE`, `API_KEY` 환경 변수와 `x-api-key` 헤더 전달 여부 확인
- 성능 저하
  - 대용량 입력은 리사이즈(`max_image_px`) 사용, 배치 엔드포인트(`/ocr/batch`) 활용

### 6) 빠른 실행 치트시트

- 로컬 GPU
  ```bash
  make docker-build-gpu
  API_KEY=<키> docker run --rm --gpus all -e API_KEY=$API_KEY -p 8080:8080 --name ocr-api ocr-fastapi:gpu \
    sh -c "uvicorn app.main:app --host 0.0.0.0 --port 8080"
  curl -sS -H "x-api-key: $API_KEY" http://localhost:8080/health | jq .
  ```
- ECS
  ```bash
  make docker-build-gpu
  docker tag ocr-fastapi:gpu <ECR_URI>
  docker push <ECR_URI>
  cd infra/terraform && terraform init && \
    terraform apply -auto-approve -var="ecr_image=<ECR_URI>"
  ```

### 참고 문서

- 로컬/도커: [docs/docker.md](docs/docker.md)
- 헬스/디버그: [docs/health.md](docs/health.md)
- 인프라/Terraform: [docs/infra-terraform.md](docs/infra-terraform.md)
- 모니터링: [docs/monitoring.md](docs/monitoring.md)
