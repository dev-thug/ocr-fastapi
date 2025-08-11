## 로깅 전략

- 포맷: JSON (구조화)
- 필드: timestamp, level, message, request_id, path, latency_ms, device(GPU/CPU), error_code
- 샘플레이트: 정상 요청 샘플링, 에러는 전체 수집
- 상관관계: ALB/Nginx X-Request-ID 전달
