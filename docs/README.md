# OCR FastAPI Backend (PaddleOCR 3.1.0)

이 문서는 PaddleOCR 기반 OCR 처리용 FastAPI 백엔드 서버 구현과 배포를 빠르게 진행하기 위한 실무 가이드입니다. GPU 기반 ECS 배포, Amplify Gen2 연동, Terraform IaC, CI/CD, 모니터링까지 포함합니다.

- 주요 기술: FastAPI, PaddleOCR 3.1.0, PaddlePaddle GPU 3.1, CUDA 12.9, Docker, AWS ECS(EC2 GPU), ALB, ECR, CloudWatch, Terraform, GitHub Actions, Amplify Gen2
- Python: 3.10, 서버: Uvicorn
- 배포 대상: GPU 워크로드(ECS, g4dn.xlarge), Amplify Gen2와 API 통합 (CORS/인증 고려)
- 설치 레퍼런스: [PaddlePaddle Docker 설치 가이드](https://www.paddlepaddle.org.cn/en/install/quick?docurl=/documentation/docs/en/install/docker/linux-docker_en.html)

## 빠른 시작 체크리스트

1. 인프라(IaC)

- [ ] `infra/terraform`로 VPC, ECS(EC2 GPU), ASG/Capacity Provider, ALB, ECR 구성
- [ ] Terraform backend(S3/DynamoDB) 설정
- [ ] API Gateway(선택)로 프록시 구성 (Amplify Gen2 연동 시)

2. 애플리케이션

- [ ] `docker/Dockerfile` 작성: NVIDIA CUDA 12.9 runtime 베이스, PaddlePaddle GPU 3.1 설치, PaddleOCR 3.1.0 설치
- [ ] `app`에 FastAPI 구현: `/ocr`, `/structure`, `/extraction`, `/health` 엔드포인트
- [ ] CORS/인증 미들웨어 및 설정 적용 (Amplify 도메인, Cognito 또는 API Key)
- [ ] 유닛 테스트(Pytest) 및 부하 테스트 계획

3. 배포/운영

- [ ] GitHub Actions로 Docker 빌드→ECR 푸시→Terraform apply→ECS 서비스 롤링/블루그린
- [ ] CloudWatch 로그/지표(GPU 포함) 설정, 알람 구성
- [ ] Amplify Gen2의 Next.js에서 API 호출 및 인증 검증

## 문서 맵

- 아키텍처: `docs/architecture.md`
- API 스펙: `docs/api.md`
- OCR 파이프라인/모델: `docs/ocr-pipeline.md`, `docs/models.md`
- Docker: `docs/docker.md`
- Terraform(IaC): `docs/infra-terraform.md`
- 배포(CI/CD): `docs/deployment-ci-cd.md`
- 모니터링: `docs/monitoring.md`
- 보안: `docs/security.md`
- 테스트: `docs/testing.md`
- 설정/환경변수: `docs/configuration.md`
- Amplify Gen2 연동: `docs/amplify-integration.md`
- 성능/튜닝: `docs/performance.md`
- 트러블슈팅: `docs/troubleshooting.md`
- 체크리스트: `docs/checklists.md`
- 미정 의사결정/질문: `docs/open-questions.md`

## 현재 미정 사항(확인 필요)

- 인증: Cognito(JWT) vs API Key (Amplify Auth와 연동 여부)
- 입력/출력 JSON 최종 스키마 (추출 결과, 좌표, 신뢰도 필드 표준화)

문서 각 섹션의 상세는 해당 파일을 참고하세요.
