# GPU 검증 가이드 (CUDA 12.9 기준)

## 사전 준비

- NVIDIA 드라이버 + NVIDIA Container Toolkit 설치
- API 키(또는 Cognito) 준비

## 빌드 및 검증(선택 1: Makefile)

```bash
make docker-build-gpu PADDLE_WHEEL_INDEX=https://www.paddlepaddle.org.cn/whl/linux/gpu
API_KEY=<your-key> make gpu-verify
```

## 빌드 및 검증(선택 2: 스크립트)

```bash
API_KEY=<your-key> \
PADDLE_WHEEL_INDEX=https://www.paddlepaddle.org.cn/whl/linux/gpu \
bash scripts/gpu_verify.sh
```

## 기대 결과

- `/health`: `compiled_with_cuda: true`
- `/debug/paddle`: `available: true`, `run_check: true`
