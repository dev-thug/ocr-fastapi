## API 스펙

- 베이스 URL 예시: `https://api.example.com`
- 인증: `Authorization: Bearer <JWT>` 또는 `x-api-key: <KEY>`
- CORS: Amplify 도메인 허용, `OPTIONS` 프리플라이트 지원
- 공통 응답: `StandardResponse`(success/result/error/meta)

### POST /ocr

- 설명: 이미지 OCR + 옵션 파싱/추출
- 입력: `multipart/form-data`
  - `file`: 이미지(JPEG/PNG, 최대 10MB)
  - `lang`(옵션): 기본 `en`
  - `mode`(옵션): `recognition` | `parsing` | `extraction`
  - `model`(옵션): `pp-ocrv5` | `pp-structurev3` | `pp-chatocrv4`
- 응답(JSON):

```json
{
  "success": true,
  "result": {
    "text": "...",
    "boxes": [
      {"box": [[x1,y1],[x2,y2],[x3,y3],[x4,y4]], "text": "...", "score": 0.99}
    ],
    "structure": {"tables": [], "markdown": "..."},
    "extraction": {"entities": []}
  },
  "error": null,
  "meta": {"latency_ms": 1234, "device": "GPU|CPU", "lang": "en"}
}
```

- 예시(cURL):

```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/image.png" \
  -F "lang=en" -F "mode=recognition" \
  https://api.example.com/ocr
```

### POST /structure

- 설명: 문서 파싱 전용(PP-StructureV3)
- 입력: `multipart/form-data` (동일)
- 응답: `result.structure` 중심 반환

### POST /extraction

- 설명: 정보 추출 전용(PP-ChatOCRv4)
- 입력: `multipart/form-data` (동일)
- 응답: `result.extraction` 중심 반환

### GET /health

- 설명: 상태 확인 및 GPU 이용률
- 응답(JSON):

```json
{
  "status": "ok",
  "gpu": { "visible": true, "utilization": 23, "memory_used_mb": 1024 },
  "version": { "paddleocr": "3.1.0", "paddlepaddle": "3.1" }
}
```

## 에러 규격

```json
{
  "success": false,
  "result": null,
  "error": { "code": "BadRequest", "message": "...", "details": {} },
  "meta": { "latency_ms": 0 }
}
```

## 캐싱/리밸런싱

- 대형 이미지: 리사이즈 옵션(서버 내부 파이프라인)
- 재시도: Paddle 엔진 실패 시 1회 재시도, GPU→CPU 폴백

## OpenAPI

- FastAPI로 자동 문서화(`/docs`, `/openapi.json`)
