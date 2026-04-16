# Guardrails and Quality Gates

## 문서 가드레일
- PRD/TDD 혼합 금지: 타입이 섞이면 문서를 분리한다.
- admin 특화 3축(`sidebar`, `security`, `admin history`) 누락 금지.
- 표/체크리스트 누락 금지: 자유서술만으로 제출하지 않는다.
- (권장) 다단계 구현 시 **SSOT**와 **`works/` 실행 계획**의 역할을 혼동하지 않는다. 스펙 변경은 SSOT 우선.
- (권장) Thymeleaf·static·sidebar 정합은 Cursor **14·16**; 모듈 경계는 **13** — Phase TODO 또는 `works/`에 드러낼 것.

## Red Flags (즉시 재작성 신호)
1. 수용 기준 없는 요구사항
2. 권한 정책 없는 관리자 기능
3. 이력 기록 정책 없는 변경 기능
4. Phase 목표/검증 기준이 추상적
5. Open Questions 부재(가정 숨김)

## 품질 게이트
- Blocker 항목 하나라도 FAIL이면 제출 불가.
- Blocker PASS 후 Recommend 항목을 보완한다.

## 제출 전 5분 점검
- 타입 확정 -> 템플릿 충족 -> Phase 실행성 -> 리스크/질문 -> 점수 기입
