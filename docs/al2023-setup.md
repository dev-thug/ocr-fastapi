## Amazon Linux 2023 설치 가이드 (CPU/GPU, 포트 80 노출)

본 문서는 Amazon Linux 2023(AMZN2023) 환경에서 `ocr-fastapi`를 빠르게 실행하는 방법을 정리합니다. GPU는 선택 사항이며, 먼저 CPU로 확인 후 GPU를 활성화하는 순서를 권장합니다.

### 사전 준비

- EC2 인스턴스 보안그룹 인바운드에 TCP 80 허용
- GPU 사용 시: GPU 인스턴스(g4dn/g5 등) 선택

---

### 1) 기본 설치(Docker, Git, Make)

```bash
sudo dnf update -y
sudo dnf install -y docker git make
sudo systemctl enable --now docker

# 현재 사용자에 docker 권한 부여 후 현재 세션에 즉시 반영
sudo usermod -aG docker ec2-user
newgrp docker   # (또는 SSH 재접속)
```

### 2) 소스 받기 및 이미지 빌드

```bash
cd ~
git clone https://github.com/dev-thug/ocr-fastapi.git
cd ocr-fastapi

# GPU 이미지 빌드(일반 CPU 실행도 동일 이미지 사용 가능)
make docker-build-gpu
# 네트워크 이슈 시 중국 인덱스 사용 예:
# make docker-build-gpu PADDLE_WHEEL_INDEX=https://www.paddlepaddle.org.cn/whl/linux/gpu
```

### 3) 포트 80으로 즉시 실행(먼저 CPU로 확인)

```bash
docker rm -f ocr-api 2>/dev/null || true
docker run -d -e API_KEY=test -p 80:8080 --name ocr-api --restart unless-stopped \
  ocr-fastapi:gpu \
  uvicorn app.main:app --host 0.0.0.0 --port 8080
```

한글+영어 실행

```bash
docker run -d --gpus all \
  -e API_KEY=test \
  -e PRELOAD_MODELS=true \
  -e PRELOAD_LANGS=korean,en \
  -e PADDLE_USE_GPU=true \
  -p 80:8080 --name ocr-api --restart unless-stopped ocr-fastapi:gpu
```

- 확인: `http://<EC2-퍼블릭IP>/health`, `http://<EC2-퍼블릭IP>/docs`

---

## GPU 활성화(선택)

호스트에 NVIDIA 드라이버가 설치되어야 컨테이너에서 GPU를 인식합니다. AMZN2023 전용 리포지토리와 모듈 스트림을 사용합니다.

### 4) AMZN2023 전용 CUDA 리포지토리 추가

```bash
# (있다면) RHEL9용 CUDA repo 비활성화/삭제
sudo dnf config-manager --set-disabled cuda-rhel9-x86_64 || true
sudo rm -f /etc/yum.repos.d/cuda-rhel9.repo || true

# AMZN2023 전용 repo 추가
sudo dnf config-manager --add-repo \
  https://developer.download.nvidia.com/compute/cuda/repos/amzn2023/x86_64/cuda-amzn2023.repo
sudo dnf clean all
sudo dnf makecache
```

### 5) NVIDIA 드라이버 설치(모듈 스트림)

```bash
# GPU 장치 존재 확인(없으면 GPU 인스턴스 아님)
lspci | grep -i nvidia

sudo dnf module reset -y nvidia-driver
sudo dnf module enable -y nvidia-driver:latest-dkms
sudo dnf module install -y nvidia-driver:latest-dkms

sudo reboot
```

재부팅 후 확인:

```bash
nvidia-smi
```

### 6) NVIDIA Container Toolkit 설정

```bash
sudo dnf -y install nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# 컨테이너에서 GPU 인식 테스트
docker run --rm --gpus all nvidia/cuda:12.9.0-runtime-ubi8 nvidia-smi
```

### 7) GPU 사용해 포트 80으로 실행

```bash
docker rm -f ocr-api 2>/dev/null || true
docker run -d --gpus all -e API_KEY=test -p 80:8080 --name ocr-api --restart unless-stopped \
  ocr-fastapi:gpu \
  uvicorn app.main:app --host 0.0.0.0 --port 8080
```

---

## 트러블슈팅

- Docker 권한 오류(permission denied): `newgrp docker` 또는 SSH 재접속
- `All matches were filtered out … cuda-drivers`: AMZN2023 전용 repo(`cuda-amzn2023`) + `nvidia-driver:latest-dkms` 사용
- `libnvidia-ml.so.1` 에러 / `nvidia-smi` 없음: 호스트 드라이버 미설치 → 5단계 다시 수행
- GPU 미탑재 인스턴스: `lspci | grep -i nvidia` 결과가 없으면 GPU 인스턴스(g4dn/g5 등) 필요
- 포트 80 접근 불가: 보안그룹 인바운드 TCP 80 허용 여부 점검

---

## 관련 문서

- Docker 사용: [docs/docker.md](./docker.md)
- 헬스/운영: [docs/health.md](./health.md)
- GPU 검증/팁: [docs/gpu-verify.md](./gpu-verify.md)
