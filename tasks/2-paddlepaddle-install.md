# 2. PaddlePaddle GPU 3.1 설치 자동화 (CUDA 12.9)

연관 문서: `docs/docker.md`

## 서브테스크

- [x] 2.1 베이스 이미지: nvidia/cuda:12.9.0-runtime-ubuntu22.04
- [x] 2.2 pip index/wheel 설정 및 paddlepaddle-gpu==3.1.\* 설치 — see: `docker/Dockerfile`
- [ ] 2.3 GPU 가시성 확인(nvidia-smi) 및 간단 셀프체크
- [x] 2.4 모델 프리로드 훅(엔트리포인트 또는 빌드 시) 추가 — see: `app/main.py`(startup preload)

## 승인 기준

- 컨테이너 내부에서 `import paddle; paddle.is_compiled_with_cuda()`가 True

## 구현 전략

- 공식 문서에 따라 CUDA 12.9 호환 wheel/extra-index-url 설정 후 설치
- 런타임 검증: `paddle.utils.run_check()` 및 `nvidia-smi`/`pynvml` 병행 확인
- 이미지 슬림화: 빌드 단계 분리, 캐시 레이어 최적화, 런타임에서 개발 도구 제거

## 리서치 요약

- 공식 설치 가이드: [PaddlePaddle Docker 설치](https://www.paddlepaddle.org.cn/en/install/quick?docurl=/documentation/docs/en/install/docker/linux-docker_en.html)
- CUDA 12.x 대응 wheel 제공 여부는 릴리스 노트/인덱스에 따라 고정, CI에서 설치 검증 파이프 추가
- `nvidia-container-toolkit` 필수, 호스트 드라이버 버전과 컨테이너 런타임의 호환성 확인

## 메모

- Dockerfile에 `PADDLE_WHEEL_INDEX` ARG 반영 및 `RUN_PADDLE_CHECK`로 빌드 시 검증 옵션 제공.
- 런타임 검증은 고우선 태스크 13에서 GPU 환경에서 수행 예정.
