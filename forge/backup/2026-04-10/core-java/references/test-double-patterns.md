# Test Double 패턴 (Fixture, Fake)

- [Test Double 선택 가이드](#test-double-선택-가이드)
- [BDD 스타일 테스트 규칙](#bdd-스타일-테스트-규칙)
- [Fixture 패턴](#fixture-패턴)
- [Fake Repository (4-Tier)](#fake-repository-4-tier)
- [Fake Persistence Port (헥사고날)](#fake-persistence-port-헥사고날)
- [Fake 외부 API 패턴](#fake-외부-api-패턴)
- [Controller 테스트](#controller-테스트)

---

## Test Double 선택 가이드

| 테스트 대상 | 권장 Test Double | Spring Context |
|------------|-----------------|----------------|
| Domain Entity | Fixture만 | 불필요 |
| Service 유닛 (헥사고날) | Fixture + Fake Port | 불필요 |
| Service 유닛 (4-Tier) | Fixture + Fake Repository | 불필요 |
| Facade 유닛 (4-Tier) | Fixture + 여러 Fake Repository | 불필요 |
| Controller | @MockitoBean + Fixture | @WebMvcTest |
| 통합 테스트 | 실제 Bean + Fixture | @SpringBootTest |
| 인수 테스트 | 실제 Bean + Fixture | @SpringBootTest(RANDOM_PORT) |

## BDD 스타일 테스트 규칙

- @DisplayName 한국어 필수
- Given-When-Then 주석 필수
- AssertJ만 사용, JUnit Jupiter Assertions 금지
- @Mock 남용 금지, Fake 사용 권장
- 한 테스트 = 하나의 검증
- 테스트 간 상태 공유 금지, @BeforeEach/@AfterEach로 초기화
- Thread.sleep() 금지, Awaitility 사용

## Fixture 패턴

```java
public class CouponEntityFixture {
    public static final Long DEFAULT_ID = 1L;
    public static final String DEFAULT_NAME = "테스트쿠폰";
    public static final Integer DEFAULT_COUNT = 100;

    public static CouponEntity create() {
        return CouponEntity.of(DEFAULT_NAME, DEFAULT_COUNT);
    }

    public static CouponEntity createWithId() {
        return CouponEntity.of(DEFAULT_ID, DEFAULT_NAME, DEFAULT_COUNT, CouponStatus.ACTIVE);
    }

    public static CouponEntity createWithZeroCount() {
        return CouponEntity.of(DEFAULT_ID, DEFAULT_NAME, 0, CouponStatus.ACTIVE);
    }

    public static CouponEntityBuilder builder() {
        return new CouponEntityBuilder();
    }

    public static class CouponEntityBuilder {
        private Long id = DEFAULT_ID;
        private String name = DEFAULT_NAME;
        private Integer count = DEFAULT_COUNT;
        private CouponStatus status = CouponStatus.ACTIVE;

        public CouponEntityBuilder id(Long id) { this.id = id; return this; }
        public CouponEntityBuilder name(String name) { this.name = name; return this; }
        public CouponEntityBuilder count(Integer count) { this.count = count; return this; }
        public CouponEntityBuilder status(CouponStatus status) { this.status = status; return this; }

        public CouponEntity build() {
            return CouponEntity.of(id, name, count, status);
        }
    }
}
```

## Fake Repository (4-Tier)

```java
public class FakeCouponRepository implements CouponRepository {
    private final Map<Long, CouponEntity> store = new HashMap<>();
    private final AtomicLong idGenerator = new AtomicLong(1);

    @Override
    public Long save(CouponEntity coupon) {
        Long id = (coupon.getId() != null) ? coupon.getId() : idGenerator.getAndIncrement();
        store.put(id, CouponEntity.of(id, coupon.getName(), coupon.getRemainCount(), coupon.getStatus()));
        return id;
    }

    @Override
    public Optional<CouponEntity> findById(Long id) {
        return Optional.ofNullable(store.get(id));
    }

    @Override
    public void deleteById(Long id) { store.remove(id); }

    // 테스트 헬퍼
    public void clear() { store.clear(); idGenerator.set(1); }
    public int count() { return store.size(); }
    public List<CouponEntity> findAll() { return List.copyOf(store.values()); }
}
```

## Fake Persistence Port (헥사고날)

```java
public class FakeCouponPersistencePort implements SaveCouponPort, FindCouponPort, UpdateCouponPort {
    private final Map<Long, CouponEntity> store = new HashMap<>();
    private final AtomicLong idGenerator = new AtomicLong(1);

    @Override
    public Long save(CouponEntity coupon) {
        Long id = (coupon.getId() != null) ? coupon.getId() : idGenerator.getAndIncrement();
        store.put(id, CouponEntity.of(id, coupon.getName(), coupon.getRemainCount(), coupon.getStatus()));
        return id;
    }

    @Override
    public Optional<CouponEntity> findById(Long id) {
        return Optional.ofNullable(store.get(id));
    }

    public void clear() { store.clear(); idGenerator.set(1); }
    public int count() { return store.size(); }
}
```

## Fake 외부 API 패턴

시나리오 제어 방식:

```java
public class FakeSettlementPort implements SettlementPort {
    private boolean shouldSucceed = true;
    private int callCount = 0;

    @Override
    public SettlementResult settle(SettlementRequest request) {
        callCount++;
        return shouldSucceed
            ? SettlementResult.success(request.getAmount())
            : SettlementResult.failure("정산 실패");
    }

    public void willSucceed() { this.shouldSucceed = true; }
    public void willFail() { this.shouldSucceed = false; }
    public int getCallCount() { return callCount; }
    public void reset() { shouldSucceed = true; callCount = 0; }
}
```

## Controller 테스트

@WebMvcTest + @MockitoBean 사용:

```java
@WebMvcTest(CouponCommandController.class)
class CouponCommandControllerTest {
    @Autowired MockMvc mockMvc;
    @MockitoBean CreateCouponUseCase createCouponUseCase;  // 헥사고날
    @Autowired ObjectMapper objectMapper;

    @DisplayName("쿠폰 생성 API를 호출하면 201 Created를 반환한다")
    @Test
    void create_returns201Created() throws Exception {
        // Given
        CreateCouponRequest request = new CreateCouponRequest("테스트쿠폰", 100);
        // When & Then
        mockMvc.perform(post("/api/v1/coupons")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(request)))
            .andExpect(status().isCreated());
    }
}
```
