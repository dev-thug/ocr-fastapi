# 1. 환경 준비: Terraform으로 ECS GPU 클러스터 프로비저닝

연관 문서: `docs/infra-terraform.md`

## 설명

VPC/서브넷/보안그룹, ECS 클러스터, ECR, ASG(g4dn.xlarge) + Capacity Provider, 원격 상태 구성.

## 서브테스크

- [x] 1.1 VPC/서브넷/라우팅/보안그룹 작성 — see: `docs/infra-vpc.md`
- [x] 1.2 ECR 리포지토리 생성 — see: `docs/infra-ecr.md`
- [x] 1.3 ECS 클러스터/Capacity Provider(g4dn.xlarge) 구성 — see: `docs/infra-ecs-cluster.md`
- [x] 1.4 ASG 스팟 전략 및 스케일 정책 설정 — see: `docs/infra-asg-gpu.md`
- [x] 1.5 Terraform 원격 상태(S3/DynamoDB) 구성 — see: `docs/infra-remote-state.md`
- [ ] 1.6 출력/헬스 검증(terraform plan/apply) — see: `docs/infra-apply.md`
- [ ] 1.6 출력/헬스 검증(terraform plan/apply) — see: `docs/infra-apply.md` (원격 환경에서 수행 필요)

## 승인 기준

- terraform apply 성공, ALB 없이 클러스터/용량 준비 완료
- ECR 로그인/푸시 가능

## 구현 전략

- Terraform 모듈화: `vpc`, `ecr`, `ecs-cluster`, `asg-gpu`, `service-alb`로 분리하여 재사용성 확보
- GPU 인스턴스: `g4dn.xlarge` ASG + Capacity Provider로 스팟 우선, 온디맨드 백업
- AMI: ECS 최적화 GPU AMI 사용(드라이버/NVIDIA Toolkit 사전 포함), 유저데이터에서 에이전트 업데이트만 수행
- 보안: 각 리소스 최소 권한 SG, 태스크 IAM Role 분리(실행/태스크)
- 원격 상태: S3 버킷 + DynamoDB 락으로 팀 협업/충돌 방지

## 리서치 요약

- ECS Capacity Provider로 ASG 기반 GPU 스케일 자동화 권장(AWS 공식 가이드)
- ECS-Optimized GPU AMI 사용 시 드라이버 호환성 이슈 최소화(Amazon Linux 기반 권장)
- 모듈: terraform-aws-modules/vpc, autoscaling, alb 활용
- 참고: AWS ECS Capacity Providers / Terraform AWS Provider 최신 버전
