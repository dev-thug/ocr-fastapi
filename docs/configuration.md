## 설정/환경 변수

- `APP_PORT` (기본 8080)
- `ALLOWED_ORIGINS` (CORS, 콤마 구분)
- `AUTH_MODE` (`cognito` | `api-key`)
- `API_KEY` (api-key 사용 시)
- `MAX_FILE_MB` (기본 10)
- `DEFAULT_LANG` (기본 en)
- `MODEL_DEFAULT` (`pp-ocrv5`)

FastAPI에서 Pydantic Settings로 로드하고, 헬스/메타에 노출하지 않도록 주의합니다.
