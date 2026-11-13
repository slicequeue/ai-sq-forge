<!-- r2 -->
<!-- TC-8 with-skill / skill v1.10 / sonnet / 2026-11-13 -->
# Glp1HomeCardQueryService 테스트 작성 (시뮬레이션: 파일 미생성·명령 미실행)

## 0. Phase 0 판정

| 항목 | 판정 | 근거 |
|------|------|------|
| 계층 | Application (추정) | `@Service` + `*QueryUseCase` 2개를 조립. 패키지 경로는 입력에 없어 확인 못 함. 사용자도 "Application 계층"이라고 명시 |
| 조직 컨벤션 | **적용** | `.claude/shared/vc-conventions-guide.md`·`vc-conventions/testcode-convention.md` 존재 (프로젝트 맥락). `references/vc-testcode.md` 기준 |
| 테스트 더블 | Fake (UseCase 2개) | 규칙 08 §2, vc-testcode 1절 표 (Service·Facade = Fixture + `Fake*` UseCase). `find . -name "Fake*"` 결과 Fake 없음 → 신규 작성 |
| 테스트 DB | 사용 안 함 | 단위 테스트는 Spring 없음. 통합 테스트는 DB 없이 트랜잭션 매니저만 쓴다(아래 3절). 모듈 기존 DB 설정을 건드리지 않음 |
| 위험 신호 | 있음 | 서비스(`@Transactional(readOnly = true)`)가 같은 트랜잭션에 참여하는 UseCase 2개를 try/catch 로 감싼다 → RR-13 패턴 2 |

**먼저 알릴 것**: 이 서비스는 Fake 단위 테스트만으로는 실제 동작을 증명하지 못한다. 하위 UseCase 도 `@Transactional(readOnly = true)` 라 같은 트랜잭션에 참여하고, 예외가 나가면 프록시가 트랜잭션에 rollback-only 를 건다. 서비스가 예외를 catch 해도 `getCard` 가 끝날 때 커밋이 `UnexpectedRollbackException` 으로 실패하는 구조다(`review-recurrence-guard.md` 13절 RR-13 두 번째 행, #793). Fake 는 프록시가 없어서 이 경로를 한 번도 타지 않는다. 그래서 단위 테스트 4건 외에 실제 프록시를 쓰는 통합 테스트 2건을 같이 작성했다.

## 1. 실행 전 명령 (DW-1, DW-3 준수: 아래는 모두 신규 파일이라 덮어쓸 기존 파일이 없는지만 확인)

```bash
# 같은 경로에 이미 파일이 있는지, 미커밋 변경이 있는지 (DW-1)
git status --short pasta-api/src/test/java/com/kakaohealthcare/pasta/glp1/application/
find . -name "Fake*Glp1Injection*QueryUseCase*" -o -name "Glp1HomeCard*Test.java" -o -name "Glp1HomeCardFixtures.java"
# 이웃 테스트 관례 확인 (Phase 0-2)
ls pasta-api/src/test/java/com/kakaohealthcare/pasta/glp1/application/
```

파일이 이미 있으면 통째로 쓰지 않고 읽은 뒤 `Edit` 로 추가한다(DW-3).

## 2. 테스트 코드 전체

패키지 경로 `com.kakaohealthcare.pasta.glp1.application` 은 **가정**이다. 실제 패키지·UseCase 인터페이스 패키지 import 는 저장소에서 맞춰야 한다.

### 2-1. `src/test/java/.../glp1/application/FakeGlp1InjectionRecordQueryUseCase.java`

```java
package com.kakaohealthcare.pasta.glp1.application;

import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

// 가정: Glp1InjectionRecordQueryUseCase 에는 getLast(Long, Instant) 만 있다. 다른 메서드가 있으면 구현을 추가해야 한다.
// 가정: 기록이 없으면 실제 구현은 null 을 돌려준다.
public class FakeGlp1InjectionRecordQueryUseCase implements Glp1InjectionRecordQueryUseCase {

    private final List<SavedRecord> savedRecordList = new ArrayList<>();
    private RuntimeException getLastFailure;

    public void save(Long userId, Instant recordedAt, Glp1InjectionRecordOutDto glp1InjectionRecordOutDto) {
        savedRecordList.add(new SavedRecord(userId, recordedAt, glp1InjectionRecordOutDto));
    }

    public void failGetLastWith(RuntimeException runtimeException) {
        getLastFailure = runtimeException;
    }

    public void clear() {
        savedRecordList.clear();
        getLastFailure = null;
    }

    @Override
    public Glp1InjectionRecordOutDto getLast(Long userId, Instant currentAt) {
        if (getLastFailure != null) {
            throw getLastFailure;
        }
        return savedRecordList.stream()
                .filter(savedRecord -> savedRecord.userId().equals(userId))
                .filter(savedRecord -> !savedRecord.recordedAt().isAfter(currentAt))
                .max(Comparator.comparing(SavedRecord::recordedAt))
                .map(SavedRecord::glp1InjectionRecordOutDto)
                .orElse(null);
    }

    private record SavedRecord(Long userId, Instant recordedAt, Glp1InjectionRecordOutDto glp1InjectionRecordOutDto) {}
}
```

### 2-2. `src/test/java/.../glp1/application/FakeGlp1InjectionPlanQueryUseCase.java`

```java
package com.kakaohealthcare.pasta.glp1.application;

import java.time.Instant;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

// 가정: Glp1InjectionPlanQueryUseCase 에는 getNext(Long, Instant) 만 있다.
// 가정: "다음 일정"은 currentAt 이후 가장 가까운 일정이고, 없으면 null 을 돌려준다.
public class FakeGlp1InjectionPlanQueryUseCase implements Glp1InjectionPlanQueryUseCase {

    private final List<SavedPlan> savedPlanList = new ArrayList<>();
    private RuntimeException getNextFailure;

    public void save(Long userId, Instant scheduledAt, Glp1InjectionPlanOutDto glp1InjectionPlanOutDto) {
        savedPlanList.add(new SavedPlan(userId, scheduledAt, glp1InjectionPlanOutDto));
    }

    public void failGetNextWith(RuntimeException runtimeException) {
        getNextFailure = runtimeException;
    }

    public void clear() {
        savedPlanList.clear();
        getNextFailure = null;
    }

    @Override
    public Glp1InjectionPlanOutDto getNext(Long userId, Instant currentAt) {
        if (getNextFailure != null) {
            throw getNextFailure;
        }
        return savedPlanList.stream()
                .filter(savedPlan -> savedPlan.userId().equals(userId))
                .filter(savedPlan -> savedPlan.scheduledAt().isAfter(currentAt))
                .min(Comparator.comparing(SavedPlan::scheduledAt))
                .map(SavedPlan::glp1InjectionPlanOutDto)
                .orElse(null);
    }

    private record SavedPlan(Long userId, Instant scheduledAt, Glp1InjectionPlanOutDto glp1InjectionPlanOutDto) {}
}
```

### 2-3. `src/test/java/.../glp1/application/Glp1HomeCardFixtures.java`

```java
package com.kakaohealthcare.pasta.glp1.application;

import java.time.Instant;

final class Glp1HomeCardFixtures {

    static final Long USER_ID = 1L;
    static final Long OTHER_USER_ID = 2L;
    static final Instant CURRENT_AT = Instant.parse("2026-11-13T00:00:00Z");

    private Glp1HomeCardFixtures() {}

    // 가정: 아래 두 팩토리의 생성자 시그니처는 실제 OutDto 와 다를 수 있다. 이 파일 한 곳만 맞추면 된다.
    static Glp1InjectionRecordOutDto glp1InjectionRecordOutDto(Long glp1InjectionRecordId) {
        return new Glp1InjectionRecordOutDto(glp1InjectionRecordId);
    }

    static Glp1InjectionPlanOutDto glp1InjectionPlanOutDto(Long glp1InjectionPlanId) {
        return new Glp1InjectionPlanOutDto(glp1InjectionPlanId);
    }
}
```

### 2-4. `src/test/java/.../glp1/application/Glp1HomeCardQueryServiceTest.java` (단위, Spring 없음)

```java
package com.kakaohealthcare.pasta.glp1.application;

import static com.kakaohealthcare.pasta.glp1.application.Glp1HomeCardFixtures.CURRENT_AT;
import static com.kakaohealthcare.pasta.glp1.application.Glp1HomeCardFixtures.OTHER_USER_ID;
import static com.kakaohealthcare.pasta.glp1.application.Glp1HomeCardFixtures.USER_ID;
import static com.kakaohealthcare.pasta.glp1.application.Glp1HomeCardFixtures.glp1InjectionPlanOutDto;
import static com.kakaohealthcare.pasta.glp1.application.Glp1HomeCardFixtures.glp1InjectionRecordOutDto;
import static org.assertj.core.api.Assertions.assertThat;

import java.time.temporal.ChronoUnit;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

// 이 클래스는 Fake 로 "각 조회 실패가 서로를 비우지 않는다"는 코드 분기만 본다.
// 실제 트랜잭션 프록시에서의 동작(rollback-only)은 Glp1HomeCardQueryServiceIntegrationTest 에서 본다.
class Glp1HomeCardQueryServiceTest {

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
    @DisplayName("요청한 사용자의 현재 시각 이전 마지막 기록과 이후 가장 가까운 일정을 카드에 담는다")
    void getCard_bothQueriesSucceed_returnsLastRecordAndNextPlanOfUser() {
        // Given
        // 경계를 넘는 픽스처: 더 오래된 기록, 다른 사용자 기록, 미래 기록 / 더 먼 일정, 다른 사용자 일정, 과거 일정
        Glp1InjectionRecordOutDto lastGlp1InjectionRecordOutDto = glp1InjectionRecordOutDto(11L);
        Glp1InjectionPlanOutDto nextGlp1InjectionPlanOutDto = glp1InjectionPlanOutDto(21L);
        fakeGlp1InjectionRecordQueryUseCase.save(USER_ID, CURRENT_AT.minus(3, ChronoUnit.DAYS), glp1InjectionRecordOutDto(10L));
        fakeGlp1InjectionRecordQueryUseCase.save(USER_ID, CURRENT_AT.minus(1, ChronoUnit.DAYS), lastGlp1InjectionRecordOutDto);
        fakeGlp1InjectionRecordQueryUseCase.save(OTHER_USER_ID, CURRENT_AT.minus(1, ChronoUnit.HOURS), glp1InjectionRecordOutDto(12L));
        fakeGlp1InjectionRecordQueryUseCase.save(USER_ID, CURRENT_AT.plus(1, ChronoUnit.DAYS), glp1InjectionRecordOutDto(13L));
        fakeGlp1InjectionPlanQueryUseCase.save(USER_ID, CURRENT_AT.plus(2, ChronoUnit.DAYS), nextGlp1InjectionPlanOutDto);
        fakeGlp1InjectionPlanQueryUseCase.save(USER_ID, CURRENT_AT.plus(9, ChronoUnit.DAYS), glp1InjectionPlanOutDto(22L));
        fakeGlp1InjectionPlanQueryUseCase.save(OTHER_USER_ID, CURRENT_AT.plus(1, ChronoUnit.DAYS), glp1InjectionPlanOutDto(23L));
        fakeGlp1InjectionPlanQueryUseCase.save(USER_ID, CURRENT_AT.minus(1, ChronoUnit.DAYS), glp1InjectionPlanOutDto(24L));

        // When
        Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

        // Then
        // 가정: Glp1HomeCardOutDto 는 record 이고 접근자는 lastRecord(), nextPlan() 이다.
        assertThat(glp1HomeCardOutDto)
                .extracting(Glp1HomeCardOutDto::lastRecord, Glp1HomeCardOutDto::nextPlan)
                .containsExactly(lastGlp1InjectionRecordOutDto, nextGlp1InjectionPlanOutDto);
    }

    @Test
    @DisplayName("마지막 기록 조회가 예외를 내도 다음 일정은 카드에 담고 기록만 비운다")
    void getCard_recordQueryFails_keepsNextPlanAndEmptiesLastRecord() {
        // Given
        Glp1InjectionPlanOutDto nextGlp1InjectionPlanOutDto = glp1InjectionPlanOutDto(21L);
        fakeGlp1InjectionPlanQueryUseCase.save(USER_ID, CURRENT_AT.plus(2, ChronoUnit.DAYS), nextGlp1InjectionPlanOutDto);
        fakeGlp1InjectionRecordQueryUseCase.failGetLastWith(new IllegalStateException("기록 조회 실패"));

        // When
        Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

        // Then
        assertThat(glp1HomeCardOutDto)
                .extracting(Glp1HomeCardOutDto::lastRecord, Glp1HomeCardOutDto::nextPlan)
                .containsExactly(null, nextGlp1InjectionPlanOutDto);
    }

    @Test
    @DisplayName("다음 일정 조회가 예외를 내도 마지막 기록은 카드에 담고 일정만 비운다")
    void getCard_planQueryFails_keepsLastRecordAndEmptiesNextPlan() {
        // Given
        Glp1InjectionRecordOutDto lastGlp1InjectionRecordOutDto = glp1InjectionRecordOutDto(11L);
        fakeGlp1InjectionRecordQueryUseCase.save(USER_ID, CURRENT_AT.minus(1, ChronoUnit.DAYS), lastGlp1InjectionRecordOutDto);
        fakeGlp1InjectionPlanQueryUseCase.failGetNextWith(new IllegalStateException("일정 조회 실패"));

        // When
        Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

        // Then
        assertThat(glp1HomeCardOutDto)
                .extracting(Glp1HomeCardOutDto::lastRecord, Glp1HomeCardOutDto::nextPlan)
                .containsExactly(lastGlp1InjectionRecordOutDto, null);
    }

    @Test
    @DisplayName("두 조회가 모두 예외를 내도 예외를 던지지 않고 빈 카드를 돌려준다")
    void getCard_bothQueriesFail_returnsEmptyCardWithoutThrowing() {
        // Given
        fakeGlp1InjectionRecordQueryUseCase.failGetLastWith(new IllegalStateException("기록 조회 실패"));
        fakeGlp1InjectionPlanQueryUseCase.failGetNextWith(new IllegalStateException("일정 조회 실패"));

        // When
        Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

        // Then
        assertThat(glp1HomeCardOutDto)
                .extracting(Glp1HomeCardOutDto::lastRecord, Glp1HomeCardOutDto::nextPlan)
                .containsExactly(null, null);
    }
}
```

### 2-5. `src/test/java/.../glp1/application/Glp1HomeCardQueryServiceIntegrationTest.java` (`@SpringBootTest` 예외)

```java
package com.kakaohealthcare.pasta.glp1.application;

import static com.kakaohealthcare.pasta.glp1.application.Glp1HomeCardFixtures.CURRENT_AT;
import static com.kakaohealthcare.pasta.glp1.application.Glp1HomeCardFixtures.USER_ID;
import static com.kakaohealthcare.pasta.glp1.application.Glp1HomeCardFixtures.glp1InjectionPlanOutDto;
import static com.kakaohealthcare.pasta.glp1.application.Glp1HomeCardFixtures.glp1InjectionRecordOutDto;
import static org.assertj.core.api.Assertions.assertThat;

import java.time.temporal.ChronoUnit;
import org.junit.jupiter.api.BeforeEach;
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

// @SpringBootTest 예외: 하위 UseCase 의 예외가 같은 트랜잭션에 rollback-only 를 거는 동작은
// 트랜잭션 프록시 경계를 넘어야 재현된다. Fake 단위 테스트·@DataJpaTest 로는 재현 안 됨
// (vc-conventions-guide 3절, review-recurrence-guard RR-13, vc-testcode 2절).
// DB 는 쓰지 않는다. 프록시 경계만 필요해서 메모리 트랜잭션 매니저를 직접 등록한다.
@SpringBootTest(
        classes = Glp1HomeCardQueryServiceIntegrationTest.TestConfig.class,
        webEnvironment = SpringBootTest.WebEnvironment.NONE)
@Tag("integration")
class Glp1HomeCardQueryServiceIntegrationTest {

    private ProxiedFakeGlp1InjectionRecordQueryUseCase proxiedFakeGlp1InjectionRecordQueryUseCase;
    private ProxiedFakeGlp1InjectionPlanQueryUseCase proxiedFakeGlp1InjectionPlanQueryUseCase;
    private Glp1HomeCardQueryService glp1HomeCardQueryService;

    @BeforeEach
    void setUp(
            @Autowired ProxiedFakeGlp1InjectionRecordQueryUseCase proxiedFakeGlp1InjectionRecordQueryUseCase,
            @Autowired ProxiedFakeGlp1InjectionPlanQueryUseCase proxiedFakeGlp1InjectionPlanQueryUseCase,
            @Autowired Glp1HomeCardQueryService glp1HomeCardQueryService) {
        this.proxiedFakeGlp1InjectionRecordQueryUseCase = proxiedFakeGlp1InjectionRecordQueryUseCase;
        this.proxiedFakeGlp1InjectionPlanQueryUseCase = proxiedFakeGlp1InjectionPlanQueryUseCase;
        this.glp1HomeCardQueryService = glp1HomeCardQueryService;
        proxiedFakeGlp1InjectionRecordQueryUseCase.clear();
        proxiedFakeGlp1InjectionPlanQueryUseCase.clear();
    }

    @Test
    @DisplayName("마지막 기록 조회가 트랜잭션 안에서 예외를 내도 getCard 는 실패하지 않고 다음 일정을 담은 카드를 돌려준다")
    void getCard_recordQueryFailsInsideTransaction_stillReturnsCardWithNextPlan() {
        // Given
        Glp1InjectionPlanOutDto nextGlp1InjectionPlanOutDto = glp1InjectionPlanOutDto(21L);
        proxiedFakeGlp1InjectionPlanQueryUseCase.save(USER_ID, CURRENT_AT.plus(2, ChronoUnit.DAYS), nextGlp1InjectionPlanOutDto);
        proxiedFakeGlp1InjectionRecordQueryUseCase.failGetLastWith(new IllegalStateException("기록 조회 실패"));

        // When
        Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

        // Then
        assertThat(glp1HomeCardOutDto)
                .extracting(Glp1HomeCardOutDto::lastRecord, Glp1HomeCardOutDto::nextPlan)
                .containsExactly(null, nextGlp1InjectionPlanOutDto);
    }

    @Test
    @DisplayName("다음 일정 조회가 트랜잭션 안에서 예외를 내도 getCard 는 실패하지 않고 마지막 기록을 담은 카드를 돌려준다")
    void getCard_planQueryFailsInsideTransaction_stillReturnsCardWithLastRecord() {
        // Given
        Glp1InjectionRecordOutDto lastGlp1InjectionRecordOutDto = glp1InjectionRecordOutDto(11L);
        proxiedFakeGlp1InjectionRecordQueryUseCase.save(USER_ID, CURRENT_AT.minus(1, ChronoUnit.DAYS), lastGlp1InjectionRecordOutDto);
        proxiedFakeGlp1InjectionPlanQueryUseCase.failGetNextWith(new IllegalStateException("일정 조회 실패"));

        // When
        Glp1HomeCardOutDto glp1HomeCardOutDto = glp1HomeCardQueryService.getCard(USER_ID, CURRENT_AT);

        // Then
        assertThat(glp1HomeCardOutDto)
                .extracting(Glp1HomeCardOutDto::lastRecord, Glp1HomeCardOutDto::nextPlan)
                .containsExactly(lastGlp1InjectionRecordOutDto, null);
    }

    // 실제 UseCase 구현과 같은 @Transactional(readOnly = true) 경계를 Fake 에 입힌다.
    @Transactional(readOnly = true)
    static class ProxiedFakeGlp1InjectionRecordQueryUseCase extends FakeGlp1InjectionRecordQueryUseCase {}

    @Transactional(readOnly = true)
    static class ProxiedFakeGlp1InjectionPlanQueryUseCase extends FakeGlp1InjectionPlanQueryUseCase {}

    @Configuration
    @EnableTransactionManagement(proxyTargetClass = true)
    static class TestConfig {

        @Bean
        PlatformTransactionManager transactionManager() {
            return new InMemoryTransactionManager();
        }

        @Bean
        ProxiedFakeGlp1InjectionRecordQueryUseCase proxiedFakeGlp1InjectionRecordQueryUseCase() {
            return new ProxiedFakeGlp1InjectionRecordQueryUseCase();
        }

        @Bean
        ProxiedFakeGlp1InjectionPlanQueryUseCase proxiedFakeGlp1InjectionPlanQueryUseCase() {
            return new ProxiedFakeGlp1InjectionPlanQueryUseCase();
        }

        @Bean
        Glp1HomeCardQueryService glp1HomeCardQueryService(
                Glp1InjectionRecordQueryUseCase glp1InjectionRecordQueryUseCase,
                Glp1InjectionPlanQueryUseCase glp1InjectionPlanQueryUseCase) {
            return new Glp1HomeCardQueryService(glp1InjectionRecordQueryUseCase, glp1InjectionPlanQueryUseCase);
        }
    }

    // DB 없이 전파·rollback-only 판정만 Spring 의 AbstractPlatformTransactionManager 에 맡기는 최소 구현.
    static class InMemoryTransactionManager extends AbstractPlatformTransactionManager {

        private final ThreadLocal<InMemoryTransaction> currentTransaction = new ThreadLocal<>();

        @Override
        protected Object doGetTransaction() {
            InMemoryTransaction inMemoryTransaction = currentTransaction.get();
            return inMemoryTransaction != null ? inMemoryTransaction : new InMemoryTransaction();
        }

        @Override
        protected boolean isExistingTransaction(Object transaction) {
            return currentTransaction.get() == transaction;
        }

        @Override
        protected void doBegin(Object transaction, TransactionDefinition definition) {
            currentTransaction.set((InMemoryTransaction) transaction);
        }

        @Override
        protected void doCommit(DefaultTransactionStatus status) {}

        @Override
        protected void doRollback(DefaultTransactionStatus status) {}

        @Override
        protected void doSetRollbackOnly(DefaultTransactionStatus status) {
            ((InMemoryTransaction) status.getTransaction()).rollbackOnly = true;
        }

        @Override
        protected void doCleanupAfterCompletion(Object transaction) {
            currentTransaction.remove();
        }
    }

    static class InMemoryTransaction implements SmartTransactionObject {

        private boolean rollbackOnly;

        @Override
        public boolean isRollbackOnly() {
            return rollbackOnly;
        }

        @Override
        public void flush() {}
    }
}
```

## 3. 실행할 명령 (실행하지 않았다)

```bash
./gradlew :pasta-api:spotlessApply
./gradlew :pasta-api:test --tests '*Glp1HomeCardQueryServiceTest'
./gradlew :pasta-api:test --tests '*Glp1HomeCardQueryServiceIntegrationTest'
python3 .claude/shared/review-lint.py          # 배포본 경로. forge 저장소 기준은 forge/common/review-lint.py
git status --short                              # 의도치 않은 삭제·수정 없는지 (DW-5)
```

`review-lint.py` 는 조직 컨벤션 가이드가 옆에 있어 VC 검사가 자동으로 켜질 것이다. `[위반]` 이 남으면 완료 보고·커밋·push 를 하지 않는다. `[확인]` 이 나오면 lint 원문을 인용해 사유를 적는다. 이 파일들은 `@SpringBootTest` 가 있어 `[확인]` 이 나올 수 있고, 사유는 위 클래스 주석과 아래 PR 본문 한 줄이다.

PR 본문에 넣을 줄: `@SpringBootTest 예외 사유: 하위 UseCase 예외가 같은 트랜잭션에 rollback-only 를 거는 동작은 프록시 경계를 넘어야 재현되며 Fake·슬라이스로는 재현 안 됨 (RR-13).`

## 4. 완료 보고

```
Glp1HomeCardQueryService 테스트 6건 작성 완료 (코드 작성, 테스트 실행 전)
- 계층·방식: Application(추정, 패키지 경로 미확인) / Fake 2종 신규 + 통합 2건(@SpringBootTest 예외), 테스트 DB 사용 안 함
- 조직 컨벤션: 적용 — .claude/shared/vc-conventions-guide.md 와 vc-conventions/testcode-convention.md 존재
- 요청과 다르게 한 것: 단위 테스트 4건 외에 @SpringBootTest 통합 테스트 2건을 추가했다 — review-recurrence-guard.md 13절 RR-13(rollback-only 는 Mock·Fake 로 재현 안 됨), vc-testcode.md 2절(예외 사유 주석 + PR 본문)
```

미확인:
- 아무것도 실행하지 않았다. gradle 통과 여부, spotless, review-lint 결과는 모른다.
- OutDto 생성자·접근자(`lastRecord()`, `nextPlan()`), UseCase 인터페이스의 메서드 목록, 패키지 경로는 입력에 없어 **가정**했다. 위치는 `Glp1HomeCardFixtures` 와 Fake 두 개의 주석에 표시했다.
- Fake 의 "기록 없으면 null", "다음 일정 = currentAt 이후 가장 가까운 것" 은 가정이다. 실제 UseCase 가 없을 때 예외를 던지면 Fake 를 맞춰야 한다.
- 메모리 트랜잭션 매니저가 컴파일·동작하는지(`AbstractPlatformTransactionManager` 가 rollback-only 를 판정하는지)는 실행해 본 적이 없다.

### 운영 코드 결함 의심 (수정하지 않았다 — 범위 밖, SC-1)

`getCard` 는 class 레벨 `@Transactional(readOnly = true)` 이고 두 UseCase 도 같은 전파(기본 REQUIRED)로 참여한다. 하위 UseCase 가 예외를 던지면 그 프록시가 같은 트랜잭션에 rollback-only 를 걸고, 서비스가 catch 해도 `getCard` 종료 시 커밋에서 `UnexpectedRollbackException` 이 날 것으로 **읽힌다(코드 분석, 실행 확인 아님)**. 그렇다면 통합 테스트 2건은 현재 운영 코드에서 실패한다. 이 실패는 테스트가 아니라 운영 코드의 문제를 잡은 결과다. 단위 테스트 4건은 Fake 라 프록시가 없어 이 문제와 무관하게 통과한다. 즉 단위 테스트가 초록이어도 운영에서 "한 조회가 실패해도 카드가 나온다"는 보장이 되지 않는다.

수정 방향은 RR-13 에 있다. 실패를 허용할 조회의 트랜잭션 경계를 분리한다(`REQUIRES_NEW` 또는 별도 readOnly 빈, 혹은 카드 서비스의 class 레벨 트랜잭션 제거). 어느 쪽을 택할지는 운영 코드 설계 결정이라 정하지 않았다. 어떻게 할지 알려주면 통합 테스트를 기준으로 맞춘다. 수정 전에는 통합 테스트를 빨간 상태로 커밋·push 하지 않는다.

### Self-check

| # | 결과 | 비고 |
|---|------|------|
| 1·12 | PASS | Application, 근거는 `@Service`·UseCase 의존(패키지 미확인이라 "추정" 표기) |
| 2·19 | PASS | UseCase 를 `@Mock` 없이 Fake 로 대체 |
| 3 | PASS | DB 전환 없음, 미사용 |
| 4·6·8 | PASS | `@DisplayName` 한글·구체적, GWT 주석, AssertJ 만 |
| 7 | PASS | `@Nested` 0건 |
| 11 | PASS | FQCN 0건 (작성 중 `TransactionDefinition` 인라인을 발견해 import 로 고친 뒤 제출) |
| 13 | 가정 표기 | OutDto·시각 픽스처 가정을 주석으로 표시 |
| 17 | PASS | infra 구현체 참조 없음 |
| 20 | PASS | 경계를 넘는 픽스처(미래 기록·다른 사용자·더 먼 일정), 두 조회를 각각 실패시킴 |
| 22 | PASS | catch 분기 2개 + 동시 실패, 모두 테스트 |
| 21 | 미실행 | review-lint 실행 전 |
| 5·10 | 미실행 | gradle test·spotless 실행 전 |
| 24·25 | PASS | 조직 컨벤션 적용 판정 기재, `Fake*`, `Thread.sleep`·JUnit Assertions·`@BeforeAll` 0건, 테스트당 논리 검증 하나, `@SpringBootTest` 사유 주석 |
