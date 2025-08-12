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

## 모델 프리로드(콜드스타트 감소)

- 환경변수로 프리로드를 제어합니다.
  - `PRELOAD_MODELS=true`일 때 서버 기동 시 모델을 미리 로드합니다.
  - `PRELOAD_LANGS`에 쉼표로 구분된 언어 목록을 지정하면 다국어를 순차 프리로드합니다. 미지정 시 `default_lang`만 프리로드됩니다.

예시(영어+한국어 프리로드)

```bash
docker run -d --gpus all \
  -e API_KEY=test \
  -e PRELOAD_MODELS=true \
  -e PRELOAD_LANGS=en,korean \
  -p 80:8080 --name ocr-api --restart unless-stopped ocr-fastapi:gpu
```

서버 로그에 `preload_model` 이벤트가 언어별로 출력되며, 첫 요청 지연이 줄어듭니다.
