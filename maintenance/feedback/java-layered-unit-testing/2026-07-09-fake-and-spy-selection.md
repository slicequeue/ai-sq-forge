---
component: java-layered-unit-testing
source: pasta-japan-server PR #0df4473548 (2026-07-07)
date: 2026-07-09
type: pr-review-absorption
severity: medium
---

## 증상

GLOB-566 PR 리뷰 반영에서 테스트 코드에 대한 2가지 지적:

1. `PricingChangePublisherTest`: Mockito `verify(mock, times(1))` → **Spy 콜카운트로 전환**. 이유: 발행 실패 흡수 로직 테스트 시 side-effect 관찰 필요
2. `PricingQueryServiceTest`: `InMemoryPricingRuleCache` infra 클래스 직접 참조 → **domain의 `PricingRuleCache` 인터페이스 Fake 구현체로 전환**. 4-Tier 격리 원칙 준수

## 개선 반영 (v1.4)

### 1. Mockito verify vs Spy 콜카운트 선택 기준
- `Mockito.verify`: 순수 상호작용 검증, 호출 여부·순서·인자 확인
- **Spy 콜카운트**: 실제 로직 실행하며 side-effect 관찰 필요 (발행 실패·재시도·retry 로직 등)
- 명확한 선택 기준 표 + 비교 예시

### 2. infra 직접 참조 → domain Fake 사용
- application/domain 계층 단위 테스트는 **infra 구현체 직접 참조 금지**
- domain 인터페이스의 테스트용 Fake 클래스를 test/ 하위 배치 (`FakeXxxRepository`, `FakeXxxCache`)
- Fake는 인메모리 컬렉션 기반 최소 구현. 실제 infra 로직(Redis·JDBC) 재현 금지

## AUTO FAIL 후보

application/domain 테스트에서 infra 패키지(`.infrastructure.`, `.persistence.`, `.cache.impl.`) 클래스 직접 참조 → AUTO FAIL

## 누적 검토

v1.3(FQCN 확장) → v1.4(계층 격리). 4-Tier 아키텍처 원칙을 테스트 코드까지 관철하는 방향. 다음 사이클: 회귀 평가 + pasta 재배포.
