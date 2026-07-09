---
component: self-code-reviewer
source: pasta-japan-server 7월 사고 사이클
date: 2026-07-09
type: detection-rules
severity: critical
---

## 증상

7월 pasta 활동에서 자체 리뷰가 사전 차단 못 한 사고 4건. 특히 **@Profile `&&` 문법 오류 2회 재발**과 **#633 Hibernate Session 오염**은 검출 룰 부재 원인.

## 4건 신규 검출 룰 (v1.11)

### 1. `@Profile` 문법 오류 `&&` → `&` (사고 #49c513f596, #0df4473548) — **매우 detectable**

- Spring `@Profile`은 단일 `&`만 지원. `&&`는 잘못
- GLOB-566 `PricingCacheRedisConfig`, GLOB-567 `PricingAdminConfiguration` 두 곳에서 같은 실수. PR 리뷰가 잡음
- **AUTO FAIL**: `grep -rn '@Profile.*&&' src/` 매치 시

### 2. `DataIntegrityViolationException` 광범위 catch 검출 (사고 #633)

- 무조건 catch 삼키면 NOT NULL/FK 위반 같은 실제 결함도 은폐
- SQL 에러코드로 좁혀 판별 강제
- 통과 예: `if (e.getCause() instanceof SQLException sql && sql.getErrorCode() == 1062)`

### 3. Hibernate Session 오염 재조회 검출 (사고 #633 재발 방지)

- unique/제약 위반 catch 이후 같은 Session/EntityManager로 재조회 검출
- **AUTO FAIL 후보**: catch 블록 내 `entityManager.find(...)`, `session.get(...)`, `repository.findBy...` 등 조회 호출 발견
- java-spring-coder v1.11-A와 짝. 정본 위치 참조

### 4. 입력 형식 검증 누락 (사고 #623)

- 사번·전화번호·이메일 같은 도메인 식별자 필드에 `@Pattern`/`@Email`/`@Size` 등 검증 누락 시 경고
- 검증 실패 메시지가 message.properties 4개 로케일에 정의되어 있는지 확인 (tolgee 스킬 연계)

## 근본 원인 진단

**검출 룰 자체가 부재**했음. 각 사고는 사전 차단 가능한 detectable 패턴이었으나 룰이 없어 사후 hotfix. `@Profile` `&&`는 특히 grep 한 줄로 잡히는 매우 명확한 사례.

## 개선 반영

- 자기 검증 #24~#27 신규 4항목
- v1.10 세 검사 항목 뒤에 v1.11 4건 배치
- v1.11-3(Session 오염)은 java-spring-coder v1.11-A와 정본/짝 관계

## 누적 검토

v1.10(7/2) → v1.11(7/9). 1주일 사이클. 자체 리뷰의 사각지대가 반복적으로 발견되는 현상을 보면 **다음 사이클은 자체 리뷰 강화**가 아니라 **회귀 평가**로 룰이 실제 사고를 잡는지 검증하는 게 급함.
