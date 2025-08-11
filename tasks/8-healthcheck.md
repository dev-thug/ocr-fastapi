# 8. 헬스체크 구현(/health)

연관 문서: `docs/health.md`

## 서브테스크

- [x] 8.1 nvidia-smi 파싱(utilization, memory)
- [x] 8.2 버전 정보 수집(paddlepaddle, paddleocr)
- [x] 8.3 헬스 엔드포인트 응답 스키마 고정

## 승인 기준

- GPU 지표 포함 JSON 반환, 200 OK

## 구현 전략

- 1순위: `pynvml`로 GPU 지표 수집, 2순위: `nvidia-smi` 서브프로세스 폴백
- 메타 포함: 장치(GPU/CPU), 지연 시간(ms), 버전 정보
- 워밍업: 최초 헬스 호출 시 엔진 로드/미니 배치 실행 옵션

## 리서치 요약

- NVML은 성능/정확도 우수하나 드라이버/라이브러리 의존성 존재 → `nvidia-smi` 폴백 유지
- 헬스는 가벼워야 하므로 워밍업은 비동기/옵션 처리 권장
