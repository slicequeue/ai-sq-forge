# 테스트 더블 패턴

- [테스트 더블 선택 가이드](#테스트-더블-선택-가이드)
- [BDD 스타일 규칙](#bdd-스타일-규칙)
- [Fixture 패턴](#fixture-패턴)
- [Fake Repository (4-Tier)](#fake-repository-4-tier)
- [Spy (StubCapture)](#spy-stubcapture)
- [Fake External API](#fake-external-api)
- [계층별 테스트 패턴](#계층별-테스트-패턴)
- [피할 것](#피할-것)

---

## 테스트 더블 선택 가이드

| 테스트 대상 | Test Double | Spring 컨텍스트 | 검증 방식 |
|------------|-------------|----------------|-----------|
| Domain Entity | 없음 (직접 테스트) | 불필요 | 상태 검증 |
| Application Service | Fake Repository + Spy Client | 불필요 | 상태 + 행위 |
| Web Controller | `@MockBean` Service | `@WebMvcTest` | HTTP 응답 |
| Infrastructure Repository | 없음 (실 DB) | `@DataJpaTest` + Testcontainers | 쿼리 결과 |

**골든 룰**: Fake → Stub/Spy → Real. Mockito는 **마지막 수단**.

---

## BDD 스타일 규칙

### 필수 규칙

- **`@DisplayName`**: 한글 필수, 구체적 시나리오
- **Given-When-Then**: 주석으로 구분 필수
- **AssertJ only**: `assertThat()` 사용. JUnit `assertEquals` 금지
- **한 테스트 = 한 검증**: 여러 시나리오 섞지 않음
- **상태 공유 금지**: `@BeforeEach`에서 매번 초기화

### @DisplayName 규칙

```java
// ✅ 구체적 — 입력과 결과가 명확
@DisplayName("미사용 쿠폰 코드로 사용 처리하면 할인 금액과 사용 시각이 반환된다")
@DisplayName("존재하지 않는 쿠폰 코드 입력 시 CouponNotFoundException이 발생한다")
@DisplayName("이미 사용된 쿠폰을 재사용하면 IllegalStateException이 발생한다")

// ❌ 추상적 — 무엇을 검증하는지 불명확
@DisplayName("성공한다")
@DisplayName("실패한다")
@DisplayName("쿠폰 테스트")
```

### 테스트 메서드 네이밍

```java
// 영어: Method_Scenario_ExpectedResult
void redeemCoupon_validCode_returnsOutDto()
void redeemCoupon_usedCode_throwsIllegalStateException()
void redeemCoupon_notFoundCode_throwsCouponNotFoundException()
```

---

## Fixture 패턴

테스트 데이터 생성을 정적 팩토리로 관리한다.

```java
public class CouponCodeFixture {

    public static final String DEFAULT_CODE = "SAVE5000";
    public static final long DEFAULT_DISCOUNT_AMOUNT = 5000L;

    public static CouponCodeEntity create() {
        return new CouponCodeEntity(null, DEFAULT_CODE, DEFAULT_DISCOUNT_AMOUNT, null, null);
    }

    public static CouponCodeEntity createWithId(Long id) {
        return new CouponCodeEntity(id, DEFAULT_CODE, DEFAULT_DISCOUNT_AMOUNT, null, null);
    }

    public static CouponCodeEntity createUsed(Long id, long userId) {
        return new CouponCodeEntity(id, DEFAULT_CODE, DEFAULT_DISCOUNT_AMOUNT,
                LocalDateTime.now(), userId);
    }

    public static CouponCodeEntity createWithCode(String code) {
        return new CouponCodeEntity(null, code, DEFAULT_DISCOUNT_AMOUNT, null, null);
    }
}
```

---

## Fake Repository (4-Tier)

### 기본 구조 — HashMap 기반

```java
public class FakeCouponCodeRepository implements CouponCodeRepository {

    private final Map<Long, CouponCodeEntity> store = new HashMap<>();
    private final AtomicLong idGenerator = new AtomicLong(1L);

    @Override
    public Optional<CouponCodeEntity> findByCode(String code) {
        return store.values().stream()
                .filter(couponCodeEntity -> couponCodeEntity.getCode().equals(code))
                .findFirst();
    }

    @Override
    public Optional<CouponCodeEntity> findById(Long id) {
        return Optional.ofNullable(store.get(id));
    }

    @Override
    public CouponCodeEntity save(CouponCodeEntity couponCodeEntity) {
        Long id = couponCodeEntity.getId();
        if (id == null) {
            id = idGenerator.getAndIncrement();
        }
        CouponCodeEntity savedEntity = new CouponCodeEntity(
                id,
                couponCodeEntity.getCode(),
                couponCodeEntity.getDiscountAmount(),
                couponCodeEntity.getUsedAt(),
                couponCodeEntity.getUsedBy()
        );
        store.put(id, savedEntity);
        return savedEntity;
    }

    @Override
    public void deleteById(Long id) {
        store.remove(id);
    }

    // 테스트 헬퍼
    public void clear() {
        store.clear();
        idGenerator.set(1L);
    }

    public int count() {
        return store.size();
    }

    public List<CouponCodeEntity> findAll() {
        return List.copyOf(store.values());
    }
}
```

### Fake 핵심 원칙

- **`setResult` 금지** → 데이터를 `save()`로 넣고 `find*`에서 조건 적용하여 반환
- Stream으로 WHERE, LIMIT, OFFSET 로직 구현
- 과도한 비즈니스 로직은 넣지 않음
- **테스트는 최종 상태(반환값)만 검증** — 호출 검증은 Spy 역할

### Fake 기반 Service 테스트

```java
class CouponRedeemServiceTest {

    private FakeCouponCodeRepository fakeCouponCodeRepository;
    private CouponRedeemService couponRedeemService;

    @BeforeEach
    void setUp() {
        fakeCouponCodeRepository = new FakeCouponCodeRepository();
        couponRedeemService = new CouponRedeemService(fakeCouponCodeRepository);
    }

    @Test
    @DisplayName("유효한 쿠폰 코드로 사용 처리하면 할인 금액과 사용 시각이 반환된다")
    void redeemCoupon_validCode_returnsOutDtoWithDiscountAndUsedAt() {
        // Given
        fakeCouponCodeRepository.save(CouponCodeFixture.create());

        // When
        CouponRedeemOutDto couponRedeemOutDto = couponRedeemService.redeemCoupon(
                CouponRedeemInDto.of("SAVE5000", 42L));

        // Then
        assertThat(couponRedeemOutDto.discountAmount()).isEqualTo(5000L);
        assertThat(couponRedeemOutDto.usedAt()).isNotNull();
    }

    @Test
    @DisplayName("존재하지 않는 쿠폰 코드 입력 시 MoneyballException이 발생한다")
    void redeemCoupon_notFoundCode_throwsMoneyballException() {
        // When & Then
        assertThatThrownBy(() -> couponRedeemService.redeemCoupon(
                CouponRedeemInDto.of("INVALID", 1L)))
                .isInstanceOf(MoneyballException.class);
    }
}
```

---

## Spy (StubCapture)

### 행위 검증이 필요한 경우

```java
public class SpyTaskClientService implements TaskClientService {

    private final StubCapture<EnqueueCall, Void> enqueueCapture = new StubCapture<>();

    @Override
    public void enqueue(TaskType taskType, Object payload) {
        enqueueCapture.record(new EnqueueCall(taskType, payload));
    }

    public int getEnqueueCallCount() {
        return enqueueCapture.getCallCount();
    }

    public EnqueueCall getLastEnqueueCall() {
        return enqueueCapture.getLastCall();
    }

    public record EnqueueCall(TaskType taskType, Object payload) {}
}
```

### Spy 기반 테스트

```java
@Test
@DisplayName("리포트 태스크를 올바른 페이로드로 큐에 넣는다")
void enqueueReportTask_sendsCorrectPayload() {
    // Given
    List<Long> userIdList = List.of(1L, 2L);

    // When
    reportTaskService.enqueueReportTask(userIdList, "daily");

    // Then — 결과 검증
    SpyTaskClientService.EnqueueCall enqueueCall = spyTaskClientService.getLastEnqueueCall();
    ReportTaskPayload reportTaskPayload = (ReportTaskPayload) enqueueCall.payload();
    assertThat(reportTaskPayload.userIdList()).containsExactlyInAnyOrder(1L, 2L);

    // Then — 호출 검증 (빈 줄로 구분)
    assertThat(spyTaskClientService.getEnqueueCallCount()).isOne();
    assertThat(enqueueCall.taskType()).isEqualTo(TaskType.REPORT);
}
```

---

## Fake External API

### 시나리오 제어 패턴

```java
public class FakePaymentApiClient implements PaymentApiClient {

    private boolean willSucceed = true;
    private int callCount = 0;

    public void willSucceed() { this.willSucceed = true; }
    public void willFail() { this.willSucceed = false; }
    public int getCallCount() { return callCount; }

    @Override
    public PaymentResult charge(long amount) {
        callCount++;
        if (!willSucceed) {
            throw new PaymentFailedException("결제 실패");
        }
        return new PaymentResult("txn-" + callCount, amount);
    }
}
```

---

## 계층별 테스트 패턴

### Domain Entity — 순수 JUnit 5

```java
class CouponCodeEntityTest {

    @Test
    @DisplayName("미사용 쿠폰은 사용 처리 후 usedAt과 usedBy가 설정된다")
    void redeem_unusedCoupon_setsUsedAtAndUsedBy() {
        // Given
        CouponCodeEntity couponCodeEntity = CouponCodeFixture.createWithId(1L);
        LocalDateTime redeemedAt = LocalDateTime.of(2026, 4, 9, 12, 0);

        // When
        CouponCodeEntity redeemedCouponCodeEntity = couponCodeEntity.redeem(42L, redeemedAt);

        // Then
        assertThat(redeemedCouponCodeEntity.getUsedAt()).isEqualTo(redeemedAt);
        assertThat(redeemedCouponCodeEntity.getUsedBy()).isEqualTo(42L);
        assertThat(redeemedCouponCodeEntity.isUsed()).isTrue();
    }
}
```

### Web Controller — `@WebMvcTest` + `@MockBean`

```java
@WebMvcTest(CouponRedeemController.class)
class CouponRedeemControllerTest {

    private MockMvc mockMvc;

    @MockBean
    private CouponRedeemService couponRedeemService;

    @BeforeEach
    void setUp(@Autowired WebApplicationContext webApplicationContext) {
        mockMvc = MockMvcBuilders.webAppContextSetup(webApplicationContext).build();
    }

    @Test
    @DisplayName("POST /api/v1/coupons/redeem — 200 OK와 할인 금액을 반환한다")
    void redeemCoupon_validRequest_returnsOkWithDiscount() throws Exception {
        // Given
        CouponRedeemOutDto couponRedeemOutDto = new CouponRedeemOutDto(
                "SAVE5000", 5000L, LocalDateTime.now());
        given(couponRedeemService.redeemCoupon(any())).willReturn(couponRedeemOutDto);

        // When & Then
        mockMvc.perform(post("/api/v1/coupons/redeem")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"code\": \"SAVE5000\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.discountAmount").value(5000));
    }
}
```

### Infrastructure — `@DataJpaTest` + Testcontainers

```java
@DataJpaTest
@ActiveProfiles("test")
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class CouponCodeRepositoryImplTest {

    private CouponCodeRepositoryImpl couponCodeRepositoryImpl;

    @BeforeEach
    void setUp(@Autowired CouponCodeJpaRepository couponCodeJpaRepository) {
        couponCodeRepositoryImpl = new CouponCodeRepositoryImpl(couponCodeJpaRepository);
    }

    @Test
    @DisplayName("저장된 쿠폰을 코드로 조회하면 할인 금액이 일치한다")
    void findByCode_existingCode_returnsEntityWithMatchingDiscount() {
        // Given
        couponCodeRepositoryImpl.save(CouponCodeFixture.create());

        // When
        Optional<CouponCodeEntity> couponCodeEntityOptional =
                couponCodeRepositoryImpl.findByCode("SAVE5000");

        // Then
        assertThat(couponCodeEntityOptional).isPresent();
        assertThat(couponCodeEntityOptional.get().getDiscountAmount()).isEqualTo(5000L);
    }
}
```

---

## 피할 것

| 금지 | 대안 |
|------|------|
| `Mockito.verify()` 호출 검증 | Spy의 `getCallCount()` / `getLastCall()` |
| Fake에 `setResult`로 정답 주입 | `save()` 후 조건 적용 반환 |
| Spy/Fake 내부에 Mockito 사용 | JDK 자료구조 + StubCapture |
| 통합 테스트에서 `@MockBean` 다수 | `@TestConfiguration` + `@Primary` Fake/Spy |
| H2 DB | Testcontainers MySQL |
| `var` 키워드 | 명시적 타입 선언 |
| `assertEquals` | `assertThat` (AssertJ) |
| `@DisplayName("성공한다")` | 구체적 시나리오 기술 |
| `Thread.sleep()` | Awaitility 사용 |
| 커버리지 목적만의 테스트 | 실제 동작 검증에 집중 |
