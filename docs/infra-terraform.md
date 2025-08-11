## Terraform (IaC)

### 디렉토리 구조 제안

```
infra/terraform/
  backend.tf        # S3/DynamoDB state
  providers.tf
  variables.tf
  vpc.tf
  ecr.tf
  ecs-cluster.tf
  asg-gpu.tf        # g4dn.xlarge ASG + Capacity Provider
  ecs-taskdef.tf    # gpuCount=1, memory/cpu
  ecs-service.tf    # ALB target group/listener
  api-gateway.tf    # (옵션) Amplify 프록시
  outputs.tf
```

### 핵심 포인트

- VPC: /16 CIDR, 2AZ, 퍼블릭/프라이빗 서브넷
- ASG: g4dn.xlarge, 최소 1 ~ 최대 10, 스팟 우선(비용 절감)
- ECS Capacity Provider: ASG 연동, GPU 인스턴스 보장
- Task Definition: resourceRequirements `{ name = "GPU", value = "1" }`
- ALB: HTTPS 리스너, 헬스체크 `/health`
- AMI/유저데이터: NVIDIA 드라이버가 CUDA 12.x 호환인지 확인 (NVIDIA Toolkit 필수)
- API Gateway(옵션): Amplify Gen2와 외부 컨테이너 연동 시

### 참고

- Terraform AWS 공식 레지스트리 모듈 활용 권장
- 원격 상태(백엔드) 필수 설정
