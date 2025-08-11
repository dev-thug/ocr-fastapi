# 4. FastAPI 백엔드 구성(엔드포인트/스키마/CORS)

연관 문서: `docs/api.md`, `docs/configuration.md`, `docs/amplify-integration.md`, `docs/app-backend.md`

## 서브테스크

- [x] 4.1 프로젝트 구조(app/)와 라우터 스켈레톤 생성 — see: `docs/app-backend.md`
- [x] 4.2 요청/응답 스키마 공통 래퍼(success/result/error/meta) — see: `docs/api.md`
- [x] 4.3 CORS 설정(ALLOWED_ORIGINS) 및 OPTIONS 핸들링 — see: `docs/app-backend.md`
- [x] 4.4 예외/에러 응답 표준화 — see: `docs/api.md`

## 승인 기준

- `/health` 200, `/ocr` 모의 입력으로 200/표준 스키마 반환

## 구현 전략

- 구조: `app/main.py`, `app/api/routes.py`, `app/core/config.py`, `app/core/logging.py`
- 스키마: Pydantic v2 모델, 파일 업로드는 `UploadFile` + 사이즈 제한 미들웨어
- 성능: 비동기 라우터 + `asyncio.to_thread`로 CPU 경로 격리, 백그라운드 태스크 활용
- CORS: 환경변수 기반 다중 오리진 허용, 프리플라이트 자동 처리

## 리서치 요약

- 대용량 파일 업로드 시 `UploadFile` 스트리밍 활용이 메모리 효율적(FastAPI/Starlette 권장)
- 에러 핸들러 신설로 일관된 JSON 에러 포맷 유지, 로깅 연계
