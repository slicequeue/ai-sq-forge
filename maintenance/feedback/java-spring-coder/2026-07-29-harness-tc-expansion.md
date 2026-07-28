---
component: java-spring-coder
source: forge 내부 (회귀 평가 커버리지 갭 대응)
date: 2026-07-29
type: harness-expansion
severity: high
---

## 증상 (2026-07-09 회귀 시점)

- java-spring-coder v1.11 회귀 95/100 PASS (TC 4/4)
- **하네스가 v1.5 시절 그대로** — v1.6~v1.11 신규 20+ 룰 중 검증 3건 미만
- 실전 사고 이력 있는 룰인데 TC 없음: Bean Qualifier / Session 오염 / DataIntegrityViolationException / REQUIRES_NEW

## 확장 반영 (TC 4 → 10)

### 신규 TC 6개
- **TC-5 Negative**: Bean Qualifier cross-module 재발 (#593·#588)
- **TC-6 Negative**: Hibernate Session 오염 재조회 (#633 재현, v1.11-A)
- **TC-7 Negative**: DataIntegrityViolationException 광범위 catch (v1.11-B)
- **TC-8 Edge**: 외부 API DTO 시간 파싱 (Dexcom #581·#582)
- **TC-9 Negative**: @ConditionalOnBean 사용 유도 (GLOB-566, v1.11)
- **TC-10 Happy**: 어노테이션+인터셉터 조합 (@ApiGroup, GLOB-549)

### AUTO FAIL 신규 6건 (#7~#12)
각 신규 TC와 1:1 매핑. 총 AUTO FAIL 12건.

### harness 갱신
- 축 2 판정 기준: Negative 100% 거절 명시
- TC 개수 4 → 10

## 파일 크기 변화

| 파일 | 이전 | 이후 |
|---|---|---|
| test-cases | 61줄 (4 TC) | 154줄 (10 TC) |
| harness | 118줄 | 124줄 |

## 다음 사이클

- 이번 확장 하네스로 v1.13 재평가 (--skip-baseline)
- Bean Qualifier / Session 오염 재발 방지 룰의 실전 검증 능력 확인

## 누적 검토

**하네스 커버리지 갭 심각도 최고**. v1.5 → v1.13까지 8단계 bump 사이 하네스 확장 없이 룰만 축적. 이번 리팩터로 검증 가능성 확보.
