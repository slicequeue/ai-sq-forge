<!-- TC-8 with-skill / skill v1.10 트레이닝 후 / sonnet / 2026-11-13 -->
Glp1HomeCardQueryService.getCard 테스트 9건 작성 완료 (코드 작성, 테스트 실행 전)
- 계층·방식: Application / 단위 7건은 Fake UseCase 2개(Spring 없음), 통합 2건은 `@SpringBootTest`(DB 없음, 테스트 DB 설정 변경 없음)
- 조직 컨벤션: 적용 — `.claude/shared/vc-conventions-guide.md`, `vc-conventions/testcode-convention.md` 있음 (프로젝트 맥락)
- 요청과 다르게 한 것: 단위 테스트 요청에 통합 테스트 2건 추가(RR-13 실패 격리, 스킬 "실패 격리 테스트", 가이드 3절 `@SpringBootTest` 예외)
- 미확인: gradle·lint 를 실행하지 않았다. 통합 테스트 2건은 현재 서비스 코드에서 `UnexpectedRollbackException` 으로 실패할 것으로 보이며, 실패하면 테스트 결함이 아니라 서비스 결함이다(아래 세부)

## 확인한 것 / 가정한 것

| 구분 | 내용 |
|------|------|
| 확인 | 대상 `Glp1HomeCardQueryService`: `@Service`, 협력 객체가 `*QueryUseCase` 2개, 호출 메서드는 `getLast(Long, Instant)`·`getNext(Long, Instant)`, 두 호출을 각각 `try/catch (RuntimeException)` 으로 감쌈 |
| 확인 | 두 UseCase 의 Fake 가 없음(`find . -name "Fake*"` 결과) → 새로 만든다 |
| 확인 | Spring Boot 3.2.2 → `@MockitoBean` 없음. 이번 테스트는 Controller 가 아니라 해당 없음 |
| 가정 | 패키지 `com.kakaohealthcare.pasta.glp1.application` (실제 경로 미확인, 맞춰 바꿔야 함) |
| 가정 | UseCase 인터페이스 메서드가 `getLast`·`getNext` 뿐이다. 더 있으면 Fake 에 구현을 추가해야 컴파일된다 |
| 가정 | `Glp1InjectionRecordOutDto(Long id, Instant injectedAt)`, `Glp1InjectionPlanOutDto(Long id, Instant plannedAt)` 생성자 시그니처와 `Glp1HomeCardOutDto` 의 접근자 `lastRecord()`·`nextPlan()`. Fixture 한 곳(`Glp1HomeCardFixture`)에만 모아 두었다 |
| 가정 | 대상이 없을 때 UseCase 가 `null` 을 반환하는 것으로 Fake 를 만들었다. 실제가 예외라면 서비스가 catch 해서 같은 결과(null)가 나온다 |
| 가정 | `log` 는 `@Slf4j` 로 선언되어 있다(전제 코드에 선언부가 없음) |

## 계층 식별 근거
`@Service` + `*QueryUseCase` 를 생성자로 받음 + 사용자가 "Application 계층"이라고 명시. 조직 컨벤션 표(원문 3절)의 "Service·Facade = Fixture + `Fake*` Repository·UseCase, Spring Context 없음"을 따른다. UseCase 는 상태를 가진 협력 객체라 규칙 08 §2 에 따라 `@Mock` 이 아니라 Fake 다.

## 작성한 파일 (신규 5개, 모두 `pasta-api/src/test/java/com/kakaohealthcare/pasta/glp1/application/`)

신규 파일이라 기존 테스트를 덮어쓰지 않는다(DW-3). 같은 이름 파일이 이미 있는지는 아래 명령 1번에서 확인한다.

### 1. Glp1HomeCardFixture.java

```java
package com.kakaohealthcare.pasta.glp1.application;

import java.time.Instant;

final class Glp1HomeCardFixture {

    static final Long USER_ID = 1001L;
    static final Long OTHER_USER_ID = 2002L;
    static final Instant CURRENT_AT = Instant.parse("2026-11-13T00:00:00Z");

    private Glp1HomeCardFixture() {
    }

    // 가정: 생성자 시그니처 — 실제 OutDto 에 맞춰 이 두 메서드만 고친다
    static Glp1InjectionRecordOutDto injectionRecordOutDto(Long id, Instant injectedAt) {
        return new Glp1InjectionRecordOutDto(id, injectedAt);
    }

    static Glp1InjectionPlanOutDto injectionPlanOutDto(Long id, Instant plannedAt) {
        return new Glp1InjectionPlanOutDto(id, plannedAt);
    }
}
```

### 2. FakeGlp1InjectionRecordQueryUseCase.java

```java
package com.kakaohealthcare.pasta.glp1.application;

import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

class FakeGlp1InjectionRecordQueryUseCase implements Glp1InjectionRecordQueryUseCase {

    private final List<SavedRecord> savedRecordList = new ArrayList<>();
    private RuntimeException getLastException;

    void save(Long userId, Instant recordedAt, Glp1InjectionRecordOutDto glp1InjectionRecordOutDto) {
        savedRecordList.add(new SavedRecord(userId, recordedAt, glp1InjectionRecordOutDto));
    }

    void failOnGetLast(RuntimeException runtimeException) {
        this.getLastException = runtimeException;
    }

    void reset() {
        savedRecordList.clear();
        getLastException = null;
    }

    // 실제와 같은 조건: 같은 사용자, currentAt 이하(미래 기록 제외), 가장 최근 1건. 없으면 null
    @Override
    public Glp1InjectionRecordOutDto getLast(Long userId, Instant currentAt) {
        if (getLastException != null) {
            throw getLastException;
        }
        return savedRecordList.stream()
                .filter(savedRecord -> savedRecord.userId().equals(userId))
                .filter(savedRecord -> !savedRecord.recordedAt().isAfter(currentAt))
                .max(Comparator.comparing(SavedRecord::recordedAt))
                .map(SavedRecord::glp1InjectionRecordOutDto)
                .orElse(null);
    }

    private record SavedRecord(
            Long userId, Instant recordedAt, Glp1InjectionRecordOutDto glp1InjectionRecordOutDto) {
    }
}
```

### 3. FakeGlp1InjectionPlanQueryUseCase.java

```java
package com.kakaohealthcare.pasta.glp1.application;

import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

class FakeGlp1InjectionPlanQueryUseCase implements Glp1InjectionPlanQueryUseCase {

    private final List<SavedPlan> savedPlanList = new ArrayList<>();
    private RuntimeException getNextException;

    void save(Long userId, Instant plannedAt, Glp1InjectionPlanOutDto glp1InjectionPlanOutDto) {
        savedPlanList.add(new SavedPlan(userId, plannedAt, glp1InjectionPlanOutDto));
    }

    void failOnGetNext(RuntimeException runtimeException) {
        this.getNextException = runtimeException;
    }

    void reset() {
        savedPlanList.clear();
        getNextException = null;
    }

    // 실제와 같은 조건: 같은 사용자, currentAt 이후(지난 일정 제외), 가장 가까운 1건. 없으면 null
    @Override
    public Glp1InjectionPlanOutDto getNext(Long userId, Instant currentAt) {
        if (getNextException != null) {
            throw getNextException;
        }
        return savedPlanList.stream()
                .filter(savedPlan -> savedPlan.userId().equals(userId))
                .filter(savedPlan -> savedPlan.plannedAt().isAfter(currentAt))
                .min(Comparator.comparing(SavedPlan::plannedAt))
                .map(SavedPlan::glp1InjectionPlanOutDto)
                .orElse(null);
    }

    private record SavedPlan(Long userId, Instant plannedAt, Glp1InjectionPlanOutDto glp1InjectionPlanOutDto) {
    }
}
```

### 4. Glp1HomeCardQueryServiceTest.java (단위, 7건)

```java
package com.kakaohealthcare.pasta.glp1.application;

import static com.kakaohealthcare.pasta.glp1.application.Glp1HomeCardFixture.CURRENT_AT;
import static com.kakaohealthcare.pasta.glp1.application.Glp1HomeCardFixture.OTHER_USER_ID;
import static com.kakaohealthcare.pasta.glp1.application.Glp1HomeCardFixture.USER_ID;
import static org.assertj.core.api.Assertions.assertThat;

import java.time.Duration;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class Glp1HomeCardQueryServiceTest {

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

    @Test
    @DisplayName("마지막 기록과 다음 일정이 모두 있으면 둘 다 담아 응답한다")
    void getCard_recordAndPlanExist_returnsBoth() {
        // Given
        Glp1InjectionRecordOutDto lastGlp1InjectionRecordOutDto =
                Glp1HomeCardFixture.injectionRecordOutDto(11L, CURRENT_AT.minus(Duration.ofDays(3)));
        Glp1InjectionPlanOutDto nextGlp1InjectionPlanOutDto =
                Glp1HomeCardFixture.injectionPlanOutDto(21L, CURRENT_AT.plus(Duration.ofDays(4)));
        fakeGlp1InjectionRecordQueryUseCase.save(
                USER_ID, CURRENT_AT.minus(Duration.ofDays(3)), lastGlp1InjectionRecordOutDto);
        fakeGlp1InjectionPlanQueryUseCase.save(
                USER_ID, CURRENT_AT.plus(Duration.ofDays(4)), nextGlp1InjectionPlanOutDto);

        // When
        Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

        // Then
        assertThat(glp1HomeCardOutDto)
                .extracting(Glp1HomeCardOutDto::lastRecord, Glp1HomeCardOutDto::nextPlan)
                .containsExactly(lastGlp1InjectionRecordOutDto, nextGlp1InjectionPlanOutDto);
    }

    @Test
    @DisplayName("기록과 일정이 하나도 없으면 마지막 기록과 다음 일정을 모두 null 로 응답한다")
    void getCard_noRecordAndNoPlan_returnsBothNull() {
        // Given: 아무것도 저장하지 않는다

        // When
        Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

        // Then
        assertThat(glp1HomeCardOutDto)
                .extracting(Glp1HomeCardOutDto::lastRecord, Glp1HomeCardOutDto::nextPlan)
                .containsExactly(null, null);
    }

    @Test
    @DisplayName("다른 사용자의 기록과 일정은 담지 않고 요청한 사용자의 것만 응답한다")
    void getCard_otherUserDataExists_returnsOnlyRequestedUserData() {
        // Given
        Glp1InjectionRecordOutDto userGlp1InjectionRecordOutDto =
                Glp1HomeCardFixture.injectionRecordOutDto(11L, CURRENT_AT.minus(Duration.ofDays(7)));
        Glp1InjectionPlanOutDto userGlp1InjectionPlanOutDto =
                Glp1HomeCardFixture.injectionPlanOutDto(21L, CURRENT_AT.plus(Duration.ofDays(7)));
        fakeGlp1InjectionRecordQueryUseCase.save(
                USER_ID, CURRENT_AT.minus(Duration.ofDays(7)), userGlp1InjectionRecordOutDto);
        fakeGlp1InjectionPlanQueryUseCase.save(
                USER_ID, CURRENT_AT.plus(Duration.ofDays(7)), userGlp1InjectionPlanOutDto);
        // 다른 사용자 데이터가 더 최근·더 가까워서, userId 를 넘기지 않으면 이쪽이 선택된다
        fakeGlp1InjectionRecordQueryUseCase.save(
                OTHER_USER_ID,
                CURRENT_AT.minus(Duration.ofDays(1)),
                Glp1HomeCardFixture.injectionRecordOutDto(12L, CURRENT_AT.minus(Duration.ofDays(1))));
        fakeGlp1InjectionPlanQueryUseCase.save(
                OTHER_USER_ID,
                CURRENT_AT.plus(Duration.ofDays(1)),
                Glp1HomeCardFixture.injectionPlanOutDto(22L, CURRENT_AT.plus(Duration.ofDays(1))));

        // When
        Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

        // Then
        assertThat(glp1HomeCardOutDto)
                .extracting(Glp1HomeCardOutDto::lastRecord, Glp1HomeCardOutDto::nextPlan)
                .containsExactly(userGlp1InjectionRecordOutDto, userGlp1InjectionPlanOutDto);
    }

    @Test
    @DisplayName("현재 시각 이후에 기록된 주사는 마지막 기록에서, 지난 일정은 다음 일정에서 제외한다")
    void getCard_futureRecordAndPastPlanExist_excludesThem() {
        // Given
        Glp1InjectionRecordOutDto pastGlp1InjectionRecordOutDto =
                Glp1HomeCardFixture.injectionRecordOutDto(11L, CURRENT_AT.minus(Duration.ofDays(5)));
        Glp1InjectionPlanOutDto upcomingGlp1InjectionPlanOutDto =
                Glp1HomeCardFixture.injectionPlanOutDto(21L, CURRENT_AT.plus(Duration.ofDays(5)));
        fakeGlp1InjectionRecordQueryUseCase.save(
                USER_ID, CURRENT_AT.minus(Duration.ofDays(5)), pastGlp1InjectionRecordOutDto);
        fakeGlp1InjectionPlanQueryUseCase.save(
                USER_ID, CURRENT_AT.plus(Duration.ofDays(5)), upcomingGlp1InjectionPlanOutDto);
        // currentAt 을 넘기지 않으면 이쪽이 선택되도록 경계를 충분히 넘는 픽스처
        fakeGlp1InjectionRecordQueryUseCase.save(
                USER_ID,
                CURRENT_AT.plus(Duration.ofDays(2)),
                Glp1HomeCardFixture.injectionRecordOutDto(12L, CURRENT_AT.plus(Duration.ofDays(2))));
        fakeGlp1InjectionPlanQueryUseCase.save(
                USER_ID,
                CURRENT_AT.minus(Duration.ofDays(2)),
                Glp1HomeCardFixture.injectionPlanOutDto(22L, CURRENT_AT.minus(Duration.ofDays(2))));

        // When
        Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

        // Then
        assertThat(glp1HomeCardOutDto)
                .extracting(Glp1HomeCardOutDto::lastRecord, Glp1HomeCardOutDto::nextPlan)
                .containsExactly(pastGlp1InjectionRecordOutDto, upcomingGlp1InjectionPlanOutDto);
    }

    @Nested
    @DisplayName("한 조회가 예외를 내면")
    class WhenOneQueryFails {

        @Test
        @DisplayName("마지막 기록 조회가 실패해도 다음 일정은 담고 마지막 기록만 null 로 응답한다")
        void getCard_recordQueryFails_returnsPlanWithNullRecord() {
            // Given
            Glp1InjectionPlanOutDto nextGlp1InjectionPlanOutDto =
                    Glp1HomeCardFixture.injectionPlanOutDto(21L, CURRENT_AT.plus(Duration.ofDays(4)));
            fakeGlp1InjectionPlanQueryUseCase.save(
                    USER_ID, CURRENT_AT.plus(Duration.ofDays(4)), nextGlp1InjectionPlanOutDto);
            fakeGlp1InjectionRecordQueryUseCase.failOnGetLast(new IllegalStateException("기록 조회 실패"));

            // When
            Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

            // Then
            assertThat(glp1HomeCardOutDto)
                    .extracting(Glp1HomeCardOutDto::lastRecord, Glp1HomeCardOutDto::nextPlan)
                    .containsExactly(null, nextGlp1InjectionPlanOutDto);
        }

        @Test
        @DisplayName("다음 일정 조회가 실패해도 마지막 기록은 담고 다음 일정만 null 로 응답한다")
        void getCard_planQueryFails_returnsRecordWithNullPlan() {
            // Given
            Glp1InjectionRecordOutDto lastGlp1InjectionRecordOutDto =
                    Glp1HomeCardFixture.injectionRecordOutDto(11L, CURRENT_AT.minus(Duration.ofDays(3)));
            fakeGlp1InjectionRecordQueryUseCase.save(
                    USER_ID, CURRENT_AT.minus(Duration.ofDays(3)), lastGlp1InjectionRecordOutDto);
            fakeGlp1InjectionPlanQueryUseCase.failOnGetNext(new IllegalStateException("일정 조회 실패"));

            // When
            Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

            // Then
            assertThat(glp1HomeCardOutDto)
                    .extracting(Glp1HomeCardOutDto::lastRecord, Glp1HomeCardOutDto::nextPlan)
                    .containsExactly(lastGlp1InjectionRecordOutDto, null);
        }

        @Test
        @DisplayName("두 조회가 모두 실패하면 예외를 던지지 않고 둘 다 null 로 응답한다")
        void getCard_bothQueriesFail_returnsBothNull() {
            // Given
            fakeGlp1InjectionRecordQueryUseCase.failOnGetLast(new IllegalStateException("기록 조회 실패"));
            fakeGlp1InjectionPlanQueryUseCase.failOnGetNext(new IllegalStateException("일정 조회 실패"));

            // When
            Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

            // Then
            assertThat(glp1HomeCardOutDto)
                    .extracting(Glp1HomeCardOutDto::lastRecord, Glp1HomeCardOutDto::nextPlan)
                    .containsExactly(null, null);
        }
    }
}
```

### 5. Glp1HomeCardQueryServiceIntegrationTest.java (통합, 2건)

```java
package com.kakaohealthcare.pasta.glp1.application;

import static com.kakaohealthcare.pasta.glp1.application.Glp1HomeCardFixture.CURRENT_AT;
import static com.kakaohealthcare.pasta.glp1.application.Glp1HomeCardFixture.USER_ID;
import static org.assertj.core.api.Assertions.assertThat;

import java.time.Duration;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.test.util.AopTestUtils;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.TransactionDefinition;
import org.springframework.transaction.annotation.EnableTransactionManagement;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.AbstractPlatformTransactionManager;
import org.springframework.transaction.support.DefaultTransactionStatus;
import org.springframework.transaction.support.SmartTransactionObject;

// @SpringBootTest 예외: 같은 트랜잭션에 참여한 하위 UseCase 가 예외를 내면 rollback-only 가 걸리는지는
// 서비스·UseCase 프록시 경계를 넘어야 재현된다. Fake 직접 주입(단위)·@DataJpaTest 로는 재현 안 됨
// (vc-conventions-guide 3절, review-recurrence-guard RR-13 #793). DB 는 쓰지 않는다.
@SpringBootTest(classes = Glp1HomeCardQueryServiceIntegrationTest.TestConfig.class)
@Tag("integration")
class Glp1HomeCardQueryServiceIntegrationTest {

    private FakeGlp1InjectionRecordQueryUseCase fakeGlp1InjectionRecordQueryUseCase;
    private FakeGlp1InjectionPlanQueryUseCase fakeGlp1InjectionPlanQueryUseCase;
    private Glp1HomeCardQueryService glp1HomeCardQueryService;

    @BeforeEach
    void setUp(
            @Autowired Glp1InjectionRecordQueryUseCase glp1InjectionRecordQueryUseCase,
            @Autowired Glp1InjectionPlanQueryUseCase glp1InjectionPlanQueryUseCase,
            @Autowired Glp1HomeCardQueryService glp1HomeCardQueryService) {
        // 컨텍스트는 클래스 안에서 공유되므로 프록시 뒤의 실제 Fake 를 꺼내 매번 비운다
        this.fakeGlp1InjectionRecordQueryUseCase =
                AopTestUtils.getUltimateTargetObject(glp1InjectionRecordQueryUseCase);
        this.fakeGlp1InjectionPlanQueryUseCase =
                AopTestUtils.getUltimateTargetObject(glp1InjectionPlanQueryUseCase);
        fakeGlp1InjectionRecordQueryUseCase.reset();
        fakeGlp1InjectionPlanQueryUseCase.reset();
        this.glp1HomeCardQueryService = glp1HomeCardQueryService;
    }

    @Test
    @DisplayName("트랜잭션 안에서 마지막 기록 조회가 실패해도 다음 일정은 담아 응답한다")
    void getCard_recordQueryFailsInTransaction_returnsPlanWithNullRecord() {
        // Given
        Glp1InjectionPlanOutDto nextGlp1InjectionPlanOutDto =
                Glp1HomeCardFixture.injectionPlanOutDto(21L, CURRENT_AT.plus(Duration.ofDays(4)));
        fakeGlp1InjectionPlanQueryUseCase.save(
                USER_ID, CURRENT_AT.plus(Duration.ofDays(4)), nextGlp1InjectionPlanOutDto);
        fakeGlp1InjectionRecordQueryUseCase.failOnGetLast(new IllegalStateException("기록 조회 실패"));

        // When
        Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

        // Then
        assertThat(glp1HomeCardOutDto)
                .extracting(Glp1HomeCardOutDto::lastRecord, Glp1HomeCardOutDto::nextPlan)
                .containsExactly(null, nextGlp1InjectionPlanOutDto);
    }

    @Test
    @DisplayName("트랜잭션 안에서 다음 일정 조회가 실패해도 마지막 기록은 담아 응답한다")
    void getCard_planQueryFailsInTransaction_returnsRecordWithNullPlan() {
        // Given
        Glp1InjectionRecordOutDto lastGlp1InjectionRecordOutDto =
                Glp1HomeCardFixture.injectionRecordOutDto(11L, CURRENT_AT.minus(Duration.ofDays(3)));
        fakeGlp1InjectionRecordQueryUseCase.save(
                USER_ID, CURRENT_AT.minus(Duration.ofDays(3)), lastGlp1InjectionRecordOutDto);
        fakeGlp1InjectionPlanQueryUseCase.failOnGetNext(new IllegalStateException("일정 조회 실패"));

        // When
        Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

        // Then
        assertThat(glp1HomeCardOutDto)
                .extracting(Glp1HomeCardOutDto::lastRecord, Glp1HomeCardOutDto::nextPlan)
                .containsExactly(lastGlp1InjectionRecordOutDto, null);
    }

    @Configuration(proxyBeanMethods = false)
    @EnableTransactionManagement
    static class TestConfig {

        @Bean
        PlatformTransactionManager transactionManager() {
            return new FakeRollbackOnlyTransactionManager();
        }

        @Bean
        Glp1InjectionRecordQueryUseCase glp1InjectionRecordQueryUseCase() {
            return new TransactionalFakeGlp1InjectionRecordQueryUseCase();
        }

        @Bean
        Glp1InjectionPlanQueryUseCase glp1InjectionPlanQueryUseCase() {
            return new TransactionalFakeGlp1InjectionPlanQueryUseCase();
        }

        @Bean
        Glp1HomeCardQueryService glp1HomeCardQueryService(
                Glp1InjectionRecordQueryUseCase glp1InjectionRecordQueryUseCase,
                Glp1InjectionPlanQueryUseCase glp1InjectionPlanQueryUseCase) {
            return new Glp1HomeCardQueryService(glp1InjectionRecordQueryUseCase, glp1InjectionPlanQueryUseCase);
        }
    }

    // 실제 UseCase 구현이 @Transactional(readOnly = true) 인 것과 같은 조건으로 프록시를 만든다
    @Transactional(readOnly = true)
    static class TransactionalFakeGlp1InjectionRecordQueryUseCase extends FakeGlp1InjectionRecordQueryUseCase {
    }

    @Transactional(readOnly = true)
    static class TransactionalFakeGlp1InjectionPlanQueryUseCase extends FakeGlp1InjectionPlanQueryUseCase {
    }

    // DB 없이 전파·rollback-only 판정만 하는 최소 트랜잭션 매니저. 참여 트랜잭션 실패 시 전역 rollback-only 를 표시하고,
    // 바깥 트랜잭션 커밋 시점에 UnexpectedRollbackException 을 내는 것은 AbstractPlatformTransactionManager 가 한다
    static class FakeRollbackOnlyTransactionManager extends AbstractPlatformTransactionManager {

        private FakeTransactionObject currentFakeTransactionObject;

        @Override
        protected Object doGetTransaction() {
            return currentFakeTransactionObject != null ? currentFakeTransactionObject : new FakeTransactionObject();
        }

        @Override
        protected boolean isExistingTransaction(Object transaction) {
            return ((FakeTransactionObject) transaction).active;
        }

        @Override
        protected void doBegin(Object transaction, TransactionDefinition transactionDefinition) {
            FakeTransactionObject fakeTransactionObject = (FakeTransactionObject) transaction;
            fakeTransactionObject.active = true;
            currentFakeTransactionObject = fakeTransactionObject;
        }

        @Override
        protected void doCommit(DefaultTransactionStatus status) {
            currentFakeTransactionObject = null;
        }

        @Override
        protected void doRollback(DefaultTransactionStatus status) {
            currentFakeTransactionObject = null;
        }

        @Override
        protected void doSetRollbackOnly(DefaultTransactionStatus status) {
            ((FakeTransactionObject) status.getTransaction()).rollbackOnly = true;
        }
    }

    static class FakeTransactionObject implements SmartTransactionObject {

        private boolean active;
        private boolean rollbackOnly;

        @Override
        public boolean isRollbackOnly() {
            return rollbackOnly;
        }

        @Override
        public void flush() {
        }
    }
}
```

## 요청과 다르게 한 것의 근거
- 요청은 `getCard` 단위 테스트였다. 단위 7건에 더해 통합 2건을 넣었다. 서비스와 두 UseCase 가 모두 `@Transactional(readOnly = true)` 이고 서비스가 하위 호출 예외를 catch 하는 구조라, 하위 호출이 예외를 내면 호출부 catch 와 무관하게 rollback-only 가 걸려 바깥 커밋에서 `UnexpectedRollbackException` 이 날 수 있다(review-recurrence-guard RR-13, 표의 #793 행). Fake 직접 주입 단위 테스트는 이 경로를 한 번도 실행하지 못한다(RR-12 "목표 경로 미실행"). 단위의 실패 격리 3건만 통과시키고 끝내면 이 결함이 가려진다.
- `@SpringBootTest` 는 조직 컨벤션상 E2E 에만 쓰지만, 트랜잭션 전파처럼 슬라이스로 재현되지 않는 검증은 예외다(vc-conventions-guide 3절 `@SpringBootTest` 행, 스킬 "실패 격리 테스트"). 사유는 테스트 클래스 주석에 적었고 PR 본문에도 같은 문장을 넣는다: "`@SpringBootTest` 예외 사유: rollback-only 전파는 서비스·UseCase 프록시 경계를 넘어야 재현되며 Fake·슬라이스로는 재현 안 됨". 앱 전체 컨텍스트가 아니라 `classes = TestConfig` 로 4개 빈만 띄우고 DB 를 쓰지 않는다.
- 요청 외 추가: 다른 사용자 데이터 제외, currentAt 이후 기록·지난 일정 제외 테스트. 두 인자를 UseCase 에 넘기는 줄을 지워도 잡는 테스트가 없어서 넣었다(RR-14). 각 픽스처는 인자를 안 넘기면 다른 값이 선택되도록 경계를 넘게 만들었다.
- 사용자가 부른 이름 "Stub" 은 없다. 인메모리 대역은 `Fake*` 로 지었다(testcode-convention 원문 4절).

## Self-check

| # | 결과 | 비고 |
|---|------|------|
| 1 | PASS | Application, `@Service` + `*QueryUseCase` 생성자 의존으로 확정 |
| 2 | PASS | Fake 우선, Spy·Mock 없음 |
| 3 | PASS | 테스트 DB 사용·전환 없음. 통합 테스트도 DB 없는 최소 트랜잭션 매니저 |
| 4 | PASS | 9건 모두 구체적 한국어 `@DisplayName` |
| 5 | 미확인 | 실행하지 않았다. 통합 2건은 현재 서비스 코드에서 실패할 것으로 보인다(아래 리스크) |
| 6 | PASS | `// Given` `// When` `// Then` |
| 7 | PASS | `@Nested` 1개, 안에 테스트 3개 |
| 8 | PASS | AssertJ 만 |
| 9 | 미확인 | 같은 패키지의 기존 테스트를 읽지 못했다(과제 입력에 없음). 명령 1번 이후 확인 |
| 10 | 미실행 | spotlessApply 명령 아래 |
| 11 | PASS | FQCN 인라인 없음, 모두 import |
| 12 | PASS | 위 "계층 식별 근거" |
| 13 | PASS | 임의 문자열 없이 사용자 ID·시각 상수와 도메인 시각 사용. DTO 생성자는 가정 표기 |
| 14 | 미확인 | 기존 테스트 미확인(#9 와 동일) |
| 15 | N/A | `@MockBean` 없음 |
| 16 | PASS | enum 인라인 없음 |
| 17 | PASS | infra 구현체 참조 없음, domain 계약 Fake |
| 18 | PASS | 호출 검증 대신 Fake 상태·반환값으로 검증 |
| 19 | PASS | UseCase 를 `@Mock` 으로 두지 않음 |
| 20 | PASS | 인자 전달 줄을 깨뜨리면 실패하는 픽스처, 두 조회의 실패 분기 각각, 두 조회 동시 실패 |
| 21 | 미실행 | review-lint 명령 아래 |
| 22 | PASS | 대상의 분기는 두 try/catch 의 정상·예외 4가지, 모두 테스트 |
| 23 | PASS | 스스로 찾은 결함(rollback-only)은 서비스 수정이 범위 밖이라 코드를 고치지 않고, 그 결함을 잡는 테스트로 제출했다. 요청을 바꾼 지점마다 RR-13·RR-14·가이드 3절 인용 |
| 24 | PASS | 적용 판정과 근거를 요약에 적음 |
| 25 | PASS | `Fake*`, GWT, `Thread.sleep` 0, JUnit `Assertions` 0, `@BeforeAll` 0, `@SpringBootTest` 는 사유 주석 + PR 본문 문장, 테스트당 논리 검증 하나(두 필드 `extracting` 은 하나로 본다) |

테스트 변수명은 타입명 전체(`glp1HomeCardOutDto` 등), `result`·`dto`·`e`·`var` 를 쓰지 않았다. 람다 파라미터도 `savedRecord`·`savedPlan` 으로 풀어 썼다.

## 실행할 명령 (실행하지 않았다)

```bash
# 1. 작성 전 확인: 같은 이름 파일·기존 Fake·기존 테스트 패턴 (DW-1, DW-3)
git status --short pasta-api/src/test/java/com/kakaohealthcare/pasta/glp1/application/
find pasta-api/src/test -name "Glp1HomeCard*" -o -name "FakeGlp1Injection*"
ls pasta-api/src/test/java/com/kakaohealthcare/pasta/glp1/application/

# 2. 포매팅
./gradlew :pasta-api:spotlessApply

# 3. 테스트 (단위 + 통합)
./gradlew :pasta-api:test --tests '*Glp1HomeCardQueryService*'

# 4. 리뷰 린트 (VC 검사는 가이드가 옆에 있으면 자동으로 켜짐)
python3 .claude/shared/review-lint.py

# 5. 의도하지 않은 삭제 확인 (DW-5)
git status
```

린트에서 `[확인]` 으로 나올 것으로 보이는 항목은 신규 `@SpringBootTest`(사유 주석·PR 본문 문장으로 대응)와 `@Transactional` 달린 `TransactionalFake*` 의 `Stub*`/`Fake*` 이름 검사 정도다. 실제 출력은 실행해 봐야 안다.

## 남은 리스크

- 통합 2건이 실패하면 서비스 결함이다. 서비스·UseCase 가 같은 읽기 트랜잭션에 참여하는 한 하위 조회 예외가 바깥 커밋을 깨뜨린다. 해결은 트랜잭션 경계 분리(`REQUIRES_NEW` 또는 서비스의 `@Transactional` 제거 등)인데, 어느 쪽을 택할지는 프로덕션 코드 설계 결정이라 이번 범위(테스트 작성)에서 정하지 않았다. 방향을 정해 주시면 서비스 수정 후 이 통합 테스트로 회귀를 막는다. 서비스에서 `@Transactional` 을 뺄 경우 UseCase 가 각자 트랜잭션을 열기 때문에 단위 테스트는 그대로 유효하다
- 가정 표(DTO 생성자·접근자, 인터페이스 메서드, 패키지 경로)가 틀리면 컴파일 단계에서 드러난다. 고칠 곳은 Fixture 와 Fake 두 파일로 한정했다
- 통합 테스트의 최소 트랜잭션 매니저는 Spring 의 `AbstractPlatformTransactionManager` 전파 로직을 이용한 것이다. 실제 `JpaTransactionManager` 와 동작이 같은지는 실행해 보기 전에는 확인하지 못했다. 다르게 나오면 모듈의 기존 통합 테스트 설정을 확인한 뒤 사용자에게 묻는다
