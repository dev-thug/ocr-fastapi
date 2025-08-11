# 9. 로깅/관찰성 구성

연관 문서: `docs/logging.md`, `docs/monitoring.md`

## 서브테스크

- [ ] 9.1 구조화 로거(uvicorn/fastapi 핸들러) 설정
- [ ] 9.2 요청 ID 상관관계(X-Request-ID) 처리
- [ ] 9.3 에러 코드/트레이스 로깅 규약

## 승인 기준

- CloudWatch에서 JSON 로그 필드가 쿼리 가능

## 구현 전략

- `python-json-logger` 또는 `structlog`로 JSON 포맷 통일, 필수 필드 담기(timestamp, level, request_id, latency_ms, device)
- 요청 ID 미들웨어로 상관관계 유지(ALB/X-Request-ID 연계)
- OpenTelemetry(옵션)로 트레이스/메트릭 연동, X-Ray 대안 검토

## 리서치 요약

- ECS Fargate/EC2 모두 CloudWatch Logs가 기본 경로, 구조화 포맷이 검색/알람에 유리
- OTEL SDK 도입 시 서비스 경계(Amplify→ECS) 추적 가능
