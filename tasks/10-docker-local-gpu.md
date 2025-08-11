# 10. Docker 컨테이너화 및 로컬 GPU 실행

연관 문서: `docs/docker.md`

## 서브테스크

- [x] 10.1 Dockerfile 구현 및 이미지 빌드 — run: `make docker-build`
- [x] 10.2 로컬 GPU 실행 스크립트/Makefile — run: `make docker-run-gpu`, `scripts/gpu_verify.sh`
- [x] 10.3 기본 헬스체크 및 엔드포인트 스모크 테스트 — run: `make docker-run && make smoke-health && make smoke-ocr && make docker-stop`

## 승인 기준

- `docker run --gpus all` 환경에서 /health, /ocr 정상 동작

## 구현 전략

- `Makefile` 타깃: build/run/test/logs, `--gpus all` 기본 포함
- 개발 루프 단축: 바인드 마운트 + `--reload` (개발용 전용 이미지)
- nvidia-container-toolkit 설치 안내 및 드라이버 버전 체크 스크립트 제공

## 리서치 요약

- 로컬 환경 불일치로 인한 GPU 인식 실패가 잦음 → 사전 체크 스크립트로 진단 자동화 필요
- 개발용/배포용 Dockerfile 분리 시 속도/보안 모두 유리
