---
description: Test Code 작성 가이드 (TDD, Fake Objects, Mocking)
globs: **/test/**/*.java
alwaysApply: false
---
# Testing Guidelines

## 1. Principles
- **TDD**: 실패하는 테스트 작성 -> 구현 -> 리팩토링 사이클을 따릅니다.
- **Naming**: 테스트 **메서드명은 영어**로 작성 (`[Method]_[Scenario]_[ExpectedResult]` 형식). **@DisplayName은 한글**로 작성하여 시나리오를 설명합니다.
- **Assertions**: `AssertJ` (`assertThat`) 사용. JUnit Assertions 금지.

## 2. Test Doubles Strategy

- **선택 순서 (골든 룰)**: **Fake** → **Stub/Spy** → **가능하면 Real**. 단위 테스트에서는 상태 기반 **Fake** 또는 행위 검증용 **Spy**를 우선하고, 통합·E2E에서는 가능하면 Real을 사용합니다.
- **상태 vs 행위 구분**: **상태(State)를 가지는 객체**(Repository, 저장소)는 **Fake**(메모리 상태 + 쿼리 로직)로 구현해 `save()` 후 최종 반환값만 검증합니다. **행위(Behavior)만 검증하는 객체**(외부 통신 Client 등)는 **Spy**(호출 이력 기록)로 구현해 `getCallCount()`, `getLastCall()`로 검증합니다.
- **Spring Context 최소화**: 단위 테스트는 **Spring Context를 띄우지 않고** 순수 JUnit + Fake/Spy로 작성합니다. Spring이 꼭 필요한 경우(Job/Step 연동 검증, `@WebMvcTest` 등)에만 `@SpringBootTest`, `@SpringBatchTest` 등을 사용합니다.
- **통합 테스트에서 @MockBean 최소화**: `@MockBean`이 많으면 컨텍스트 캐싱이 깨져 테스트가 느려집니다. **@TestConfiguration**으로 **@Bean @Primary** Fake/Spy를 등록해 POJO 테스트 더블을 주입하고, Mockito 의존을 줄입니다.
- **Mock (Mockito)**: 외부 API·복잡한 협력 객체가 꼭 필요할 때만 제한적으로 사용합니다.

## 2-1. Test Doubles 용어 (Fake vs Stub vs Spy)

| 용어 | 정의 | 사용처 | 검증 방식 |
|------|------|--------|-----------|
| **Fake** | 내부 상태(메모리)를 갖고, 실제와 유사한 로직(필터·조건·LIMIT/OFFSET)을 수행하는 객체 | Repository, 저장소 | `save(...)` 후 find 메서드 호출 → **반환값(상태)** 만 검증 |
| **Stub** | 반환값을 테스트에서 미리 설정하고, 호출 시 그대로 반환하는 객체 | 협력 객체의 반환만 중요할 때 | `setResult(...)` 후 호출 → 반환값 검증. (호출 검증은 선택) |
| **Spy** | 호출 이력(횟수·마지막 인자)을 기록해 행위 검증에 쓰는 객체 | 외부 통신·void 메서드 | `getCallCount()`, `getLastCall()` 로 검증. StubCapture 위임 권장 |

- **Fake**는 `setResult`로 정답을 주입하지 않고, **데이터를 넣어두면**(`save`) **스스로 조건을 적용해 반환**하도록 구현합니다. 테스트는 최종 **결과(상태)만** 검증해 리팩토링에 강합니다.
- **Spy**는 반환값이 없거나 부수 효과만 있을 때(예: Task enqueue) **StubCapture&lt;C,R&gt;** 로 호출 1회분을 record로 노출하고, 예외 설정이 필요하면 별도 필드(setXxxThrowException)를 둡니다.

## 2-2. Fake / Spy 구현 가이드

### Fake (상태 기반)

- **내부 저장소**: `List`/`Map` 등으로 레코드를 보관하고, `save(...)` 헬퍼로 테스트 데이터를 넣습니다.
- **find 메서드**: Stream 등으로 WHERE, LIMIT, OFFSET에 해당하는 로직을 구현합니다. 실제 SQL과 동작을 맞추되, **과도한 비즈니스 로직**은 넣지 않습니다.
- **테스트**: `fake.save(...)` → 서비스 호출 → **반환값만** assert. 호출 횟수·인자는 검증하지 않습니다.

### Spy (행위 검증, StubCapture 활용)

- **StubCapture&lt;C,R&gt;**: 호출 1회분 인자 `C`(record), 반환 `R`(void면 `Void`). `record(call)`, `getLastCall()`, `getCallCount()`.
- **테스트**: 결과(payload 등) 검증 후 빈 줄, 그 다음 `getEnqueueCallCount()`, `getLastEnqueueCall().taskType()` 등으로 호출 검증.

### 테스트 코드 패턴 (Given-When-Then)

- **설정**: `@BeforeEach`에서 `Fake/Spy xxx = new Xxx();` 후, 테스트 대상에 **생성자로** 주입.
- **Given**: Fake면 `fake.save(...)`; Spy만 쓰는 경우 Given 생략 가능.
- **When**: 대상 서비스/유스케이스 메서드 호출.
- **Then**: **결과(상태) 검증 우선**, 필요 시 빈 줄 뒤 **호출 검증**(Spy의 getCallCount, getLastCall).

### 피할 것

- Mockito verify로 호출 검증 (Spy의 getCallCount / getLastCall 사용).
- Fake에 `setResult`로 정답만 주입하고 내부 로직 없이 반환하는 방식 (진짜 Fake는 상태 + 로직).
- Spy/Fake 내부에 Mockito 사용. JDK 자료구조·StubCapture만 사용.
- 통합 테스트에서 불필요한 @MockBean 다수 사용 (@TestConfiguration + @Primary Fake/Spy로 대체).

## 3. Layered Testing
- **Domain/Application Unit Test**: **Spring 없이** Fake 객체를 활용하여 고속으로 실행. 생성자로 Fake를 주입하고, 검증은 Fake 상태·호출 이력으로 수행합니다.
- **Web Unit Test (`@WebMvcTest`)**: `MockMvc`와 `@MockBean`을 사용하여 컨트롤러 계층만 검증.
- **Integration/Acceptance Test**: `@SpringBootTest`나 `AcceptanceSupport`를 상속받아 시나리오 검증. H2 DB 사용.

## 3-1. 테스트에서 의존성 주입
- ✅ **필드 주입 지양**: `@WebMvcTest` 등 Spring 테스트에서도 `@Autowired` **필드 주입**은 지양합니다.
- ✅ **메서드 파라미터 주입 권장**: `@BeforeEach void setUp(@Autowired WebApplicationContext context)`처럼 **메서드 파라미터**에 `@Autowired`를 붙여 주입받습니다. 테스트 인스턴스 필드는 setUp에서 대입합니다.
- **이유**: 생성자/파라미터 주입은 필수 의존성이 명확하고, 테스트 가독성과 일관성(프로덕션 코드의 생성자 주입 원칙과 유사)을 유지합니다. `@MockBean`은 Spring이 테스트 컨텍스트에 등록하는 용도이므로 필드에 두는 것은 허용합니다.

## 4. E2E Test Guidelines
- **Test Configuration**: 테스트 설정은 별도 클래스로 분리합니다 (`@TestConfiguration` 사용).
- **Test Properties**: `@TestPropertySource`의 properties는 별도 파일로 분리합니다 (`application-{test-name}.properties`).
- **Test Naming**: 메서드명은 영어, `@DisplayName`은 한글 BDD 스타일("한다", "한다면" 등)로 작성합니다.
  - ✅ 좋은 예: 메서드 `createTemporaryAsleepRecord_withStartedAtAndSessionId_returnsId`, DisplayName `"startedAt과 asleepSessionId를 보내면 임시 레코드를 생성하고 id를 돌려준다"`
  - ❌ 나쁜 예: 메서드명 한글만 사용, DisplayName 생략
- **Entity Modification in Tests**: 테스트에서 엔티티 필드를 수정할 때는 네이티브 쿼리 대신 JPA `save()`와 Reflection을 활용합니다.
  ```java
  // ❌ 나쁜 예: 네이티브 쿼리 사용
  entityManager.createQuery("update Entity e set e.field = :value where e.id = :id")
      .setParameter("value", value)
      .setParameter("id", id)
      .executeUpdate();

  // ✅ 좋은 예: JPA save + Reflection
  Entity entity = repository.findById(id).orElseThrow();
  setField(entity, "field", value); // Reflection 헬퍼 메서드
  repository.save(entity);
  ```
- **Unnecessary Tests**: QueryDSL Q 클래스 초기화 테스트나 커버리지 목적만을 위한 테스트는 작성하지 않습니다. 실제 동작 검증에 집중합니다.

## 5. Infrastructure Layer Testing
- **AttributeConverter**: `AttributeConverter` 구현체는 예외 처리를 포함해야 합니다.
  ```java
  @Override
  public ZoneId convertToEntityAttribute(String dbData) {
    if (dbData == null) {
      return null;
    }
    try {
      return ZoneId.of(dbData);
    } catch (Exception e) {
      throw new IllegalArgumentException("Invalid time zone ID: " + dbData, e);
    }
  }
  ```

## 6. Example

**Fake (상태 기반)** — save 후 반환값만 검증:

```java
class UserQueryServiceTest {
    private FakeXxxRepository fakeRepository;
    private UserQueryService service;

    @BeforeEach
    void setUp() {
        fakeRepository = new FakeXxxRepository();
        service = new UserQueryService(fakeRepository);
    }

    @Test
    void fetchUserIds_returnsUsersMatchingDateAndVersion() {
        // Given
        String targetDate = "2025-01-15";
        fakeRepository.saveReportUser(1L, targetDate, 100, 90);
        fakeRepository.saveReportUser(2L, targetDate, 100, 90);

        // When
        List<Long> result = service.fetchUserIds(zoneId, 100, 90, 10, 0);

        // Then
        assertThat(result).containsExactlyInAnyOrder(1L, 2L);
    }
}
```

**Spy (행위 검증, StubCapture)** — enqueue 호출 검증:

```java
class ReportTaskServiceTest {
    private SpyAiInsightTaskClientService spyTaskClientService;
    private AiInsightReportTaskService service;

    @BeforeEach
    void setUp() {
        spyTaskClientService = new SpyAiInsightTaskClientService();
        service = new AiInsightReportTaskService(spyTaskClientService);
    }

    @Test
    void enqueueReportTask_sendsCorrectPayload() {
        // Given
        List<Long> userIds = List.of(1L, 2L);

        // When
        service.enqueueReportTask(userIds, Locale.JAPAN, ZoneId.of("Asia/Tokyo"), "glucose_daily", "2025-01-15");

        // Then
        var dto = (AiInsightReportTaskRequestInDto) spyTaskClientService.getLastEnqueueCall().payload();
        assertThat(dto.userIds()).containsExactlyInAnyOrder("1", "2");

        assertThat(spyTaskClientService.getEnqueueCallCount()).isOne();
        assertThat(spyTaskClientService.getLastEnqueueCall().taskType()).isEqualTo(CloudTaskType.AI_INSIGHT_REPORT);
    }
}
```
