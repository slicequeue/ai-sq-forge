---
component: java-spring-coder
source: pasta-japan-server 7월 사고 사이클
date: 2026-07-09
type: pattern-expansion
severity: critical
---

## 증상

2026-07-03 ~ 2026-07-09 pasta-japan-server 활동(20+ 커밋, GLOB-548/549/566/567 유료화 시리즈 + #633 미션 사고)에서 4건의 신규 패턴이 발견됐다. 특히 **#633 미션 사고는 한국 moneyball 저장소 재발 사고**로 forge 룰 부재의 대가.

## 사례별 요약

### 사례 1. Hibernate Session 오염 회귀 (#633, 2026-07-08) — **최우선**

- 뱃지 중복 발급 방어 코드가 `DataIntegrityViolationException` catch 후 **같은 Session으로 재조회** → `AssertionFailure` → 앞서 저장된 미션 달성 기록까지 함께 롤백
- CodeRabbit 피드백: `DataIntegrityViolationException` 무조건 catch 삼키면 NOT NULL/FK 위반도 은폐. SQL 에러코드 1062(ER_DUP_ENTRY)로 좁혀 판별
- 최종 리팩터: 뱃지 발급을 `REQUIRES_NEW` 별도 트랜잭션으로 격리 + Testcontainers 통합 테스트 추가
- **재발 배경**: 한국 moneyball 저장소에서 이미 겪은 사고. forge 룰에 없어서 pasta에 재발

### 사례 2. `@ConditionalOnBean` 순서 취약성 (#584ced0b97, 2026-07-07)

- pub-sub 설정을 `@ConditionalOnBean(RedisTemplate.class)`로 게이팅 → Bean 로드 순서 문제로 실패
- `@Profile`로 안정화

### 사례 3. 캐시 pub-sub 즉시 무효화 + 폴링 백스톱 + 발행 실패 흡수 (GLOB-566 시리즈)

- v1.10 캐시 3층 폴백의 한 단계 진화 패턴
- Redis pub-sub 발행 실패 흡수 (커밋 후 발행 → 어드민 API 실패 방지, 폴링 백스톱이 자가 치유)
- refresh 실패 로그 WARN → ERROR + 스택트레이스

### 사례 4. 어노테이션 + 인터셉터 조합 패턴 (GLOB-549 `@ApiGroup`)

- 컨트롤러 메서드 `@ApiGroup(FEATURE_X)` 어노테이션 마킹 → 인터셉터가 유료화 적용
- shared 모듈에 어노테이션, api 모듈에 인터셉터 (4-Tier 유지)
- enum 파라미터 사용

## 개선 반영 (v1.11)

- 하드 가드레일 v1.11-A/B/C 신규 3건 (Session 오염 재조회 금지 / SQL 에러코드 좁혀 판별 / REQUIRES_NEW 격리)
- 아키텍처 원칙: `@Profile` 선호 · `@ConditionalOnBean` 회피
- 캐시 섹션 확장: pub-sub 무효화 + 폴링 백스톱 + 발행 실패 흡수
- 어노테이션+인터셉터 조합 패턴 신설
- 자기 검증 #36~#41 신규 6항목

## 누적 검토

v1.10(7/2) → v1.11(7/9), 1주일 간격 사이클 최단 기록. 특히 v1.11-A/B/C 3연타 하드 가드레일은 **moneyball → pasta 재발 방지**가 목적. 다음 사이클은 회귀 평가(`/eval-harness --skip-baseline`) + pasta 재배포.
