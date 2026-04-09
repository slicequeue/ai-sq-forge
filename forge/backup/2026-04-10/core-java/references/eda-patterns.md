# EDA (Event-Driven Architecture) 코드 패턴

- [패키지 구조](#패키지-구조)
- [DomainEvent 인터페이스](#domainevent-인터페이스)
- [DomainEventPublisher 포트](#domaineventpublisher-포트)
- [Spring 구현체](#spring-구현체)
- [도메인 이벤트 정의](#도메인-이벤트-정의)
- [Service에서 이벤트 발행](#service에서-이벤트-발행)
- [@TransactionalEventListener 패턴](#transactionaleventlistener-패턴)
- [@Async 리스너 패턴](#async-리스너-패턴)

---

## 패키지 구조

```
common/
└── event/
    ├── DomainEvent.java                   # 도메인 이벤트 마커 인터페이스
    ├── DomainEventPublisher.java          # 이벤트 발행 포트 (인터페이스)
    └── infrastructure/
        └── SpringEventPublisher.java      # Spring 기반 이벤트 발행 구현체

command/
└── event/
    ├── coupon/
    │   ├── CouponCreatedEvent.java
    │   ├── CouponDeletedEvent.java
    │   └── listener/
    │       └── CouponEventListener.java
    └── member/
        ├── MemberCreatedEvent.java
        └── listener/
            └── MemberEventListener.java
```

## DomainEvent 인터페이스

```java
// common/event/DomainEvent.java
public interface DomainEvent {
    LocalDateTime occurredAt();

    default String eventType() {
        return this.getClass().getSimpleName();
    }

    default String domain() {
        String packageName = this.getClass().getPackage().getName();
        String[] parts = packageName.split("\\.");
        return parts.length > 0 ? parts[parts.length - 2] : "unknown";
    }
}
```

## DomainEventPublisher 포트

```java
// common/event/DomainEventPublisher.java
public interface DomainEventPublisher {
    void publish(DomainEvent event);
    void publishAll(List<DomainEvent> events);
}
```

## Spring 구현체

```java
// common/event/infrastructure/SpringEventPublisher.java
@Slf4j
@Component
@RequiredArgsConstructor
public class SpringEventPublisher implements DomainEventPublisher {
    private final ApplicationEventPublisher applicationEventPublisher;

    @Override
    public void publish(DomainEvent event) {
        log.debug("Publishing domain event: {} at {}", event.eventType(), event.occurredAt());
        applicationEventPublisher.publishEvent(event);
    }

    @Override
    public void publishAll(List<DomainEvent> events) {
        events.forEach(this::publish);
    }
}
```

## 도메인 이벤트 정의

```java
// command/event/coupon/CouponCreatedEvent.java
@Getter
@RequiredArgsConstructor
public class CouponCreatedEvent implements DomainEvent {
    private final Long couponId;
    private final String couponName;
    private final int totalQuantity;
    private final LocalDateTime occurredAt;

    public CouponCreatedEvent(Long couponId, String couponName, int totalQuantity) {
        this(couponId, couponName, totalQuantity, LocalDateTime.now());
    }

    @Override
    public LocalDateTime occurredAt() {
        return occurredAt;
    }
}
```

이벤트 네이밍:

| 이벤트 유형 | 패턴 | 예시 |
|------------|------|------|
| 생성 | {Domain}CreatedEvent | CouponCreatedEvent |
| 수정 | {Domain}UpdatedEvent | CouponUpdatedEvent |
| 삭제 | {Domain}DeletedEvent | CouponDeletedEvent |
| 상태 변경 | {Domain}{Action}Event | MemberCouponIssuedEvent |

## Service에서 이벤트 발행

```java
@Service
@Transactional
@RequiredArgsConstructor
class CreateCouponService implements CreateCouponUseCase {
    private final SaveCouponPort saveCouponPort;
    private final DomainEventPublisher eventPublisher;

    @Override
    public Long create(CreateCouponCommand command) {
        CouponEntity coupon = command.toEntity();
        Long id = saveCouponPort.save(coupon);

        eventPublisher.publish(new CouponCreatedEvent(
            id, coupon.getName(), coupon.getRemainCount()));

        return id;
    }
}
```

## @TransactionalEventListener 패턴

```java
// command/event/coupon/listener/CouponEventListener.java
@Slf4j
@Component
public class CouponEventListener {

    // 동기 처리 - 트랜잭션 커밋 후 실행
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleCouponCreated(CouponCreatedEvent event) {
        log.info("[이벤트] 쿠폰 생성됨 - 이름: {}, 수량: {}",
            event.getCouponName(), event.getTotalQuantity());
    }
}
```

@TransactionalEventListener Phase:

| Phase | 설명 | 사용 시나리오 |
|-------|------|-------------|
| AFTER_COMMIT | 트랜잭션 커밋 후 실행 (기본값) | 대부분의 경우 |
| AFTER_ROLLBACK | 롤백 후 실행 | 보상 트랜잭션 |
| AFTER_COMPLETION | 트랜잭션 완료 후 실행 | 커밋/롤백 무관 |
| BEFORE_COMMIT | 커밋 전 실행 | 커밋 전 검증 |

## @Async 리스너 패턴

```java
@Slf4j
@Component
public class MemberCouponEventListener {

    // 동기 처리
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleMemberCouponIssued(MemberCouponIssuedEvent event) {
        log.info("[이벤트] 쿠폰 발급됨 - 회원ID: {}, 쿠폰ID: {}",
            event.getMemberId(), event.getCouponId());
    }

    // 비동기 처리
    @Async
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleMemberCouponIssuedAsync(MemberCouponIssuedEvent event) {
        log.info("[이벤트-비동기] 통계 업데이트 - 회원ID: {}", event.getMemberId());
    }
}
```

이벤트 규칙:
- 이벤트에 비즈니스 로직 금지 (데이터만 담음)
- 이벤트 필드 불변성 (final + Getter만, @Setter 금지)
- DB 저장 후 이벤트 발행 (데이터 일관성)
- 리스너에서 DB 쓰기 시 별도 트랜잭션 (REQUIRES_NEW) 고려
