#!/usr/bin/env bash
set -euo pipefail

: "${PADDLE_WHEEL_INDEX:=https://www.paddlepaddle.org.cn/whl/linux/gpu}"
: "${API_KEY:=}"

if [[ -z "${API_KEY}" ]]; then
  echo "API_KEY env is required for auth (or unset api_key in settings)." >&2
  exit 1
fi

echo "[1/3] Build GPU image with paddle check..."
docker build --build-arg PADDLE_WHEEL_INDEX="${PADDLE_WHEEL_INDEX}" \
             --build-arg RUN_PADDLE_CHECK=true \
             -t ocr-fastapi:gpu -f docker/Dockerfile .

echo "[2/3] Run container with --gpus all..."
docker run --rm --gpus all -e API_KEY=${API_KEY} -p 8080:8080 --name ocr-api-dev \
  ocr-fastapi:gpu sh -c "uvicorn app.main:app --host 0.0.0.0 --port 8080" &
PID=$!
sleep 3

echo "[3/3] Verify endpoints..."
curl -sS -H "x-api-key: ${API_KEY}" http://localhost:8080/health | jq .
curl -sS -H "x-api-key: ${API_KEY}" http://localhost:8080/debug/paddle | jq .

echo "Stopping container..."
docker rm -f ocr-api-dev >/dev/null 2>&1 || true
