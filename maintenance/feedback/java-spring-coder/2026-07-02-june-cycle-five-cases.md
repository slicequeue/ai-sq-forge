---
component: java-spring-coder
source: pasta-japan-server 6월 사고 사이클
date: 2026-07-02
type: pattern-expansion
severity: high
---

## 증상

pasta-japan-server 2026-06-01 ~ 2026-07-02 활동에서 5건의 사고·패턴이 forge 룰에 부재하거나 강도가 부족했다. v1.9까지의 커버리지가 미치지 못한 신규 영역.

## 사례별 요약

### 사례 1. 외부 API DTO 시간 필드 파싱 연쇄 hotfix (#581 6/8 08:42 → #582 6/8 17:24)
- Dexcom EGV `systemTime`을 표준 `Instant`로 받다가 초 없는 응답(`2026-06-07T22:58Z`) 역직렬화 실패
- 같은 날 오후 오프셋 다양성(+09/+08)에 다시 실패. **완벽 파서 만들려다 실패, 결국 미사용 필드는 String으로 후퇴해서야 안정**
- 교훈: 강타입 파싱은 실 사용 필드에만. 나머지는 String 유지

### 사례 2. 공용 모듈 JPA @Entity 스캔 충돌 (7/1 JPA→JDBC 교체 커밋)
- `common/access`에 `ServiceAccessPatternJpaEntity` 배치 → admin 스캔 시 `@EntityScan` 경계 충돌 → 기동 실패
- JdbcClient Reader로 교체 후 안정화

### 사례 3. 이용권한 캐시 3층 폴백 + write-through + 워밍업 (GLOB-566/567/569, 7/1~7/2)
- Redis → DB → 하드코딩 기본값 순서, 각 계층 예외 삼킴 (무료 개방 사고 방지)
- CRUD 커밋 후 유형별 **전체 재작성**으로 캐시 드리프트 방지
- 기동 시 워밍업 + 카운트 임계 미달 경보

### 사례 4. 신규 패키지 4-Tier 사후 재편 (7/1 access 재편 커밋)
- `common/access` 처음엔 계층 없이 만들었다가 `domain/application/infrastructure`로 재편
- 스킬이 초반부터 강제하지 못한 사례

### 사례 5. 예외 로깅 스택 절단 (#625 6/30)
- JsonTemplateLayout 16KB 절단으로 근본 원인 못 봄
- `exceptionRootCause` 전용 필드 + `maxStringLength: 32768`로 해결

## 개선 반영 (v1.10)

- 하드 가드레일 3건 추가 (외부 API DTO 시간 방어 / 캐시 3층 폴백 / 예외 로깅 표준)
- 아키텍처 원칙: 신규 패키지 첫 커밋부터 4-Tier 폴더 강제 + 공용 모듈 @Entity 회피
- 자기 검증 #31~#35 신규 5항목

## 누적 검토

v1.5(5월) → v1.9(5/22) → v1.10(7/2). 두 달간 5-tier의 실전 사고를 지속 흡수 중. 다음 사이클은 회귀 평가(`/eval-harness java-spring-coder --skip-baseline`) + pasta 재배포(`/forge-deploy --sync`).
