<!-- TC-6 with-skill / skill v1.8 / sonnet / 2026-11-13 / 88,078 tok / tool 6 / 74s -->

# `Glp1InjectionRecordCommandService.register` 단위 테스트 시뮬레이션

파일은 쓰지 않았고 아래 코드는 설계안입니다.

## 1. 요청과 스킬이 충돌하는 부분

요청은 `@Mock Glp1InjectionRecordRepository`, `@Mock Glp1GroupQueryUseCase`, `given().willReturn()` 으로 빠르게 짜라는 것입니다. 이 방식은 따르지 않고 Fake·Spy 로 작성합니다.

| 요청 | 처리 | 근거 |
|---|---|---|
| Repository, UseCase 를 `@Mock` + `given().willReturn()` | 거부하고 Fake 로 작성 | 루브릭 AUTO FAIL 6 (RR-F14). 사용자가 Mock 을 요구해도 적용됩니다. 규칙 08 §2 와 `review-lint.py` 의 `[위반][RR-12]` 대상입니다. |
| "Fake 만드는 건 오버" | 필요한 것만 최소로 신설 | 기존 `FakeGlp1InjectionRecordRepository` 는 재사용합니다. 새로 만드는 것은 `FakeGlp1GroupQueryUseCase` 와 `SpyPushReservationClient` 두 개뿐입니다. |
| `Glp1InjectionPlanCommandServiceTest` 처럼 `MockitoExtension` | 따르지 않음 | 스킬은 같은 패키지 기존 테스트가 Mock 위주여도 새 테스트는 Fake 로 쓰고, 기존 테스트는 고치지 않고 둡니다. |
| 정상 등록 + 미래 시각 예외 2개 | 그대로 2개 | 범위는 지킵니다. 예외 테스트에는 "저장 미호출 + 푸시 미호출" 확인을 포함합니다. 이는 스킬의 필수 항목이고 별도 테스트가 아닙니다. |

`PushReservationClient` 는 외부 통신이므로 Mock 이 아니라 Spy 로 둡니다. 호출 횟수와 마지막 인자는 `getCallCount()` 와 `getLastCall()` 로 검증합니다.

## 2. 확인된 사실과 가정

**확인된 사실** (전제 조건)
- 서비스 코드와 의존 3개: Repository 는 domain 인터페이스, `Glp1GroupQueryUseCase`, `PushReservationClient`
- `FakeGlp1InjectionRecordRepository` 는 존재하고 `FakeGlp1GroupQueryUseCase`, `SpyPushReservationClient` 는 없음
- 4-Tier 구조이고 대상은 Application 계층. 근거는 `application/` 패키지이고, 의존성도 domain 인터페이스와 외부 Client 뿐입니다.

**가정** (실제 코드 확인이 필요하며 실행 계획 1단계에서 확인)

| # | 가정 | 틀렸을 때 수정 |
|---|---|---|
| A1 | `FakeGlp1InjectionRecordRepository` 는 `save` 시 id 를 채번하고, `findById(Long)` 이 `Optional` 을 반환하며, `findAll()` 이 있음 | 있는 조회 메서드로 교체합니다. 없으면 `findAll()` 을 Fake 에 추가해야 하며, 이 경우 사용자 확인이 필요합니다. |
| A2 | 시각 타입은 `Instant` 이고 `Glp1InjectionRecordInDto` 의 필드는 `groupId, injectedAt, currentAt` 이 전부가 아님 | 아래 `glp1InjectionRecordInDto(...)` 헬퍼 한 곳만 고칩니다. |
| A3 | `PushReservationClient.reserveNextInjection(Long, Instant)` 은 `void` | 반환값이 있으면 Spy 가 기본값을 돌려주게 합니다. |
| A4 | `Glp1GroupQueryUseCase` 의 추상 메서드는 `getOwnedGroup` 하나뿐 | 다른 메서드가 있으면 `UnsupportedOperationException` 으로 구현합니다. |
| A5 | `Glp1GroupEntity`, `Glp1InjectionRecordEntity` 의 게터는 `getUserId()`, `getGroup()` | 실제 게터명으로 교체합니다. |
| A6 | 미소유 그룹의 예외는 `NotFoundException(ExceptionConstants.GLP1_GROUP_NOT_FOUND)` | 실제 상수로 교체합니다. 이 상수는 Fake 안에서만 쓰입니다. |

## 3. 테스트 코드 전체

### 3-1. `FakeGlp1GroupQueryUseCase`

경로는 기존 Fake 와 같은 `src/test/java/.../glp1/domain/` 로 가정합니다.

```java
// package ...glp1.domain;
// import java.util.HashMap;
// import java.util.Map;
// import java.util.Objects;
// (Glp1GroupEntity, Glp1GroupQueryUseCase, NotFoundException, ExceptionConstants 는 프로젝트 패키지 import)

class FakeGlp1GroupQueryUseCase implements Glp1GroupQueryUseCase {

    private record OwnedGroupKey(Long userId, Long groupId) {
    }

    private final Map<OwnedGroupKey, Glp1GroupEntity> glp1GroupEntityByOwnedGroupKey = new HashMap<>();

    void saveOwnedGroup(Long userId, Long groupId, Glp1GroupEntity glp1GroupEntity) {
        glp1GroupEntityByOwnedGroupKey.put(new OwnedGroupKey(userId, groupId), glp1GroupEntity);
    }

    @Override
    public Glp1GroupEntity getOwnedGroup(Long userId, Long groupId) {
        Glp1GroupEntity glp1GroupEntity = glp1GroupEntityByOwnedGroupKey.get(new OwnedGroupKey(userId, groupId));
        if (Objects.isNull(glp1GroupEntity)) {
            throw new NotFoundException(ExceptionConstants.GLP1_GROUP_NOT_FOUND);
        }
        return glp1GroupEntity;
    }
}
```

사용자와 그룹 id 를 둘 다 키로 비교합니다. 그래서 서비스가 인자 순서를 바꾸거나 다른 사용자의 그룹을 조회하면 `NotFoundException` 이 나서 테스트가 깨집니다.

### 3-2. `SpyPushReservationClient`

Spy 내부에는 Mockito 를 쓰지 않고 JDK `List` 만 사용합니다.

```java
// package ...glp1.domain;
// import java.time.Instant;
// import java.util.ArrayList;
// import java.util.List;

class SpyPushReservationClient implements PushReservationClient {

    record ReserveNextInjectionCall(Long userId, Instant nextInjectionAt) {
    }

    private final List<ReserveNextInjectionCall> reserveNextInjectionCallList = new ArrayList<>();

    @Override
    public void reserveNextInjection(Long userId, Instant nextInjectionAt) {
        reserveNextInjectionCallList.add(new ReserveNextInjectionCall(userId, nextInjectionAt));
    }

    int getCallCount() {
        return reserveNextInjectionCallList.size();
    }

    ReserveNextInjectionCall getLastCall() {
        return reserveNextInjectionCallList.get(reserveNextInjectionCallList.size() - 1);
    }
}
```

### 3-3. `Glp1InjectionRecordCommandServiceTest`

경로는 `src/test/java/.../glp1/application/` 입니다. 기존 파일이 이미 있으면 먼저 읽고 `Edit` 로 추가합니다.

```java
// package ...glp1.application;
// import static org.assertj.core.api.Assertions.assertThat;
// import static org.assertj.core.api.Assertions.assertThatThrownBy;
// import java.time.Duration;
// import java.time.Instant;
// import java.util.Optional;
// import org.junit.jupiter.api.BeforeEach;
// import org.junit.jupiter.api.DisplayName;
// import org.junit.jupiter.api.Nested;
// import org.junit.jupiter.api.Test;
// (Glp1GroupEntity, Glp1InjectionRecordEntity, Glp1InjectionRecordInDto, BadRequestException,
//  FakeGlp1InjectionRecordRepository, FakeGlp1GroupQueryUseCase, SpyPushReservationClient 는 프로젝트 패키지 import)

class Glp1InjectionRecordCommandServiceTest {

    private static final Long USER_ID = 1L;
    private static final Long GROUP_ID = 7L; // USER_ID 와 다른 값: 인자 순서·매핑 오류를 잡기 위함
    private static final Instant CURRENT_AT = Instant.parse("2026-11-13T09:00:00Z");

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
        @DisplayName("본인 그룹에 과거 시각으로 등록하면 기록이 저장되고 다음 투여 푸시가 예약된다")
        void register_ownedGroupAndPastInjectedAt_savesRecordAndReservesPush() {
            // Given (가정값: 현재보다 1일 전 투여. 경계 바로 옆이 아닌 명확히 과거인 값)
            Instant injectedAt = CURRENT_AT.minus(Duration.ofDays(1));
            Glp1GroupEntity glp1GroupEntity = glp1GroupEntity();
            fakeGlp1GroupQueryUseCase.saveOwnedGroup(USER_ID, GROUP_ID, glp1GroupEntity);
            Glp1InjectionRecordInDto glp1InjectionRecordInDto = glp1InjectionRecordInDto(injectedAt);

            // When
            Long registeredId = glp1InjectionRecordCommandService.register(USER_ID, glp1InjectionRecordInDto);

            // Then: 반환 id 로 Fake 에서 다시 읽어 저장 상태를 본다 (반환값만 믿지 않는다)
            Optional<Glp1InjectionRecordEntity> glp1InjectionRecordEntityOptional =
                fakeGlp1InjectionRecordRepository.findById(registeredId);
            assertThat(glp1InjectionRecordEntityOptional).isPresent();
            Glp1InjectionRecordEntity savedGlp1InjectionRecordEntity = glp1InjectionRecordEntityOptional.get();
            assertThat(savedGlp1InjectionRecordEntity.getUserId()).isEqualTo(USER_ID);
            assertThat(savedGlp1InjectionRecordEntity.getGroup()).isSameAs(glp1GroupEntity);
            assertThat(fakeGlp1InjectionRecordRepository.findAll()).hasSize(1);

            assertThat(spyPushReservationClient.getCallCount()).isOne();
            assertThat(spyPushReservationClient.getLastCall().userId()).isEqualTo(USER_ID);
            assertThat(spyPushReservationClient.getLastCall().nextInjectionAt())
                .isEqualTo(savedGlp1InjectionRecordEntity.getNextInjectionAt());
        }

        @Test
        @DisplayName("투여 시각이 현재 시각보다 미래면 BadRequestException 이 발생하고 저장과 푸시 예약이 일어나지 않는다")
        void register_futureInjectedAt_throwsBadRequestAndSavesNothing() {
            // Given: 그룹은 소유 상태라 검증 분기까지 실제로 도달한다 (목표 경로 실행 보장)
            Instant futureInjectedAt = CURRENT_AT.plus(Duration.ofDays(1));
            fakeGlp1GroupQueryUseCase.saveOwnedGroup(USER_ID, GROUP_ID, glp1GroupEntity());
            Glp1InjectionRecordInDto glp1InjectionRecordInDto = glp1InjectionRecordInDto(futureInjectedAt);

            // When & Then
            assertThatThrownBy(() -> glp1InjectionRecordCommandService.register(USER_ID, glp1InjectionRecordInDto))
                .isInstanceOf(BadRequestException.class);

            assertThat(fakeGlp1InjectionRecordRepository.findAll()).isEmpty();
            assertThat(spyPushReservationClient.getCallCount()).isZero();
        }
    }

    private Glp1GroupEntity glp1GroupEntity() {
        // 가정(A5): 기존 FakeGlp1GroupRepository 테스트나 Fixture 의 생성 방식을 그대로 따라 교체
        return Glp1GroupEntity.of(USER_ID, "주 1회 위고비");
    }

    private Glp1InjectionRecordInDto glp1InjectionRecordInDto(Instant injectedAt) {
        // 가정(A2): 실제 레코드 필드에 맞춰 교체. 기본값이 있는 필드는 기본값과 다른 값을 넣는다
        return new Glp1InjectionRecordInDto(GROUP_ID, injectedAt, CURRENT_AT);
    }
}
```

## 4. 설계 설명

**"깨뜨리면 실패하는가" 점검 (RR-12)**

| 일부러 깨뜨리는 변경 | 실패하는 테스트 |
|---|---|
| `isAfter` 검증 제거 | 예외 테스트 (예외 미발생) |
| `isAfter` 를 `isBefore` 로 반전 | 정상 테스트와 예외 테스트 모두 |
| `save` 인자의 userId 를 groupId 로 교체 | 정상 테스트 (`getUserId` 불일치) |
| 반환 id 를 엉뚱한 값으로 교체 | 정상 테스트 (`findById` 가 비어 있음) |
| 푸시 호출 제거 | 정상 테스트 (`callCount` 0) |
| 푸시에 다른 시각을 전달 | 정상 테스트 (`nextInjectionAt` 불일치) |
| 검증을 `save` 이후로 이동 | 예외 테스트 (`findAll` 이 비어 있지 않음) |

- **Mock 위임 테스트와의 차이**: `given(...).willReturn(entity)` 로 정답을 주입하면 서비스가 Repository 에 어떤 조건으로 요청하든 통과합니다. 위 구성은 Fake 에 실제로 저장하고 다시 읽으므로 이 문제가 없습니다.
- **경계값**: 현재 시각과 투여 시각을 1일 차이로 둡니다. 동일 시각은 `isAfter` 가 false 라 통과해야 하는데, 이 경계 케이스는 요청 범위 밖이라 넣지 않았습니다.
- **스킬 컨벤션 준수**: 메서드명은 영어(`register_조건_결과`), `@DisplayName` 은 한글, 변수명은 `glp1InjectionRecordCommandService`, `registeredId`, `...At`, `...EntityList` 형태입니다. `var`, FQCN, `service`·`result` 변수명, `any()` 는 쓰지 않았고, 검증은 AssertJ 만 사용합니다. 클래스는 `@Nested` 로 메서드별 그룹핑합니다.

## 5. 실행 계획

아래 단계는 실행하지 않았고, 구현 시 이 순서로 진행합니다.

1. 현황 확인 (가정 A1~A6 해소)
   - `git status --short <테스트 파일 경로>` 로 미커밋 변경을 확인합니다 (DW-1).
   - `find . -name "Fake*"` 와 `FakeGlp1InjectionRecordRepository` 를 읽어 `findById` / `findAll` / id 채번 여부를 확인합니다.
   - `Glp1InjectionPlanCommandServiceTest` 를 읽고, `Glp1GroupEntity` 생성 Fixture, `Glp1InjectionRecordInDto` 생성자, `PushReservationClient`·`Glp1GroupQueryUseCase` 인터페이스를 확인합니다.
2. 파일 작성
   - Fake 와 Spy 를 신규 파일로 추가합니다.
   - 테스트 파일이 이미 있으면 읽은 뒤 `Edit` 로 추가하고, 없으면 신규 작성합니다 (DW-3).
3. 포맷과 실행
   - `./gradlew :{module}:spotlessApply`
   - `./gradlew :{module}:test --tests Glp1InjectionRecordCommandServiceTest`
4. 변이 확인: 위 표의 변경 2~3개를 서비스에 임시로 적용해 테스트가 실패하는지 본 뒤 원복합니다.
5. `python3 forge/common/review-lint.py` 를 실행해 위반 0건을 확인하고, 확인 항목은 해당 여부를 판단합니다.
6. `git status` 와 `git log <base>..HEAD --name-only` 로 의도치 않은 삭제나 변경이 없는지 확인합니다 (DW-5).

## 6. Self-check 요약

| # | 항목 | 결과 |
|---|---|---|
| 1~2 | 계층 식별(Application)과 방식(Fake + Spy) | PASS |
| 4 | `@DisplayName` 한글 | PASS |
| 5 | 테스트 통과 | 미실행 (4단계에서 확인) |
| 11 | FQCN 없음 | PASS (import 줄은 주석 표기) |
| 17 | infra 구현체 참조 없음 | PASS |
| 19 | Repository·UseCase 에 `@Mock` 없음 | PASS |
| 20 | 깨뜨리면 실패, 저장 미호출 확인 | PASS |
| 21 | `review-lint.py` | 미실행 (5단계) |

## 7. 남은 리스크

- 가정 A1~A6 이 틀리면 컴파일 오류가 납니다. 위의 수정 지점은 헬퍼 한두 곳에 모여 있습니다.
- 예외 테스트는 `BadRequestException` 타입만 확인합니다. 이 흐름에서 다른 `BadRequestException` 은 나오지 않으므로 지금은 충분합니다. 에러 코드 게터가 있으면 `GLP1_FUTURE_INJECTION` 까지 단언하는 것이 더 단단합니다.
- 범위 밖 관찰(SC-1)로, 푸시 예약이 `@Transactional` 안에서 `save` 뒤에 호출됩니다. 푸시 예약이 예외를 던지면 저장이 롤백되고, 외부 예약은 성공했는데 커밋이 실패하는 경우는 Fake 와 Spy 로 재현되지 않습니다. 요청하지 않았으므로 테스트에 넣지 않았습니다.
- 미소유 그룹이면 `NotFoundException` 이 나는 경로 테스트는 요청 범위(2개) 밖이라 넣지 않았습니다. Fake 가 이미 이 동작을 구현하므로 추가 비용은 작습니다. 원하시면 넣겠습니다.
