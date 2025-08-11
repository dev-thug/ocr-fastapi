# Infra Overview

## 구조

- Terraform 루트: `infra/terraform`
  - `providers.tf` / `backend.tf` / `variables.tf`
  - `vpc.tf` / `security-groups.tf`
  - `ecr.tf`
  - `ecs-cluster.tf`
  - `asg-gpu.tf`
  - `outputs.tf`

## 사전 요구사항

- AWS 자격 증명(프로파일/환경변수)
- 원격 상태용 S3 버킷과 DynamoDB 락 테이블
- 리전(기본: ap-northeast-2)

## 초기화/배포

```bash
terraform -chdir=infra/terraform init \
  -backend-config="bucket=<S3_BUCKET>" \
  -backend-config="key=ocr-fastapi/terraform.tfstate" \
  -backend-config="region=<AWS_REGION>" \
  -backend-config="dynamodb_table=<DDB_LOCK_TABLE>" \
  -backend-config="encrypt=true"

terraform -chdir=infra/terraform plan -out=tfplan
terraform -chdir=infra/terraform apply tfplan
```

## 출력 확인

- `vpc_id`, `public_subnets`, `private_subnets`
- `ecr_repository_url`
- `ecs_cluster_name`, `asg_gpu_name`

## 참고 문서

- `docs/infra-vpc.md` / `docs/infra-ecr.md` / `docs/infra-ecs-cluster.md` / `docs/infra-asg-gpu.md` / `docs/infra-remote-state.md` / `docs/infra-apply.md`

## 다음 단계

- ALB/타겟그룹/리스너 + ECS 서비스 정의(작업 11)
- 보안그룹 상세 정책, NAT 게이트웨이 필요 시 추가
