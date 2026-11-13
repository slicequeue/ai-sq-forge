<!-- TC-8 with-skill / skill v1.8 / sonnet / 2026-11-13 / 96,270 tok / tool 5 / 88s -->

# `Glp1HomeCardQueryService.getCard` 단위 테스트 시뮬레이션 (파일은 쓰지 않음)

## 1. 대상과 테스트 방식

- **대상 클래스**: `Glp1HomeCardQueryService`, Application 계층. 근거는 두 가지입니다. 전제에서 4-Tier 중 application 패키지의 `@Service`로 주어졌습니다. 의존성도 다른 도메인의 `*QueryUseCase` 두 개입니다. (체크 #12)
- **테스트 방식**: 두 UseCase 모두 상태를 가진 협력 객체입니다. 그래서 `@Mock`이 아니라 **Fake**를 씁니다 (규칙 08 §2, RR-F14). `find . -name "Fake*"` 결과 Fake가 없으므로 2개를 새로 만듭니다.
- **Mockito**: 사용하지 않습니다. 그래서 Mock 사유 주석도 필요 없습니다.
- **Spring Context**: 띄우지 않습니다. 순수 JUnit과 Fake를 생성자로 주입합니다.

### 확인된 사실과 가정

| 구분 | 내용 |
|------|------|
| 확인된 사실 | 서비스 코드, 두 UseCase의 시그니처(`getLast`, `getNext`), 두 조회를 각각 `try/catch (RuntimeException)`으로 격리, Fake 없음 |
| 가정 1 | `Glp1InjectionRecordOutDto`, `Glp1InjectionPlanOutDto`는 `id`를 받는 record이고, `Glp1HomeCardOutDto`의 접근자는 `lastRecord()`와 `nextPlan()`. 생성자 인자는 실제 시그니처에 맞춰 조정 |
| 가정 2 | 두 UseCase 인터페이스는 각각 메서드가 `getLast`, `getNext` 하나뿐 |
| 가정 3 | "마지막 기록"은 `injectedAt <= currentAt` 중 가장 늦은 것, "다음 일정"은 `scheduledAt > currentAt` 중 가장 이른 것. 데이터가 없으면 `null`을 반환 |
| 가정 4 | 패키지 `com.kakaohealthcare.pasta.glp1.application`, 모듈 `pasta-api` |

- 가정 3은 Fake가 재현할 조건입니다. 실제 UseCase 구현과 다르면 Fake를 맞춰야 합니다. 이 가정이 틀리면 아래 "데이터 없음" 테스트도 같이 틀어집니다. 실제 구현이 없을 때 예외를 던진다면 그 테스트는 사실상 격리 경로를 한 번 더 타는 셈이 되기 때문입니다. 구현에서 확인이 필요합니다.
- 가정 1의 생성자 모양은 컴파일 단계에서 확인해야 합니다.

## 2. 실행 계획 (명령은 실행하지 않음)

1. **기존 테스트 확인 (DW-1, DW-3)**:
   - `git status --short`로 `Glp1HomeCardQueryServiceTest.java`의 존재와 미커밋 여부를 확인합니다.
   - 있으면 먼저 읽고 `Edit`로 추가합니다. 통째로 덮어쓰지 않습니다.
   - 같은 패키지의 기존 `*Test`도 읽어 `@Nested`와 `@DisplayName` 톤을 맞춥니다.
2. **Fake 재확인**: `find . -name "Fake*Glp1Injection*"`를 다시 돌려 중복 신설을 막습니다. 없을 때만 아래 Fake 2개를 `src/test/`의 같은 도메인 패키지에 만듭니다.
3. 테스트 파일 작성.
4. `./gradlew :pasta-api:spotlessApply`
5. `./gradlew :pasta-api:test --tests Glp1HomeCardQueryServiceTest`
6. `python3 forge/common/review-lint.py`: 위반 0건이어야 합니다. 확인 항목은 해당 여부를 판단합니다.
7. **변이 확인 (RR-12)**: 서비스를 일부러 깨뜨려 테스트가 실패하는지 봅니다. 깨뜨린 뒤에는 반드시 원복합니다.
   - 두 조회를 하나의 try로 합침: 격리 테스트 2건이 실패해야 합니다.
   - `currentAt` 대신 `Instant.now()`를 전달: 정상 조회 테스트가 실패해야 합니다. 픽스처가 과거 시각 `CURRENT_AT` 기준이라 미래 기록이 현재 시각에는 "과거"가 되기 때문입니다.
   - `userId` 인자를 바꿈: 사용자 격리 테스트가 실패해야 합니다.
8. **DW-5**: `git status`와 `git diff --stat`으로 의도치 않은 삭제가 없는지 확인합니다.

## 3. 테스트 코드

### 3-1. `FakeGlp1InjectionRecordQueryUseCase`

`src/test/java/com/kakaohealthcare/pasta/glp1/application/FakeGlp1InjectionRecordQueryUseCase.java`

```java
package com.kakaohealthcare.pasta.glp1.application;

import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

class FakeGlp1InjectionRecordQueryUseCase implements Glp1InjectionRecordQueryUseCase {

    private final List<StoredRecord> storedRecordList = new ArrayList<>();
    private RuntimeException failure;

    void save(Long userId, Instant injectedAt, Glp1InjectionRecordOutDto glp1InjectionRecordOutDto) {
        storedRecordList.add(new StoredRecord(userId, injectedAt, glp1InjectionRecordOutDto));
    }

    void failWith(RuntimeException failure) {
        this.failure = failure;
    }

    @Override
    public Glp1InjectionRecordOutDto getLast(Long userId, Instant currentAt) {
        if (failure != null) {
            throw failure;
        }
        return storedRecordList.stream()
                .filter(storedRecord -> storedRecord.userId().equals(userId))
                .filter(storedRecord -> !storedRecord.injectedAt().isAfter(currentAt))
                .max(Comparator.comparing(StoredRecord::injectedAt))
                .map(StoredRecord::glp1InjectionRecordOutDto)
                .orElse(null);
    }

    private record StoredRecord(
            Long userId, Instant injectedAt, Glp1InjectionRecordOutDto glp1InjectionRecordOutDto) {}
}
```

### 3-2. `FakeGlp1InjectionPlanQueryUseCase`

`src/test/java/com/kakaohealthcare/pasta/glp1/application/FakeGlp1InjectionPlanQueryUseCase.java`

```java
package com.kakaohealthcare.pasta.glp1.application;

import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

class FakeGlp1InjectionPlanQueryUseCase implements Glp1InjectionPlanQueryUseCase {

    private final List<StoredPlan> storedPlanList = new ArrayList<>();
    private RuntimeException failure;

    void save(Long userId, Instant scheduledAt, Glp1InjectionPlanOutDto glp1InjectionPlanOutDto) {
        storedPlanList.add(new StoredPlan(userId, scheduledAt, glp1InjectionPlanOutDto));
    }

    void failWith(RuntimeException failure) {
        this.failure = failure;
    }

    @Override
    public Glp1InjectionPlanOutDto getNext(Long userId, Instant currentAt) {
        if (failure != null) {
            throw failure;
        }
        return storedPlanList.stream()
                .filter(storedPlan -> storedPlan.userId().equals(userId))
                .filter(storedPlan -> storedPlan.scheduledAt().isAfter(currentAt))
                .min(Comparator.comparing(StoredPlan::scheduledAt))
                .map(StoredPlan::glp1InjectionPlanOutDto)
                .orElse(null);
    }

    private record StoredPlan(Long userId, Instant scheduledAt, Glp1InjectionPlanOutDto glp1InjectionPlanOutDto) {}
}
```

Fake에는 Mockito를 쓰지 않고, 조회 조건(사용자, 기준 시각, 정렬)만 최소한으로 구현했습니다. 정답을 주입하는 `setResult` 방식은 쓰지 않았습니다.

### 3-3. `Glp1HomeCardQueryServiceTest`

```java
package com.kakaohealthcare.pasta.glp1.application;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.Duration;
import java.time.Instant;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class Glp1HomeCardQueryServiceTest {

    // 가정: 실제 도메인에서 유효한 식별자·시각. 기준 시각을 과거로 고정해 Instant.now() 사용 시 실패하게 한다.
    private static final Long USER_ID = 1001L;
    private static final Long OTHER_USER_ID = 2002L;
    private static final Instant CURRENT_AT = Instant.parse("2026-11-01T00:00:00Z");

    private FakeGlp1InjectionRecordQueryUseCase fakeGlp1InjectionRecordQueryUseCase;
    private FakeGlp1InjectionPlanQueryUseCase fakeGlp1InjectionPlanQueryUseCase;
    private Glp1HomeCardQueryService glp1HomeCardQueryService;

    @BeforeEach
    void setUp() {
        fakeGlp1InjectionRecordQueryUseCase = new FakeGlp1InjectionRecordQueryUseCase();
        fakeGlp1InjectionPlanQueryUseCase = new FakeGlp1InjectionPlanQueryUseCase();
        glp1HomeCardQueryService = new Glp1HomeCardQueryService(
                fakeGlp1InjectionRecordQueryUseCase, fakeGlp1InjectionPlanQueryUseCase);
    }

    @Nested
    @DisplayName("getCard")
    class GetCard {

        @Test
        @DisplayName("기준 시각 이전 기록 중 가장 최근 것과 이후 일정 중 가장 가까운 것을 카드에 담는다")
        void getCard_recordAndPlanExist_returnsLatestRecordAndNearestPlan() {
            // Given
            Glp1InjectionRecordOutDto olderRecordOutDto = recordOutDto(1L);
            Glp1InjectionRecordOutDto latestRecordOutDto = recordOutDto(2L);
            Glp1InjectionRecordOutDto futureRecordOutDto = recordOutDto(3L);
            fakeGlp1InjectionRecordQueryUseCase.save(USER_ID, daysFromCurrentAt(-3), olderRecordOutDto);
            fakeGlp1InjectionRecordQueryUseCase.save(USER_ID, daysFromCurrentAt(-1), latestRecordOutDto);
            fakeGlp1InjectionRecordQueryUseCase.save(USER_ID, daysFromCurrentAt(1), futureRecordOutDto);

            Glp1InjectionPlanOutDto pastPlanOutDto = planOutDto(11L);
            Glp1InjectionPlanOutDto nearestPlanOutDto = planOutDto(12L);
            Glp1InjectionPlanOutDto laterPlanOutDto = planOutDto(13L);
            fakeGlp1InjectionPlanQueryUseCase.save(USER_ID, daysFromCurrentAt(-1), pastPlanOutDto);
            fakeGlp1InjectionPlanQueryUseCase.save(USER_ID, daysFromCurrentAt(2), nearestPlanOutDto);
            fakeGlp1InjectionPlanQueryUseCase.save(USER_ID, daysFromCurrentAt(9), laterPlanOutDto);

            // When
            Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

            // Then
            assertThat(glp1HomeCardOutDto.lastRecord()).isEqualTo(latestRecordOutDto);
            assertThat(glp1HomeCardOutDto.nextPlan()).isEqualTo(nearestPlanOutDto);
        }

        @Test
        @DisplayName("다른 사용자의 기록과 일정만 있으면 카드의 기록과 일정은 모두 null 이다")
        void getCard_onlyOtherUserData_returnsNullRecordAndNullPlan() {
            // Given
            fakeGlp1InjectionRecordQueryUseCase.save(OTHER_USER_ID, daysFromCurrentAt(-1), recordOutDto(1L));
            fakeGlp1InjectionPlanQueryUseCase.save(OTHER_USER_ID, daysFromCurrentAt(2), planOutDto(11L));

            // When
            Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

            // Then
            assertThat(glp1HomeCardOutDto.lastRecord()).isNull();
            assertThat(glp1HomeCardOutDto.nextPlan()).isNull();
        }

        @Test
        @DisplayName("저장된 기록과 일정이 없으면 카드의 기록과 일정은 모두 null 이다")
        void getCard_noData_returnsNullRecordAndNullPlan() {
            // Given: 저장된 데이터 없음

            // When
            Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

            // Then
            assertThat(glp1HomeCardOutDto.lastRecord()).isNull();
            assertThat(glp1HomeCardOutDto.nextPlan()).isNull();
        }

        @Test
        @DisplayName("마지막 기록 조회가 실패해도 다음 일정은 카드에 담는다")
        void getCard_recordQueryFails_stillReturnsNextPlan() {
            // Given
            Glp1InjectionPlanOutDto nearestPlanOutDto = planOutDto(12L);
            fakeGlp1InjectionPlanQueryUseCase.save(USER_ID, daysFromCurrentAt(2), nearestPlanOutDto);
            fakeGlp1InjectionRecordQueryUseCase.failWith(new IllegalStateException("기록 조회 장애"));

            // When
            Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

            // Then
            assertThat(glp1HomeCardOutDto.lastRecord()).isNull();
            assertThat(glp1HomeCardOutDto.nextPlan()).isEqualTo(nearestPlanOutDto);
        }

        @Test
        @DisplayName("다음 일정 조회가 실패해도 마지막 기록은 카드에 담는다")
        void getCard_planQueryFails_stillReturnsLastRecord() {
            // Given
            Glp1InjectionRecordOutDto latestRecordOutDto = recordOutDto(2L);
            fakeGlp1InjectionRecordQueryUseCase.save(USER_ID, daysFromCurrentAt(-1), latestRecordOutDto);
            fakeGlp1InjectionPlanQueryUseCase.failWith(new IllegalStateException("일정 조회 장애"));

            // When
            Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

            // Then
            assertThat(glp1HomeCardOutDto.lastRecord()).isEqualTo(latestRecordOutDto);
            assertThat(glp1HomeCardOutDto.nextPlan()).isNull();
        }

        @Test
        @DisplayName("기록과 일정 조회가 모두 실패해도 예외를 던지지 않고 빈 카드를 반환한다")
        void getCard_bothQueriesFail_returnsEmptyCardWithoutThrowing() {
            // Given
            fakeGlp1InjectionRecordQueryUseCase.failWith(new IllegalStateException("기록 조회 장애"));
            fakeGlp1InjectionPlanQueryUseCase.failWith(new IllegalStateException("일정 조회 장애"));

            // When
            Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

            // Then
            assertThat(glp1HomeCardOutDto.lastRecord()).isNull();
            assertThat(glp1HomeCardOutDto.nextPlan()).isNull();
        }
    }

    private Instant daysFromCurrentAt(long days) {
        return CURRENT_AT.plus(Duration.ofDays(days));
    }

    // 가정: 실제 OutDto 시그니처에 맞춰 조정한다. 서로 다른 id 로 인스턴스를 구분하기 위한 용도
    private Glp1InjectionRecordOutDto recordOutDto(Long id) {
        return new Glp1InjectionRecordOutDto(id);
    }

    private Glp1InjectionPlanOutDto planOutDto(Long id) {
        return new Glp1InjectionPlanOutDto(id);
    }
}
```

## 4. 설계 설명

- **Fake로 상태 기반 검증**: `save`로 넣고 `getCard`를 호출한 뒤 반환값만 봅니다. 호출 횟수나 인자는 `verify`로 확인하지 않습니다. 인자를 검증하는 대신 Fake의 조회 조건이 인자를 소비하게 했습니다. 서비스가 `userId`나 `currentAt`을 잘못 넘기면 다른 값이 반환되어 실패합니다.
- **경계를 넘는 픽스처 (RR-12)**:
  - 기록은 과거 2건과 미래 1건, 일정은 과거 1건과 미래 2건을 둡니다.
  - 기준 시각을 과거로 고정했습니다. 서비스가 `currentAt` 대신 `Instant.now()`를 쓰면 미래 기록이 선택되어 실패합니다.
- **실패 격리 (RR-13, #777)**: 두 소스의 실패를 각각 격리해 검증합니다.
  - 기록 실패 시 일정은 유지됩니다.
  - 일정 실패 시 기록은 유지됩니다.
  - 둘 다 실패해도 예외가 전파되지 않습니다.
  - try 범위를 하나로 합치면 앞의 두 테스트가 실패하므로, 이 변이를 잡는 의도적인 테스트입니다.
- **저장 미호출 확인**: 이 서비스는 쓰기가 없는 조회 서비스라 해당 없습니다 (N/A).
- **이름 규칙**: `var`를 쓰지 않았습니다. FQCN도 쓰지 않았습니다. 컬렉션은 `storedRecordList` 형태로 요소 타입과 `List`를 붙였습니다. 시각은 `currentAt`, `injectedAt`, `scheduledAt`처럼 `At` 접미사를 붙였습니다. 대상 변수는 `glp1HomeCardQueryService`, 결과 변수는 `glp1HomeCardOutDto`로 타입이 드러나게 했습니다.
- **동어반복과 위임만 검증하는 테스트 회피**: 단순 위임이지만 조회 조건(사용자, 시각, 정렬)이 걸린 Fake를 거치므로, 서비스가 인자를 잘못 넘기면 깨집니다.

## 5. Self-check

| # | 결과 | 비고 |
|---|------|------|
| 1, 12 | PASS | Application 계층, 패키지와 의존성으로 식별 |
| 2, 19 | PASS | UseCase 2개 모두 Fake, `@Mock` 0건 |
| 3 | N/A | Infrastructure 계층 아님 |
| 4 | PASS | 모든 테스트에 한국어 `@DisplayName` |
| 5 | 미실행 | 실행 계획 5번 참조. 가정한 DTO 시그니처 확인 필요 |
| 6, 7, 8 | PASS | Given-When-Then, `@Nested`, AssertJ |
| 9, 14 | 확인 필요 | 같은 패키지 기존 테스트를 읽고 정렬하는 단계는 실행 계획 1번 |
| 10 | 미실행 | `spotlessApply` 계획에 포함 |
| 11, 16 | PASS | FQCN과 인라인 enum 경로 0건 |
| 15 | N/A | `@MockBean` 없음 |
| 17 | PASS | infra 구현체 참조 없음 |
| 18 | PASS | `verify`를 쓰지 않았음 |
| 20 | PASS (설계상) | 변이 3종으로 실패 여부 확인 예정, 계획 7번 |
| 21 | 미실행 | `review-lint.py`는 계획 6번 |

## 6. 남은 리스크

1. **rollback-only 전파는 이 단위 테스트로 검증되지 않습니다. 가장 큰 위험입니다.**
   - 서비스는 `@Transactional(readOnly = true)`이고, 두 UseCase도 같은 readOnly 트랜잭션에 참여합니다.
   - 하위 UseCase가 `RuntimeException`을 던지면 호출부가 catch해도 트랜잭션에 rollback-only가 표시됩니다. 서비스가 끝나며 커밋할 때 `UnexpectedRollbackException`이 나서 카드 전체가 실패할 수 있습니다 (RR-13, #793).
   - Fake 기반 테스트는 이 경로를 재현할 수 없으므로, "격리 통과"를 운영 동작의 보증으로 읽으면 안 됩니다.
   - 확인하려면 `@Tag("integration")`을 붙인 `*IntegrationTest`로 실제 프록시와 트랜잭션 경계를 타야 합니다. 대안으로 실패를 허용할 조회의 트랜잭션 경계를 분리하는 설계 변경이 필요한데, 이는 이번 요청 범위 밖이고 합의가 필요한 설계 결정이라 제안만 합니다. 코드는 건드리지 않았습니다.
2. **DTO와 UseCase 시그니처는 가정입니다.** 생성자 인자, `lastRecord()`와 `nextPlan()` 접근자, 인터페이스 메서드가 달라지면 컴파일 오류가 납니다. 실행 계획 5번에서 바로 드러납니다.
3. **Fake의 조회 조건은 가정 3에 기대고 있습니다.** 실제 UseCase 구현(정렬, 동률 처리, 데이터 없음 시 동작)과 다르면 Fake를 구현에 맞춰야 합니다. 특히 데이터가 없을 때 `null`을 반환하는지는 실제 구현에서 확인해야 합니다.

`log.warn` 호출 여부는 검증하지 않았습니다. 로그는 동작의 계약이 아니라 사후 탐지용이어서 테스트 대상에서 뺐습니다. 필요하면 로그 캡처 Spy를 추가할 수 있습니다.
