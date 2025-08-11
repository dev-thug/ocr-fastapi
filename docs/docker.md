## Docker 가이드

- 베이스: `nvidia/cuda:12.9.0-runtime-ubuntu22.04`
- Python: 3.10 (Ubuntu 22.04 기본 제공)
- 패키지: PaddlePaddle GPU 3.1 (CUDA 12.9 대응), PaddleOCR 3.1.0
- 런타임: Uvicorn
- 참조: [PaddlePaddle Docker 설치 가이드](https://www.paddlepaddle.org.cn/en/install/quick?docurl=/documentation/docs/en/install/docker/linux-docker_en.html)

### 예시 스케치

```Dockerfile
FROM nvidia/cuda:12.9.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 python3.10-venv python3-pip git wget curl \
 && rm -rf /var/lib/apt/lists/*

# 가상환경(Optional) 또는 시스템 Python 사용
RUN python3.10 -m pip install --upgrade pip

# PaddlePaddle GPU 3.1 설치 (공식 wheel 경로/extra-index-url은 최신 문서에 따라 설정)
# RUN pip install --extra-index-url <PADDLE_WHEEL_INDEX> "paddlepaddle-gpu==3.1.*"

# PaddleOCR 3.1.0
RUN pip install paddleocr==3.1.0

# 앱 의존성 (Poetry 권장)
# COPY pyproject.toml poetry.lock ./
# RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# 애플리케이션
# COPY app/ /app
# WORKDIR /app
# EXPOSE 8080
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 빌드/실행 테스트

```bash
docker build -t ocr-fastapi:dev -f docker/Dockerfile .
# 로컬 GPU 테스트 (NVIDIA Container Toolkit 필요)
docker run --rm --gpus all -p 8080:8080 ocr-fastapi:dev
```
