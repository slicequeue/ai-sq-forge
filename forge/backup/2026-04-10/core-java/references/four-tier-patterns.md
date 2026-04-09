# 4-Tier 아키텍처 코드 패턴

- [Domain Repository 인터페이스](#domain-repository-인터페이스)
- [Service (단일 도메인)](#service-단일-도메인)
- [Facade (다중 도메인 조합)](#facade-다중-도메인-조합)
- [InDto / OutDto](#indto--outdto)
- [Infrastructure - Domain Repository 구현](#infrastructure---domain-repository-구현)
- [Service 테스트 (Fake Repository)](#service-테스트-fake-repository)
- [Facade 테스트 (여러 Fake 조합)](#facade-테스트-여러-fake-조합)

---

## Domain Repository 인터페이스

```java
// command/domain/coupon/CouponRepository.java
public interface CouponRepository {
    Long save(CouponEntity coupon);
    Optional<CouponEntity> findById(Long id);
    List<CouponEntity> findAllByStatus(CouponStatus status);
    void deleteById(Long id);
}
```

## Service (단일 도메인)

```java
@Service
@Transactional
@RequiredArgsConstructor
public class CouponService {
    private final CouponRepository couponRepository;

    public CreateCouponOutDto create(CreateCouponInDto inDto) {
        CouponEntity coupon = inDto.toEntity();
        Long id = couponRepository.save(coupon);
        return CreateCouponOutDto.from(
            CouponEntity.of(id, coupon.getName(), coupon.getRemainCount(), coupon.getStatus()));
    }

    public void decreaseRemainCount(Long couponId) {
        CouponEntity coupon = couponRepository.findById(couponId)
            .orElseThrow(() -> new CouponNotFoundException(couponId));
        coupon.decreaseRemainCount();
        couponRepository.save(coupon);
    }

    @Transactional(readOnly = true)
    public Optional<CouponOutDto> findById(Long id) {
        return couponRepository.findById(id).map(CouponOutDto::from);
    }
}
```

## Facade (다중 도메인 조합)

```java
@Service
@Transactional
@RequiredArgsConstructor
public class IssueCouponFacade {
    private final CouponService couponService;
    private final MemberService memberService;
    private final IssuanceHistoryService issuanceHistoryService;

    public IssueCouponOutDto issue(IssueCouponInDto inDto) {
        MemberEntity member = memberService.getById(inDto.memberId());
        CouponEntity coupon = couponService.getById(inDto.couponId());
        IssuanceHistory history = issuanceHistoryService
            .findByMemberAndCoupon(member.getId(), coupon.getId());

        // 비즈니스 판단은 Domain에서 수행 (Rich Domain Model)
        coupon.validateIssuable(member, history);
        coupon.decreaseRemainCount();
        couponService.save(coupon);
        issuanceHistoryService.record(member.getId(), coupon.getId());

        return IssueCouponOutDto.from(coupon, member);
    }
}
```

Facade / Service 분리 기준:

| 구분 | Facade | Service |
|------|--------|---------|
| 네이밍 | {Action}{Domain}Facade (액션 단위) | {Domain}Service (도메인 단위) |
| 역할 | 여러 Service를 조합하여 하나의 유스케이스 완성 | 단일 도메인 CRUD 및 비즈니스 메서드 호출 |
| 사용 시점 | 2개 이상 도메인 Service 조합 | 단일 도메인 로직 |
| 트랜잭션 | @Transactional (전체 묶음) | @Transactional (단일 도메인) |

- 단순 CRUD: Controller -> Service 직접 호출
- 복합 오케스트레이션: Controller -> Facade -> 여러 Service 조합

## InDto / OutDto

```java
// command/application/coupon/dto/in/CreateCouponInDto.java
public record CreateCouponInDto(String name, Integer count) {
    public CouponEntity toEntity() {
        return CouponEntity.of(name, count);
    }
}

// command/application/coupon/dto/out/CreateCouponOutDto.java
public record CreateCouponOutDto(Long id, String name, Integer remainCount) {
    public static CreateCouponOutDto from(CouponEntity entity) {
        return new CreateCouponOutDto(entity.getId(), entity.getName(), entity.getRemainCount());
    }
}
```

## Infrastructure - Domain Repository 구현

```java
// command/infrastructure/persistence/coupon/CouponRepositoryImpl.java
@Component
@RequiredArgsConstructor
class CouponRepositoryImpl implements CouponRepository {
    private final CouponJpaRepository couponJpaRepository;

    @Override
    public Long save(CouponEntity coupon) {
        CouponJpaEntity saved = couponJpaRepository.save(CouponJpaEntity.fromDomain(coupon));
        return saved.getId();
    }

    @Override
    public Optional<CouponEntity> findById(Long id) {
        return couponJpaRepository.findById(id).map(CouponJpaEntity::toDomain);
    }

    @Override
    public List<CouponEntity> findAllByStatus(CouponStatus status) {
        return couponJpaRepository.findAllByStatus(status).stream()
            .map(CouponJpaEntity::toDomain)
            .toList();
    }

    @Override
    public void deleteById(Long id) {
        couponJpaRepository.deleteById(id);
    }
}
```

## Service 테스트 (Fake Repository)

```java
class CouponServiceTest {
    private CouponService couponService;
    private FakeCouponRepository fakeCouponRepository;

    @BeforeEach
    void setUp() {
        fakeCouponRepository = new FakeCouponRepository();
        couponService = new CouponService(fakeCouponRepository);
    }

    @AfterEach
    void tearDown() { fakeCouponRepository.clear(); }

    @DisplayName("쿠폰 생성 요청을 하면 쿠폰이 저장된다")
    @Test
    void create_savesCoupon() {
        // Given
        CreateCouponInDto inDto = CreateCouponInDtoFixture.create();
        // When
        CreateCouponOutDto result = couponService.create(inDto);
        // Then
        assertThat(fakeCouponRepository.count()).isEqualTo(1);
        assertThat(result.name()).isEqualTo(inDto.name());
    }
}
```

## Facade 테스트 (여러 Fake 조합)

```java
class IssueCouponFacadeTest {
    private IssueCouponFacade issueCouponFacade;
    private FakeCouponRepository fakeCouponRepository;
    private FakeMemberRepository fakeMemberRepository;
    private FakeIssuanceHistoryRepository fakeHistoryRepository;

    @BeforeEach
    void setUp() {
        fakeCouponRepository = new FakeCouponRepository();
        fakeMemberRepository = new FakeMemberRepository();
        fakeHistoryRepository = new FakeIssuanceHistoryRepository();

        CouponService couponService = new CouponService(fakeCouponRepository);
        MemberService memberService = new MemberService(fakeMemberRepository);
        IssuanceHistoryService historyService = new IssuanceHistoryService(fakeHistoryRepository);

        issueCouponFacade = new IssueCouponFacade(couponService, memberService, historyService);
    }

    @DisplayName("발급 조건을 충족한 회원에게 쿠폰을 발급하면 잔여 수량이 감소한다")
    @Test
    void issue_whenEligible_decreasesRemainCount() {
        // Given
        MemberEntity member = MemberEntityFixture.createEligible();
        fakeMemberRepository.save(member);
        CouponEntity coupon = CouponEntityFixture.createWithId();
        fakeCouponRepository.save(coupon);
        // When
        issueCouponFacade.issue(new IssueCouponInDto(member.getId(), coupon.getId()));
        // Then
        CouponEntity saved = fakeCouponRepository.findById(coupon.getId()).orElseThrow();
        assertThat(saved.getRemainCount()).isEqualTo(CouponEntityFixture.DEFAULT_COUNT - 1);
    }
}
```
