# ASG(GPU) / 스케일 정책 (1.4)

- 인스턴스: g4dn.xlarge, Amazon ECS GPU 최적화 AMI
- 서브넷: 프라이빗 2개 AZ
- 스케일: min=1, max=10 (스팟/온디맨드 혼합 가능)
- 관리 스케일: Capacity Provider Managed Scaling ENABLED

파일: `infra/terraform/asg-gpu.tf`
