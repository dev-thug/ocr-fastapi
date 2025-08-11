## OCR 파이프라인

### 지원 컴포넌트

- PP-OCRv5: 다국어 텍스트 인식(80+), 필기체 향상
- PP-StructureV3: 문서 레이아웃/테이블/차트/인장 인식, Markdown/JSON 변환
- PP-ChatOCRv4: ERNIE 기반 정보 추출 파이프라인
- PP-DocTranslation: 문서 번역(옵션, 후속 확장)

### 모드/파라미터

- `mode=recognition` → 인식 중심(텍스트+박스)
- `mode=parsing` → 구조화 결과 중심(StructureV3)
- `mode=extraction` → 엔티티/키밸류 추출 중심(ChatOCRv4)
- `lang` 기본값 `en` (예: `ko`, `ja`, `zh`, `th`, `ar` 등)
- `model` 선택: `pp-ocrv5` | `pp-structurev3` | `pp-chatocrv4` (확장 가능)

### GPU/CPU 폴백

1. GPU 가용 시 CUDA로 실행
2. 예외 발생 시 CPU 폴백 후 1회 재시도
3. 폴백 기록을 로그/메트릭에 남김

### 출력 스키마(요약)

- `text`: 전체 텍스트
- `boxes[]`: `box`(사각형 4점 좌표), `text`, `score`
- `structure`: 테이블/도형/차트/도장 등 문서 요소
- `extraction`: 엔티티/키밸류/요약 등

### 성능 팁

- 배치 크기 및 입력 리사이즈로 지연 단축
- FP16/TensorRT(가능 시) 검토
- 컨테이너 시작 시 모델 프리로드

### 런타임 전제

- PaddlePaddle GPU 3.1 + CUDA 12.9 기준. 설치는 공식 Docker 가이드를 참조: [PaddlePaddle Docker 설치](https://www.paddlepaddle.org.cn/en/install/quick?docurl=/documentation/docs/en/install/docker/linux-docker_en.html)
