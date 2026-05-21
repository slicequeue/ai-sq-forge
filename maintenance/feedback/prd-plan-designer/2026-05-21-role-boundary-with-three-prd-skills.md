---
component: prd-plan-designer
source: forge 내부
date: 2026-05-21
type: convention-mismatch
severity: medium
---

## 증상

prd-plan-designer 에이전트는 forge에 있는 3개 스킬(prd-designer / tdd-designer / admin-prd-plan-designer)과 영역이 겹침. 사용자 혼란 위험.

## 개선 제안 (prd-plan-designer v0.2)

본문 "v0.2 보강" 섹션:

1. **역할 경계 표**: 4개 컴포넌트 (이 에이전트 + 3개 스킬) 차별 가치 비교
2. **판단 기준**: 단일 문서 → 각 스킬 / **PRD + TDD 통합 산출** → 이 에이전트
3. **가드레일 위임**: PRD는 prd-designer v1.2 / TDD는 tdd-designer v1.4 정본
4. **통합 검토 필요**: 차별 가치(통합 산출)가 명확하지 않으면 폐기 후보. 또는 PRD ↔ TDD 일관성 검사·매핑 표 자동 생성 같은 본질 추가

## 누적 검토

forge 등록 직후 첫 보강. 본질적 통합 검토 다음 마일스톤.
