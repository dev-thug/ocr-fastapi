# 11. ECS 배포(Terraform) 및 CI/CD

연관 문서: `docs/infra-terraform.md`, `docs/deployment-ci-cd.md`

## 서브테스크

- [x] 11.1 Task Definition(GPU=1) 및 Service+ALB 구성 — see: `infra/terraform/*`
- [x] 11.2 오토스케일링 정책(CPU/GPU/큐) 적용 — see: `infra/terraform/ecs-autoscaling.tf`
- [x] 11.3 GitHub Actions: build→ECR push→terraform apply→deploy — see: `.github/workflows/deploy.yml`

## 승인 기준

- main 브랜치 푸시 시 자동 배포 성공, ALB 헬스체크 그린

## 구현 전략

- GitHub OIDC + `aws-actions/configure-aws-credentials`로 키리스 배포
- 단계화: build/test → push(ECR) → plan → apply → deploy, 실패 시 롤백
- 배포 전략: 롤링 기본, Blue/Green(CodeDeploy) 옵션화

## 리서치 요약

- OIDC는 장기 액세스 키 제거로 보안/관리성 향상
- ALB 타겟 그룹 헬스 체크 경로 `/health`, 임계치/간격으로 다운타임 최소화
