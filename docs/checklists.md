## 구현 체크리스트

### 인프라(IaC)

- [ ] VPC/서브넷/라우팅/보안그룹
- [ ] ECS 클러스터/Capacity Provider(ASG g4dn)
- [ ] ECR/ALB/타겟그룹/리스너
- [ ] (옵션) API Gateway

### 앱

- [ ] FastAPI 라우터 `/ocr` `/structure` `/extraction` `/health`
- [ ] Pydantic 모델/유효성 검사
- [ ] CORS/인증 미들웨어
- [ ] 로깅/에러 핸들링

### 배포/운영

- [ ] Dockerfile (CUDA 11.8, PaddlePaddle GPU, PaddleOCR 3.1.0)
- [ ] GitHub Actions(ECR 푸시, Terraform apply)
- [ ] CloudWatch 로그/지표/알람
- [ ] Amplify 연동 테스트
