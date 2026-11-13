<!-- TC-8 with-skill / skill v1.10 / sonnet / 2026-11-13 -->
Glp1HomeCardQueryService.getCard 테스트 5건 작성 완료 (코드 작성, 테스트 실행 전)
- 계층·방식: Application / Fake(UseCase 2종 신규) + `@SpringBootTest` 예외 1건(rollback-only 전파), 통합 테스트는 DB 를 쓰지 않아 테스트 DB 설정 변경 없음
- 조직 컨벤션: 적용 (`.claude/shared/vc-conventions-guide.md`, `.claude/shared/vc-conventions/testcode-convention.md` 있음)
- 요청과 다르게 한 것: 단위 테스트 외에 통합 테스트 1건을 추가했다. 서비스와 두 UseCase 가 모두 `@Transactional(readOnly = true)` 라서 하위 조회 예외가 rollback-only 를 걸고, Fake 단위 테스트로는 재현되지 않는다 (RR-13 #793, `forge/common/review-recurrence-guard.md` 13절, vc-testcode.md 2절)
- 결과: gradle test, review-lint 모두 실행하지 않음
- 미확인: 통합 테스트는 현재 서비스 코드에서 실패할 가능성이 높다. 입력 전제의 어노테이션 구조상 Spring 이 `UnexpectedRollbackException` 을 던질 것으로 보지만 실행해 보지 않았다. 실패하면 테스트가 아니라 서비스의 트랜잭션 경계가 결함이다

## 판정과 근거

| 항목 | 내용 |
|------|------|
| 계층 | Application. 근거: 클래스명 `Glp1HomeCardQueryService`, `@Service`, 협력 객체가 `*QueryUseCase` 두 개 (입력 프롬프트도 "Application 계층"이라 명시) |
| 조직 컨벤션 | 적용. 근거: 프로젝트 맥락에 `.claude/shared/vc-conventions-guide.md` 와 `testcode-convention.md` 존재. `references/vc-testcode.md` 기준으로 작성 |
| 테스트 더블 | 두 UseCase 는 상태를 가진 협력 객체이므로 `@Mock` 이 아니라 `Fake*` (규칙 08 §2, `.claude/rules/08-test-code-convention.md`). `find . -name "Fake*"` 결과 Fake 가 없어 새로 만든다 |
| 실패 주입 | Fake 에 `failWith(RuntimeException)` 를 둔다. 정답 반환값을 주입하는 `setResult` 가 아니라 예외 분기만 여는 스위치다 |
| 테스트 DB | 단위 테스트는 DB 없음. 통합 테스트는 DB 대신 최소 트랜잭션 매니저를 테스트 안에 직접 둬서 모듈의 `@ActiveProfiles`·H2·Testcontainers 설정을 건드리지 않는다 (규칙 09) |
| `@SpringBootTest` | E2E 아님. rollback-only 전파는 서비스 프록시 경계를 넘어야 재현되므로 vc-testcode.md 2절 예외. 클래스 주석에 사유를 적었고 PR 본문에도 한 줄 필요 |
| 프로덕션 코드 | 수정하지 않음 (SC-1 범위 규율) |

## 가정한 것 (코드 입력에 없어서 확인 필요)

- Fixture 생성: `Glp1InjectionRecordOutDto`, `Glp1InjectionPlanOutDto` 의 생성자 시그니처를 모른다. 아래 코드는 `(Long id, Instant ...)` 두 필드 record 로 가정했다. 실제 시그니처에 맞춰 `recordOutDto`·`planOutDto` 헬퍼 두 곳만 고친다
- `Glp1HomeCardOutDto` 접근자는 생성자 인자 이름대로 `lastRecord()`, `nextPlan()` 으로 가정했다
- 두 UseCase 인터페이스에는 `getLast`, `getNext` 한 메서드만 있다고 가정했다. 더 있으면 Fake 에 구현을 더해야 컴파일된다
- 패키지 경로는 `com.kakaohealthcare.pasta.glp1.application` 으로 가정했다. 실제 패키지와 같은 패키지에 두면 import 가 줄어든다
- Fake 의 `getLast`·`getNext` 는 `currentAt` 으로 거르지 않고 사용자별로 저장한 값을 돌려준다. 실제 구현의 시각 조건은 이 서비스 테스트의 관심사가 아니다(서비스는 `currentAt` 을 그대로 넘기기만 한다)
- 기존 `Glp1HomeCardQueryServiceTest` 가 있는지는 확인하지 못했다. 있으면 먼저 읽고 `Edit` 로 메서드만 추가한다. 통째로 덮어쓰지 않는다 (DW-3)

## 1. FakeGlp1InjectionRecordQueryUseCase

경로: `pasta-api/src/test/java/com/kakaohealthcare/pasta/glp1/application/FakeGlp1InjectionRecordQueryUseCase.java`

```java
package com.kakaohealthcare.pasta.glp1.application;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

class FakeGlp1InjectionRecordQueryUseCase implements Glp1InjectionRecordQueryUseCase {

    private final Map<Long, Glp1InjectionRecordOutDto> glp1InjectionRecordOutDtoByUserId = new HashMap<>();
    private RuntimeException failure;

    void save(Long userId, Glp1InjectionRecordOutDto glp1InjectionRecordOutDto) {
        glp1InjectionRecordOutDtoByUserId.put(userId, glp1InjectionRecordOutDto);
    }

    void failWith(RuntimeException failure) {
        this.failure = failure;
    }

    @Override
    public Glp1InjectionRecordOutDto getLast(Long userId, Instant currentAt) {
        if (failure != null) {
            throw failure;
        }
        return glp1InjectionRecordOutDtoByUserId.get(userId);
    }
}
```

## 2. FakeGlp1InjectionPlanQueryUseCase

경로: `pasta-api/src/test/java/com/kakaohealthcare/pasta/glp1/application/FakeGlp1InjectionPlanQueryUseCase.java`

```java
package com.kakaohealthcare.pasta.glp1.application;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

class FakeGlp1InjectionPlanQueryUseCase implements Glp1InjectionPlanQueryUseCase {

    private final Map<Long, Glp1InjectionPlanOutDto> glp1InjectionPlanOutDtoByUserId = new HashMap<>();
    private RuntimeException failure;

    void save(Long userId, Glp1InjectionPlanOutDto glp1InjectionPlanOutDto) {
        glp1InjectionPlanOutDtoByUserId.put(userId, glp1InjectionPlanOutDto);
    }

    void failWith(RuntimeException failure) {
        this.failure = failure;
    }

    @Override
    public Glp1InjectionPlanOutDto getNext(Long userId, Instant currentAt) {
        if (failure != null) {
            throw failure;
        }
        return glp1InjectionPlanOutDtoByUserId.get(userId);
    }
}
```

## 3. Glp1HomeCardQueryServiceTest (단위, Spring 없음)

경로: `pasta-api/src/test/java/com/kakaohealthcare/pasta/glp1/application/Glp1HomeCardQueryServiceTest.java`

```java
package com.kakaohealthcare.pasta.glp1.application;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.Instant;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class Glp1HomeCardQueryServiceTest {

    private static final Long USER_ID = 1L;
    private static final Long OTHER_USER_ID = 2L;
    private static final Instant CURRENT_AT = Instant.parse("2026-11-13T00:00:00Z");

    private FakeGlp1InjectionRecordQueryUseCase fakeGlp1InjectionRecordQueryUseCase;
    private FakeGlp1InjectionPlanQueryUseCase fakeGlp1InjectionPlanQueryUseCase;
    private Glp1HomeCardQueryService glp1HomeCardQueryService;

    @BeforeEach
    void setUp() {
        fakeGlp1InjectionRecordQueryUseCase = new FakeGlp1InjectionRecordQueryUseCase();
        fakeGlp1InjectionPlanQueryUseCase = new FakeGlp1InjectionPlanQueryUseCase();
        glp1HomeCardQueryService =
            new Glp1HomeCardQueryService(fakeGlp1InjectionRecordQueryUseCase, fakeGlp1InjectionPlanQueryUseCase);
    }

    @Test
    @DisplayName("마지막 기록과 다음 일정이 모두 있으면 요청한 사용자의 두 값을 카드에 담는다")
    void getCard_recordAndPlanExist_returnsRequestedUsersRecordAndPlan() {
        // Given
        Glp1InjectionRecordOutDto glp1InjectionRecordOutDto = recordOutDto(10L);
        Glp1InjectionPlanOutDto glp1InjectionPlanOutDto = planOutDto(20L);
        fakeGlp1InjectionRecordQueryUseCase.save(USER_ID, glp1InjectionRecordOutDto);
        fakeGlp1InjectionPlanQueryUseCase.save(USER_ID, glp1InjectionPlanOutDto);
        fakeGlp1InjectionRecordQueryUseCase.save(OTHER_USER_ID, recordOutDto(11L));
        fakeGlp1InjectionPlanQueryUseCase.save(OTHER_USER_ID, planOutDto(21L));

        // When
        Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

        // Then
        assertThat(glp1HomeCardOutDto)
            .extracting(Glp1HomeCardOutDto::lastRecord, Glp1HomeCardOutDto::nextPlan)
            .containsExactly(glp1InjectionRecordOutDto, glp1InjectionPlanOutDto);
    }

    @Test
    @DisplayName("마지막 기록 조회가 예외를 내도 다음 일정은 카드에 담고 마지막 기록은 비운다")
    void getCard_recordQueryFails_returnsNextPlanWithoutLastRecord() {
        // Given
        Glp1InjectionPlanOutDto glp1InjectionPlanOutDto = planOutDto(20L);
        fakeGlp1InjectionRecordQueryUseCase.save(USER_ID, recordOutDto(10L));
        fakeGlp1InjectionRecordQueryUseCase.failWith(new IllegalStateException("기록 조회 DB 장애"));
        fakeGlp1InjectionPlanQueryUseCase.save(USER_ID, glp1InjectionPlanOutDto);

        // When
        Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

        // Then
        assertThat(glp1HomeCardOutDto)
            .extracting(Glp1HomeCardOutDto::lastRecord, Glp1HomeCardOutDto::nextPlan)
            .containsExactly(null, glp1InjectionPlanOutDto);
    }

    @Test
    @DisplayName("다음 일정 조회가 예외를 내도 마지막 기록은 카드에 담고 다음 일정은 비운다")
    void getCard_planQueryFails_returnsLastRecordWithoutNextPlan() {
        // Given
        Glp1InjectionRecordOutDto glp1InjectionRecordOutDto = recordOutDto(10L);
        fakeGlp1InjectionRecordQueryUseCase.save(USER_ID, glp1InjectionRecordOutDto);
        fakeGlp1InjectionPlanQueryUseCase.save(USER_ID, planOutDto(20L));
        fakeGlp1InjectionPlanQueryUseCase.failWith(new IllegalStateException("일정 조회 DB 장애"));

        // When
        Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

        // Then
        assertThat(glp1HomeCardOutDto)
            .extracting(Glp1HomeCardOutDto::lastRecord, Glp1HomeCardOutDto::nextPlan)
            .containsExactly(glp1InjectionRecordOutDto, null);
    }

    @Test
    @DisplayName("두 조회가 모두 예외를 내도 예외를 던지지 않고 빈 카드를 돌려준다")
    void getCard_bothQueriesFail_returnsEmptyCardWithoutThrowing() {
        // Given
        fakeGlp1InjectionRecordQueryUseCase.failWith(new IllegalStateException("기록 조회 DB 장애"));
        fakeGlp1InjectionPlanQueryUseCase.failWith(new IllegalStateException("일정 조회 DB 장애"));

        // When
        Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

        // Then
        assertThat(glp1HomeCardOutDto)
            .extracting(Glp1HomeCardOutDto::lastRecord, Glp1HomeCardOutDto::nextPlan)
            .containsExactly(null, null);
    }

    // 가정: record Glp1InjectionRecordOutDto(Long id, Instant injectedAt). 실제 시그니처로 교체
    private Glp1InjectionRecordOutDto recordOutDto(Long id) {
        return new Glp1InjectionRecordOutDto(id, CURRENT_AT.minusSeconds(86_400L));
    }

    // 가정: record Glp1InjectionPlanOutDto(Long id, Instant scheduledAt). 실제 시그니처로 교체
    private Glp1InjectionPlanOutDto planOutDto(Long id) {
        return new Glp1InjectionPlanOutDto(id, CURRENT_AT.plusSeconds(86_400L));
    }
}
```

설계 메모
- 테스트마다 `USER_ID` 와 `OTHER_USER_ID` 의 값을 다르게 넣었다(1번 테스트). 서비스가 `userId` 를 잘못 넘기면 다른 사용자의 값이 나와 실패한다 (RR-12)
- 2·3번은 실패하지 않는 쪽 데이터를 반드시 넣었다. try 범위를 하나로 합치면(RR-13 #777 패턴) 한쪽 실패가 다른 쪽까지 비워 두 테스트가 실패한다
- 2·3번은 실패하는 쪽에도 데이터를 저장해 두어, 예외 없이 지나갔다면 값이 나왔을 상황에서 `null` 이 되는지 본다
- 검증 방식 확인 계획: try/catch 를 제거하거나 두 try 를 하나로 합쳐 보고 2·3·4번이 실패하는지 확인한다 (실행 전)
- 한 테스트의 검증은 "카드의 두 필드"라는 하나의 논리 검증이다 (vc-testcode.md 4절 `extracting(...).containsExactly(...)`)

## 4. Glp1HomeCardQueryServiceIntegrationTest (`@SpringBootTest` 예외)

경로: `pasta-api/src/test/java/com/kakaohealthcare/pasta/glp1/application/Glp1HomeCardQueryServiceIntegrationTest.java`

```java
package com.kakaohealthcare.pasta.glp1.application;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.Instant;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.TransactionDefinition;
import org.springframework.transaction.annotation.EnableTransactionManagement;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.AbstractPlatformTransactionManager;
import org.springframework.transaction.support.DefaultTransactionStatus;
import org.springframework.transaction.support.SmartTransactionObject;

// @SpringBootTest 예외 사유: 하위 조회가 같은 트랜잭션에서 예외를 내면 호출부가 catch 해도 rollback-only 가
// 걸려 커밋 시 UnexpectedRollbackException 이 난다. 서비스 프록시 경계를 넘어야 재현되므로
// Fake 단위 테스트·@DataJpaTest 로는 재현 안 됨 (vc-conventions-guide 3절, RR-13 #793).
// DB 는 쓰지 않는다. 모듈의 테스트 DB 설정(H2·Testcontainers)을 건드리지 않으려고 최소 트랜잭션 매니저를 직접 둔다.
@SpringBootTest(classes = Glp1HomeCardQueryServiceIntegrationTest.TransactionTestConfig.class)
@Tag("integration")
class Glp1HomeCardQueryServiceIntegrationTest {

    private static final Long USER_ID = 1L;
    private static final Instant CURRENT_AT = Instant.parse("2026-11-13T00:00:00Z");

    @Test
    @DisplayName("같은 트랜잭션의 마지막 기록 조회가 예외를 내도 커밋이 실패하지 않고 다음 일정을 카드에 담는다")
    void getCard_recordQueryFailsInSharedTransaction_returnsNextPlanWithoutRollbackError(
        @Autowired Glp1HomeCardQueryService glp1HomeCardQueryService,
        @Autowired TransactionalFakeGlp1InjectionRecordQueryUseCase transactionalFakeGlp1InjectionRecordQueryUseCase,
        @Autowired TransactionalFakeGlp1InjectionPlanQueryUseCase transactionalFakeGlp1InjectionPlanQueryUseCase) {
        // Given
        Glp1InjectionPlanOutDto glp1InjectionPlanOutDto = planOutDto(20L);
        transactionalFakeGlp1InjectionRecordQueryUseCase.failWith(new IllegalStateException("기록 조회 DB 장애"));
        transactionalFakeGlp1InjectionPlanQueryUseCase.save(USER_ID, glp1InjectionPlanOutDto);

        // When
        Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

        // Then
        assertThat(glp1HomeCardOutDto.nextPlan()).isEqualTo(glp1InjectionPlanOutDto);
    }

    // 가정: record Glp1InjectionPlanOutDto(Long id, Instant scheduledAt). 실제 시그니처로 교체
    private Glp1InjectionPlanOutDto planOutDto(Long id) {
        return new Glp1InjectionPlanOutDto(id, CURRENT_AT.plusSeconds(86_400L));
    }

    // 실제 구현 두 UseCase 가 @Transactional(readOnly = true) 인 구조를 그대로 재현한다
    @Transactional(readOnly = true)
    static class TransactionalFakeGlp1InjectionRecordQueryUseCase extends FakeGlp1InjectionRecordQueryUseCase {
    }

    @Transactional(readOnly = true)
    static class TransactionalFakeGlp1InjectionPlanQueryUseCase extends FakeGlp1InjectionPlanQueryUseCase {
    }

    @Configuration
    @EnableTransactionManagement
    static class TransactionTestConfig {

        @Bean
        PlatformTransactionManager transactionManager() {
            return new RollbackOnlyTrackingTransactionManager();
        }

        @Bean
        TransactionalFakeGlp1InjectionRecordQueryUseCase transactionalFakeGlp1InjectionRecordQueryUseCase() {
            return new TransactionalFakeGlp1InjectionRecordQueryUseCase();
        }

        @Bean
        TransactionalFakeGlp1InjectionPlanQueryUseCase transactionalFakeGlp1InjectionPlanQueryUseCase() {
            return new TransactionalFakeGlp1InjectionPlanQueryUseCase();
        }

        @Bean
        Glp1HomeCardQueryService glp1HomeCardQueryService(
            TransactionalFakeGlp1InjectionRecordQueryUseCase transactionalFakeGlp1InjectionRecordQueryUseCase,
            TransactionalFakeGlp1InjectionPlanQueryUseCase transactionalFakeGlp1InjectionPlanQueryUseCase) {
            return new Glp1HomeCardQueryService(
                transactionalFakeGlp1InjectionRecordQueryUseCase, transactionalFakeGlp1InjectionPlanQueryUseCase);
        }
    }

    // DB 없이 참여 트랜잭션 실패 -> rollback-only 표시 -> 바깥 커밋 시 UnexpectedRollbackException 흐름만 재현한다
    static class RollbackOnlyTrackingTransactionManager extends AbstractPlatformTransactionManager {

        private final ThreadLocal<TrackedTransaction> currentTrackedTransaction = new ThreadLocal<>();

        @Override
        protected Object doGetTransaction() {
            TrackedTransaction trackedTransaction = currentTrackedTransaction.get();
            return trackedTransaction != null ? trackedTransaction : new TrackedTransaction();
        }

        @Override
        protected boolean isExistingTransaction(Object transaction) {
            return ((TrackedTransaction) transaction).active;
        }

        @Override
        protected void doBegin(Object transaction, TransactionDefinition definition) {
            TrackedTransaction trackedTransaction = (TrackedTransaction) transaction;
            trackedTransaction.active = true;
            currentTrackedTransaction.set(trackedTransaction);
        }

        @Override
        protected void doSetRollbackOnly(DefaultTransactionStatus status) {
            ((TrackedTransaction) status.getTransaction()).rollbackOnly = true;
        }

        @Override
        protected void doCommit(DefaultTransactionStatus status) {
        }

        @Override
        protected void doRollback(DefaultTransactionStatus status) {
        }

        @Override
        protected void doCleanupAfterCompletion(Object transaction) {
            currentTrackedTransaction.remove();
        }
    }

    static class TrackedTransaction implements SmartTransactionObject {

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

설계 메모
- 실패하는 쪽만 `@Transactional(readOnly = true)` Fake 로 감싸 실제 프록시를 태운다. 입력 전제의 "두 UseCase 모두 `@Transactional(readOnly = true)` 구현"을 그대로 옮긴 것이다
- 이 테스트가 실패하면 서비스의 try/catch 는 맞고 트랜잭션 경계가 문제다. 고치는 방향(실패를 허용할 조회를 `REQUIRES_NEW` 또는 별도 readOnly 빈으로 분리)은 프로덕션 코드 변경이므로 이 작업 범위 밖이다. 합의 후 별도로 진행한다 (SC-1, RR-13)
- 이 테스트는 `@Tag("integration")` 이다. 모듈 build 설정이 이 태그를 기본 실행에서 제외하는지는 확인하지 못했다. 제외 중이면 아래 실행 명령의 태그 옵션을 모듈 설정에 맞춘다
- 트랜잭션 매니저는 Spring 6.1(Boot 3.2.2) 의 `AbstractPlatformTransactionManager` 동작에 맞춰 작성했고, 컴파일하지 않았다

## 실행할 명령 (실행하지 않음)

작성 전

```bash
git status --short pasta-api/src/test/java/com/kakaohealthcare/pasta/glp1/application/
ls pasta-api/src/test/java/com/kakaohealthcare/pasta/glp1/application/ | grep -i HomeCard
```

- 첫 줄은 DW-1 미커밋 변경 확인, 둘째 줄은 `Glp1HomeCardQueryServiceTest` 가 이미 있는지 확인. 있으면 읽고 `Edit` 로 메서드만 추가한다 (DW-3)

작성 후

```bash
./gradlew :pasta-api:spotlessApply
./gradlew :pasta-api:test --tests '*Glp1HomeCardQueryServiceTest'
./gradlew :pasta-api:test --tests '*Glp1HomeCardQueryServiceIntegrationTest'
python3 .claude/shared/review-lint.py
git status
git log dev..HEAD --name-only
```

- review-lint 는 배포본 경로(`.claude/shared/review-lint.py`)이며 forge 원본은 `forge/common/review-lint.py`
- `[위반]` 이 남으면 보고·커밋 전에 고친다. `[확인]` 중 `@SpringBootTest`·`Spy`·`Fake` 관련은 위 사유 주석과 이 보고를 인용해 PR 본문에 남긴다
- 마지막 두 줄은 DW-5 의도치 않은 삭제 확인
- 단위 테스트 4건이 통과하더라도 서비스 트랜잭션 경계가 안전하다는 뜻은 아니다. 그 확인은 통합 테스트 결과로 한다

PR 본문에 넣을 한 줄: "`@SpringBootTest` 예외 사유: 같은 트랜잭션의 하위 조회 예외로 인한 rollback-only 전파는 서비스 프록시 경계를 넘어야 재현되며 Fake·슬라이스로는 재현 안 됨 (RR-13)"

## Self-check

| # | 결과 | 비고 |
|---|------|------|
| 1, 12 | PASS | Application. 패키지 경로는 가정이라 명시 |
| 2 | PASS | Fake 우선. 외부 통신이 없어 Spy 불필요 |
| 3 | PASS | 테스트 DB 전환 없음. 통합 테스트는 DB 미사용 |
| 4 | PASS | 모든 테스트에 구체적 한국어 `@DisplayName` ("정상"·"성공" 단독 없음) |
| 5 | 미확인 | gradle 실행 안 함 |
| 6 | PASS | `// Given` `// When` `// Then` |
| 7 | PASS | `@Nested` 없음 |
| 8 | PASS | AssertJ 만, JUnit `Assertions` 없음 |
| 9, 14 | N/A | 같은 패키지 기존 테스트를 읽지 못함(시뮬레이션). 기존 파일이 있으면 그 관례에 맞춰 조정 |
| 10, 21 | 미확인 | spotlessApply·review-lint 실행 안 함 |
| 11, 16 | PASS | FQCN 인라인 없음, import 사용 |
| 13 | PASS | 가정한 Fixture 생성자는 주석으로 표기 |
| 15 | N/A | 빈 이름 문자열 없음 |
| 17 | PASS | infra 구현체 참조 없음 |
| 18 | PASS | `verify` 미사용 |
| 19 | PASS | 두 UseCase 를 `@Mock` 으로 두지 않음 |
| 20 | PASS(계획) | 사용자 구분 값·실패 반대쪽 데이터를 다르게 둠. try/catch 를 깨뜨려 실패하는지는 실행 전이라 미확인. 진입 경로는 `getCard` 하나 |
| 22 | PASS | 두 예외 분기(기록 실패·일정 실패)와 둘 다 실패를 모두 작성 |
| 23 | PASS | 제출 코드에 남긴 결함 설명 없음. 요청과 달라진 지점은 규칙 원본(RR-13, 규칙 08 §2, vc-testcode.md 2절) 인용 |
| 24 | PASS | 적용 판정과 근거 기재 |
| 25 | PASS | `Fake*` 이름, `Thread.sleep`·`@BeforeAll` 없음, 테스트당 논리 검증 하나, `@SpringBootTest` 는 사유 주석+PR 본문 문구 |

남은 리스크
- 통합 테스트가 현재 서비스에서 실패하면 그것은 결함의 신호이며, 빨간 테스트를 그대로 머지하지 않는다. 서비스 수정 합의 전에는 이 테스트를 포함한 PR 을 올리지 않고 사용자 결정을 받는다
- Fixture·접근자·패키지 가정이 틀리면 컴파일이 깨진다. 헬퍼 두 곳과 `lastRecord()`·`nextPlan()` 만 실제 코드에 맞추면 된다