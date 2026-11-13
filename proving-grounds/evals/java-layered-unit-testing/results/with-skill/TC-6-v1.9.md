<!-- TC-6 with-skill rerun / skill v1.9 / sonnet / 2026-11-13 / 103,690 tok / tool 7 / 92s -->

## 1. 대상 클래스와 계층

- 대상: `Glp1InjectionRecordCommandService.register`
- 계층: Application. 근거는 패키지 `application/`과 의존성입니다. `Glp1InjectionRecordRepository`는 domain 인터페이스, `Glp1GroupQueryUseCase`는 다른 도메인 UseCase, `PushReservationClient`는 외부 통신입니다.
- 이 작업은 파일을 쓰지 않는 시뮬레이션입니다. 아래 코드는 제안이고, 명령 실행 단계는 실행 계획으로만 적었습니다.

## 2. 요청과 다르게 간 부분

| 요청 | 적용 | 근거 |
|---|---|---|
| `@Mock` Repository·UseCase + `given().willReturn()` | **Fake** 사용 | 규칙 08 §2 (Fake → Stub/Spy → Mock). `forge/common/pasta-rules/08-test-code-convention.md` 및 RR-12·RR-F14 (`review-recurrence-guard.md`). 루브릭 AUTO FAIL 6은 사용자가 "기존처럼 Mock으로"라고 해도 적용됩니다. #789·#794에서 같은 지적을 받았습니다. |
| "Fake 만드는 건 오버" | `FakeGlp1GroupQueryUseCase`(신규), `SpyPushReservationClient`(신규), `FakeGlp1InjectionRecordRepository`(기존 재사용) | `find . -name "Fake*"` 결과 Fake Repository만 있어서 없는 두 개만 만듭니다. 규칙 08 §2-1은 상태를 가진 객체에 Fake, 외부 통신 Client에 Spy를 요구합니다. 각각 30줄 안팎입니다. |
| 기존 `Glp1InjectionPlanCommandServiceTest` 스타일(Mockito) | 따르지 않음 | 스킬 §2에 "같은 패키지 기존 테스트가 Mock 위주여도 새 테스트는 Fake로 쓴다. 기존 테스트는 고칠 범위가 아니면 그대로 둔다"고 되어 있습니다. 기존 파일은 건드리지 않습니다. |
| 정상 + 미래 시각 2개 | **3개** (미소유 그룹 1개 추가) | 스킬 v1.9 규칙입니다. 요청된 케이스가 예외 분기(`getOwnedGroup` 미소유 NotFoundException)보다 적으면 빠진 분기를 작성하고 주석으로 표시합니다. 아래 코드에 `// 요청 외 추가` 주석을 달았습니다. |
| (암묵) 검증 순서 | 미소유 테스트에 미래 시각을 함께 사용 | RR-14 "존재·소유 확인 → 입력 검증" 순서를 같은 테스트로 고정합니다. 순서가 뒤집히면 `NotFoundException` 대신 `BadRequestException`이 나와 실패합니다. |

## 3. 확인된 것과 가정한 것

**확인된 것** (전제 조건 + 스킬)
- `register`의 로직은 소유 확인, `injectedAt.isAfter(currentAt)` 검사, save, 푸시 예약, id 반환 순서입니다.
- `FakeGlp1InjectionRecordRepository`는 존재합니다.
- `FakeGlp1GroupQueryUseCase`와 `SpyPushReservationClient`는 없습니다.

**가정한 것** (실제 소스는 못 봤으므로 Phase 0에서 대조 후 교체)

| 번호 | 가정 | 틀리면 |
|---|---|---|
| A1 | `FakeGlp1InjectionRecordRepository`는 `save` 시 id를 채번하고 `findById(Long)`→`Optional`, `findAll()`→`List`를 제공 | 없는 메서드는 Fake에 추가(기존 파일은 Edit로만) |
| A2 | `Glp1InjectionRecordInDto`는 3개 컴포넌트(`groupId`, `injectedAt`, `currentAt`) 외에 `dose`·`site` 등이 더 있을 수 있어 헬퍼 한 곳에서 맞춥니다. 시각 타입은 `Instant` | 헬퍼 `glp1InjectionRecordInDto()`만 수정 |
| A3 | 엔티티 접근자는 `getId()`, `getUserId()`, `getGlp1GroupEntity()`, `getInjectedAt()`, `getNextInjectionAt()` | 실제 접근자명으로 교체 |
| A4 | `Glp1GroupEntity`는 `builder().id(...)`로 생성 가능 | 헬퍼 `glp1GroupEntity()`만 수정 |
| A5 | `PushReservationClient.reserveNextInjection(Long, Instant)`는 `void` | Spy 시그니처 조정 |
| A6 | `NotFoundException(ExceptionConstants.GLP1_GROUP_NOT_FOUND)` 생성자·상수 | Fake 한 곳만 수정 |
| A7 | `Glp1GroupQueryUseCase`의 메서드는 `getOwnedGroup` 하나 | 더 있으면 Fake에 구현 추가 |
| A8 | 패키지 `com.kakaohealthcare.pasta.glp1.*`, 예외·상수 import 경로 | 실제 경로 확인 |

## 4. 제안 코드

### 4-1. `FakeGlp1GroupQueryUseCase` (신규)
`src/test/java/.../glp1/domain/FakeGlp1GroupQueryUseCase.java`는 기존 Fake Repository와 같은 위치입니다. 소유 조건(`userId` + `groupId`)을 실제처럼 적용하고, 정답을 주입하는 `setResult` 방식은 쓰지 않습니다.

```java
package com.kakaohealthcare.pasta.glp1.domain;

import com.kakaohealthcare.pasta.global.exception.ExceptionConstants;
import com.kakaohealthcare.pasta.global.exception.NotFoundException;
import java.util.HashMap;
import java.util.Map;

public class FakeGlp1GroupQueryUseCase implements Glp1GroupQueryUseCase {

    private record OwnedGroupKey(Long userId, Long groupId) {}

    private final Map<OwnedGroupKey, Glp1GroupEntity> glp1GroupEntityByOwnedGroupKey = new HashMap<>();

    public Glp1GroupEntity addOwnedGroup(Long userId, Glp1GroupEntity glp1GroupEntity) {
        glp1GroupEntityByOwnedGroupKey.put(new OwnedGroupKey(userId, glp1GroupEntity.getId()), glp1GroupEntity);
        return glp1GroupEntity;
    }

    @Override
    public Glp1GroupEntity getOwnedGroup(Long userId, Long groupId) {
        Glp1GroupEntity glp1GroupEntity = glp1GroupEntityByOwnedGroupKey.get(new OwnedGroupKey(userId, groupId));
        if (glp1GroupEntity == null) {
            throw new NotFoundException(ExceptionConstants.GLP1_GROUP_NOT_FOUND);
        }
        return glp1GroupEntity;
    }
}
```

### 4-2. `SpyPushReservationClient` (신규)
JDK 컬렉션만 쓰고 Mockito는 쓰지 않습니다(규칙 08 §2-2).

```java
package com.kakaohealthcare.pasta.glp1.domain;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

public class SpyPushReservationClient implements PushReservationClient {

    public record ReserveNextInjectionCall(Long userId, Instant nextInjectionAt) {}

    private final List<ReserveNextInjectionCall> reserveNextInjectionCallList = new ArrayList<>();

    @Override
    public void reserveNextInjection(Long userId, Instant nextInjectionAt) {
        reserveNextInjectionCallList.add(new ReserveNextInjectionCall(userId, nextInjectionAt));
    }

    public int getCallCount() {
        return reserveNextInjectionCallList.size();
    }

    public ReserveNextInjectionCall getLastCall() {
        return reserveNextInjectionCallList.get(reserveNextInjectionCallList.size() - 1);
    }
}
```

### 4-3. `Glp1InjectionRecordCommandServiceTest` (신규 파일)
Phase 0에서 같은 이름의 파일이 이미 있는지 확인합니다. 있으면 Edit로 추가하고 통째로 덮지 않습니다(DW-3).

```java
package com.kakaohealthcare.pasta.glp1.application;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.kakaohealthcare.pasta.global.exception.BadRequestException;
import com.kakaohealthcare.pasta.global.exception.NotFoundException;
import com.kakaohealthcare.pasta.glp1.domain.FakeGlp1GroupQueryUseCase;
import com.kakaohealthcare.pasta.glp1.domain.FakeGlp1InjectionRecordRepository;
import com.kakaohealthcare.pasta.glp1.domain.Glp1GroupEntity;
import com.kakaohealthcare.pasta.glp1.domain.Glp1InjectionRecordEntity;
import com.kakaohealthcare.pasta.glp1.domain.SpyPushReservationClient;
import java.time.Duration;
import java.time.Instant;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

class Glp1InjectionRecordCommandServiceTest {

    // 값이 서로 겹치지 않게 둬서 userId/groupId 인자를 바꿔 넘기는 회귀를 잡는다
    private static final Long USER_ID = 7L;
    private static final Long OTHER_USER_ID = 8L;
    private static final Long GROUP_ID = 11L;
    private static final Instant CURRENT_AT = Instant.parse("2026-11-13T09:00:00Z");
    private static final Instant PAST_INJECTED_AT = CURRENT_AT.minus(Duration.ofDays(2));
    private static final Instant FUTURE_INJECTED_AT = CURRENT_AT.plus(Duration.ofDays(1));

    private FakeGlp1InjectionRecordRepository fakeGlp1InjectionRecordRepository;
    private FakeGlp1GroupQueryUseCase fakeGlp1GroupQueryUseCase;
    private SpyPushReservationClient spyPushReservationClient;
    private Glp1InjectionRecordCommandService glp1InjectionRecordCommandService;

    @BeforeEach
    void setUp() {
        fakeGlp1InjectionRecordRepository = new FakeGlp1InjectionRecordRepository();
        fakeGlp1GroupQueryUseCase = new FakeGlp1GroupQueryUseCase();
        spyPushReservationClient = new SpyPushReservationClient();
        glp1InjectionRecordCommandService = new Glp1InjectionRecordCommandService(
            fakeGlp1InjectionRecordRepository, fakeGlp1GroupQueryUseCase, spyPushReservationClient);
    }

    @Nested
    @DisplayName("register")
    class Register {

        @Test
        @DisplayName("본인 그룹에 과거 시각 주사 기록을 등록하면 저장하고 id 를 돌려주며 다음 주사 푸시를 1회 예약한다")
        void register_ownedGroupAndPastInjectedAt_savesRecordAndReservesPush() {
            // Given
            Glp1GroupEntity glp1GroupEntity = fakeGlp1GroupQueryUseCase.addOwnedGroup(USER_ID, glp1GroupEntity());
            Glp1InjectionRecordInDto glp1InjectionRecordInDto =
                glp1InjectionRecordInDto(GROUP_ID, PAST_INJECTED_AT);

            // When
            Long registeredId = glp1InjectionRecordCommandService.register(USER_ID, glp1InjectionRecordInDto);

            // Then
            Glp1InjectionRecordEntity glp1InjectionRecordEntity =
                fakeGlp1InjectionRecordRepository.findById(registeredId).orElseThrow();
            assertThat(glp1InjectionRecordEntity.getUserId()).isEqualTo(USER_ID);
            assertThat(glp1InjectionRecordEntity.getGlp1GroupEntity().getId()).isEqualTo(glp1GroupEntity.getId());
            assertThat(glp1InjectionRecordEntity.getInjectedAt()).isEqualTo(PAST_INJECTED_AT);

            assertThat(spyPushReservationClient.getCallCount()).isOne();
            assertThat(spyPushReservationClient.getLastCall().userId()).isEqualTo(USER_ID);
            assertThat(spyPushReservationClient.getLastCall().nextInjectionAt())
                .isNotNull()
                .isEqualTo(glp1InjectionRecordEntity.getNextInjectionAt());
        }

        @Test
        @DisplayName("주사 시각이 현재 시각보다 미래이면 예외를 던지고 저장도 푸시 예약도 하지 않는다")
        void register_futureInjectedAt_throwsBadRequestAndSavesNothing() {
            // Given
            fakeGlp1GroupQueryUseCase.addOwnedGroup(USER_ID, glp1GroupEntity());
            Glp1InjectionRecordInDto glp1InjectionRecordInDto =
                glp1InjectionRecordInDto(GROUP_ID, FUTURE_INJECTED_AT);

            // When & Then
            assertThatThrownBy(() -> glp1InjectionRecordCommandService.register(USER_ID, glp1InjectionRecordInDto))
                .isInstanceOf(BadRequestException.class);

            List<Glp1InjectionRecordEntity> glp1InjectionRecordEntityList =
                fakeGlp1InjectionRecordRepository.findAll();
            assertThat(glp1InjectionRecordEntityList).isEmpty();
            assertThat(spyPushReservationClient.getCallCount()).isZero();
        }

        // 요청 외 추가: 미소유 그룹 NotFoundException 분기 — 이 분기를 깨도 잡는 테스트가 없어서
        @Test
        @DisplayName("다른 사용자의 그룹이면 주사 시각이 미래여도 입력 검증보다 먼저 소유 확인 실패로 NotFound 를 던진다")
        void register_groupOwnedByOtherUser_throwsNotFoundBeforeTimeValidation() {
            // Given
            fakeGlp1GroupQueryUseCase.addOwnedGroup(OTHER_USER_ID, glp1GroupEntity());
            Glp1InjectionRecordInDto glp1InjectionRecordInDto =
                glp1InjectionRecordInDto(GROUP_ID, FUTURE_INJECTED_AT);

            // When & Then
            assertThatThrownBy(() -> glp1InjectionRecordCommandService.register(USER_ID, glp1InjectionRecordInDto))
                .isInstanceOf(NotFoundException.class);

            assertThat(fakeGlp1InjectionRecordRepository.findAll()).isEmpty();
            assertThat(spyPushReservationClient.getCallCount()).isZero();
        }
    }

    private Glp1GroupEntity glp1GroupEntity() {
        return Glp1GroupEntity.builder().id(GROUP_ID).build();  // 가정 A4: 실제 빌더/팩토리에 맞춰 교체
    }

    private Glp1InjectionRecordInDto glp1InjectionRecordInDto(Long groupId, Instant injectedAt) {
        // 가정 A2: 나머지 컴포넌트(용량·부위 등)는 실제 시그니처에 맞춰 도메인상 유효한 값으로 채운다
        return new Glp1InjectionRecordInDto(groupId, injectedAt, CURRENT_AT);
    }
}
```

## 5. Self-check 결과

| # | 항목 | 결과 |
|---|---|---|
| 1·2 | 계층 식별, Fake 우선·외부 통신만 Spy | PASS |
| 4 | `@DisplayName` 한국어 | PASS |
| 5 | 테스트 통과 | 미실행 (가정 A1~A8 대조 후 확인 필요) |
| 6·7·8 | Given-When-Then, `@Nested`, AssertJ | PASS |
| 9·14 | 기존 테스트 스타일 정렬 | 의도적 예외. 기존은 Mockito인데 스킬 §2 에 따라 Fake로 작성 |
| 11·16 | FQCN 없음 | PASS. 전부 `import`, `var` 없음 |
| 17 | infra 구현체 직접 참조 | PASS (0건) |
| 18 | verify 대신 Spy 콜카운트 | PASS. Mockito를 전혀 쓰지 않음 |
| 19 | 상태 저장소 `@Mock` 금지 | PASS |
| 20 | 깨뜨리면 실패 | 아래 변이 계획 참조 |
| 21 | review-lint 0건 | 미실행 (실행 계획에 포함) |
| 22 | 빠진 예외 분기 | PASS. 미소유 분기를 추가하고 주석으로 표시 |
| 23 | 제출 코드가 최종 코드 | PASS. 아래 6번 항목 참조 |

## 6. 작성 중 스스로 고친 결함

- 정상 테스트에서 `nextInjectionAt`을 `isNotNull()` 없이 엔티티 값과 비교하면 둘 다 `null`일 때도 통과합니다. `isNotNull()`을 붙여 코드에서 고쳤습니다.
- 반환 id는 반환값 자체가 아니라 Fake에서 `findById(registeredId)`로 다시 조회해 확인합니다. `savedEntity.getId()` 반환을 `null`로 바꾸는 회귀를 잡습니다.

## 7. 실행 계획 (미실행)

1. **Phase 0**
   - `git status --short <테스트 경로>`로 미커밋 변경을 확인합니다 (DW-1).
   - 같은 이름의 `Glp1InjectionRecordCommandServiceTest`가 있는지 확인합니다. 있으면 Edit로 추가합니다.
   - `FakeGlp1InjectionRecordRepository`를 읽어 A1을 확인합니다.
   - `Glp1GroupQueryUseCase`, `PushReservationClient`의 실제 시그니처로 A5~A7을 확인합니다.
2. **파일 생성**: 신규 파일 3개(Fake, Spy, Test)를 만듭니다.
3. **실행**:
   - `./gradlew :{module}:spotlessApply`
   - `./gradlew :{module}:test --tests "*Glp1InjectionRecordCommandServiceTest"`
   - `python3 forge/common/review-lint.py` (위반 0건, 확인 항목은 사유 기록)
   - `git status`로 의도하지 않은 삭제가 없는지 확인합니다 (DW-5).
4. **변이 확인** (RR-12 확인 방법). 각각 일부러 깨뜨렸을 때 테스트가 실패해야 합니다.
   - `userId`를 다른 값으로 넘기게 바꾼다 → 정상 테스트 실패
   - `isAfter`를 `isBefore`로 바꾼다 → 정상·미래 테스트 실패
   - 미래 시각 검사를 소유 확인 앞으로 옮긴다 → 미소유 테스트 실패
   - `pushReservationClient` 호출을 삭제한다 → 정상 테스트 실패

## 8. 남은 리스크

1. **외부 호출 성공 후 DB 저장 실패 / 푸시 예약 실패 시 롤백** (RR-13 질문 2)은 이 단위 테스트로 검증되지 않습니다. 현재 코드는 save 후 푸시를 호출하고, 푸시 예외는 `@Transactional`을 롤백합니다. 동작이 의도인지는 별도 확인이 필요하고, 프록시 동작을 보려면 `@SpringBootTest`가 필요합니다. 범위 밖이라 보고만 합니다 (SC-1).
2. **`injectedAt == currentAt` 경계**(`isAfter`는 같으면 통과)는 테스트하지 않았습니다. 요청 범위(정상·미래)를 넘는 케이스라서 넣지 않았고, 원하시면 1개 추가하겠습니다.
3. 가정 A1~A8이 맞는지에 따라 헬퍼 몇 군데는 컴파일 에러가 날 수 있습니다. 수정 지점은 헬퍼 2개와 Fake 1개로 한정했습니다.
