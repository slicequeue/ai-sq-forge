# 계층별 공통 코드 패턴

- [Domain Entity](#domain-entity)
- [Domain VO / 일급 컬렉션](#domain-vo--일급-컬렉션)
- [Domain 예외](#domain-예외)
- [Presentation / Adapter In](#presentation--adapter-in)
- [Infrastructure / Adapter Out (JPA Entity)](#infrastructure--adapter-out-jpa-entity)
- [Scheduler / Event Consumer Adapter](#scheduler--event-consumer-adapter)
- [외부 연동 유형별 구조](#외부-연동-유형별-구조)

---

## Domain Entity

- record 금지 (class만 사용), JPA 어노테이션 없음
- private 생성자 + 팩토리 메서드 (of), @Setter 금지
- 상태 변경: change{Field}(), 비즈니스 행위: expire(), decreaseRemainCount()
- 비즈니스 규칙 위반 시 도메인 예외 throw
- copy & paste 가능: 다른 프로젝트에 복사해도 컴파일 가능
- Domain이 의존 가능한 라이브러리: lombok, java.time, 자체 공통 라이브러리
- 금지: jakarta.validation, Spring, JPA 등 프레임워크

```java
// command/domain/coupon/CouponEntity.java
public class CouponEntity {
    private Long id;
    private String name;
    private Integer remainCount;
    private CouponStatus status;

    // private 생성자 - 외부 직접 생성 금지
    private CouponEntity(Long id, String name, Integer remainCount, CouponStatus status) {
        this.id = id;
        this.name = name;
        this.remainCount = remainCount;
        this.status = status;
    }

    // 팩토리 메서드 - 생성 시 검증
    public static CouponEntity of(String name, Integer count) {
        validateName(name);
        validateCount(count);
        return new CouponEntity(null, name, count, CouponStatus.ACTIVE);
    }

    public static CouponEntity of(Long id, String name, Integer remainCount, CouponStatus status) {
        return new CouponEntity(id, name, remainCount, status);
    }

    // 비즈니스 메서드 - 도메인 규칙을 Domain에서 판단
    public void decreaseRemainCount() {
        if (this.remainCount <= 0) {
            throw new CouponNotRemainException();
        }
        this.remainCount--;
    }

    public void expire() {
        if (this.status == CouponStatus.EXPIRED) {
            throw new CouponAlreadyExpiredException(this.id);
        }
        this.status = CouponStatus.EXPIRED;
    }

    public boolean isUsable() {
        return this.status == CouponStatus.ACTIVE && this.remainCount > 0;
    }

    // 상태 변경: change{Field}()
    public void changeName(String name) {
        validateName(name);
        this.name = name;
    }

    // 자기 검증
    private static void validateName(String name) {
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("쿠폰 이름은 필수입니다");
        }
    }

    private static void validateCount(Integer count) {
        if (count == null || count < 1) {
            throw new IllegalArgumentException("수량은 1 이상이어야 합니다");
        }
    }

    // Getter만 허용 (@Getter 사용 시 이 메서드들은 Lombok이 생성)
    public Long getId() { return id; }
    public String getName() { return name; }
    public Integer getRemainCount() { return remainCount; }
    public CouponStatus getStatus() { return status; }
}
```

## Domain VO / 일급 컬렉션

- VO: record 허용 (값의 동일성이 곧 객체의 동일성)
- 일급 컬렉션: record 금지 (class만 사용), 복수형 네이밍 ({Domain}s)
- Domain Service: 안티패턴에 가까움, 최소 사용, 순수 Java 클래스

record compact constructor 검증:

```java
public record CreateCouponCommand(String name, Integer count) {
    public CreateCouponCommand {
        if (name == null || name.isBlank()) {
            throw new IllegalArgumentException("name은 필수입니다");
        }
        if (count == null || count < 1) {
            throw new IllegalArgumentException("count는 1 이상이어야 합니다");
        }
    }
}
```

## Domain 예외

```java
// support/exception/BusinessException.java
@Getter
public class BusinessException extends RuntimeException {
    private final String errorCode;
    public BusinessException(String errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
    }
}

// support/exception/coupon/CouponNotRemainException.java
public class CouponNotRemainException extends BusinessException {
    public CouponNotRemainException() {
        super("COUPON_NOT_REMAIN", "쿠폰 잔여 수량이 없습니다");
    }
}
```

HTTP 상태코드 매핑은 GlobalExceptionHandler에서 처리. Exception에 HTTP 상태코드를 포함하지 않는다.

## Presentation / Adapter In

Web DTO 역할:
- Request: Swagger 어노테이션 + validation + toCommand()/toInDto() 변환
- Response: Swagger 어노테이션 + 화면 표시값 변환 (Enum -> 한글, 날짜 포맷, 금액 포맷)

```java
public record CreateCouponRequest(
    @Schema(description = "쿠폰 이름", example = "봄맞이 할인 쿠폰")
    @NotBlank String name,
    @Schema(description = "발급 수량", example = "100")
    @Min(1) Integer count
) {
    public CreateCouponCommand toCommand() { return new CreateCouponCommand(name, count); }  // 헥사고날
    public CreateCouponInDto toInDto() { return new CreateCouponInDto(name, count); }         // 4-Tier
}
```

## Infrastructure / Adapter Out (JPA Entity)

Domain Entity <-> JPA Entity 변환:

```java
@Entity
@Table(name = "coupon")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class CouponJpaEntity extends BaseTimeJpaEntity {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name;
    private Integer remainCount;
    @Enumerated(EnumType.STRING)
    private CouponStatus status;

    @Builder
    private CouponJpaEntity(String name, Integer remainCount, CouponStatus status) {
        this.name = name;
        this.remainCount = remainCount;
        this.status = status;
    }

    public static CouponJpaEntity fromDomain(CouponEntity coupon) {
        return CouponJpaEntity.builder()
            .name(coupon.getName())
            .remainCount(coupon.getRemainCount())
            .status(coupon.getStatus())
            .build();
    }

    public CouponEntity toDomain() {
        return CouponEntity.of(id, name, remainCount, status);
    }
}
```

## Scheduler / Event Consumer Adapter

Scheduler:

```java
// command/adapter/in/scheduler/ExpireCouponScheduler.java (헥사고날)
@Slf4j
@Component
@RequiredArgsConstructor
class ExpireCouponScheduler {
    private final ExpireCouponUseCase expireCouponUseCase;

    @Scheduled(cron = "0 0 0 * * *")
    void expireOldCoupons() {
        log.info("[Scheduler] 만료 대상 쿠폰 처리 시작");
        expireCouponUseCase.expireAll();
    }
}
```

Event Consumer:

```java
// command/adapter/in/event/MemberCreatedEventConsumer.java (헥사고날)
@Slf4j
@Component
@RequiredArgsConstructor
class MemberCreatedEventConsumer {
    private final GrantWelcomeCouponUseCase grantWelcomeCouponUseCase;

    @KafkaListener(topics = "member-created", groupId = "coupon-service")
    void onMemberCreated(MemberCreatedMessage message) {
        log.info("[Event] 회원 생성 이벤트 수신 - memberId: {}", message.memberId());
        grantWelcomeCouponUseCase.grant(new GrantWelcomeCouponCommand(message.memberId()));
    }
}
```

Scheduler/Event Consumer는 Presentation/Adapter In의 한 종류다. UseCase(헥사고날) 또는 Service/Facade(4-Tier)를 주입받아 위임만 수행한다. 비즈니스 로직을 포함하지 않는다.

## 외부 연동 유형별 구조

| 유형 | 헥사고날 (Port + Adapter) | 4-Tier |
|------|-------------------------|--------|
| JPA 영속화 | Save{Domain}Port -> {Domain}PersistenceAdapter | {Domain}Repository -> {Domain}RepositoryImpl |
| 외부 API | {Action}{Domain}Port -> {Service}{Action}{Domain}Adapter | {Service}{Domain}Client |
| 메시징 | Publish{Event}Port -> Kafka{Event}Adapter | Kafka{Event}Publisher |
| 캐시 | Cache{Domain}Port -> Redis{Domain}Adapter | Redis{Domain}Cache |
