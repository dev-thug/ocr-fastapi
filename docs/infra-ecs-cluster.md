# ECS 클러스터/용량 공급자 (1.3)

- 클러스터: `${project}-cluster`
- 용량: EC2 ASG(g4dn.xlarge) + Capacity Provider 연결
- 관리 스케일: ENABLED, 종료 보호 ENABLED

파일: `infra/terraform/ecs-cluster.tf`, `infra/terraform/asg-gpu.tf`
