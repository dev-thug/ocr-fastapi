# VPC 설계 (1.1)

- CIDR: 10.0.0.0/16
- 서브넷: 퍼블릭 2개, 프라이빗 2개 (2 AZ)
- IGW: 퍼블릭 라우팅(0.0.0.0/0)
- NAT: 단순화를 위해 미구현(필요 시 추가)
- 보안그룹: ECS 인스턴스 SG(egress only)

파일: `infra/terraform/vpc.tf`, `infra/terraform/security-groups.tf`
