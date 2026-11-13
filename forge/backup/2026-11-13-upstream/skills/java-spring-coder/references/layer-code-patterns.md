# 계층별 상세 구현 패턴

- [Domain Entity 상세](#domain-entity-상세)
- [Domain VO / 일급 컬렉션](#domain-vo--일급-컬렉션)
- [Domain 예외](#domain-예외)
- [JPA Entity 상세](#jpa-entity-상세)
- [Client / ClientService 패턴](#client--clientservice-패턴)
- [ThreadLocal 유틸리티](#threadlocal-유틸리티)
- [Scheduler / Event Consumer](#scheduler--event-consumer)
- [환경변수 설정](#환경변수-설정)
- [시큐리티 경로 등록](#시큐리티-경로-등록)
- [이미지 업로드](#이미지-업로드)

---

## Domain Entity 상세

### 구조 원칙

```java
public class CouponCodeEntity {
    // 1. 필드 — final 권장, not-null은 primitive, nullable은 Wrapper
    private final Long id;
    private final long discountAmount;     // not-null → primitive
    private final LocalDateTime usedAt;    // nullable → Wrapper

    // 2. 생성자 — private/package-private + of() 팩토리
    private CouponCodeEntity(Long id, long discountAmount, LocalDateTime usedAt) { ... }

    public static CouponCodeEntity of(long discountAmount) {
        return new CouponCodeEntity(null, discountAmount, null);
    }

    // 3. 상태 변경 메서드 — 새 인스턴스 반환 (불변)
    public CouponCodeEntity redeem(long userId, LocalDateTime at) { ... }

    // 4. 비즈니스 질의 메서드
    public boolean isUsed() { return usedAt != null; }
    public boolean isExpired(LocalDateTime now) { ... }
}
```

### Domain Entity가 의존할 수 있는 것

| 허용 | 금지 |
|------|------|
| `java.time.*` | `jakarta.persistence.*` (JPA) |
| `java.util.*` | `org.springframework.*` (Spring) |
| Lombok (`@Getter` 등) | `jakarta.validation.*` (Bean Validation) |
| 내부 common 라이브러리 | 다른 레이어 클래스 |

### 상태 변경 메서드 패턴

```java
// ✅ Rich Domain — Entity가 비즈니스 로직 소유
public CouponCodeEntity redeem(long userId, LocalDateTime redeemedAt) {
    if (this.usedAt != null) {
        throw new IllegalStateException("이미 사용된 쿠폰입니다.");
    }
    return new CouponCodeEntity(id, code, discountAmount, redeemedAt, userId);
}

// ❌ Anemic Domain — Service에서 판단
// if (coupon.getUsedAt() != null) throw ...;  ← 금지
// coupon.setUsedAt(now); coupon.setUsedBy(userId);  ← 금지
```

---

## Domain VO / 일급 컬렉션

### VO (Value Object) — record 허용

```java
// 값 동등성이 중요한 객체
public record Money(long amount, String currency) {
    public Money {  // compact constructor로 검증
        if (amount < 0) throw new IllegalArgumentException("금액은 0 이상이어야 합니다.");
    }
}
```

### 일급 컬렉션 — class 필수 (record 금지)

```java
// 복수형 이름 사용: CouponCodes (not CouponCodeList)
@Getter
public class CouponCodes {
    private final List<CouponCodeEntity> couponCodeEntityList;

    public CouponCodes(List<CouponCodeEntity> couponCodeEntityList) {
        this.couponCodeEntityList = List.copyOf(couponCodeEntityList);
    }

    public long totalDiscountAmount() {
        return couponCodeEntityList.stream()
                .mapToLong(CouponCodeEntity::getDiscountAmount)
                .sum();
    }

    public List<CouponCodeEntity> getUsedCouponCodeEntityList() {
        return couponCodeEntityList.stream()
                .filter(CouponCodeEntity::isUsed)
                .toList();
    }
}
```

---

## 예외 처리 패턴

### 원칙

- 커스텀 예외는 **Application Layer**에 배치
- `MoneyballException` 구현체를 상속, `ExceptionConstants`의 에러 코드 사용
- **기존 프로젝트의 예외 패턴을 반드시 확인** 후 일관되게 사용

### 예외 클래스 정의

```java
// pghd/{domain}/application/exception/CouponNotFoundException.java
public class CouponNotFoundException extends MoneyballException {
    public CouponNotFoundException() {
        super(ExceptionConstants.COUPON_NOT_FOUND);
    }
}
```

### 사용 패턴

```java
// ✅ 올바른 예외 처리 — MoneyballException + ExceptionConstants
couponCodeRepository.findByCode(code)
    .orElseThrow(CouponNotFoundException::new);

// ✅ 또는 직접 MoneyballException 사용
couponCodeRepository.findByCode(code)
    .orElseThrow(() -> new MoneyballException(ExceptionConstants.COUPON_NOT_FOUND));

// ❌ 금지 — 범용 예외 사용
// .orElseThrow(() -> new IllegalArgumentException("쿠폰을 찾을 수 없습니다."));
// .orElseThrow(() -> new RuntimeException("Not found"));
```

### i18n 메시지 조회

```java
// Application 이하에서 i18n 메시지 필요 시 — MessageUtil 사용
String message = MessageUtil.getMessage("coupon.not.found");

// ❌ 금지 — MessageSource 직접 주입
// private final MessageSource messageSource; ← 금지
```

---

## JPA Entity 상세

### 변환 메서드 규칙

| 메서드 | 방향 | 위치 |
|--------|------|------|
| `toEntity()` | JPA → Domain | JpaEntity 인스턴스 메서드 |
| `from(DomainEntity)` | Domain → JPA | JpaEntity 정적 메서드 |

```java
// RepositoryImpl에서 사용
@Override
public CouponCodeEntity save(CouponCodeEntity couponCodeEntity) {
    CouponCodeJpaEntity couponCodeJpaEntity = CouponCodeJpaEntity.from(couponCodeEntity);
    return couponCodeJpaRepository.save(couponCodeJpaEntity).toEntity();
}
```

### @Builder 위치

```java
// ✅ 생성자 레벨에만
@Builder
private CouponCodeJpaEntity(Long id, String code, long discountAmount) { ... }

// ❌ 클래스 레벨 금지
// @Builder  ← 금지
// public class CouponCodeJpaEntity { ... }
```

---

## Client / ClientService 패턴

### 판단 기준

| 상황 | 구현 방식 |
|------|-----------|
| 단순 변환 (1:1 매핑) | `*Client`가 `*ClientService` 직접 구현 |
| 가공 필요 (여러 소스 병합, enrichment) | `*ClientServiceImpl`(ACL) 별도 구현 |

### 단순 변환 — Client가 ClientService 직접 구현

```java
@Component
@RequiredArgsConstructor
public class S2sFoodClient implements FoodClientService {
    private final FoodQueryService foodQueryService; // 다른 도메인 서비스
    // 서비스 응답 → 도메인 모델 1:1 변환
}
```

### 가공 필요 — ClientServiceImpl(ACL) 분리

```java
// 내부 Client 분리
public class S2sPghdMealRecordClient { /* MealRecord 서비스 호출 */ }
public class S2sPghdImageClient { /* Image 서비스 호출 */ }

// ACL: 여러 Client 조합, enrichment 후 도메인 모델 반환
public class S2sMealRecordClientServiceImpl implements S2sMealRecordClientService {
    private final S2sPghdMealRecordClient mealRecordClient;
    private final S2sPghdImageClient imageClient;
    // MealRecord + Image 병합 → S2sPghdMealRecord 반환
}
```

### 빈 이름 충돌 방지

- S2S: `S2s` 접두사 (`S2sObesityRoutineRaceClient`)
- 도메인 간: 도메인명 접두사 (`PghdRoutineRaceClient`)
- 도메인 객체도 접두사: `S2sFood`, `S2sPghdMealRecord`

---

## ThreadLocal 유틸리티

| 유틸리티 | 사용 위치 | 주의 |
|---------|----------|------|
| `TimeZoneContext.getZoneId()` | **Controller만** | Service에는 `ZoneId` 파라미터로 전달 |
| `MessageUtil.getMessage(key)` | **Application 이하** | `MessageSource` 직접 주입 금지 |
| `LocaleContextHolder.getLocale()` | **Infrastructure만** (외부 API) | Service 파라미터로 `Locale` 전달 금지 |

```java
// ✅ Controller에서 ZoneId 얻어 Service로 전달
@GetMapping
public ResponseEntity<...> getRecords(@AuthenticationPrincipal long userId) {
    ZoneId zoneId = TimeZoneContext.getZoneId();
    return ResponseEntity.ok(service.getRecords(userId, zoneId));
}

// ❌ Service에서 TimeZoneContext 직접 호출 금지
```

---

## Scheduler / Event Consumer

```java
// Scheduler — Adapter In 역할, 비즈니스 로직 없이 위임만
@Component
@RequiredArgsConstructor
public class RaceAutoCompleteScheduler {
    private final RaceAutoCompleteService raceAutoCompleteService;

    @Scheduled(cron = "0 0 0 * * *")
    public void autoCompleteExpiredRaces() {
        raceAutoCompleteService.autoCompleteExpiredRaces();
    }
}
```

---

## 환경변수 설정

새 환경변수 추가 시 **4곳 모두 필수**:

| 파일 | 형식 | 환경 |
|------|------|------|
| `.env` | `KEY=value` | 로컬 |
| `application.yml` | `${env.KEY:기본값}` | 로컬 (spring-dotenv) |
| `application-jp-dev/stg/prd.yml` | `${KEY}` | Cloud Run (`env.` 없이) |

**흔한 실수**: `application.yml`에만 추가 → Cloud Run에서 빈 문자열 → 인증 실패

---

## 시큐리티 경로 등록

새 API 엔드포인트 추가 시 **SecurityConstants.airArray** 등록 필수.

- 파일: `api/src/main/java/.../common/config/SecurityConstants.java`
- 누락 시: 인증 필터 미적용 → `@AuthenticationPrincipal` null → NPE

---

## 이미지 업로드

- 모든 이미지 `MultipartFile`에 `@ValidImageFile` 필수
- 패턴 1 (직접 파라미터): `@Validated` 클래스 레벨 필수
- 패턴 2 (DTO 필드): `@Valid`만으로 충분
