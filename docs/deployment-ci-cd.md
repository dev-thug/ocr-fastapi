## 배포 및 CI/CD

### 파이프라인 단계

1. Lint/Test → 2) Docker Build → 3) ECR Push → 4) Terraform Apply → 5) ECS Deploy(롤링/블루그린)

### GitHub Actions 예시(개요)

```yaml
name: deploy
on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up QL/Poetry (옵션)
        run: |
          python -m pip install --upgrade pip
          pip install poetry
      - name: Build Docker
        run: |
          docker build -t $ECR_REPO:latest -f docker/Dockerfile .
      - name: Login ECR & Push
        run: |
          # aws ecr get-login-password ...
          # docker tag / docker push
      - name: Terraform Apply
        run: |
          cd infra/terraform
          terraform init -input=false
          terraform apply -auto-approve
```

### 배포 전략

- 기본: 롤링 업데이트
- 무중단: Blue-Green (ECS + CodeDeploy)

### Amplify 연동

- Amplify 빌드 훅으로 Next.js 재배포 트리거(선택)
