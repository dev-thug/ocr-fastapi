## 모델 관리

- PaddleOCR: 3.1.0 고정(릴리스 태그 기준)
- PaddlePaddle(GPU): 3.1 (CUDA 12.9 호환)

### 다운로드/캐시

- 컨테이너 빌드 시 주요 가중치 사전 다운로드로 콜드스타트 단축
- `/models` 또는 `/root/.paddleocr` 캐시 디렉터리 사용

### 다국어

- `lang` 파라미터에 따라 알맞은 언어 모델/사전 로딩

### 향후 확장

- 새 릴리스 추가 시 `model` 파라미터 확장 → 백엔드 팩토리에서 라우팅

### 설치 레퍼런스

- 공식 가이드(필수 확인): [PaddlePaddle Docker 설치](https://www.paddlepaddle.org.cn/en/install/quick?docurl=/documentation/docs/en/install/docker/linux-docker_en.html)
