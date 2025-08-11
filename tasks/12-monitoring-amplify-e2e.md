# 12. 모니터링/알람 및 Amplify 연동 E2E 테스트

연관 문서: `docs/monitoring.md`, `docs/amplify-integration.md`

## 서브테스크

- [x] 12.1 로그 그룹/대시보드 생성 및 유지정책 설정 — `infra/terraform/ecs-service.tf`, `monitoring.tf`
- [x] 12.2 알람 설정(GPU>80%, p95>5s, 5xx>1%) — `infra/terraform/monitoring.tf`
- [ ] 12.3 Amplify Next.js에서 API 호출 E2E 검증

### 참고

- ALB p95, Target 5xx, GPU Utilization 알람 리소스: `infra/terraform/monitoring.tf`

## 승인 기준

- 알람 정상 발송, Amplify→ECS 호출 성공

## 구현 전략

- Container Insights 활성화, GPU 메트릭 수집(DCGM Exporter 대안 검토)
- 지표 기반 알람: ALB Target p95/p99, 5xx 비율, GPU Utilization/Memory
- E2E: Amplify Server Component에서 인증 토큰 포함 폼업로드 테스트

## 리서치 요약

- GPU 메트릭은 DCGM Exporter가 세밀하지만 관리 오버헤드 ↑ → Container Insights 우선, 보완적으로 Exporter 도입 검토
- Next.js(Server Actions)에서 FormData 업로드시 CORS/인증 헤더 동작 검증 필요

## 메모

- 배포 완료 후 CloudWatch 로그 그룹(`/ecs/ocr-fastapi`)과 ALB TG 지표를 대시보드/알람에 연결.
