# 7. 인증/권한 및 CORS(Amplify 연동)

연관 문서: `docs/amplify-integration.md`, `docs/security.md`

## 서브테스크

- [x] 7.1 AUTH_MODE(cognito|api-key) 설정 및 미들웨어 — see: `app/api/auth.py`
- [x] 7.2 JWT 검증 로직 또는 API Key 헤더 검증 — API Key 완료, Cognito는 설정값 필요
- [x] 7.3 CORS 프리플라이트 및 헤더 노출 설정 — see: `app/main.py`

## 승인 기준

- Amplify 도메인에서 브라우저 호출 시 CORS 에러 없음

## 구현 전략

- Cognito 권장: JWKS 캐시 기반 `python-jose` 검증, `aud/iss` 체크 및 만료 처리
- API Key는 내부/자동화 용도로만 제한, 레이트리밋/WAF 연계
- CORS 오리진 화이트리스트 환경변수화, 인증 헤더 노출 설정

## 리서치 요약

- Amplify Auth(JWT) + ALB/ECS 조합이 표준적이며, AppSync 대안은 권한/캐싱 요건에 따라 선택
- JWKS 주기적 리프레시와 키 회전 대응 필요, 401/403 응답 표준화

## 메모

- Cognito 사용 시 환경변수 필요: `AUTH_MODE=cognito`, `COGNITO_ISSUER`, `COGNITO_AUDIENCE`.
