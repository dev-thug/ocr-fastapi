FROM nvidia/cuda:12.9.0-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 python3.10-venv python3-pip git curl ca-certificates \
    libglib2.0-0 libsm6 libxext6 libxrender1 libgomp1 libgl1 \
 && rm -rf /var/lib/apt/lists/*

RUN python3.10 -m pip install --upgrade pip poetry
WORKDIR /app

COPY pyproject.toml ./
RUN poetry config virtualenvs.create false \
 && poetry install --only main --no-interaction --no-ansi --no-root

# Paddle 관련 설치 (공식 가이드에 맞춰 wheel 인덱스 경로를 전달 가능)
ARG PADDLE_WHEEL_INDEX=https://www.paddlepaddle.org.cn/whl/linux/gpu
# Note: As of now, 3.x wheels are not available on the GPU index above. Pin to 2.6.2 which is published.
RUN pip install --no-cache-dir --extra-index-url ${PADDLE_WHEEL_INDEX} "paddlepaddle-gpu==2.6.2" \
 && pip install --no-cache-dir "paddleocr==2.7.0"

# 캐시 디렉토리 준비
ENV PADDLEOCR_HOME=/root/.paddleocr
RUN mkdir -p /root/.paddleocr

# 선택적 빌드 검증: paddle run_check (GPU 환경 아닐 때 실패할 수 있으므로 스킵 가능)
ARG RUN_PADDLE_CHECK=false
RUN if [ "$RUN_PADDLE_CHECK" = "true" ]; then \
      python3 -c "import sys;\nimport paddle;\nfrom paddle.utils.run_check import run_check;\nprint('paddle version:', getattr(paddle, '__version__', None));\ntry:\n    run_check();\n    print('paddle run_check: OK')\nexcept Exception as e:\n    print('paddle run_check failed:', e, file=sys.stderr)" || true; \
    fi

COPY app/ /app/app/
EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
