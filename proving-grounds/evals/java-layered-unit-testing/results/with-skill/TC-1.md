<!-- TC-1 with-skill (regression) / skill v1.8 / sonnet / 2026-11-13 / 79,984 tok / tool 5 / 58s -->

# MyPlanRoutineRaceQueryService 단위 테스트 (시뮬레이션, 파일 미작성)

적용 스킬은 `java-layered-unit-testing` v1.8입니다. `SKILL.md`, `references/evaluation-rubric.md`, `forge/common/pasta-rules/08-test-code-convention.md`, `review-recurrence-guard.md`(RR-12), `review-lint.py`를 읽었고 `proving-grounds/`는 열지 않았습니다. 실제 프로젝트 코드는 없어서 시그니처는 전부 가정이고, 아래 "가정" 항목에 모았습니다.

## 1. 대상과 계층

| 항목 | 내용 |
|---|---|
| 대상 클래스 | `MyPlanRoutineRaceQueryService`, `getRoutineRace(routineRaceId)` |
| 계층 | Application. 요청에 명시돼 있고 `application/` 패키지로 추정합니다. 실제 경로는 Phase 0 에서 확인합니다. |
| 테스트 방식 | 순수 JUnit 5 + Fake. Spring 컨텍스트와 Mockito 는 쓰지 않습니다. |
| 더블 선택 근거 | 레이스와 체중 목표 조회는 둘 다 상태를 가진 저장소(Repository)입니다. 규칙 08 §2 와 RR-F14 에 따라 `@Mock` 이 아니라 Fake 로 씁니다. 외부 통신과 void 부수효과가 없어 Spy 와 Mock 은 필요 없습니다. |

## 2. 실행 계획 (실제 실행은 하지 않음)

1. 대상 클래스의 패키지와 생성자를 찾습니다. `find . -name "MyPlanRoutineRaceQueryService*.java"`
2. 같은 패키지의 기존 `*Test`를 읽어 `@Nested` 그룹핑과 `@DisplayName` 톤을 맞춥니다.
3. 쓸 수 있는 Fake 가 이미 있는지 확인합니다. `find . -name "Fake*Routine*" -o -name "Fake*WeightGoal*"`
   - 이미 있으면 재사용하고, 없을 때만 아래 Fake 를 만듭니다.
4. 대상 테스트 파일이 이미 있는지 확인합니다. `git status --short <경로>`
   - 있으면 먼저 읽고 Edit 로 추가합니다(DW-3). Write 로 통째로 덮지 않습니다.
5. 작성 후 `./gradlew :{module}:spotlessApply`, `./gradlew :{module}:test --tests MyPlanRoutineRaceQueryServiceTest`, `python3 forge/common/review-lint.py` 순서로 실행합니다. 위반은 0건이어야 합니다.
6. 테스트가 실제로 잡는지 확인합니다. 서비스 코드를 일시적으로 깨뜨립니다.
   - 예: 목표 조회 키를 `routineRaceId`로 바꾸기, 필드 매핑 빼기, 예외 분기 제거
   - 각각 최소 1개 테스트가 실패해야 합니다.
7. `git status`로 의도하지 않은 삭제나 변경이 없는지 확인합니다(DW-5).

## 3. 가정 (확인된 것과 구분)

가정 A~F 가 틀리면 아래 코드의 대응 부분만 고치면 됩니다.

| # | 가정 | 틀릴 경우 영향 |
|---|---|---|
| A | 의존성은 `RoutineRaceRepository`와 `MyPlanWeightGoalRepository` 두 개이고 생성자로 주입한다. | 체중 목표를 다른 `*QueryService`로 받으면 Fake 대상만 바뀝니다. |
| B | `RoutineRaceRepository.findById(Long)`는 `Optional<RoutineRace>`를 반환한다. | 거의 영향 없음 |
| C | `RoutineRace`는 `id`, `userId`, `name`, `startDate`, `endDate`를 가진다. | 생성 방식이 빌더면 픽스처 헬퍼만 수정합니다. |
| D | `MyPlanWeightGoalRepository.findByUserId(Long)`는 `Optional<MyPlanWeightGoal>`를 반환한다. 목표는 레이스의 `userId`로 찾고, 목표 필드는 `startWeightKg`, `targetWeightKg`다. | 조회 키가 다르면 "다른 사용자 목표 혼입" 테스트를 수정합니다. |
| E | 레이스가 없으면 `RoutineRaceNotFoundException`이 발생한다. | 실제 예외 계층에 맞춥니다. |
| F | 목표가 없으면 `QueryResult.weightGoal()`이 null 이다. | 정책이 다르면(예외나 `Optional`) 해당 테스트를 바꿉니다. 도메인 정책 확인이 필요합니다. |

`QueryResult`는 `MyPlanRoutineRaceQueryService.QueryResult` 중첩 record 이고 `routineRace()`, `weightGoal()` 접근자를 가진다고 가정했습니다.

## 4. 테스트 코드

### 4-1. FakeRoutineRaceRepository

`src/test/java/.../myplan/FakeRoutineRaceRepository.java`

```java
package com.kakaohealthcare.pasta.myplan;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;

// 도메인 인터페이스 RoutineRaceRepository 의 인메모리 Fake (가정 A, B)
class FakeRoutineRaceRepository implements RoutineRaceRepository {

    private final Map<Long, RoutineRace> routineRaceById = new LinkedHashMap<>();

    RoutineRace save(RoutineRace routineRace) {
        routineRaceById.put(routineRace.getId(), routineRace);
        return routineRace;
    }

    @Override
    public Optional<RoutineRace> findById(Long routineRaceId) {
        return Optional.ofNullable(routineRaceById.get(routineRaceId));
    }
}
```

### 4-2. FakeMyPlanWeightGoalRepository

`src/test/java/.../myplan/FakeMyPlanWeightGoalRepository.java`

```java
package com.kakaohealthcare.pasta.myplan;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

// 도메인 인터페이스 MyPlanWeightGoalRepository 의 인메모리 Fake (가정 A, D)
// 사용자 조건을 실제 쿼리처럼 적용하고, 정답을 주입하지 않는다.
class FakeMyPlanWeightGoalRepository implements MyPlanWeightGoalRepository {

    private final List<MyPlanWeightGoal> myPlanWeightGoalList = new ArrayList<>();

    MyPlanWeightGoal save(MyPlanWeightGoal myPlanWeightGoal) {
        myPlanWeightGoalList.add(myPlanWeightGoal);
        return myPlanWeightGoal;
    }

    @Override
    public Optional<MyPlanWeightGoal> findByUserId(Long userId) {
        return myPlanWeightGoalList.stream()
                .filter(myPlanWeightGoal -> myPlanWeightGoal.getUserId().equals(userId))
                .findFirst();
    }
}
```

### 4-3. MyPlanRoutineRaceQueryServiceTest

```java
package com.kakaohealthcare.pasta.myplan;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.kakaohealthcare.pasta.myplan.MyPlanRoutineRaceQueryService.QueryResult;
import java.time.LocalDate;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class MyPlanRoutineRaceQueryServiceTest {

    // 픽스처 값은 가정 C, D 에 따른 임의 도메인 값이다. 서로 다른 값으로 두어 필드 매핑 오류가 드러나게 한다.
    private static final Long TARGET_ROUTINE_RACE_ID = 10L;
    private static final Long TARGET_USER_ID = 100L;
    private static final Long OTHER_ROUTINE_RACE_ID = 11L;
    private static final Long OTHER_USER_ID = 200L;
    private static final Long MISSING_ROUTINE_RACE_ID = 999L;
    private static final LocalDate TARGET_START_DATE = LocalDate.of(2026, 11, 2);
    private static final LocalDate TARGET_END_DATE = LocalDate.of(2026, 11, 29);
    private static final double TARGET_USER_START_WEIGHT_KG = 82.4;
    private static final double TARGET_USER_TARGET_WEIGHT_KG = 75.0;
    private static final double OTHER_USER_START_WEIGHT_KG = 60.1;
    private static final double OTHER_USER_TARGET_WEIGHT_KG = 55.5;

    private FakeRoutineRaceRepository fakeRoutineRaceRepository;
    private FakeMyPlanWeightGoalRepository fakeMyPlanWeightGoalRepository;
    private MyPlanRoutineRaceQueryService myPlanRoutineRaceQueryService;

    @BeforeEach
    void setUp() {
        fakeRoutineRaceRepository = new FakeRoutineRaceRepository();
        fakeMyPlanWeightGoalRepository = new FakeMyPlanWeightGoalRepository();
        myPlanRoutineRaceQueryService =
                new MyPlanRoutineRaceQueryService(fakeRoutineRaceRepository, fakeMyPlanWeightGoalRepository);
    }

    @Nested
    @DisplayName("getRoutineRace")
    class GetRoutineRace {

        @Test
        @DisplayName("레이스 정보와 해당 레이스 소유자의 체중 목표를 결합해 반환한다")
        void getRoutineRace_existingRaceAndGoal_returnsCombinedResult() {
            // Given
            fakeRoutineRaceRepository.save(routineRace(TARGET_ROUTINE_RACE_ID, TARGET_USER_ID));
            fakeMyPlanWeightGoalRepository.save(
                    weightGoal(TARGET_USER_ID, TARGET_USER_START_WEIGHT_KG, TARGET_USER_TARGET_WEIGHT_KG));

            // When
            QueryResult routineRaceQueryResult = myPlanRoutineRaceQueryService.getRoutineRace(TARGET_ROUTINE_RACE_ID);

            // Then
            assertThat(routineRaceQueryResult.routineRace().getId()).isEqualTo(TARGET_ROUTINE_RACE_ID);
            assertThat(routineRaceQueryResult.routineRace().getStartDate()).isEqualTo(TARGET_START_DATE);
            assertThat(routineRaceQueryResult.routineRace().getEndDate()).isEqualTo(TARGET_END_DATE);
            assertThat(routineRaceQueryResult.weightGoal().getStartWeightKg())
                    .isEqualTo(TARGET_USER_START_WEIGHT_KG);
            assertThat(routineRaceQueryResult.weightGoal().getTargetWeightKg())
                    .isEqualTo(TARGET_USER_TARGET_WEIGHT_KG);
        }

        @Test
        @DisplayName("여러 레이스와 여러 사용자의 목표가 있어도 요청한 레이스와 그 소유자의 목표만 반환한다")
        void getRoutineRace_multipleRacesAndGoals_returnsOnlyRequestedRaceAndOwnerGoal() {
            // Given — 대상이 첫 번째가 아니도록, 다른 사용자 데이터를 앞과 뒤에 둔다
            fakeRoutineRaceRepository.save(routineRace(OTHER_ROUTINE_RACE_ID, OTHER_USER_ID));
            fakeRoutineRaceRepository.save(routineRace(TARGET_ROUTINE_RACE_ID, TARGET_USER_ID));
            fakeMyPlanWeightGoalRepository.save(
                    weightGoal(OTHER_USER_ID, OTHER_USER_START_WEIGHT_KG, OTHER_USER_TARGET_WEIGHT_KG));
            fakeMyPlanWeightGoalRepository.save(
                    weightGoal(TARGET_USER_ID, TARGET_USER_START_WEIGHT_KG, TARGET_USER_TARGET_WEIGHT_KG));

            // When
            QueryResult routineRaceQueryResult = myPlanRoutineRaceQueryService.getRoutineRace(TARGET_ROUTINE_RACE_ID);

            // Then
            assertThat(routineRaceQueryResult.routineRace().getId()).isEqualTo(TARGET_ROUTINE_RACE_ID);
            assertThat(routineRaceQueryResult.routineRace().getUserId()).isEqualTo(TARGET_USER_ID);
            assertThat(routineRaceQueryResult.weightGoal().getUserId()).isEqualTo(TARGET_USER_ID);
            assertThat(routineRaceQueryResult.weightGoal().getTargetWeightKg())
                    .isEqualTo(TARGET_USER_TARGET_WEIGHT_KG);
        }

        @Test
        @DisplayName("레이스 소유자의 체중 목표가 없으면 다른 사용자 목표를 섞지 않고 목표 없음으로 반환한다")
        void getRoutineRace_ownerHasNoGoal_returnsRaceWithoutWeightGoal() {
            // Given — 가정 F: 목표 부재는 weightGoal() == null
            fakeRoutineRaceRepository.save(routineRace(TARGET_ROUTINE_RACE_ID, TARGET_USER_ID));
            fakeMyPlanWeightGoalRepository.save(
                    weightGoal(OTHER_USER_ID, OTHER_USER_START_WEIGHT_KG, OTHER_USER_TARGET_WEIGHT_KG));

            // When
            QueryResult routineRaceQueryResult = myPlanRoutineRaceQueryService.getRoutineRace(TARGET_ROUTINE_RACE_ID);

            // Then
            assertThat(routineRaceQueryResult.routineRace().getId()).isEqualTo(TARGET_ROUTINE_RACE_ID);
            assertThat(routineRaceQueryResult.weightGoal()).isNull();
        }

        @Test
        @DisplayName("존재하지 않는 레이스 ID 로 조회하면 예외가 발생한다")
        void getRoutineRace_missingRace_throwsNotFoundException() {
            // Given — 다른 레이스와 목표만 존재한다
            fakeRoutineRaceRepository.save(routineRace(OTHER_ROUTINE_RACE_ID, OTHER_USER_ID));
            fakeMyPlanWeightGoalRepository.save(
                    weightGoal(OTHER_USER_ID, OTHER_USER_START_WEIGHT_KG, OTHER_USER_TARGET_WEIGHT_KG));

            // When & Then
            assertThatThrownBy(() -> myPlanRoutineRaceQueryService.getRoutineRace(MISSING_ROUTINE_RACE_ID))
                    .isInstanceOf(RoutineRaceNotFoundException.class);
        }
    }

    private RoutineRace routineRace(Long routineRaceId, Long userId) {
        return new RoutineRace(routineRaceId, userId, "11월 루틴 레이스", TARGET_START_DATE, TARGET_END_DATE);
    }

    private MyPlanWeightGoal weightGoal(Long userId, double startWeightKg, double targetWeightKg) {
        return new MyPlanWeightGoal(userId, startWeightKg, targetWeightKg);
    }
}
```

## 5. 설계 설명

- **Fake 를 선택한 이유**: 레이스와 체중 목표는 모두 상태를 가진 저장소입니다. 규칙 08 §2 의 Fake → Stub/Spy → Mock 순서와 RR-F14 를 따랐고, `@Mock`과 `given().willReturn()`으로 정답을 주입하는 방식은 AUTO FAIL 6 에 해당해 쓰지 않았습니다.
- **Fake 의 동작**: `findByUserId`가 사용자 조건을 직접 적용합니다. 서비스가 조회 키를 잘못 쓰면 다른 사용자 목표가 섞이거나 null 이 되어 테스트가 실패합니다.
- **위임만 검증하는 테스트를 피한 방법(RR-12)**:
  - 레이스 필드와 목표 필드를 각각 서로 다른 값으로 단언해서, 결합이나 매핑이 빠지면 깨집니다.
  - 대상 레이스를 목록의 첫 번째에 두지 않았습니다.
  - 다른 사용자의 레이스와 목표를 앞뒤에 둬서, 고정 인덱스나 `findFirst` 식 구현을 잡습니다.
- **기본값과 다른 값**: 체중 값은 모두 다르게 잡았습니다(82.4/75.0 대 60.1/55.5). 값이 같으면 필드가 뒤바뀌어도 통과합니다.
- **Spy 와 verify 를 쓰지 않은 이유**: 외부 통신이나 void 부수효과가 없습니다. 상태 기반으로 반환값만 검증했습니다.
- **컨벤션 준수**:
  - 테스트 메서드명은 영어(`[Method]_[Scenario]_[Expected]`), `@DisplayName`은 한국어입니다.
  - Given-When-Then 구조에 `@Nested`와 AssertJ 를 사용했습니다.
  - `var`와 FQCN 은 쓰지 않았고 모든 타입을 import 했습니다.
  - 컬렉션 변수는 요소 타입+`List`, 결과 변수는 `routineRaceQueryResult`, 대상은 `myPlanRoutineRaceQueryService`처럼 타입이 드러나게 지었습니다.
  - infra 구현체는 참조하지 않고 domain 인터페이스 Fake 만 사용했습니다.

## 6. Self-check 결과표

| # | 등급 | 결과 | 비고 |
|---|---|---|---|
| 1 | B | PASS (추정) | 계층은 사용자 명시이고 패키지 경로는 Phase 0 에서 확인합니다. |
| 2 | B | PASS | Fake 방식입니다(체크리스트 문구의 "App=Mockito"는 본문 v1.8 과 충돌하는 잔재라 본문 기준을 따랐습니다). |
| 3 | B | N/A | Infra 계층이 아닙니다. |
| 4 | B | PASS | 모든 테스트에 한국어 `@DisplayName`이 있습니다. |
| 5 | B | 미확인 | 실행 계획 5 단계에서 확인합니다. 시그니처가 가정이라 컴파일 가능 여부는 확정할 수 없습니다. |
| 6~10 | R | PASS | spotlessApply 는 실행 계획에 포함했습니다. 같은 패키지 기존 테스트와의 일관성은 Phase 0 에서 확인합니다. |
| 11, 16 | B | PASS | FQCN 0건입니다. |
| 12 | R | PASS | 계층 근거와 추정 표기를 명시했습니다. |
| 13 | R | PASS | 가정값에 주석을 달았습니다. |
| 15 | B | N/A | `@MockBean`을 쓰지 않았습니다. |
| 17 | B | PASS | infra 구현체 직접 참조가 0건입니다. |
| 18 | R | N/A | Spy 와 verify 를 쓰지 않았습니다. |
| 19 | B | PASS | Mock 0건입니다. |
| 20 | B | PASS | 기본값과 다른 값으로 검증했습니다. 진입 경로는 `getRoutineRace` 하나이고, JSON 단언은 없습니다. |
| 21 | B | 미확인 | review-lint 는 실행 계획에 포함했습니다. |

## 7. 테스트 실행 결과

실제 코드가 없어 실행하지 않았습니다. 통과 여부는 미확인입니다.

## 8. 남은 리스크

1. 가정 A~F 가 실제와 다르면 컴파일이 깨지거나 목표 부재 정책(가정 F)이 틀릴 수 있습니다. 특히 F 는 도메인 확인이 필요합니다.
2. 레이스 조회 후 목표 조회가 한 트랜잭션에서 일관되는지, 목표 조회 실패가 레이스 응답에 영향을 주는지는 이 단위 테스트의 범위 밖입니다. 서비스가 여러 소스를 조립하는 구조이므로 "한 소스 실패 시 격리"가 요구사항이라면 별도 테스트(실패 Fake 또는 `@SpringBootTest`)가 필요합니다(RR-13).
3. 수동으로 나열한 케이스 4개입니다. 서비스에 분기(예: 레이스 종료 여부에 따른 가공)가 있다면 그 분기 테스트를 추가해야 합니다.
