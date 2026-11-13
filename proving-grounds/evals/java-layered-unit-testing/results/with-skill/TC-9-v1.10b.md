<!-- TC-9 with-skill / skill v1.10 트레이닝 후 / sonnet / 2026-11-13 -->
MealReminderCommandService.register 테스트 8건 작성 완료 (코드 작성, 테스트 실행 전)
- 계층·방식: Application / Fake 우선(`FakeMealReminderRepository`), 외부 통신·실행기는 손으로 쓴 Spy, Spring 컨텍스트 없음. 이 작업은 DB 를 쓰지 않아 테스트 DB 설정(H2)은 건드리지 않음
- 조직 컨벤션: 적용 — `.claude/shared/vc-conventions-guide.md` 와 `testcode-convention.md` 가 있음
- 요청과 다르게 한 것: Stub→Fake·Spy 3종(testcode-convention 4절), `@SpringBootTest`→컨텍스트 없는 단위 테스트(testcode-convention 핵심 원칙, guide 3절), `Thread.sleep(500)`→실행기를 Spy 로 주입해 대기 제거(testcode-convention 핵심 원칙), DisplayName "성공"→구체적 행동·결과(testcode-convention 1절)
- 미확인: `MealReminderEntity` 의 id 포함 생성자·getter, 도메인 패키지 경로, `ReminderPushClient` 시그니처는 대상 코드에서 보이는 범위로 가정. 컴파일은 하지 않음

## 1. 요청을 바꾼 이유

| 요청 | 처리 | 근거 |
|------|------|------|
| "Stub 하나 만들고" | `FakeMealReminderRepository`(상태 저장소), `SpyReminderPushClient`(외부 푸시 호출 기록), `SpyReminderPushExecutor`(실행기) 3개. `Stub*` 이름은 쓰지 않음 | `.claude/shared/vc-conventions/testcode-convention.md` 4절 "Fake 우선 사용"(`Stub*` ❌), `.claude/rules/08-test-code-convention.md` §2 Fake → Spy 순서. 저장소는 상태가 있어 Fake, 푸시 클라이언트는 호출 여부만 보므로 Spy. 하나로는 둘을 다 못 덮는다 |
| "`@SpringBootTest` 로 띄워서" | 쓰지 않음. 세 협력 객체가 모두 생성자 주입이라 `new` 로 조립 | testcode-convention 핵심 원칙 "@SpringBootTest 는 인수 테스트(E2E)에만", `vc-conventions-guide.md` 3절. 이 테스트는 E2E 가 아니고, 예외 허용 대상(rollback-only 전파·다중 트랜잭션 경합)도 아니다. 예외 사유 주석·PR 본문 항목도 필요 없다 |
| "`Thread.sleep(500)` 기다렸다가" | `Executor` 를 `SpyReminderPushExecutor` 로 바꿔 넣고 `runAll()` 로 대기 없이 실행 | testcode-convention 핵심 원칙 "Thread.sleep() 금지, 비동기 검증은 Awaitility". 실행기가 주입 가능하므로 기다릴 필요가 없다. 실제 스레드풀을 띄워 검증해야 한다면 Awaitility `await().atMost(…).untilAsserted(…)` 를 쓴다 |
| DisplayName "성공" | 상황과 결과를 쓴 한국어 문장 | testcode-convention 1절 "정상·성공 같은 말 대신 구체적인 행동과 결과" |

## 2. 요청 외 추가

- `register_sameTimeOfOtherUser_registers`: `existsByUserIdAndRemindAt` 가 사용자 조건을 빼먹어도 중복 예외 테스트는 통과한다. 그 경우를 잡는 테스트가 없어서 추가했다(RR-14).
- 중복 분기는 요청에 없었지만 `register` 의 예외 분기라서 3건(예외, 저장 미호출, 푸시 미예약)을 작성했다. 성격이 다른 검증은 테스트를 나눈다(vc-testcode.md 4절).

## 3. 테스트 더블 (src/test, domain 패키지)

경로의 패키지는 가정이다. 실제 `MealReminderRepository` 가 있는 패키지로 맞춘다.

`src/test/java/com/kakaohealthcare/moneyball/mealreminder/domain/FakeMealReminderRepository.java`

```java
package com.kakaohealthcare.moneyball.mealreminder.domain;

import java.time.LocalTime;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;

public class FakeMealReminderRepository implements MealReminderRepository {

    private final Map<Long, MealReminderEntity> store = new LinkedHashMap<>();
    private final AtomicLong idGenerator = new AtomicLong(1);

    @Override
    public MealReminderEntity save(MealReminderEntity mealReminderEntity) {
        Long id = (mealReminderEntity.getId() != null) ? mealReminderEntity.getId() : idGenerator.getAndIncrement();
        idGenerator.accumulateAndGet(id + 1, Math::max);
        // 가정: id 를 받는 생성자가 있다. 없으면 프로젝트의 id 주입 방식(테스트용 팩토리, 리플렉션 유틸)으로 교체
        MealReminderEntity savedMealReminderEntity =
                new MealReminderEntity(id, mealReminderEntity.getUserId(), mealReminderEntity.getRemindAt());
        store.put(id, savedMealReminderEntity);
        return savedMealReminderEntity;
    }

    @Override
    public boolean existsByUserIdAndRemindAt(Long userId, LocalTime remindAt) {
        return store.values().stream()
                .anyMatch(storedMealReminderEntity ->
                        storedMealReminderEntity.getUserId().equals(userId)
                                && storedMealReminderEntity.getRemindAt().equals(remindAt));
    }

    public List<MealReminderEntity> findAll() {
        return new ArrayList<>(store.values());
    }
}
```

`src/test/java/com/kakaohealthcare/moneyball/mealreminder/domain/SpyReminderPushClient.java`

```java
package com.kakaohealthcare.moneyball.mealreminder.domain;

import java.util.ArrayList;
import java.util.List;

public class SpyReminderPushClient implements ReminderPushClient {

    public record SendCall(Long userId, Long mealReminderId) {
    }

    private final List<SendCall> sendCallList = new ArrayList<>();

    @Override
    public void sendRegisteredNotice(Long userId, Long mealReminderId) {
        sendCallList.add(new SendCall(userId, mealReminderId));
    }

    public int getCallCount() {
        return sendCallList.size();
    }

    public List<SendCall> getSendCallList() {
        return List.copyOf(sendCallList);
    }
}
```

`src/test/java/com/kakaohealthcare/moneyball/mealreminder/application/SpyReminderPushExecutor.java`

```java
package com.kakaohealthcare.moneyball.mealreminder.application;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executor;

public class SpyReminderPushExecutor implements Executor {

    private final List<Runnable> reminderPushTaskList = new ArrayList<>();

    @Override
    public void execute(Runnable reminderPushTask) {
        reminderPushTaskList.add(reminderPushTask);
    }

    public int getQueuedTaskCount() {
        return reminderPushTaskList.size();
    }

    public void runAll() {
        List<Runnable> queuedReminderPushTaskList = new ArrayList<>(reminderPushTaskList);
        reminderPushTaskList.clear();
        queuedReminderPushTaskList.forEach(Runnable::run);
    }
}
```

## 4. 테스트 코드

`src/test/java/com/kakaohealthcare/moneyball/mealreminder/application/MealReminderCommandServiceTest.java`

```java
package com.kakaohealthcare.moneyball.mealreminder.application;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.assertj.core.api.Assertions.tuple;

import com.kakaohealthcare.moneyball.mealreminder.domain.DuplicateMealReminderException;
import com.kakaohealthcare.moneyball.mealreminder.domain.FakeMealReminderRepository;
import com.kakaohealthcare.moneyball.mealreminder.domain.MealReminderEntity;
import com.kakaohealthcare.moneyball.mealreminder.domain.SpyReminderPushClient;
import com.kakaohealthcare.moneyball.mealreminder.domain.SpyReminderPushClient.SendCall;
import java.time.LocalTime;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class MealReminderCommandServiceTest {

    private static final Long USER_ID = 1001L;
    private static final Long OTHER_USER_ID = 2002L;
    private static final LocalTime REMIND_AT = LocalTime.of(12, 30);

    private FakeMealReminderRepository fakeMealReminderRepository;
    private SpyReminderPushClient spyReminderPushClient;
    private SpyReminderPushExecutor spyReminderPushExecutor;
    private MealReminderCommandService mealReminderCommandService;

    @BeforeEach
    void setUp() {
        fakeMealReminderRepository = new FakeMealReminderRepository();
        spyReminderPushClient = new SpyReminderPushClient();
        spyReminderPushExecutor = new SpyReminderPushExecutor();
        mealReminderCommandService = new MealReminderCommandService(
                fakeMealReminderRepository, spyReminderPushClient, spyReminderPushExecutor);
    }

    @Test
    @DisplayName("중복 없는 시각으로 등록하면 해당 사용자와 시각의 알림이 저장된다")
    void register_newReminder_storesMealReminder() {
        // Given
        // (Fake 가 비어 있는 초기 상태)

        // When
        mealReminderCommandService.register(USER_ID, REMIND_AT);

        // Then
        assertThat(fakeMealReminderRepository.findAll())
                .extracting(MealReminderEntity::getUserId, MealReminderEntity::getRemindAt)
                .containsExactly(tuple(USER_ID, REMIND_AT));
    }

    @Test
    @DisplayName("등록하면 저장된 알림의 id 를 반환한다")
    void register_newReminder_returnsStoredId() {
        // Given
        // (사용자 id 와 생성 id 가 우연히 같아지지 않도록 USER_ID 는 1001 로 둔다)

        // When
        Long registeredMealReminderId = mealReminderCommandService.register(USER_ID, REMIND_AT);

        // Then
        MealReminderEntity storedMealReminderEntity =
                fakeMealReminderRepository.findAll().get(0);
        assertThat(registeredMealReminderId).isEqualTo(storedMealReminderEntity.getId());
    }

    @Test
    @DisplayName("실행기가 작업을 실행하면 저장된 알림 id 로 등록 푸시가 한 번 나간다")
    void register_newReminder_sendsRegisteredNoticeWhenExecutorRuns() {
        // Given
        Long registeredMealReminderId = mealReminderCommandService.register(USER_ID, REMIND_AT);

        // When
        spyReminderPushExecutor.runAll();

        // Then
        assertThat(spyReminderPushClient.getSendCallList())
                .containsExactly(new SendCall(USER_ID, registeredMealReminderId));
    }

    @Test
    @DisplayName("실행기가 작업을 실행하기 전에는 등록 푸시가 나가지 않는다")
    void register_beforeExecutorRuns_doesNotSendNotice() {
        // Given
        // (SpyReminderPushExecutor 는 runAll() 을 부르기 전까지 작업을 쌓아 두기만 한다)

        // When
        mealReminderCommandService.register(USER_ID, REMIND_AT);

        // Then
        assertThat(spyReminderPushClient.getCallCount()).isZero();
    }

    // 요청 외 추가: 같은 시각 다른 사용자 — existsByUserIdAndRemindAt 의 사용자 조건을 빼도 잡는 테스트가 없어서
    @Test
    @DisplayName("같은 시각이라도 다른 사용자의 알림만 있으면 중복이 아니라 등록된다")
    void register_sameTimeOfOtherUser_registers() {
        // Given
        fakeMealReminderRepository.save(new MealReminderEntity(OTHER_USER_ID, REMIND_AT));

        // When
        mealReminderCommandService.register(USER_ID, REMIND_AT);

        // Then
        assertThat(fakeMealReminderRepository.findAll())
                .extracting(MealReminderEntity::getUserId)
                .containsExactlyInAnyOrder(OTHER_USER_ID, USER_ID);
    }

    @Test
    @DisplayName("같은 사용자가 같은 시각으로 다시 등록하면 DuplicateMealReminderException 이 발생한다")
    void register_duplicateReminder_throwsException() {
        // Given
        fakeMealReminderRepository.save(new MealReminderEntity(USER_ID, REMIND_AT));

        // When & Then
        assertThatThrownBy(() -> mealReminderCommandService.register(USER_ID, REMIND_AT))
                .isInstanceOf(DuplicateMealReminderException.class);
    }

    // 요청 외 추가: 중복 분기의 저장 미호출
    @Test
    @DisplayName("중복 등록이 거부되면 알림이 추가로 저장되지 않는다")
    void register_duplicateReminder_doesNotSave() {
        // Given
        fakeMealReminderRepository.save(new MealReminderEntity(USER_ID, REMIND_AT));

        // When
        assertThatThrownBy(() -> mealReminderCommandService.register(USER_ID, REMIND_AT))
                .isInstanceOf(DuplicateMealReminderException.class);

        // Then
        assertThat(fakeMealReminderRepository.findAll()).hasSize(1);
    }

    // 요청 외 추가: 중복 분기의 푸시 미예약
    @Test
    @DisplayName("중복 등록이 거부되면 푸시 작업이 실행기에 예약되지 않는다")
    void register_duplicateReminder_doesNotEnqueuePush() {
        // Given
        fakeMealReminderRepository.save(new MealReminderEntity(USER_ID, REMIND_AT));

        // When
        assertThatThrownBy(() -> mealReminderCommandService.register(USER_ID, REMIND_AT))
                .isInstanceOf(DuplicateMealReminderException.class);

        // Then
        assertThat(spyReminderPushExecutor.getQueuedTaskCount()).isZero();
    }
}
```

## 5. 실행할 명령 (실행하지 않았다)

```bash
# 기존 Fake·Spy 재확인
find . -name "Fake*" -o -name "Spy*"

# 신규 파일이라 덮어쓰기 위험은 없지만 경로 충돌 확인
git status --short pasta-api/src/test

# 포매팅 후 해당 클래스만 실행
./gradlew :pasta-api:spotlessApply
./gradlew :pasta-api:test --tests "*MealReminderCommandServiceTest"

# 리뷰 가드 (배포본 경로)
python3 .claude/shared/review-lint.py

# 작업 후 의도치 않은 삭제 확인
git status
```

`./gradlew test` 와 `review-lint.py` 는 아직 돌리지 않았다. 결과를 확인하기 전에는 통과라고 보고하지 않는다.

## 6. 자기 검증 (Self-check)

| # | 결과 | 비고 |
|---|------|------|
| 1·12 | PASS | `application/MealReminderCommandService`, 의존이 domain 인터페이스·Executor 라서 Application |
| 2·19 | PASS | Repository 는 Fake, 외부 푸시는 Spy, `@Mock` 0건 |
| 3 | N/A | DB 미사용. H2 설정 변경 없음 |
| 4 | PASS | 8건 모두 구체적 한국어 DisplayName |
| 5 | 미확인 | 테스트 실행 전 |
| 6 | PASS | `// Given` `// When` `// Then`, 예외 단독 단언은 `// When & Then` |
| 7 | PASS | `@Nested` 0건 |
| 8 | PASS | AssertJ 만 사용 |
| 11·16 | PASS | 최종본에서 FQCN 0건 |
| 17 | PASS | infra 구현체 참조 0건, domain 인터페이스 대역 사용 |
| 20 | PASS | 사용자 id(1001)와 생성 id(1)를 다르게 두고, 다른 사용자·같은 시각 케이스 포함 |
| 21 | 미확인 | review-lint 미실행 |
| 22 | PASS | 중복 예외 분기 3건 작성, 요청 외 추가는 주석으로 표시 |
| 23 | PASS | 자기 발견 결함(FQCN, 미사용 상수)은 최종본에서 수정, 요청 변경마다 원본 인용 |
| 24 | PASS | 적용 판정 근거 위에 명시 |
| 25 | PASS | `Fake*`, GWT 주석, `Thread.sleep` 0, JUnit `Assertions` 0, `@BeforeAll` 0, `@SpringBootTest` 0 |

## 7. 남은 리스크

- `MealReminderEntity` 에 id 를 받는 생성자와 `getUserId()`·`getRemindAt()` 이 없으면 `FakeMealReminderRepository` 가 컴파일되지 않는다. 기존 엔티티 코드를 읽고 맞춰야 한다.
- 운영 `ThreadPoolTaskExecutor` 와 실제 스레드 경계에서의 동작(예: 트랜잭션 커밋 전에 푸시가 먼저 나가는 문제)은 이 단위 테스트로 확인되지 않는다. 필요하면 별도 논의가 필요하다.
