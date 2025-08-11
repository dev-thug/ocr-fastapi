# FastAPI 백엔드 스켈레톤

## 구조

- `app/main.py`: 앱 엔트리포인트, CORS, 라우트(/health, /ocr, /structure, /extraction)
- `app/core/config.py`: Pydantic Settings
- `app/core/logging.py`: structlog 기반 JSON 로깅 설정

## 실행(로컬 가상환경)

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install .
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## 헬스체크

- `/health`: GPU 가시성(NVIDIA 없으면 false), 버전 정보 반환
