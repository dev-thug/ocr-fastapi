# 5. OCR 엔진 파이프라인 구현(인식/파싱/추출)

연관 문서: `docs/ocr-pipeline.md`, `docs/models.md`

## 서브테스크

- [x] 5.1 recognition 모드 구현(text+boxes+score) — 스텁/파들 연동 기초 완료
- [x] 5.2 parsing 모드 구현(PP-StructureV3) — `app/ocr/paddle_backend.py` parse_structure 폴백 포함
- [ ] 5.3 extraction 모드 구현(PP-ChatOCRv4)
- [x] 5.4 lang/model 선택 파이프라인 팩토리 — `mode`에 따라 엔진 경로 라우팅 구현

## 승인 기준

- 세 모드 각각 샘플 입력으로 정상 결과(JSON) 반환

## 구현 전략

- 파이프라인 팩토리: `mode`/`model`/`lang`에 따라 엔진 선택, 인터페이스 통일
- 리소스 관리: GPU 세션 재사용, 메모리 누수 방지를 위한 컨텍스트 관리
- 결과 표준화: boxes/structure/extraction를 옵션 필드로 병합, 신뢰도(score) 포함

## 리서치 요약

- 구조화 파싱(StructureV3)와 인식 파이프를 분리하여 독립 스케일링 가능(향후 마이크로서비스화)
- 멀티이미지 배치 경로 도입 시 처리량 향상, 단일 요청 지연은 트레이드오프
