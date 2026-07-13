---
component: java-spring-coder
source: pasta-japan-server (PR #654)
date: 2026-07-13
type: convention-mismatch
severity: medium
related_pr: 654
related_feedback: 2026-07-09-july-cycle-four-cases.md (사례 1 #633 후속)
---

## 증상

`pghd_food_glucose_spike_mean`의 동시 삽입 경합(중복키) 수정에서, `REQUIRES_NEW`로 격리하는 쓰기 전용 빈을 **`GlucoseSpikeMeanWriter`** 로 생성했다. 사용자가 "`~~Writer` 이게 좀 어색하다. 저번 유사 PR에서는 어떻게 했나"라고 지적.

- 참조 PR #633은 **이미 같은 실수를 겪고 리팩터로 정정**한 이력이 있었다: 커밋 `refactor: DailyMissionAchievementWriter를 Service/Impl 패턴으로 정리` — "package-private Writer 클래스가 mission.service 패키지 컨벤션(XxxService/Impl)과 어긋난다"는 이유.
- 즉 #633의 **최종 확정 네이밍은 `*Service`/`*Impl`** 인데, 초기 커밋의 잔재나 mechanism(REQUIRES_NEW)만 학습하고 **네이밍 결정을 놓쳐 `Writer`를 재사용** → 사용자 반복 지적.
- 해당 패키지(`pghd.meal.service`)에는 이미 write 전용 서비스 관례 `*CommandService`(`PghdFoodCommandService`, `RedisLockingPghdFoodCommandService`)가 존재했는데 확인하지 않음.

## 수정 내용

- `GlucoseSpikeMeanWriter` → **`GlucoseSpikeMeanCommandService`** 로 리네임 (PR #654). 메서드명 `saveInNewTransaction`은 `*InNewTransaction` 관례(#633의 `accumulateInNewTransaction`과 대칭)로 유지.
- 테스트 클래스·필드·@ContextConfiguration 참조 일괄 정정.

## 개선 제안 (스킬 반영 필요)

1. **새 빈/클래스 네이밍 규칙 추가**: 새 클래스를 만들기 전 **같은 패키지의 기존 접미사 패턴을 먼저 스캔**(`ls <package>`)하고 따른다. `~~Writer`/`~~Helper`/`~~Manager` 같은 프레임워크색 접미사는 그 패키지에 선례가 있을 때만 사용.
   - write 전용 서비스: 패키지 관례 우선. pghd 계열은 `*CommandService`, commerce mission 계열은 `*Service`/`*Impl`.
2. **참조 PR 모방 규칙 강화**: 기존 PR을 참고할 때 초기 커밋이 아니라 **리팩터·리뷰 반영 커밋까지 포함한 최종 상태**를 학습해 네이밍·구조 결정을 따른다. mechanism(REQUIRES_NEW, 1062 판별)뿐 아니라 **네이밍 결정**도 이식 대상이다.
3. 기존 `2026-05-21-bean-name-constant-and-requires-new.md`(REQUIRES_NEW 격리) + 이번 건은 "격리 쓰기 빈"의 **mechanism은 정착됐으나 네이밍 규칙이 누락**된 것 → SKILL 규칙에 네이밍 항목 명시.

## 변경 파일 (PR #654)

- `GlucoseSpikeMeanCommandService.java` (신규, ex-Writer)
- `GlucoseSpikeMeanService.java` (위임 필드/호출)
- `DuplicateKeyViolations.java` (신규, 1062 판별)
- `GlucoseSpikeMean.java` (uniqueConstraint 메타)
- 테스트 3종 (CommandServiceTest / ServiceTest / ConcurrencyTest)

## 비고

- java-spring-coder 누적 피드백 5건째(≥3) → 스킬의 소프트 가드레일상 구조적 개선 검토 대상. 네이밍 규칙은 #633(2026-07-09)·이번(2026-07-13) 연속 지적이므로 SKILL.md 반영 우선순위 높음.
