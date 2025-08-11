# PaddleOCR 3.1 FastAPI Application

FastAPI 기반의 PaddleOCR 3.1 OCR(광학 문자 인식) 애플리케이션입니다. Docker Compose를 사용하여 한국어 문서 OCR 서비스를 구축합니다.

## 주요 기능

- 🖼️ 이미지 업로드 및 OCR 처리
- 🇰🇷 한국어 문서 최적화 지원
- 🌍 다국어 지원 (중국어, 영어, 프랑스어, 독일어, 한국어, 일본어)
- 📊 신뢰도 점수 제공
- 💾 결과 데이터베이스 저장
- 📄 페이지네이션 지원
- 🔍 결과 검색 및 필터링
- 🛡️ 파일 업로드 보안 검증
- ⚡ 고성능 PaddleOCR 3.1 엔진
- 🐳 Docker Compose 다중 서비스 구조
- 🔄 자동 헬스체크 및 복구

## 기술 스택

- **FastAPI**: 고성능 웹 프레임워크
- **PaddleOCR 3.1**: 최신 OCR 엔진 (PP-OCRv5)
- **PaddlePaddle 3.1**: 딥러닝 프레임워크
- **Docker Compose**: 다중 컨테이너 오케스트레이션
- **Nginx**: 리버스 프록시 및 로드 밸런서
- **Redis**: 캐싱 (선택사항)
- **SQLAlchemy**: ORM 및 데이터베이스 관리
- **Pydantic**: 데이터 검증 및 직렬화
- **OpenCV**: 이미지 전처리
- **Poetry**: 의존성 관리

## 시스템 요구사항

### 하드웨어

- **CPU**: 4 vCPU 이상 (GPU 사용 시 권장)
- **RAM**: 8GB 이상 (16GB 권장)
- **GPU**: NVIDIA GPU (T4 이상 권장, CUDA 12.9 지원)
- **Storage**: 50GB 이상

### 소프트웨어

- **Docker**: 27.0.3 이상
- **Docker Compose**: v2.29.0 이상
- **NVIDIA Container Toolkit**: GPU 사용 시 필수
- **NVIDIA Driver**: 575.x 이상

## 설치 및 실행

### 1. 저장소 클론

```bash
git clone <repository-url>
cd ocr-fastapi
```

### 2. 환경 변수 설정

```bash
cp env.example .env
# .env 파일을 편집하여 필요한 설정을 변경
```

### 3. Docker Compose 실행

```bash
# 모든 서비스 빌드 및 실행
docker compose up -d

# 로그 확인
docker compose logs -f

# 특정 서비스 로그 확인
docker compose logs -f paddleocr-fastapi
```

### 4. 서비스 상태 확인

```bash
# 서비스 상태 확인
docker compose ps

# 헬스체크 확인
curl http://localhost/health

# API 문서 확인
curl http://localhost/docs
```

## Docker Compose 서비스 구성

### 1. PaddleOCR FastAPI 서비스

- **이미지**: `paddlepaddle/paddle:3.1.0-gpu-cuda12.9-cudnn9.9`
- **포트**: 8000 (내부)
- **기능**: OCR 처리, API 제공
- **GPU**: NVIDIA GPU 지원

### 2. Nginx 서비스

- **이미지**: `nginx:latest`
- **포트**: 80 (HTTP), 443 (HTTPS)
- **기능**: 리버스 프록시, 로드 밸런싱, 보안 헤더

### 3. Redis 서비스 (선택사항)

- **이미지**: `redis:7-alpine`
- **포트**: 6379
- **기능**: 캐싱, 세션 저장

## API 엔드포인트

### OCR 처리

- `POST /api/v1/ocr/upload`: 이미지 업로드 및 OCR 처리
- `GET /api/v1/ocr/results`: OCR 결과 목록 조회 (페이지네이션 지원)
- `GET /api/v1/ocr/results/{id}`: 특정 OCR 결과 조회
- `DELETE /api/v1/ocr/results/{id}`: OCR 결과 삭제

### 시스템 정보

- `GET /api/v1/ocr/languages`: 지원 언어 목록 조회
- `GET /api/v1/ocr/health`: 서비스 상태 확인
- `GET /api/v1/ocr/system-info`: 상세 시스템 정보

## 사용 예시

### 이미지 업로드 및 OCR 처리

```bash
curl -X POST "http://localhost/api/v1/ocr/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@korean_document.jpg" \
  -F "language=korean" \
  -F "confidence_threshold=0.5"
```

### OCR 결과 조회

```bash
curl -X GET "http://localhost/api/v1/ocr/results?page=1&size=10"
```

### 시스템 정보 확인

```bash
curl -X GET "http://localhost/api/v1/ocr/system-info"
```

## PaddleOCR 3.1 설정

### GPU 설정

```yaml
# docker-compose.yml
environment:
  - PADDLE_OCR_USE_GPU=true
  - DEFAULT_LANGUAGE=korean
```

### 성능 최적화

- `PADDLE_OCR_USE_MP=true`: 멀티프로세싱 활성화
- `PADDLE_OCR_ENABLE_MKLDNN=true`: Intel MKL-DNN 최적화
- `PADDLE_OCR_DROP_SCORE=0.5`: 최소 신뢰도 임계값

## 지원 언어

- `korean`: 한국어 (기본)
- `ch`: 중국어
- `en`: 영어
- `french`: 프랑스어
- `german`: 독일어
- `japan`: 일본어

## 문제 해결

### GPU 관련 문제

```bash
# NVIDIA 드라이버 확인
nvidia-smi

# Docker GPU 테스트
docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi

# NVIDIA Container Toolkit 재설치
sudo nvidia-ctk runtime configure --runtime=docker --force
sudo systemctl restart docker
```

### 서비스 연결 문제

```bash
# 네트워크 확인
docker network ls
docker network inspect ocr-fastapi_ocr-net

# 컨테이너 재시작
docker compose restart
```

### 모델 로딩 문제

```bash
# 로그 확인
docker compose logs paddleocr-fastapi

# 컨테이너 내부 확인
docker exec -it paddleocr-fastapi-service bash
```

## 성능 최적화

### GPU 사용 시

- 5-10배 속도 향상
- 배치 처리 지원
- 메모리 사용량 최적화

### 확장성

```bash
# 서비스 스케일링
docker compose up --scale paddleocr-fastapi=3

# 로드 밸런싱
# nginx.conf에서 upstream 설정 수정
```

## 모니터링

### 로그 모니터링

```bash
# 실시간 로그
docker compose logs -f

# 특정 서비스 로그
docker compose logs -f paddleocr-fastapi
```

### 메트릭 수집

- Prometheus + Grafana 설정 가능
- CloudWatch 연동 (AWS 환경)

## 보안

### Nginx 보안 헤더

- X-Frame-Options
- X-XSS-Protection
- X-Content-Type-Options
- Content-Security-Policy

### Rate Limiting

- API 요청 제한: 10 req/s
- Burst 허용: 20 req/s

## 배포

### 프로덕션 환경

```bash
# 프로덕션 빌드
docker compose -f docker-compose.prod.yml up -d

# SSL 인증서 설정
# nginx.conf에서 HTTPS 블록 활성화
```

### AWS EC2 배포

```bash
# EC2 인스턴스 생성 (g4dn.xlarge 권장)
# NVIDIA 드라이버 설치
# Docker 및 Docker Compose 설치
# 애플리케이션 배포
```

## 개발

### 로컬 개발

```bash
# 개발 모드 실행
docker compose -f docker-compose.dev.yml up -d

# 코드 변경 시 자동 재시작
# 볼륨 마운트로 코드 동기화
```

### 테스트

```bash
# 단위 테스트
docker compose exec paddleocr-fastapi poetry run pytest

# 통합 테스트
curl -X POST "http://localhost/api/v1/ocr/upload" \
  -F "file=@test_image.jpg" \
  -F "language=korean"
```

## 라이선스

MIT License

## 작성자

**Hyunjoong Kim**

- 📧 이메일: [de0978@gmail.com](mailto:de0978@gmail.com)
- 🌐 웹사이트: [https://hyunjoong.kim](https://hyunjoong.kim)
- 💻 GitHub: [https://github.com/dev-thug](https://github.com/dev-thug)

## 기여

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 참고 자료

- [PaddleOCR 공식 문서](https://paddlepaddle.github.io/PaddleOCR/)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Docker Compose 공식 문서](https://docs.docker.com/compose/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/)
