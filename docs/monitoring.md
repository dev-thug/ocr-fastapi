## 모니터링/로깅

### 로그

- FastAPI 구조화 로깅(JSON) → CloudWatch Logs
- 접근/오류/성능 로그 분리 권장

### 지표

- Container Insights: CPU/메모리/네트워크
- GPU 컬렉션: nvidia-smi 기반 스크레이핑(에이전트) 또는 DCGM Exporter

### 알람 예시

- GPU Utilization > 80% (5분 연속)
- 응답 지연 p95 > 5s (ALB Target Group 지표)
- 5xx 에러율 > 1%

### 대시보드

- 지연/에러율/트래픽/GPU 메모리/사용률
