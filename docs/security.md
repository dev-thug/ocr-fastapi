## 보안 가이드

- 인증: Cognito JWT 권장(Amplify Auth), 대안으로 API Key
- 권한: ECS 태스크 IAM 역할 최소 권한, S3 접근 제한
- 네트워크: VPC 프라이빗, ALB만 퍼블릭. SG 최소 포트만 허용
- 전송: TLS(HTTPS) 종단. 내부 통신도 TLS 고려(옵션)
- 입력 검증: 파일 타입/크기(10MB 제한), 이미지 스캐닝(옵션)
- 로깅: PII 최소화(마스킹), 감사 로그 보관 정책
