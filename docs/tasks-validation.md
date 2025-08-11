# 테스크 검증 가이드

## 로컬 검증

```bash
make validate-tasks
make tf-fmt
make tf-validate
```

## CI 검증

- GitHub Actions: `.github/workflows/validate.yml`
  - tasks JSON/링크 검증
  - terraform fmt/validate

## 원칙(메모)

- 모든 작업/서브테스크 완료 시 문서를 작성/갱신하고, `tasks/*.md`에서 링크로 연결
- 테스크/문서 일관성은 커밋 시점에 항상 유효해야 함
