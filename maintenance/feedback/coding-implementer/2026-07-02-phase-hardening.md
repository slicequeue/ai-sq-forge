---
component: coding-implementer
source: pasta-japan-server 6월 사고 사이클
date: 2026-07-02
type: phase-hardening
severity: medium
---

## 증상

v0.3 오케스트레이터로 격상 후 첫 사이클(2026-06). 위임 스킬(java-spring-coder / self-code-reviewer)에서 발견된 신규 사고 패턴이 Phase 체크리스트에 반영 안 됨.

## 개선 반영 (v0.4)

### Phase 0 현황 점검 (신규 항목 7)
- 신규 패키지 필요 시 **첫 커밋부터** `domain/application/infrastructure` 폴더 강제 (사고 7/1 access 재편 반영)

### Phase 3-4 자체 리뷰 (신규 강조)
- self-code-reviewer v1.10 신규 룰: Bean Qualifier cross-module 검증 강조
- 신규 인터페이스 도입 시 → 사용 모든 모듈에 구현체 존재 확인

### Phase 3-6 커밋 세분화 원칙 (신규 블록)
- 대형 리네임: enum → 참조 → 문자열 → 테스트 → 설정 → 문서 순 개별 커밋 (safe-mass-rename 스킬 위임)
- 외부 API hotfix: fix 1 + test 1 최소 2커밋, **재현 테스트가 fix보다 먼저**
- 리팩터·기능 추가 절대 같은 커밋 금지

### 자기 검증 #13~#15 신규 3항목

## 하드 가드레일 유지

기존 7건 유지. 오케스트레이터 정체성은 v0.3 그대로.

## 누적 검토

v0.3 격상 후 마이너 bump. 다음 실전 적용 시 위임 스킬 v1.10과 통합 검증 필요.
