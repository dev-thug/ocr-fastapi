## 아키텍처 개요

- 백엔드: FastAPI on ECS(EC2 GPU, g4dn.xlarge) + ALB
- 컨테이너: Docker(nvidia/cuda:12.9.0-runtime-ubuntu22.04)
- 모델: PaddleOCR 3.1.0, PaddlePaddle GPU 3.1
- 프록시: API Gateway(선택, Amplify Gen2와 연결 시)
- 스토리지: S3(Amplify Storage), Presigned URL
- 관측성: CloudWatch Logs/Container Insights(GPU), 알람

```mermaid
graph TD
  A[Next.js (Amplify Gen2)] -->|HTTPS| B[API Gateway (옵션)]
  B -->|Private/HTTPS| C[ALB]
  A -->|HTTPS (직접연결 대안)| C
  C --> D[ECS Service (GPU)]
  D --> E[FastAPI (Uvicorn)]
  E --> F[PaddleOCR 3.1.0 + PaddlePaddle 3.1]
  E --> G[S3 Presigned URL (입력 이미지)]
  E --> H[CloudWatch Logs]
  D --> I[CloudWatch Container Insights - GPU/CPU/Mem]
  E -.-> J[AppSync(GraphQL, 대안)]
```

- 기본 경로: Amplify(Next.js) → (옵션) API Gateway → ALB → ECS(FastAPI)
- 인증: Cognito JWT(권장) 또는 API Key (Amplify Auth 통합)
- 내부 네트워킹: VPC 프라이빗 서브넷, 보안그룹 최소 권한
- 확장: ECS 오토스케일링(GPU 지표 기반), 무중단 배포(Blue-Green 선택)
