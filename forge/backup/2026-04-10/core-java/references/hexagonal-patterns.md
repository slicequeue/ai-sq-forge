# 헥사고날 아키텍처 코드 패턴

- [UseCase (Port In)](#usecase-port-in)
- [Port Out](#port-out)
- [Service (UseCase 구현체)](#service-usecase-구현체)
- [Persistence Adapter (Port Out 구현체)](#persistence-adapter-port-out-구현체)
- [Service 테스트 (Fake Port)](#service-테스트-fake-port)

---

## UseCase (Port In)

단일 메서드 인터페이스:

```java
// command/application/coupon/port/in/CreateCouponUseCase.java
public interface CreateCouponUseCase {
    Long create(CreateCouponCommand command);
}

// command/application/coupon/port/in/CreateCouponCommand.java
public record CreateCouponCommand(String name, Integer count) {
    public CouponEntity toEntity() {
        return CouponEntity.of(name, count);
    }
}
```

UseCase 반환 타입:

| UseCase 유형 | 반환 타입 |
|-------------|----------|
| 생성(Create) | Long (생성된 ID) 또는 {Action}{Domain}Result |
| 변경(Update) | void 또는 {Action}{Domain}Result |
| 단건 조회(Find) | Optional<{Domain}Result> |
| 목록 조회(Search) | List<{Domain}Result> 또는 Page<{Domain}Result> |

## Port Out

행위 기반 인터페이스 분리:

```java
// command/application/coupon/port/out/SaveCouponPort.java
public interface SaveCouponPort {
    Long save(CouponEntity coupon);
}

// command/application/coupon/port/out/FindCouponPort.java
public interface FindCouponPort {
    Optional<CouponEntity> findById(Long id);
}

// command/application/coupon/port/out/UpdateCouponPort.java
public interface UpdateCouponPort {
    void update(CouponEntity coupon);
}

// command/application/coupon/port/out/DeleteCouponPort.java
public interface DeleteCouponPort {
    void deleteById(Long id);
}

// command/application/coupon/port/out/LoadCouponPort.java
public interface LoadCouponPort {
    CouponEntity loadById(Long id);  // 없으면 예외
}
```

Port Out 네이밍 규칙:

| 접두사 | 의미 | 메서드 |
|--------|------|--------|
| Save{Domain}Port | 저장 | save() |
| Find{Domain}Port | 조회 (Optional) | findById(), findByName() |
| Load{Domain}Port | 조회 (예외) | loadById() |
| Update{Domain}Port | 수정 | update() |
| Delete{Domain}Port | 삭제 | deleteById() |

## Service (UseCase 구현체)

```java
@Service
@Transactional
@RequiredArgsConstructor
class CreateCouponService implements CreateCouponUseCase {
    private final SaveCouponPort saveCouponPort;

    @Override
    public Long create(CreateCouponCommand command) {
        CouponEntity coupon = command.toEntity();
        return saveCouponPort.save(coupon);
    }
}
```

## Persistence Adapter (Port Out 구현체)

```java
@Component
@RequiredArgsConstructor
class CouponPersistenceAdapter implements SaveCouponPort, FindCouponPort, UpdateCouponPort {
    private final CouponCommandRepository couponCommandRepository;

    @Override
    public Long save(CouponEntity coupon) {
        CouponJpaEntity saved = couponCommandRepository.save(CouponJpaEntity.fromDomain(coupon));
        return saved.getId();
    }

    @Override
    public Optional<CouponEntity> findById(Long id) {
        return couponCommandRepository.findById(id).map(CouponJpaEntity::toDomain);
    }

    @Override
    public void update(CouponEntity coupon) {
        couponCommandRepository.save(CouponJpaEntity.fromDomain(coupon));
    }
}
```

## Service 테스트 (Fake Port)

```java
class CreateCouponServiceTest {
    private CreateCouponService createCouponService;
    private FakeCouponPersistencePort fakeCouponPersistencePort;

    @BeforeEach
    void setUp() {
        fakeCouponPersistencePort = new FakeCouponPersistencePort();
        createCouponService = new CreateCouponService(fakeCouponPersistencePort);
    }

    @AfterEach
    void tearDown() { fakeCouponPersistencePort.clear(); }

    @DisplayName("쿠폰 생성 요청을 하면 쿠폰이 저장된다")
    @Test
    void create_savesCoupon() {
        // Given
        CreateCouponCommand command = CreateCouponCommandFixture.create();
        // When
        createCouponService.create(command);
        // Then
        assertThat(fakeCouponPersistencePort.count()).isEqualTo(1);
    }
}
```
