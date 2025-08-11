# Terraform 원격 상태 (1.5)

- S3 버킷: 버전 관리 + 암호화
- DynamoDB: state lock 테이블
- 변수: `tf_state_bucket`, `tf_lock_table`

파일: `infra/terraform/backend.tf`, `infra/terraform/variables.tf`
