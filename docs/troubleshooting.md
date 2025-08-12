## 트러블슈팅

### GPU 미인식

- 원인: 드라이버/런타임 불일치
- 조치: 호스트 NVIDIA 드라이버 버전 확인, Container Toolkit 설치, `--gpus all` 확인

### `/health`에서 Paddle 값이 null 또는 `/ocr`가 stub 반환

- 증상:
  - `/health` → `paddlepaddle`는 보이나 `paddleocr`가 null
  - `/ocr` → `{"text":"stub"}` 반환
- 원인:
  - PaddleOCR 미설치 또는 import 실패(의존 패키지/버전 불일치)
    - NumPy 2.x와 PaddleOCR 2.7.x 호환 이슈
    - OpenCV/Shapely/pyclipper/scikit-image/Scipy 미설치 또는 버전 불일치
- 해결(도커 이미지 기준):
  1. Dockerfile 고정(이미 반영됨)
     - 베이스: `nvidia/cuda:12.9.0-cudnn-runtime-ubuntu22.04`
     - 필수 라이브러리: `libglib2.0-0 libsm6 libxext6 libxrender1 libgomp1 libgl1`
     - 파이썬 패키지 핀:
       - `numpy==1.26.4`
       - `paddlepaddle-gpu==2.6.2` (GPU wheel 제공 버전)
       - `paddleocr==2.7.0`
       - `opencv-python-headless==4.8.1.78 shapely==2.0.2 pyclipper==1.3.0.post5 scikit-image==0.21.0 imgaug==0.4.0 scipy==1.10.1`
  2. 재빌드/재기동
     ```bash
     docker build --no-cache --build-arg PADDLE_WHEEL_INDEX=https://www.paddlepaddle.org.cn/whl/linux/gpu \
       -t ocr-fastapi:gpu -f docker/Dockerfile .
     docker rm -f ocr-api 2>/dev/null || true
     docker run -d --gpus all -e API_KEY=test -p 80:8080 --name ocr-api --restart unless-stopped ocr-fastapi:gpu
     ```
  3. 검증
     ```bash
     curl -sS http://<HOST>/health           # paddleocr 값 채워짐
     curl -sS -H "x-api-key: test" http://<HOST>/ocr -F file=@/etc/hosts  # text가 stub가 아님
     ```

### Docker 빌드 중 No space left on device

- 원인: Paddle GPU wheel(>750MB) 등으로 루트 볼륨/도커 공간 부족
- 해결:
  - 정리:
    ```bash
    docker system prune -af --volumes
    docker builder prune -af
    sudo systemctl restart docker
    ```
  - 루트 EBS 확장(권장): 30GB+로 확장 후 파일시스템 확장(`growpart`, `xfs_growfs`/`resize2fs`)
  - Docker 데이터 루트 이동: `/etc/docker/daemon.json`에 `{"data-root":"/mnt/docker"}` 설정

### OOM

- 원인: 큰 이미지/동시 처리 과다
- 조치: 입력 크기 제한, 워커 축소, 배치 크기 조정

### Latency 증가

- 원인: 콜드스타트/모델 미캐시
- 조치: 시작 시 가중치 프리로드, 헬스체크 시 warmup
