## 헬스체크 설계

- 경로: `GET /health`
- 응답: 상태, 버전, GPU 메트릭(가용 여부/사용률/메모리)
- 구현 팁: `nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader,nounits`
- 런타임 기준: CUDA 12.9 + PaddlePaddle GPU 3.1

예시 응답:

```json
{
  "status": "ok",
  "gpu": { "visible": true, "utilization": 23, "memory_used_mb": 1024 },
  "version": {
    "paddleocr": "3.1.0",
    "paddlepaddle": "3.1",
    "compiled_with_cuda": true
  }
}
```
