---
component: coding-implementer
source: forge 내부
date: 2026-05-21
type: convention-mismatch
severity: medium
---

## 증상

coding-implementer 에이전트는 `java-spring-coder` 스킬과 본질적으로 같은 영역(Spring Boot 4-Tier 구현). forge 표준에는 한 영역에 두 컴포넌트가 있으면 사용자 혼란.

## 개선 제안 (coding-implementer v0.2)

본문 "v0.2 보강" 섹션에 명시:

1. **역할 경계**: skill vs agent 형태 차이 표
2. **가드레일 위임**: 모든 코딩 가드레일·자기 검증은 `java-spring-coder` v1.9를 정본. coding-implementer는 중복 정의 안 함.
3. **판단 기준**: 일반 구현 → skill / 컨텍스트 격리 필요한 대량 구현 → agent
4. **통합 검토 필요**: 사용자 결정 대기 (현재 v0.2는 agent 형태 유지 선택)

## 누적 검토

forge 등록 직후 첫 보강. 본질적 통합 검토는 다음 마일스톤 (v0.3+).
