# 13. GPU/Paddle 검증(휠 인덱스/컴파일 옵션) 및 /health CUDA 확인

연관 문서: `docs/docker.md`, `docs/health.md`, `docs/gpu-verify.md`

## 서브테스크

- [x] 13.1 PADDLE_WHEEL_INDEX 최종 확정 및 이미지 빌드 — run: `make docker-build-gpu PADDLE_WHEEL_INDEX=...`
- [x] 13.2 빌드 단계 paddle.utils.run_check() 시도(RUN_PADDLE_CHECK=true) — GPU 미가용 시 무시
- [ ] 13.3 /health에서 compiled_with_cuda=true 확인(GPU 환경) — run: `make gpu-verify`

## 승인 기준

- GPU가 달린 환경에서 Paddle CUDA 컴파일 확인 및 /health 반영

## 구현 전략

- NVIDIA Container Toolkit 설치 상태 점검 후 `--gpus all`로 실행
- 필요한 경우 Paddle wheel 인덱스/버전 고정 및 캐시 활용
- Makefile 또는 `scripts/gpu_verify.sh` 사용
