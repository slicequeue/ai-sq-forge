---
component: acceptance-tester
source: pasta-japan-server
date: 2026-05-21
type: improvement
related_commits: 7bfd27dce2, 02a419d175, 9b6dd02e3a, 2c37d5e77d
severity: medium
---

## 증상

forge-upstream으로 acceptance-tester를 v0.1로 가져온 직후, **이번 주(5/15~5/21) pasta에서 인수 테스트 관련 사고/개선 4건**이 있었음에도 본 에이전트에 반영되지 않았음. 사용자의 회고 요청으로 일괄 흡수.

### 1. testAcceptance 사각지대 (사고)

- **commit 7bfd27dce2, 02a419d175**
- 일반 `:api:test`는 `excludeTags 'acceptance'`로 인수 테스트 제외 → CI의 testAcceptance 단계에서만 컨텍스트 로딩 실패 발견
- OAuth manager `@MockBean` 익명 등록이 빈 등록자의 `@Qualifier("dexcomAuthorizedClientManager")`와 매칭 안 됨

### 2. @TestConfiguration 중복 Bean 정의

- 같은 commit에서 `@TestConfiguration`의 `@Bean @Primary OAuth2AuthorizedClientManager`도 함께 제거됨
- `@MockBean(name=...)`이 충분 — 중복 정의는 컨텍스트 로딩 시 충돌 위험

### 3. @Nested → flat 구조

- **commit 9b6dd02e3a**: 위임청구 중복 검증 테스트 @Nested 제거 → flat (155줄 → +77/-78)
- 의미 있는 시나리오 그룹화가 없을 때는 flat이 가독성 우수 — 이번 사례는 단순 케이스 나열

### 4. 인수 테스트 신규 추가 패턴

- **commit 2c37d5e77d**: 이벤트 응모 acceptance 테스트 추가 — 신규 기능 인수 테스트 작성 워크플로

## 수정 내용

PR 리뷰 / CI 실패로 사용자가 직접 수정. 본 에이전트에 사전 가드레일 없었음.

## 개선 제안 (acceptance-tester v0.2 가드레일)

본 에이전트 v0.2 본문 "v0.2 보강" 섹션에 4가지 패턴 박제:
1. testAcceptance 사각지대 인지 — 작업 종료 시 `:module:testAcceptance` 별도 실행 강제
2. OAuth MockBean 이름 명시 + 빈 이름 상수 import (java-spring-coder v1.7 패턴 연계)
3. @TestConfiguration 중복 Bean 정의 제거
4. @Nested vs flat 정책 — 의심이면 flat

## 누적 검토

acceptance-tester 신규 forge 등록(2026-05-19) 직후 첫 보강. 1건 누적이지만 4사례 포함이라 v0.2 즉시 갱신 정당함.

## 연계 스킬

- `java-spring-coder` v1.7+ (Bean 이름 상수 패턴) — `@MockBean(name=...)` 작성 시 정본
- `java-layered-unit-testing` v1.3+ (`@MockBean` 매직 스트링 금지) — 단위 테스트 측 동일 룰
