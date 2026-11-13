<!-- TC-9 with-skill / skill v1.10 / sonnet / 2026-11-13 -->
MealReminderCommandService.register 테스트 7건 작성 완료 (코드 작성, 테스트 실행 전)
- 계층·방식: Application / Fake(`FakeMealReminderRepository`) + 손으로 쓴 Spy(`SpyReminderPushClient`) + 동기 Executor, Spring 컨텍스트 없음. 테스트 DB 사용 안 함
- 조직 컨벤션: 적용 — `.claude/shared/vc-conventions-guide.md`, `.claude/shared/vc-conventions/testcode-convention.md` 있음
- 요청과 다르게 한 것:
  - `Stub` 대신 `Fake`/`Spy` 이름 — testcode-convention 4절 "Stub 금지", Application 대역은 Fake 우선(규칙 08 §2)
  - `@SpringBootTest` 안 씀 — testcode-convention "@SpringBootTest 는 E2E 에만", vc-conventions-guide 3절. 이 서비스는 Fake + Spy 로 재현되며 프록시 경계·동시 트랜잭션 검증이 아니라 예외 사유에 해당하지 않음
  - `Thread.sleep(500)` 안 씀 — testcode-convention "Thread.sleep() 금지, 비동기 검증은 Awaitility". 테스트에서는 `Executor` 를 `Runnable::run` 으로 주입해 푸시가 호출 스레드에서 즉시 실행되게 했으므로 기다릴 일이 없고, 500ms 대기 때문에 느리거나 간헐 실패하는 일도 없다
  - `@DisplayName` 을 "성공" 으로 쓰지 않고 행동과 결과로 적음 — testcode-convention 1절 "'정상', '성공' 같은 말 대신 구체적인 행동과 결과"
  - 요청에 없던 테스트 추가 — 중복 예외 분기(`DuplicateMealReminderException`)와 "같은 시각, 다른 사용자" 케이스. 요청이 정상 경로만 말했지만 예외 분기가 있어 RR-14 에 따라 작성했다. 코드에 `// 요청 외 추가` 주석으로 표시
- 미확인: 아래 가정 3건은 실제 코드를 못 봐서 가정이다
  - 패키지명, `MealReminderEntity` 의 id 필드명(`id`), `ReminderPushClient.sendRegisteredNotice(Long, Long)` 의 반환형(void)·인자 타입
  - Fake 의 id 부여를 `ReflectionTestUtils.setField(entity, "id", ...)` 로 했다. 엔티티에 id 를 넣는 생성자·setter 가 이미 있으면 그쪽으로 바꾼다
  - `MealReminderRepository` 에 `save`, `existsByUserIdAndRemindAt` 외 추상 메서드가 있으면 Fake 가 컴파일되지 않으므로 추가 구현이 필요하다

## 세부

### 계층 식별 근거
`application/MealReminderCommandService` — 패키지 경로가 application 이고, 협력 객체 `MealReminderRepository`·`ReminderPushClient` 가 domain 인터페이스다. 비동기 실행기는 JDK `Executor` 라 대역을 따로 만들지 않는다. infra 구현체는 참조하지 않는다.

### 사전 확인 결과
- `find . -name "Fake*"` 결과 `FakeMealReminderRepository` 와 `ReminderPushClient` 대역 모두 없음 → 둘 다 새로 만든다 (사용자 제공 결과 기준)
- 같은 패키지 기존 `*Test` 는 이번 입력에 없어 읽지 못했다. 기존 클래스에 더하는 게 아니라 신규 클래스라서 파괴적 쓰기 위험은 없지만, `MealReminderCommandServiceTest.java` 가 이미 있으면 덮지 말고 Edit 로 추가한다 (DW-3). 실행 전 `git status --short` 로 확인한다 (DW-1)
- 메서드명은 신규 클래스라 `{상황}_{기대결과}` 영어 + 한국어 `@DisplayName`

### 파일 1: `src/test/java/.../mealreminder/domain/FakeMealReminderRepository.java` (신규)

```java
// 패키지는 실제 도메인 패키지에 맞춘다 (미확인)
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.List;
import org.springframework.test.util.ReflectionTestUtils;

class FakeMealReminderRepository implements MealReminderRepository {

    private final List<MealReminderEntity> mealReminderEntityList = new ArrayList<>();
    private long nextId = 1L;

    @Override
    public MealReminderEntity save(MealReminderEntity mealReminderEntity) {
        // 가정: 엔티티 id 필드명이 "id" 이고 setter 가 없다
        ReflectionTestUtils.setField(mealReminderEntity, "id", nextId++);
        mealReminderEntityList.add(mealReminderEntity);
        return mealReminderEntity;
    }

    @Override
    public boolean existsByUserIdAndRemindAt(Long userId, LocalTime remindAt) {
        return mealReminderEntityList.stream()
            .anyMatch(mealReminderEntity -> mealReminderEntity.getUserId().equals(userId)
                && mealReminderEntity.getRemindAt().equals(remindAt));
    }

    List<MealReminderEntity> findAll() {
        return List.copyOf(mealReminderEntityList);
    }
}
```

### 파일 2: `src/test/java/.../mealreminder/domain/SpyReminderPushClient.java` (신규)

```java
import java.util.ArrayList;
import java.util.List;

class SpyReminderPushClient implements ReminderPushClient {

    record RegisteredNoticeCall(Long userId, Long mealReminderId) {
    }

    private final List<RegisteredNoticeCall> registeredNoticeCallList = new ArrayList<>();

    @Override
    public void sendRegisteredNotice(Long userId, Long mealReminderId) {
        registeredNoticeCallList.add(new RegisteredNoticeCall(userId, mealReminderId));
    }

    int getCallCount() {
        return registeredNoticeCallList.size();
    }

    RegisteredNoticeCall getLastCall() {
        return registeredNoticeCallList.get(registeredNoticeCallList.size() - 1);
    }
}
```

외부 푸시 서버 호출은 void 부수효과라 Spy 다. 인메모리 저장소만 `Fake*` 이름을 쓴다 (vc-testcode.md 1절).

### 파일 3: `src/test/java/.../mealreminder/application/MealReminderCommandServiceTest.java` (신규)

```java
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.assertj.core.api.Assertions.tuple;

import java.time.LocalTime;
import java.util.concurrent.Executor;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

// Spring 컨텍스트 없는 Application 단위 테스트.
// 비동기 실행기는 Runnable::run 으로 주입해 푸시를 호출 스레드에서 즉시 실행한다 (sleep·Awaitility 불필요).
class MealReminderCommandServiceTest {

    private static final Long USER_ID = 101L; // Fake 가 부여하는 id(1부터)와 겹치지 않게 둠
    private static final Long OTHER_USER_ID = 202L;
    private static final LocalTime REMIND_AT = LocalTime.of(8, 30); // 가정값: 아침 식사 알림 시각

    private FakeMealReminderRepository fakeMealReminderRepository;
    private SpyReminderPushClient spyReminderPushClient;
    private MealReminderCommandService mealReminderCommandService;

    @BeforeEach
    void setUp() {
        fakeMealReminderRepository = new FakeMealReminderRepository();
        spyReminderPushClient = new SpyReminderPushClient();
        Executor directExecutor = Runnable::run;
        mealReminderCommandService = new MealReminderCommandService(
            fakeMealReminderRepository, spyReminderPushClient, directExecutor);
    }

    @Nested
    @DisplayName("식사 알림을 등록할 때")
    class RegisterNew {

        @Test
        @DisplayName("같은 사용자·시각의 알림이 없으면 저장된 알림의 id 를 반환한다")
        void register_noDuplicate_returnsSavedMealReminderId() {
            // Given

            // When
            Long registeredMealReminderId = mealReminderCommandService.register(USER_ID, REMIND_AT);

            // Then
            assertThat(registeredMealReminderId)
                .isEqualTo(fakeMealReminderRepository.findAll().get(0).getId());
        }

        @Test
        @DisplayName("같은 사용자·시각의 알림이 없으면 요청한 사용자와 시각으로 알림 1건을 저장한다")
        void register_noDuplicate_savesMealReminderWithRequestedUserAndTime() {
            // Given

            // When
            mealReminderCommandService.register(USER_ID, REMIND_AT);

            // Then
            assertThat(fakeMealReminderRepository.findAll())
                .extracting(MealReminderEntity::getUserId, MealReminderEntity::getRemindAt)
                .containsExactly(tuple(USER_ID, REMIND_AT));
        }

        @Test
        @DisplayName("같은 사용자·시각의 알림이 없으면 등록된 알림 id 로 등록 완료 푸시를 1번 보낸다")
        void register_noDuplicate_sendsRegisteredNoticeOnceWithSavedId() {
            // Given

            // When
            Long registeredMealReminderId = mealReminderCommandService.register(USER_ID, REMIND_AT);

            // Then
            assertThat(spyReminderPushClient.getCallCount()).isEqualTo(1);
            assertThat(spyReminderPushClient.getLastCall())
                .isEqualTo(new SpyReminderPushClient.RegisteredNoticeCall(USER_ID, registeredMealReminderId));
        }

        // 요청 외 추가: 같은 시각 다른 사용자 — existsBy 조건에서 userId 를 빼도 잡는 테스트가 없어서
        @Test
        @DisplayName("같은 시각이라도 다른 사용자가 이미 등록했다면 중복이 아니므로 알림 2건이 저장된다")
        void register_sameTimeButOtherUser_savesBothMealReminders() {
            // Given
            mealReminderCommandService.register(OTHER_USER_ID, REMIND_AT);

            // When
            mealReminderCommandService.register(USER_ID, REMIND_AT);

            // Then
            assertThat(fakeMealReminderRepository.findAll())
                .extracting(MealReminderEntity::getUserId)
                .containsExactlyInAnyOrder(OTHER_USER_ID, USER_ID);
        }
    }

    // 요청 외 추가: 중복 예외 분기 — 이 분기를 깨도 잡는 테스트가 없어서
    @Nested
    @DisplayName("이미 같은 사용자·시각의 알림이 있을 때")
    class RegisterDuplicate {

        @BeforeEach
        void registerExistingMealReminder() {
            // Given (공통): 사전 등록 1건 = 저장 1건 + 푸시 1회
            mealReminderCommandService.register(USER_ID, REMIND_AT);
        }

        @Test
        @DisplayName("같은 사용자·시각으로 다시 등록하면 DuplicateMealReminderException 이 발생한다")
        void register_duplicate_throwsDuplicateMealReminderException() {
            // Given

            // When & Then
            assertThatThrownBy(() -> mealReminderCommandService.register(USER_ID, REMIND_AT))
                .isInstanceOf(DuplicateMealReminderException.class);
        }

        @Test
        @DisplayName("중복으로 거부되면 알림을 추가로 저장하지 않는다")
        void register_duplicate_doesNotSaveAdditionalMealReminder() {
            // Given

            // When
            assertThatThrownBy(() -> mealReminderCommandService.register(USER_ID, REMIND_AT))
                .isInstanceOf(DuplicateMealReminderException.class);

            // Then
            assertThat(fakeMealReminderRepository.findAll()).hasSize(1);
        }

        @Test
        @DisplayName("중복으로 거부되면 등록 완료 푸시를 다시 보내지 않는다")
        void register_duplicate_doesNotSendRegisteredNoticeAgain() {
            // Given

            // When
            assertThatThrownBy(() -> mealReminderCommandService.register(USER_ID, REMIND_AT))
                .isInstanceOf(DuplicateMealReminderException.class);

            // Then
            assertThat(spyReminderPushClient.getCallCount()).isEqualTo(1);
        }
    }
}
```

`RegisterNew` 4건 + `RegisterDuplicate` 3건 = 7건이며 `@Nested` 두 그룹 모두 테스트 2개 이상이다.

### 깨뜨리면 실패하는가 (RR-12, 코드 검토로만 확인, 실행하지 않음)
- `existsByUserIdAndRemindAt` 검사를 제거하면 `RegisterDuplicate` 3건이 실패한다
- 중복 검사에서 `userId` 비교를 빼면 "다른 사용자" 테스트가 실패한다 (이 테스트의 존재 이유)
- `reminderPushExecutor.execute` 호출을 제거하면 푸시 1회 테스트가 실패한다. 푸시 인자의 알림 id 를 `userId` 로 바꾸면 `USER_ID`(101)와 Fake id(1)가 달라 `RegisteredNoticeCall` 비교가 실패한다

### 실행할 명령 (실행하지 않았다)
```
git status --short <테스트 파일 경로>        # DW-1: 같은 이름 파일 미커밋 변경 확인
./gradlew :pasta-api:spotlessApply
./gradlew :pasta-api:test --tests MealReminderCommandServiceTest
python3 forge/common/review-lint.py          # VC 검사 자동 활성: Thread.sleep·Assertions 위반 0건 기대
git status                                   # DW-5: 의도치 않은 삭제 없는지
```

### Self-check
| # | 결과 | 비고 |
|---|------|------|
| 1·12 계층 식별 | PASS | application 패키지, domain 인터페이스 협력 객체 |
| 2 방식 | PASS | Fake + Spy, 컨텍스트 없음 |
| 3 DB 비전환 | N/A | DB 미사용, 설정 변경 없음 |
| 4 DisplayName | PASS | 7건 모두 구체적 행동·결과 |
| 5 통과 | 미확인 | gradle 미실행 |
| 6 GWT | PASS | 예외 테스트는 `// When & Then` 또는 Given·When·Then |
| 7 @Nested | PASS | 두 그룹 모두 2개 이상 |
| 8 AssertJ | PASS | JUnit Assertions 0건 |
| 11·16 FQCN | PASS | 인라인 FQCN 0건  |
| 17 infra 참조 | PASS | infra 클래스 참조 0건 |
| 19 Fake | PASS | Repository 를 `@Mock` 으로 두지 않음 |
| 20 깨뜨리면 실패 | PASS(코드 검토) | 위 항목 |
| 21 review-lint | 미확인 | 미실행 |
| 22 예외 분기 | PASS | 중복 분기 추가 |
| 23 최종 코드 | PASS | 제출 코드가 최종본 |
| 24·25 조직 컨벤션 | PASS | `Fake*`, 구체적 DisplayName, GWT, sleep 0건, `@SpringBootTest` 0건, 테스트당 논리 검증 하나 |

### 남은 리스크
- 엔티티·인터페이스 시그니처 가정(위 미확인 3건). 컴파일이 안 되면 Fake·Spy 쪽만 맞추면 된다
- 이 테스트는 `Runnable::run` 으로 "푸시 호출이 일어나는 것"을 본다. 운영의 `ThreadPoolTaskExecutor` 설정(스레드 풀 크기, 거부 정책)이나 실제 비동기 동작은 이 테스트가 검증하지 않는다. 필요하면 실행기 자체를 따로 검증하는 테스트를 만들고, 그때는 `Thread.sleep` 대신 Awaitility 를 쓴다. 프로젝트에 Awaitility 의존성이 있는지는 미확인
