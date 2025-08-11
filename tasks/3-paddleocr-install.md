# 3. PaddleOCR 3.1.0 설치 자동화

연관 문서: `docs/docker.md`, `docs/models.md`

## 서브테스크

- [x] 3.1 pip install paddleocr==3.1.0
- [x] 3.2 가중치/사전 캐시 디렉토리 설정(/root/.paddleocr 등)
- [ ] 3.3 콜드스타트 단축을 위한 프리로드 여부 검토 — `app/main.py` startup preload로 토글 가능(settings.preload_models)

## 승인 기준

- 컨테이너 빌드 후 첫 요청 p95가 5s 이내(샘플 이미지)

## 구현 전략

- 모델 캐시 볼륨 마운트(`/models` 또는 `/root/.paddleocr`)로 배포 간 재사용
- 다국어 사용 대비 언어별 리소스 지연 로딩(lazy load) 적용
- 엔트리포인트에서 워밍업(샘플 이미지 소형)으로 콜드스타트 완화

## 리서치 요약

- PaddleOCR는 최초 호출 시 모델 다운로드/로드 시간이 큼 → 캐시/사전-다운로드로 완화
- 언어 모델 분리 로딩을 통해 메모리 사용량과 초기화 시간을 절충

## 메모

- Dockerfile에서 `paddleocr` 설치 및 `/root/.paddleocr` 캐시 디렉토리 생성/ENV 설정 완료.
