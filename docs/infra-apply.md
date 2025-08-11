# Terraform 적용/검증 (1.6)

## 준비물

- AWS 자격 증명(프로파일/환경변수)
- S3 버킷(상태 저장), DynamoDB 테이블(락)

## 초기화

```bash
terraform -chdir=infra/terraform init \
  -backend-config="bucket=<S3_BUCKET>" \
  -backend-config="key=ocr-fastapi/terraform.tfstate" \
  -backend-config="region=<AWS_REGION>" \
  -backend-config="dynamodb_table=<DDB_LOCK_TABLE>" \
  -backend-config="encrypt=true"
```

## 계획/적용

```bash
terraform -chdir=infra/terraform plan -out=tfplan
terraform -chdir=infra/terraform apply tfplan
```

## 확인 사항

- VPC/서브넷/IGW 생성 여부
- ECR 리포지토리 URL 출력
- ECS 클러스터 존재 및 Capacity Provider 연결
- ASG 생성 및 인스턴스 기동(조건 충족 시)
