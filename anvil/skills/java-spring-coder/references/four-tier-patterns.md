# 4-Tier 계층별 코드 패턴

- [Domain 계층](#domain-계층)
- [Infrastructure 계층](#infrastructure-계층)
- [Application 계층](#application-계층)
- [Web 계층](#web-계층)

---

## Domain 계층

### Domain Entity

```java
// pghd/{domain}/domain/CouponCodeEntity.java
@Getter
@ToString
@EqualsAndHashCode
public class CouponCodeEntity {

    private final Long id;                    // nullable → Wrapper
    private final String code;
    private final long discountAmount;        // not-null → primitive
    private final LocalDateTime usedAt;       // nullable → Wrapper
    private final Long usedBy;                // nullable → Wrapper

    // 생성자 — 외부에서 직접 호출 (10필드 미만이면 Builder 불필요)
    public CouponCodeEntity(Long id, String code, long discountAmount,
                            LocalDateTime usedAt, Long usedBy) {
        this.id = id;
        this.code = code;
        this.discountAmount = discountAmount;
        this.usedAt = usedAt;
        this.usedBy = usedBy;
    }

    // 정적 팩토리 메서드 — 새 인스턴스 생성
    public static CouponCodeEntity of(String code, long discountAmount) {
        return new CouponCodeEntity(null, code, discountAmount, null, null);
    }

    // 도메인 행위 — 비즈니스 로직은 Entity가 소유
    public CouponCodeEntity redeem(long userId, LocalDateTime redeemedAt) {
        if (this.usedAt != null) {
            throw new IllegalStateException("이미 사용된 쿠폰입니다.");
        }
        return new CouponCodeEntity(id, code, discountAmount, redeemedAt, userId);
    }

    // 도메인 질의 — Service에서 if 판단 대신 Entity 메서드 호출
    public boolean isUsed() {
        return usedAt != null;
    }

    public boolean isExpired(LocalDateTime now) {
        // 비즈니스 규칙은 여기에
        return false; // 실제 만료 로직
    }
}
```

**핵심**: Rich Domain. 상태 변경(`redeem`), 유효성 검증(`isUsed`), 비즈니스 판단을 모두 Entity가 소유.

### Domain Repository (Interface)

```java
// pghd/{domain}/domain/CouponCodeRepository.java
public interface CouponCodeRepository {
    Optional<CouponCodeEntity> findByCode(String code);
    Optional<CouponCodeEntity> findById(Long id);
    CouponCodeEntity save(CouponCodeEntity entity);
    void deleteById(Long id);
}
```

**규칙**: JPA 의존 없음. 도메인 모델만 사용. Spring Data 메서드(`findAll`, `count` 등) 무분별 노출 금지.

### Domain ClientService (Interface)

```java
// pghd/{domain}/domain/FoodClientService.java
// 다른 도메인 데이터 조회 시 — DIP
public interface FoodClientService {
    List<S2sFood> getAllFoodsByIds(List<Long> foodIdList);
}
```

---

## Infrastructure 계층

### JPA Entity

```java
// pghd/{domain}/infrastructure/CouponCodeJpaEntity.java
@Entity
@Table(name = "coupon_code")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class CouponCodeJpaEntity extends BaseTimeJpaEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    @Column(nullable = false, unique = true)
    private String code;

    @Column(nullable = false)  // primitive 타입은 @NotNull 생략 허용
    private long discountAmount;

    private LocalDateTime usedAt;
    private Long usedBy;

    @Builder  // 생성자 레벨에만 적용
    private CouponCodeJpaEntity(Long id, String code, long discountAmount,
                                LocalDateTime usedAt, Long usedBy) {
        this.id = id;
        this.code = code;
        this.discountAmount = discountAmount;
        this.usedAt = usedAt;
        this.usedBy = usedBy;
    }

    // JPA → Domain 변환
    public CouponCodeEntity toEntity() {
        return new CouponCodeEntity(id, code, discountAmount, usedAt, usedBy);
    }

    // Domain → JPA 변환
    public static CouponCodeJpaEntity from(CouponCodeEntity entity) {
        return CouponCodeJpaEntity.builder()
                .id(entity.getId())
                .code(entity.getCode())
                .discountAmount(entity.getDiscountAmount())
                .usedAt(entity.getUsedAt())
                .usedBy(entity.getUsedBy())
                .build();
    }
}
```

### JPA Repository

```java
// pghd/{domain}/infrastructure/CouponCodeJpaRepository.java
public interface CouponCodeJpaRepository extends JpaRepository<CouponCodeJpaEntity, Long> {
    Optional<CouponCodeJpaEntity> findByCode(String code);
}
```

### RepositoryImpl (3단계 패턴)

```java
// pghd/{domain}/infrastructure/CouponCodeRepositoryImpl.java
@Repository
@RequiredArgsConstructor
public class CouponCodeRepositoryImpl implements CouponCodeRepository {

    private final CouponCodeJpaRepository couponCodeJpaRepository;

    @Override
    public Optional<CouponCodeEntity> findByCode(String code) {
        return couponCodeJpaRepository.findByCode(code)
                .map(CouponCodeJpaEntity::toEntity);
    }

    @Override
    public Optional<CouponCodeEntity> findById(Long id) {
        return couponCodeJpaRepository.findById(id)
                .map(CouponCodeJpaEntity::toEntity);
    }

    @Override
    public CouponCodeEntity save(CouponCodeEntity entity) {
        CouponCodeJpaEntity jpaEntity = CouponCodeJpaEntity.from(entity);
        return couponCodeJpaRepository.save(jpaEntity).toEntity();
    }

    @Override
    public void deleteById(Long id) {
        couponCodeJpaRepository.deleteById(id);
    }
}
```

### Client (다른 도메인 호출)

```java
// pghd/{domain}/infrastructure/S2sFoodClient.java
// 단순 변환: Client가 ClientService 직접 구현
@Component
@RequiredArgsConstructor
public class S2sFoodClient implements FoodClientService {

    private final FoodQueryService foodQueryService; // 다른 도메인 서비스 호출

    @Override
    public List<S2sFood> getAllFoodsByIds(List<Long> foodIdList) {
        return foodQueryService.getAllFoodsByIds(foodIdList).stream()
                .map(S2sFood::from)
                .toList();
    }
}
```

**규칙**: Client는 다른 도메인의 **서비스(Application)**를 호출. 리포지토리/Infrastructure 직접 접근 금지.

---

## Application 계층

### Service

```java
// pghd/{domain}/application/CouponRedeemService.java
@Service
@RequiredArgsConstructor
@Log4j2
public class CouponRedeemService {

    // Domain 인터페이스만 참조 — RepositoryImpl 직접 import 금지
    private final CouponCodeRepository couponCodeRepository;

    @Transactional
    public CouponRedeemOutDto redeemCoupon(CouponRedeemInDto inDto) {
        CouponCodeEntity couponCodeEntity = couponCodeRepository
                .findByCode(inDto.code())
                .orElseThrow(() -> new MoneyballException(ExceptionConstants.COUPON_NOT_FOUND));

        // 비즈니스 로직은 Entity에 위임 — Service는 오케스트레이션만
        CouponCodeEntity redeemedCouponCodeEntity = couponCodeEntity.redeem(
                inDto.userId(), LocalDateTime.now());

        CouponCodeEntity savedCouponCodeEntity = couponCodeRepository.save(
                redeemedCouponCodeEntity);

        return CouponRedeemOutDto.from(savedCouponCodeEntity);
    }
}
```

**핵심**: Lean Service. `if (coupon.isUsed())` 같은 판단은 `redeem()` 내부에서 수행.

### DTO (record)

```java
// Application DTO — record 타입 필수
public record CouponRedeemInDto(
        String code,
        long userId
) {
    public static CouponRedeemInDto of(String code, long userId) {
        return new CouponRedeemInDto(code, userId);
    }
}

public record CouponRedeemOutDto(
        String code,
        long discountAmount,
        LocalDateTime usedAt
) {
    public static CouponRedeemOutDto from(CouponCodeEntity entity) {
        return new CouponRedeemOutDto(
                entity.getCode(), entity.getDiscountAmount(), entity.getUsedAt());
    }
}
```

---

## Web 계층

### Controller

```java
// pghd/{domain}/web/CouponRedeemController.java
@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/coupons")
@Tag(name = "쿠폰", description = "쿠폰 API")
public class CouponRedeemController {

    private final CouponRedeemService couponRedeemService;

    @PostMapping("/redeem")
    @Operation(summary = "쿠폰 사용")
    public ResponseEntity<CouponRedeemResponse> redeemCoupon(
            @AuthenticationPrincipal long userId,
            @RequestBody @Valid CouponRedeemRequest couponRedeemRequest) {

        ZoneId zoneId = TimeZoneContext.getZoneId(); // Controller에서만 호출
        CouponRedeemOutDto couponRedeemOutDto = couponRedeemService.redeemCoupon(
                couponRedeemRequest.toInDto(userId));

        return ResponseEntity.ok(CouponRedeemResponse.from(couponRedeemOutDto));
    }
}
```

### Web DTO (record)

```java
// Request — Swagger + Validation + toInDto 변환
public record CouponRedeemRequest(
        @Schema(description = "쿠폰 코드")
        @NotBlank String code
) {
    public CouponRedeemInDto toInDto(long userId) {
        return CouponRedeemInDto.of(code, userId);
    }
}

// Response — Swagger + 표시 변환
public record CouponRedeemResponse(
        @Schema(description = "쿠폰 코드")
        String code,
        @Schema(description = "할인 금액")
        long discountAmount,
        @Schema(description = "사용 시각")
        LocalDateTime usedAt
) {
    public static CouponRedeemResponse from(CouponRedeemOutDto couponRedeemOutDto) {
        return new CouponRedeemResponse(
                couponRedeemOutDto.code(),
                couponRedeemOutDto.discountAmount(),
                couponRedeemOutDto.usedAt());
    }
}
```
