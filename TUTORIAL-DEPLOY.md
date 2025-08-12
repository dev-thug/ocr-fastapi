## 서버 배포 튜토리얼 (완전 입문자용)

이 문서는 “복사-붙여넣기”로 바로 실행할 수 있게 가장 쉬운 순서로 설명합니다. GPU는 선택 사항이며, 없다면 CPU 모드만으로도 바로 사용할 수 있습니다.

### 0. 준비물(5분)

- 필수: Docker(데스크톱/엔진). 설치 후 터미널에서 아래로 확인합니다.
  ```bash
  docker --version
  ```
- 선택(GPU 서버일 때만): NVIDIA Container Toolkit. 설치 후 아래로 확인합니다.
  ```bash
  nvidia-smi   # 정상 출력되면 GPU 사용 가능
  ```

> Amazon Linux 2023(EC2)에서 처음 환경을 세팅한다면 이 가이드를 먼저 따라하세요: [Amazon Linux 2023 설치 가이드(CPU/GPU, 포트 80)](docs/al2023-setup.md)

### 1. 코드 받기(1분)

```bash
git clone <repo-url>
cd ocr-fastapi
```

### 2-A. 가장 쉬운 실행(CPU만 사용)

1. 이미지 빌드

```bash
make docker-build
```

2. 서버 실행(8080 포트)

```bash
docker run --rm -p 8080:8080 --name ocr-api ocr-fastapi:dev \
  sh -c "uvicorn app.main:app --host 0.0.0.0 --port 8080"
```

3. 정상 동작 확인

```bash
curl -sS http://localhost:8080/health | jq .
```

보이면 성공(예시 키만 확인):

```json
{"status":"ok", "gpu": { ... }, "version": { ... }}
```

### 2-B. GPU로 실행(선택)

1. GPU 확인 후 이미지 빌드

```bash
make docker-build-gpu
# 중국 공식 인덱스가 필요한 환경이라면(네트워크 이슈):
make docker-build-gpu PADDLE_WHEEL_INDEX=https://www.paddlepaddle.org.cn/whl/linux/gpu
```

2. 서버 실행(인증 키 사용 예시)

```bash
API_KEY=<원하는키>
docker run --rm --gpus all -e API_KEY=$API_KEY -p 8080:8080 --name ocr-api ocr-fastapi:gpu \
  sh -c "uvicorn app.main:app --host 0.0.0.0 --port 8080"
```

> EC2에서 80포트로 외부 노출이 필요하면 `-p 80:8080`으로 매핑하세요. AL2023에서의 전체 절차는 [docs/al2023-setup.md](docs/al2023-setup.md)를 참고하세요.

3. 정상 동작 확인(헬스/간단 OCR)

```bash
curl -sS -H "x-api-key: $API_KEY" http://localhost:8080/health | jq .
curl -sS -H "x-api-key: $API_KEY" http://localhost:8080/ocr -F file=@/etc/hosts | jq .
```

### 3. 서버에서 계속 켜두기(가장 간단한 방법)

백그라운드/자동재시작 옵션으로 실행하면 재부팅에도 살아있습니다.

```bash
docker run -d --restart=always -p 8080:8080 --name ocr-api ocr-fastapi:dev \
  sh -c "uvicorn app.main:app --host 0.0.0.0 --port 8080"
# GPU일 때
docker run -d --restart=always --gpus all -e API_KEY=$API_KEY -p 8080:8080 --name ocr-api ocr-fastapi:gpu \
  sh -c "uvicorn app.main:app --host 0.0.0.0 --port 8080"
```

### 4. AWS에 배포(가장 단순 흐름)

1. ECR 푸시

```bash
make docker-build-gpu   # 또는 make docker-build
aws ecr get-login-password --region <REGION> | docker login --username AWS --password-stdin <acct>.dkr.ecr.<region>.amazonaws.com
docker tag ocr-fastapi:gpu <ECR_URI>
docker push <ECR_URI>
```

2. Terraform 적용

```bash
cd infra/terraform
terraform init \
  -backend-config="bucket=<STATE_BUCKET>" \
  -backend-config="key=ocr-fastapi/terraform.tfstate" \
  -backend-config="region=<REGION>" \
  -backend-config="dynamodb_table=<LOCK_TABLE>"
terraform apply -auto-approve -var="ecr_image=<ECR_URI>"
```

3. 환경 변수(예시)

- `AUTH_MODE=api-key`, `API_KEY=<키>`, `ALLOWED_ORIGINS=https://your-frontend.example.com`

4. 확인

```bash
curl -sS http://<ALB_DNS>/health | jq .
```

### 5. 자주 막히는 포인트(10초 체크)

- 401 에러: `x-api-key` 헤더를 보냈는지, `API_KEY`를 설정했는지 확인
- 8080 충돌: 같은 포트를 쓰는 프로세스 종료 후 재시도
- GPU 미인식: 호스트에서 `nvidia-smi`가 정상인지, `--gpus all` 옵션을 썼는지 확인
- 빌드 실패: 네트워크 이슈면 `PADDLE_WHEEL_INDEX`로 재시도

### 6. 참고(더 알아보기)

- 도커 사용: [docs/docker.md](docs/docker.md)
- 헬스/디버그: [docs/health.md](docs/health.md)
- 인프라/Terraform: [docs/infra-terraform.md](docs/infra-terraform.md)
- 모니터링: [docs/monitoring.md](docs/monitoring.md)
