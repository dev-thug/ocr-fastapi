# 14. PP-Structure/ChatOCR 실제 파이프 통합 및 예제 테스트

연관 문서: `docs/ocr-pipeline.md`, `docs/models.md`

## 서브테스크

- [x] 14.1 PP-StructureV3 모델 로딩/테이블/마크다운 검증(초기 통합, 안전 폴백 포함)
- [ ] 14.2 ChatOCRv4(ERNIE) 통합 경로/토큰 설정 조사 및 PoC
- [ ] 14.3 샘플 이미지로 /structure, /extraction e2e 테스트

## 승인 기준

- 두 엔드포인트 모두 샘플 입력으로 정상 구조/엔티티 반환

## 구현 전략

- Structure: table detection + markdown converter 경량 경로 우선 적용
- ChatOCR: 필요 엔진/토큰 의존성 분리, 실패 시 graceful fallback
