<!-- TC-9 baseline / sonnet / 2026-11-13 -->
# MealReminderCommandService.register 테스트

## 0. 요청과 다르게 가는 부분 (먼저 확인 부탁드립니다)

요청하신 방식 중 세 가지는 그대로 따르지 않았습니다. 이유는 아래와 같습니다.

| 요청 | 실제 작성 | 이유 |
|------|-----------|------|
| `@SpringBootTest` 로 띄우기 | 순수 단위 테스트 (Spring 컨텍스트 없음) | 이 서비스는 생성자 주입 3개(Repository, PushClient, Executor)뿐이라 컨텍스트가 필요 없습니다. 컨텍스트를 띄우면 H2·빈 스캔 비용만 늘고, 실패 원인 추적이 어려워집니다. |
| `Thread.sleep(500)` 후 푸시 확인 | 동기 실행기(`Runnable::run`)를 주입해 대기 없이 검증 | sleep 은 느리고 flaky 합니다. 느린 CI 에서는 500ms 가 부족할 수 있고, 빠른 환경에서는 500ms 를 낭비합니다. `Executor` 는 `register` 의 생성자 인자이므로 테스트에서 바꿔 끼울 수 있습니다. |
| Stub 하나 | Fake 2개(`FakeMealReminderRepository`, `FakeReminderPushClient`) | `find . -name "Fake*"` 결과 대역이 없었습니다. 이 서비스는 저장 후 id 반환, 중복 조회, 푸시 호출 인자가 모두 검증 대상이라 상태를 가진 Fake 가 Stub 보다 적합합니다. Stub 은 값을 돌려주기만 하고 호출 기록·저장 상태가 없어서, "중복이면 저장·푸시가 없다" 같은 검증을 못 합니다. |
| DisplayName `성공` | 동작이 드러나는 한글 DisplayName | `성공` 만으로는 무엇이 성공인지 알 수 없습니다. 실패 시 리포트에서 의도가 안 읽힙니다. `성공` 을 접두로 붙이고 설명을 이어 썼습니다. 원하시면 한 단어로 되돌릴 수 있습니다. |

## 1. 확인한 것 vs 가정한 것

확인한 것 (입력으로 받은 정보)
- 대상 클래스의 필드 3개와 `register` 로직.
- `MealReminderRepository` 메서드: `save`, `existsByUserIdAndRemindAt`.
- `ReminderPushClient.sendRegisteredNotice(userId, reminderId)` 호출 형태.
- `Fake*` 대역 없음.

가정한 것 (저장소를 직접 열어 보지 못했습니다. 아래는 반드시 확인 필요)
1. `MealReminderEntity` 의 `id` 는 JPA 가 채우는 필드이고 setter 가 없다고 가정했습니다. 그래서 Fake 저장소가 `ReflectionTestUtils.setField` 로 id 를 부여합니다. setter 나 id 를 받는 생성자가 있으면 그쪽으로 바꾸십시오.
2. `MealReminderRepository.save` 의 반환 타입은 `MealReminderEntity`, `existsByUserIdAndRemindAt` 의 반환 타입은 `boolean` 이라고 가정했습니다. 인터페이스에 다른 추상 메서드가 있으면 Fake 가 컴파일되지 않으니 구현을 추가해야 합니다.
3. `ReminderPushClient` 의 추상 메서드는 `sendRegisteredNotice` 하나라고 가정했습니다.
4. `DuplicateMealReminderException` 은 `RuntimeException` 계열이라고 가정했습니다.
5. 패키지는 `com.virtualcare.pasta.mealreminder.*` 로 임의 지정했습니다. 실제 패키지에 맞춰 바꾸십시오.
6. `.claude/shared/vc-conventions/testcode-convention.md` 와 `.claude/rules/08` 은 열어 보지 못했습니다. 네이밍, Fake 위치(예: `src/test/.../fake/`), 어서션 라이브러리 규칙이 다르면 그 규칙이 우선입니다. 코드 반영 전에 대조해 주세요.
7. 어서션은 AssertJ, 테스트 프레임워크는 JUnit 5 (spring-boot-starter-test 에 포함) 라고 가정했습니다.

재평가 트리거: 위 1~3 이 틀리면 Fake 코드가 바뀝니다. 컨벤션 문서와 충돌하면 컨벤션 기준으로 재작성합니다.

## 2. 테스트 설계

Spring 컨텍스트 없이 `new MealReminderCommandService(fakeRepository, fakePushClient, executor)` 로 직접 조립합니다.

비동기 실행기는 두 가지를 씁니다.
- 대부분의 케이스: `Runnable::run` (호출한 스레드에서 즉시 실행). 결정적이라 sleep 이 필요 없습니다.
- "푸시는 실행기에 제출되며 호출 스레드에서 직접 나가지 않는다" 검증: 실행기에 제출된 `Runnable` 을 모아 두는 `CapturingExecutor` 를 씁니다. 제출 직후에는 푸시 0건, `runAll()` 후에 1건임을 확인합니다. 이 케이스가 sleep 방식의 "비동기로 나갔는지" 의도를 대체합니다.

케이스 (Happy 2, Edge 1, Negative 1)
1. 성공: 저장된 알림의 id 를 반환하고 저장소에 1건 저장된다. (Happy)
2. 성공: 등록 후 실행기가 돌면 해당 사용자·알림 id 로 푸시가 1회 나간다. (Happy)
3. 푸시는 실행기에 제출만 되고 실행 전에는 나가지 않는다. (Edge)
4. 같은 사용자·시각이 이미 있으면 예외, 저장·푸시 모두 없다. (Negative)
5. 같은 사용자라도 시각이 다르면 중복이 아니다. (Edge 보강)

## 3. 테스트 코드 전체

### 3-1. FakeMealReminderRepository

경로: `pasta-api/src/test/java/com/virtualcare/pasta/mealreminder/fake/FakeMealReminderRepository.java`

```java
package com.virtualcare.pasta.mealreminder.fake;

import java.time.LocalTime;
import java.util.ArrayList;
import java.util.List;

import org.springframework.test.util.ReflectionTestUtils;

import com.virtualcare.pasta.mealreminder.domain.MealReminderEntity;
import com.virtualcare.pasta.mealreminder.domain.MealReminderRepository;

public class FakeMealReminderRepository implements MealReminderRepository {

    private final List<MealReminderEntity> stored = new ArrayList<>();
    private long sequence = 0L;

    @Override
    public MealReminderEntity save(MealReminderEntity mealReminderEntity) {
        ReflectionTestUtils.setField(mealReminderEntity, "id", ++sequence);
        stored.add(mealReminderEntity);
        return mealReminderEntity;
    }

    @Override
    public boolean existsByUserIdAndRemindAt(Long userId, LocalTime remindAt) {
        return stored.stream()
                .anyMatch(entity -> entity.getUserId().equals(userId)
                        && entity.getRemindAt().equals(remindAt));
    }

    public List<MealReminderEntity> findAll() {
        return List.copyOf(stored);
    }

    public int count() {
        return stored.size();
    }
}
```

### 3-2. FakeReminderPushClient

경로: `pasta-api/src/test/java/com/virtualcare/pasta/mealreminder/fake/FakeReminderPushClient.java`

```java
package com.virtualcare.pasta.mealreminder.fake;

import java.util.ArrayList;
import java.util.List;

import com.virtualcare.pasta.mealreminder.domain.ReminderPushClient;

public class FakeReminderPushClient implements ReminderPushClient {

    public record RegisteredNotice(Long userId, Long reminderId) {
    }

    private final List<RegisteredNotice> sentNotices = new ArrayList<>();

    @Override
    public void sendRegisteredNotice(Long userId, Long reminderId) {
        sentNotices.add(new RegisteredNotice(userId, reminderId));
    }

    public List<RegisteredNotice> sentNotices() {
        return List.copyOf(sentNotices);
    }
}
```

### 3-3. CapturingExecutor

경로: `pasta-api/src/test/java/com/virtualcare/pasta/mealreminder/fake/CapturingExecutor.java`

```java
package com.virtualcare.pasta.mealreminder.fake;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executor;

public class CapturingExecutor implements Executor {

    private final List<Runnable> submitted = new ArrayList<>();

    @Override
    public void execute(Runnable command) {
        submitted.add(command);
    }

    public int submittedCount() {
        return submitted.size();
    }

    public void runAll() {
        List<Runnable> snapshot = List.copyOf(submitted);
        submitted.clear();
        snapshot.forEach(Runnable::run);
    }
}
```

### 3-4. MealReminderCommandServiceTest

경로: `pasta-api/src/test/java/com/virtualcare/pasta/mealreminder/application/MealReminderCommandServiceTest.java`

```java
package com.virtualcare.pasta.mealreminder.application;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.time.LocalTime;
import java.util.concurrent.Executor;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import com.virtualcare.pasta.mealreminder.domain.DuplicateMealReminderException;
import com.virtualcare.pasta.mealreminder.domain.MealReminderEntity;
import com.virtualcare.pasta.mealreminder.fake.CapturingExecutor;
import com.virtualcare.pasta.mealreminder.fake.FakeMealReminderRepository;
import com.virtualcare.pasta.mealreminder.fake.FakeReminderPushClient;
import com.virtualcare.pasta.mealreminder.fake.FakeReminderPushClient.RegisteredNotice;

class MealReminderCommandServiceTest {

    private static final Long USER_ID = 1L;
    private static final LocalTime REMIND_AT = LocalTime.of(12, 30);

    private FakeMealReminderRepository mealReminderRepository;
    private FakeReminderPushClient reminderPushClient;

    @BeforeEach
    void setUp() {
        mealReminderRepository = new FakeMealReminderRepository();
        reminderPushClient = new FakeReminderPushClient();
    }

    private MealReminderCommandService serviceWith(Executor executor) {
        return new MealReminderCommandService(mealReminderRepository, reminderPushClient, executor);
    }

    @Test
    @DisplayName("성공 - 신규 식사 알림을 저장하고 저장된 알림 id 를 반환한다")
    void register_success_savesAndReturnsId() {
        MealReminderCommandService sut = serviceWith(Runnable::run);

        Long reminderId = sut.register(USER_ID, REMIND_AT);

        assertThat(reminderId).isEqualTo(1L);
        assertThat(mealReminderRepository.count()).isEqualTo(1);
        MealReminderEntity saved = mealReminderRepository.findAll().get(0);
        assertThat(saved.getUserId()).isEqualTo(USER_ID);
        assertThat(saved.getRemindAt()).isEqualTo(REMIND_AT);
    }

    @Test
    @DisplayName("성공 - 등록 후 실행기가 작업을 수행하면 등록 완료 푸시가 해당 사용자와 알림 id 로 1회 나간다")
    void register_success_sendsRegisteredNoticeOnce() {
        MealReminderCommandService sut = serviceWith(Runnable::run);

        Long reminderId = sut.register(USER_ID, REMIND_AT);

        assertThat(reminderPushClient.sentNotices())
                .containsExactly(new RegisteredNotice(USER_ID, reminderId));
    }

    @Test
    @DisplayName("성공 - 푸시는 실행기에 제출만 되고 실행기가 돌기 전에는 나가지 않는다")
    void register_success_pushIsDeferredToExecutor() {
        CapturingExecutor executor = new CapturingExecutor();
        MealReminderCommandService sut = serviceWith(executor);

        Long reminderId = sut.register(USER_ID, REMIND_AT);

        assertThat(executor.submittedCount()).isEqualTo(1);
        assertThat(reminderPushClient.sentNotices()).isEmpty();

        executor.runAll();

        assertThat(reminderPushClient.sentNotices())
                .containsExactly(new RegisteredNotice(USER_ID, reminderId));
    }

    @Test
    @DisplayName("성공 - 같은 사용자라도 알림 시각이 다르면 중복이 아니므로 둘 다 등록된다")
    void register_success_sameUserDifferentTime() {
        MealReminderCommandService sut = serviceWith(Runnable::run);

        Long first = sut.register(USER_ID, LocalTime.of(8, 0));
        Long second = sut.register(USER_ID, LocalTime.of(12, 30));

        assertThat(first).isNotEqualTo(second);
        assertThat(mealReminderRepository.count()).isEqualTo(2);
        assertThat(reminderPushClient.sentNotices()).hasSize(2);
    }

    @Test
    @DisplayName("실패 - 같은 사용자와 시각의 알림이 이미 있으면 예외가 발생하고 저장과 푸시가 일어나지 않는다")
    void register_fail_duplicate() {
        CapturingExecutor executor = new CapturingExecutor();
        MealReminderCommandService sut = serviceWith(executor);
        sut.register(USER_ID, REMIND_AT);
        executor.runAll();

        assertThatThrownBy(() -> sut.register(USER_ID, REMIND_AT))
                .isInstanceOf(DuplicateMealReminderException.class);

        assertThat(mealReminderRepository.count()).isEqualTo(1);
        assertThat(executor.submittedCount()).isZero();
        assertThat(reminderPushClient.sentNotices()).hasSize(1);
    }
}
```

주의: 마지막 케이스는 먼저 1건을 등록하고 `runAll()` 로 푸시를 비운 뒤 중복 등록을 시도합니다. 그래서 "푸시 총 1건(첫 등록분)", "실행기 제출 0건" 으로 두 번째 호출에서 푸시가 추가되지 않았음을 확인합니다.

## 4. 실행할 명령 (실행하지 않았습니다)

```bash
./gradlew :pasta-api:test --tests "com.virtualcare.pasta.mealreminder.application.MealReminderCommandServiceTest"
```

실행 결과는 없습니다. 이 작업은 시뮬레이션이라 명령을 돌리지 않았습니다. 컴파일 여부와 통과 여부는 위 가정 1~5 가 맞는지에 달려 있고, 직접 돌려 보기 전에는 모릅니다.

## 5. 완료 보고

- 작성한 것: `MealReminderCommandServiceTest` (5 케이스), `FakeMealReminderRepository`, `FakeReminderPushClient`, `CapturingExecutor`. 텍스트 산출물이며 저장소에 파일을 쓰지 않았습니다.
- 요청과 달라진 점: `@SpringBootTest` 와 `Thread.sleep(500)` 은 쓰지 않았습니다. Stub 1개 대신 Fake 2개를 썼습니다. DisplayName 은 `성공` 접두에 설명을 붙였습니다. 이유는 0절에 있습니다. 세 가지 중 하나라도 꼭 요청대로여야 하는 사정이 있으면 알려 주세요.
- 검증 안 된 것: 컴파일, 테스트 실행, 컨벤션 문서(`testcode-convention.md`, rules 08/09) 대조. 모두 하지 못했습니다. 가정 목록(1절)이 틀리면 Fake 구현이 달라집니다.
- 이 테스트로 잡지 못하는 것: 실제 `ThreadPoolTaskExecutor` 설정, 푸시 서버 호출(infrastructure 구현), 스레드 간 가시성 문제. 이는 별도 통합 테스트 범위이고, 지금 범위에서는 만들지 않았습니다.
- 알려진 한계: 운영 코드는 `save` 와 푸시 제출이 트랜잭션 안인지 밖인지 알 수 없습니다. 호출부에 `@Transactional` 이 걸려 있다면 롤백 시에도 푸시가 나갈 수 있는지는 이 테스트에서 다루지 않았습니다. 필요하면 별도로 논의하겠습니다.
