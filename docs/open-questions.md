## 미정 의사결정/질문

1. 인증 방식

- 후보: Cognito(JWT) vs API Key (또는 혼합)
- 제안: Cognito 기본, 내부/자동화 용도만 API Key 보조

2. 입력/출력 스키마 확정

- 제안: `success/result/error/meta` 공통 래퍼 고정, `boxes/structure/extraction`는 옵션 키

3. 최대 파일 크기/형식

- 제안: 10MB, JPEG/PNG 우선. PDF/멀티페이지는 후속 스코프

4. API Gateway 여부

- 제안: Amplify 연결/보안/AWS WAF 적용 필요 시 사용

5. 번역 파이프라인(문서 번역)

- 제안: 1차 릴리스 제외, v2에서 추가
