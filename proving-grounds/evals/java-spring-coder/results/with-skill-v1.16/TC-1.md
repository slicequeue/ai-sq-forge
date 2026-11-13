# TC-1 with-skill 응답 (v1.16)

쿠폰 사용(Redeem) API 를 TDD 계획서(Phase 1~4)대로 구현하는 시뮬레이션입니다. 실제 저장소가 없어 탐색·테스트·lint 는 "실행할 명령"과 "가정 결과"로 적었고, 모든 가정 결과는 `[가정]` 으로 표시했습니다. 어떤 파일도 쓰지 않았고 커밋하지 않았습니다.

---

## 0. 결론 요약

- 동작 모드: **A (TDD 전체 구현)**. Phase 1~4 를 한 번에 구현하고 테스트는 마지막에 1회 실행합니다.
- TDD 를 그대로 따르면 규칙에 어긋나거나 빠진 부분이 있어 **능동적으로 보정한 항목 5건**(3절)과 **승인이 필요한 항목 3건**(4절)이 있습니다. 승인 대기 항목은 구현을 확정하지 않고 선택지만 제시했습니다.
- 가장 큰 위험은 **동시 요청 시 쿠폰 이중 사용**입니다. TDD 설계(`findByCode` → `redeem` → `save`)만으로는 막을 수 없습니다. 4절 A 에서 선택지를 제시합니다.
- 커밋하지 않습니다. 사용자 요청 시에만 커밋합니다.

---

## 1. Phase 0 사전 확인 (실행 명령 + 가정 결과)

```bash
# 1) 작업 계획서 (모드 결정)
ls docs/tdd/ docs/plans/ 2>/dev/null
#   [가정] docs/tdd/coupon-redeem-tdd.md 존재 -> 모드 A

# 2) 규칙 로드 (스킬의 .claude/rules/ 에 해당)
#    01, 02, 03, 04, 05, 06, 08, 18, 19 를 Read (13~16 은 admin 전용이라 제외)

# 3) 현재 브랜치·작업 트리 상태 (DW-1, DW-2)
git branch --show-current
#   [가정] api/feat/coupon-redeem
git status --short pghd/coupon pasta-api/src/main/java/pghd/coupon pasta-api/src/test/java/pghd/coupon
#   [가정] 출력 없음 -> 새로 만드는 파일뿐이라 덮어쓰기 충돌 없음

# 4) 같은 도메인 기존 코드 (admin 여부 + 패턴)
find . -path "*pghd/coupon*" -name "*.java" | head -30
#   [가정] 없음 (신규 도메인). 대신 인접 도메인(glp1) 패턴을 참고: Instant 시각, ResponseEntity, 예외는 application/exception
grep -rn "class .*Exception extends \(NotFound\|Conflict\|BadRequest\)Exception" --include=*.java pasta-api shared | head
#   [가정] NotFoundException, ConflictException, BadRequestException 모두 shared 에 존재.
#          생성자 시그니처는 (ExceptionConstants 코드, 메시지 키, Object[] 인자)

# 5) DW-6 / SC-4: 신설할 식별자 전수 검색
grep -rn "COUPON_NOT_FOUND\|COUPON_ALREADY_USED\|error.coupon" --include=*.java --include=*.properties .
grep -rln "coupon_code" --include=*.sql --include=*.java .
#   [가정] 위 두 검색 모두 0건 -> ExceptionConstants·i18n 키·테이블 모두 신설 대상

# 6) JDK / 빌드
export JAVA_HOME=$(/usr/libexec/java_home -v 21) && java -version
#   [가정] openjdk 21

# 7) 보안 경로·기존 컨트롤러 테스트 패턴
grep -n "airArray" -A15 pasta-api/src/main/java/**/SecurityConstants.java
grep -rln "@WebMvcTest" pasta-api/src/test | head -3
grep -rln "@DataJpaTest" pasta-api/src/test | head -3
#   [가정] airArray 는 String[] 이며 인증 필요 경로 목록.
#          컨트롤러 테스트는 @WebMvcTest + @MockBean, Infra 테스트는 @DataJpaTest + @ActiveProfiles("test")
#          + @AutoConfigureTestDatabase(replace = NONE) (Testcontainers MySQL 은 test 프로파일 JDBC URL 로 기동)

# 8) 마이그레이션 최신 버전, Copyright 헤더 양식 (RR-11)
ls pasta-api/src/main/resources/db/migration | sort -V | tail -3
head -3 $(ls -d pasta-api/src/main/resources/db/migration/* | sort -V | tail -1)
#   [가정] 최신 V 번호 다음 값을 사용. 첫 줄은 "-- Copyright 2026 Kakao Healthcare Corp. All Rights Reserved."
```

### 작성 전 질문 5개 (RR-13, RR-14)

| # | 질문 | 답 |
|---|------|----|
| 1 | 이 한 건이 실패하면 사용자는 무엇을 보는가 | 단건 API 라 조립 응답이 없습니다. 실패 유형별로 404(코드 없음) / 409(이미 사용) / 400(입력 오류)을 내리고 틀린 성공 응답은 없습니다 |
| 2 | 외부 호출 성공 후 DB 저장 실패 | 외부 호출이 없습니다. 해당 없음 |
| 3 | 마스터 데이터가 null/0/음수 | `code` null 은 생성자 `requireNonNull`, 음수 `discountAmount` 는 생성자에서 거부합니다. 한 건의 이상 데이터는 그 쿠폰 요청 하나만 500 이 되고 다른 사용자에게 번지지 않습니다. `0` 은 허용되며 0 원 할인으로 응답합니다 (정책 질문으로 4절 C 에 남김) |
| 4 | 기존 경로 동작 변경 | 신규 엔드포인트라 기존 동작 변경 없음. PR 본문 "기존 동작 변경: 없음" 으로 명시 |
| 5 | 분기를 깨면 실패하는 테스트가 모든 진입 경로에 있는가 | 진입 경로는 POST 1개입니다. 미존재·이미 사용·정상·입력 오류를 각각 테스트합니다. 이미 사용 분기는 "저장소가 변하지 않음"까지 단언합니다 |

호출처 grep(Phase 0-9): 공용 계산기·헬퍼를 고치지 않으므로 해당 없음. 새 쿼리는 이 API 안에서만 실행됩니다 (`findByCode` 1회, `save` 1회).

---

## 2. 확인된 것 vs 가정한 것

| 구분 | 내용 |
|------|------|
| 확인된 것 (스킬·규칙 문서에서 읽음) | 4-Tier 구조, 패키지 경로, 네이밍, record/class 정책, Lombok 정책, 예외 계층 위치(`application/exception`), Fake 우선 테스트, `review-lint.py` 실행 의무, SecurityConstants airArray 등록 |
| 가정한 것 (저장소 없음) | `ConflictException` 존재 및 409 매핑, shared 예외 패키지 경로(`com.kakaohealthcare.moneyball.shared.exception`), `BaseTimeJpaEntity` 의 컬럼(`created_at`/`updated_at`, DATETIME(6)), `coupon_code` 테이블 부재, 글로벌 예외 핸들러가 `MoneyballException` 하위를 일괄 처리, CSRF 비활성(stateless), `@MockBean` 사용 관행, 시각 타입 `Instant` 관행 |
| 재평가 트리거 | 위 가정 중 grep 결과가 다르면 해당 파일의 import·상수·상태코드를 조정합니다 |

---

## 3. TDD 비판적 검증 (능동 보정·보고)

| # | TDD / 스킬 샘플 | 문제 | 이번 구현의 처리 |
|---|-----------------|------|------------------|
| 1 | Domain Repository 에 `findByCode`, `save` | 스킬 샘플은 `findById`·`deleteById` 까지 노출합니다. "Spring Data 메서드 무분별 노출 금지" 및 YAGNI | **TDD 명세대로 2개만** 둡니다 (Fake·Impl 도 2개) |
| 2 | 스킬 샘플이 `LocalDateTime.now()` 사용 | 시각 변수는 `Instant` + `At` 접미사 규칙과 어긋나고, 타임존 의존이 생깁니다 | `Instant`, 변수명 `currentAt`, 필드 `usedAt` |
| 3 | 도메인 `redeem()` 이 이미 사용된 쿠폰에서 예외 | domain 은 `ExceptionConstants`/HTTP 예외를 참조할 수 없습니다 (LAYER, 규칙 06) | 도메인은 불변식 보호용 `IllegalStateException`. 서비스는 `couponCodeEntity.isUsed()` 로 **위임 질의**한 뒤 `application/exception` 의 `CouponAlreadyUsedException`(409)을 던집니다. 판단 로직은 도메인이 소유하고 서비스는 분기만 합니다 |
| 4 | 엔티티 `@ToString` | 쿠폰 코드가 toString 에 평문으로 들어가 로그·예외 메시지로 새어 나갈 수 있습니다 (민감 정보 마스킹 규칙) | `code` 에 `@ToString.Exclude` |
| 5 | 도메인 엔티티 생성자 검증 | 스킬 규칙: NOT NULL 필드 `requireNonNull` 필수 | 생성자·`of()` 에 `requireNonNull`, 음수 할인액 거부, `usedAt`/`usedBy` 는 함께 null 이거나 함께 값이 있어야 한다는 불변식 추가 |

TDD 가 요구하지 않았지만 **동작에 필수라 포함한 것**: `ExceptionConstants` 2건, i18n 키 2건(4파일), 예외 클래스 2개, `CouponCodeFixture`, `FakeCouponCodeRepository`. 서비스 로그는 `[CouponRedeemService.redeemCoupon]` 접두사를 쓰고 쿠폰 코드와 userId 를 남기지 않으며 `couponCodeId` 만 남깁니다.

---

## 4. 승인이 필요한 항목 (SC-3, SC-4, SC-5 — 확정하지 않고 선택지 제시)

### A. 동시 요청 시 이중 사용 방지 (가장 중요)

두 요청이 동시에 `findByCode` 를 하면 둘 다 "미사용"으로 읽고 둘 다 `save` 합니다. 마지막 쓰기가 이겨서 **한 쿠폰이 두 번 사용된 것처럼 두 사용자에게 모두 성공이 내려갑니다.** 이번 구현은 TDD 명세대로 두고, 아래 선택지 중 승인을 받아 반영합니다. 단위 테스트(Fake)로는 이 문제를 재현할 수 없어 Testcontainers 동시성 테스트가 별도로 필요합니다.

| 선택지 | 변경 범위 | 장점 | 단점 |
|--------|-----------|------|------|
| 1. 조건부 UPDATE (`UPDATE coupon_code SET used_at=?, used_by=? WHERE code=? AND used_at IS NULL`, 영향 행 0 이면 이미 사용) | Domain Repository 에 메서드 추가 | 원자적이고 락 대기가 없습니다 | 벌크 연산이라 같은 트랜잭션 재조회 금지(RR-4), `clearAutomatically` 필요. 도메인 `redeem()` 과 이중 구조가 됩니다 |
| 2. 비관적 락 (`@Lock(PESSIMISTIC_WRITE)` 조회로 교체) | Repository 메서드 1개 추가 또는 `findByCode` 의미 변경 | 현재 `redeem()` 구조를 유지합니다 | 락 대기, 데드락 가능성 점검 필요 |
| 3. 낙관적 락 (`@Version` 컬럼) | **스키마 컬럼 추가** | 구현이 가장 단순합니다 | 컬럼 추가(SC-3), 충돌 시 예외 번역(`ObjectOptimisticLockingFailureException` → 409) 필요 |

권장: 1번 또는 2번. 스키마 추가가 없습니다.

### B. `coupon_code` 테이블 마이그레이션 (TDD 에 누락)

TDD Phase 2 는 JPA 엔티티만 있고 DDL 이 없습니다. Testcontainers 기반 Infra 테스트는 Flyway 스키마가 있어야 통과합니다. 새 테이블 도입이므로 승인이 필요하고, RR-11 에 따라 **애플리케이션 코드와 별도 PR** 로 분리하는 것을 권장합니다. 초안입니다.

```sql
-- Copyright 2026 Kakao Healthcare Corp. All Rights Reserved.
CREATE TABLE coupon_code (
    id BIGINT NOT NULL AUTO_INCREMENT,
    code VARCHAR(64) NOT NULL,
    discount_amount BIGINT NOT NULL,
    used_at DATETIME(6) NULL,
    used_by BIGINT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT uk_code UNIQUE (code)
);
```

기존 패턴 기준입니다. signed `BIGINT` PK, `UNSIGNED`·ENGINE·charset 미명시, 스키마 접두사(`pasta.`) 없음, 제약 이름 `uk_{컬럼}`. 쿠폰 코드는 ASCII 라 비ASCII INSERT 도 없습니다. `used_by` 의 FK 여부(users 테이블 참조)는 결정이 필요합니다. 파일명 `V{다음버전}__create_coupon_code.sql`. 기존 obesity 마이그레이션은 건드리지 않습니다.

### C. 확인 질문 (정책)

1. `discountAmount = 0` 쿠폰을 사용 가능으로 볼지 여부 (현재 허용).
2. 이미 사용된 쿠폰의 응답을 409 로 할지 400 으로 할지 (현재 409, `ConflictException` 가정).
3. 만료(`expiredAt`) 개념은 TDD 필드에 없어 **넣지 않았습니다** (엔티티 필드는 id, code, discountAmount, usedAt, usedBy 로 한정).

---

## 5. 구현 코드

패키지 루트는 TDD 경로(`pghd/coupon/...`)를 그대로 따릅니다. 아래 코드는 시뮬레이션이며 실제 파일은 쓰지 않았습니다. shared 모듈 import 경로는 `[가정]` 입니다.

### 5-1. Phase 1 — Domain

`pghd/coupon/domain/CouponCodeEntity.java`

```java
package pghd.coupon.domain;

import java.time.Instant;
import java.util.Objects;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.ToString;

@Getter
@ToString
@EqualsAndHashCode
public class CouponCodeEntity {

    private final Long id;

    // 쿠폰 코드는 민감 정보라 로그나 예외 메시지에 평문으로 남지 않도록 toString 에서 제외합니다.
    @ToString.Exclude private final String code;

    private final long discountAmount;
    private final Instant usedAt;
    private final Long usedBy;

    public CouponCodeEntity(
            Long id, String code, long discountAmount, Instant usedAt, Long usedBy) {
        Objects.requireNonNull(code, "code must not be null");
        if (discountAmount < 0) {
            throw new IllegalArgumentException("discountAmount must not be negative");
        }
        if ((usedAt == null) != (usedBy == null)) {
            throw new IllegalArgumentException("usedAt and usedBy must be set together");
        }
        this.id = id;
        this.code = code;
        this.discountAmount = discountAmount;
        this.usedAt = usedAt;
        this.usedBy = usedBy;
    }

    public static CouponCodeEntity of(String code, long discountAmount) {
        return new CouponCodeEntity(null, code, discountAmount, null, null);
    }

    public CouponCodeEntity redeem(long userId, Instant redeemedAt) {
        Objects.requireNonNull(redeemedAt, "redeemedAt must not be null");
        if (isUsed()) {
            throw new IllegalStateException("이미 사용된 쿠폰입니다.");
        }
        return new CouponCodeEntity(id, code, discountAmount, redeemedAt, userId);
    }

    public boolean isUsed() {
        return usedAt != null;
    }
}
```

`pghd/coupon/domain/CouponCodeRepository.java`

```java
package pghd.coupon.domain;

import java.util.Optional;

public interface CouponCodeRepository {

    Optional<CouponCodeEntity> findByCode(String code);

    CouponCodeEntity save(CouponCodeEntity couponCodeEntity);
}
```

### 5-2. Phase 2 — Infrastructure

`pghd/coupon/infrastructure/CouponCodeJpaEntity.java`

```java
package pghd.coupon.infrastructure;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.validation.constraints.NotNull;
import java.time.Instant;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import pghd.coupon.domain.CouponCodeEntity;
// import 경로 [가정]: BaseTimeJpaEntity 는 기존 공용 클래스를 grep 으로 찾아 사용

@Entity
@Table(name = "coupon_code")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class CouponCodeJpaEntity extends BaseTimeJpaEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotNull
    @Column(nullable = false, length = 64, unique = true)
    private String code;

    @Column(nullable = false)
    private long discountAmount;

    private Instant usedAt;

    private Long usedBy;

    @Builder
    private CouponCodeJpaEntity(
            Long id, String code, long discountAmount, Instant usedAt, Long usedBy) {
        this.id = id;
        this.code = code;
        this.discountAmount = discountAmount;
        this.usedAt = usedAt;
        this.usedBy = usedBy;
    }

    public CouponCodeEntity toEntity() {
        return new CouponCodeEntity(id, code, discountAmount, usedAt, usedBy);
    }

    public static CouponCodeJpaEntity from(CouponCodeEntity couponCodeEntity) {
        return CouponCodeJpaEntity.builder()
                .id(couponCodeEntity.getId())
                .code(couponCodeEntity.getCode())
                .discountAmount(couponCodeEntity.getDiscountAmount())
                .usedAt(couponCodeEntity.getUsedAt())
                .usedBy(couponCodeEntity.getUsedBy())
                .build();
    }
}
```

`pghd/coupon/infrastructure/CouponCodeJpaRepository.java`

```java
package pghd.coupon.infrastructure;

import java.util.Optional;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CouponCodeJpaRepository extends JpaRepository<CouponCodeJpaEntity, Long> {

    Optional<CouponCodeJpaEntity> findByCode(String code);
}
```

`pghd/coupon/infrastructure/CouponCodeRepositoryImpl.java`

```java
package pghd.coupon.infrastructure;

import java.util.Optional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Repository;
import pghd.coupon.domain.CouponCodeEntity;
import pghd.coupon.domain.CouponCodeRepository;

@Repository
@RequiredArgsConstructor
public class CouponCodeRepositoryImpl implements CouponCodeRepository {

    private final CouponCodeJpaRepository couponCodeJpaRepository;

    @Override
    public Optional<CouponCodeEntity> findByCode(String code) {
        return couponCodeJpaRepository.findByCode(code).map(CouponCodeJpaEntity::toEntity);
    }

    @Override
    public CouponCodeEntity save(CouponCodeEntity couponCodeEntity) {
        CouponCodeJpaEntity couponCodeJpaEntity = CouponCodeJpaEntity.from(couponCodeEntity);
        return couponCodeJpaRepository.save(couponCodeJpaEntity).toEntity();
    }
}
```

주의: `from()` 은 `createdAt` 을 옮기지 않으므로 기존 id 로 `save`(merge)할 때 생성 시각이 보존되는지 Infra 테스트(5-6)에서 확인합니다. `BaseTimeJpaEntity.createdAt` 이 `updatable = false` 가 아니면 이 지점에서 문제가 됩니다 `[가정: updatable=false]`.

### 5-3. Phase 3 — Application

`pghd/coupon/application/exception/CouponNotFoundException.java`

```java
package pghd.coupon.application.exception;

import com.kakaohealthcare.moneyball.shared.exception.ExceptionConstants; // [가정]
import com.kakaohealthcare.moneyball.shared.exception.NotFoundException; // [가정]

public class CouponNotFoundException extends NotFoundException {

    public CouponNotFoundException() {
        super(
                ExceptionConstants.COUPON_NOT_FOUND,
                "error.coupon.not.found",
                new Object[] {});
    }
}
```

`pghd/coupon/application/exception/CouponAlreadyUsedException.java`

```java
package pghd.coupon.application.exception;

import com.kakaohealthcare.moneyball.shared.exception.ConflictException; // [가정]
import com.kakaohealthcare.moneyball.shared.exception.ExceptionConstants; // [가정]

public class CouponAlreadyUsedException extends ConflictException {

    public CouponAlreadyUsedException() {
        super(
                ExceptionConstants.COUPON_ALREADY_USED,
                "error.coupon.already.used",
                new Object[] {});
    }
}
```

`ExceptionConstants` 에 `COUPON_NOT_FOUND`, `COUPON_ALREADY_USED` 를 추가합니다. 코드 번호는 grep 으로 확인한 **비어 있는 다음 번호**를 사용합니다 (DW-6, 5절 앞의 전수 검색 `[가정: 0건]`).

i18n 4파일(`message-shared.properties`, `_ko`, `_en`, `_ja`)에 동시에 추가합니다. 파일을 덮어쓰지 않고 Edit 로 끝에 덧붙입니다 (DW-3).

```properties
# message-shared.properties (default) / message-shared_en.properties
error.coupon.not.found=Coupon not found.
error.coupon.already.used=This coupon has already been used.
# message-shared_ko.properties
error.coupon.not.found=쿠폰을 찾을 수 없습니다.
error.coupon.already.used=이미 사용된 쿠폰입니다.
# message-shared_ja.properties
error.coupon.not.found=クーポンが見つかりません。
error.coupon.already.used=このクーポンはすでに使用されています。
```

검증 명령: `grep -l "^error.coupon.not.found=" pasta-api/src/main/resources/message-shared*.properties` 결과가 4건이어야 합니다. 플레이스홀더는 쓰지 않았습니다 (위치 기반 규칙 해당 없음).

`pghd/coupon/application/CouponRedeemInDto.java`

```java
package pghd.coupon.application;

public record CouponRedeemInDto(String code, long userId) {

    public static CouponRedeemInDto of(String code, long userId) {
        return new CouponRedeemInDto(code, userId);
    }
}
```

`pghd/coupon/application/CouponRedeemOutDto.java`

```java
package pghd.coupon.application;

import java.time.Instant;
import pghd.coupon.domain.CouponCodeEntity;

public record CouponRedeemOutDto(String code, long discountAmount, Instant usedAt) {

    public static CouponRedeemOutDto from(CouponCodeEntity couponCodeEntity) {
        return new CouponRedeemOutDto(
                couponCodeEntity.getCode(),
                couponCodeEntity.getDiscountAmount(),
                couponCodeEntity.getUsedAt());
    }
}
```

`pghd/coupon/application/CouponRedeemService.java`

```java
package pghd.coupon.application;

import java.time.Instant;
import lombok.RequiredArgsConstructor;
import lombok.extern.log4j.Log4j2;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import pghd.coupon.application.exception.CouponAlreadyUsedException;
import pghd.coupon.application.exception.CouponNotFoundException;
import pghd.coupon.domain.CouponCodeEntity;
import pghd.coupon.domain.CouponCodeRepository;

@Service
@RequiredArgsConstructor
@Log4j2
public class CouponRedeemService {

    private final CouponCodeRepository couponCodeRepository;

    @Transactional
    public CouponRedeemOutDto redeemCoupon(CouponRedeemInDto couponRedeemInDto) {
        CouponCodeEntity couponCodeEntity =
                couponCodeRepository
                        .findByCode(couponRedeemInDto.code())
                        .orElseThrow(CouponNotFoundException::new);

        if (couponCodeEntity.isUsed()) {
            throw new CouponAlreadyUsedException();
        }

        Instant currentAt = Instant.now();
        CouponCodeEntity redeemedCouponCodeEntity =
                couponCodeEntity.redeem(couponRedeemInDto.userId(), currentAt);
        CouponCodeEntity savedCouponCodeEntity =
                couponCodeRepository.save(redeemedCouponCodeEntity);

        log.info(
                "[CouponRedeemService.redeemCoupon] 쿠폰 사용 완료 couponCodeId={}",
                savedCouponCodeEntity.getId());
        return CouponRedeemOutDto.from(savedCouponCodeEntity);
    }
}
```

검증 순서는 "존재 확인 → 상태 확인"입니다. 소유자 개념이 없는 리소스라 소유 확인은 해당 없고, 입력 검증(`@NotBlank`)은 컨트롤러에서 먼저 수행되어 존재 확인보다 앞섭니다. 입력 형식 오류가 리소스 존재를 노출하지 않으므로 RR-14 순서 위반이 아닙니다. 이미 사용된 상태 확인은 `isUsed()` 위임 질의이며 판단 로직 자체는 도메인에 있습니다.

### 5-4. Phase 4 — Web

`pghd/coupon/web/CouponRedeemRequest.java`

```java
package pghd.coupon.web;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;
import pghd.coupon.application.CouponRedeemInDto;

public record CouponRedeemRequest(
        @Schema(description = "쿠폰 코드") @NotBlank String code) {

    public CouponRedeemInDto toInDto(long userId) {
        return CouponRedeemInDto.of(code, userId);
    }
}
```

`pghd/coupon/web/CouponRedeemResponse.java`

```java
package pghd.coupon.web;

import io.swagger.v3.oas.annotations.media.Schema;
import java.time.Instant;
import pghd.coupon.application.CouponRedeemOutDto;

public record CouponRedeemResponse(
        @Schema(description = "쿠폰 코드") String code,
        @Schema(description = "할인 금액") long discountAmount,
        @Schema(description = "사용 시각 (UTC)") Instant usedAt) {

    public static CouponRedeemResponse from(CouponRedeemOutDto couponRedeemOutDto) {
        return new CouponRedeemResponse(
                couponRedeemOutDto.code(),
                couponRedeemOutDto.discountAmount(),
                couponRedeemOutDto.usedAt());
    }
}
```

`pghd/coupon/web/CouponRedeemController.java`

```java
package pghd.coupon.web;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import pghd.coupon.application.CouponRedeemOutDto;
import pghd.coupon.application.CouponRedeemService;

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
        CouponRedeemOutDto couponRedeemOutDto =
                couponRedeemService.redeemCoupon(couponRedeemRequest.toInDto(userId));
        return ResponseEntity.ok(CouponRedeemResponse.from(couponRedeemOutDto));
    }
}
```

스킬 샘플에 있던 `TimeZoneContext.getZoneId()` 호출은 값을 쓰지 않는 죽은 코드라 **넣지 않았습니다.** 시각은 UTC `Instant` 로 내려가고 표시 변환은 클라이언트 몫입니다.

### 5-5. 설정 — SecurityConstants (Edit, 기존 파일 읽은 뒤 일부 수정)

```java
// SecurityConstants.airArray 에 한 줄 추가
"/api/v1/coupons/redeem",
```

환경변수·외부 API 의존이 없어 yml 4곳 override 는 해당 없습니다. 누락하면 인증 필터가 적용되지 않아 `@AuthenticationPrincipal` 이 null 이 됩니다.

### 5-6. Test Double / Fixture / 테스트 (`pasta-api/src/test/java/pghd/coupon/...`)

`CouponCodeFixture.java`

```java
package pghd.coupon;

import java.time.Instant;
import pghd.coupon.domain.CouponCodeEntity;

public class CouponCodeFixture {

    public static final String DEFAULT_CODE = "SAVE5000";
    public static final long DEFAULT_DISCOUNT_AMOUNT = 5000L;
    public static final Instant DEFAULT_USED_AT = Instant.parse("2026-11-13T03:00:00Z");
    public static final long DEFAULT_USED_BY = 7L;

    public static CouponCodeEntity create() {
        return CouponCodeEntity.of(DEFAULT_CODE, DEFAULT_DISCOUNT_AMOUNT);
    }

    public static CouponCodeEntity createWithCode(String code) {
        return CouponCodeEntity.of(code, DEFAULT_DISCOUNT_AMOUNT);
    }

    public static CouponCodeEntity createUsed() {
        return new CouponCodeEntity(
                null, DEFAULT_CODE, DEFAULT_DISCOUNT_AMOUNT, DEFAULT_USED_AT, DEFAULT_USED_BY);
    }
}
```

`FakeCouponCodeRepository.java` (HashMap 기반, `setResult` 없음)

```java
package pghd.coupon;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicLong;
import pghd.coupon.domain.CouponCodeEntity;
import pghd.coupon.domain.CouponCodeRepository;

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
    public CouponCodeEntity save(CouponCodeEntity couponCodeEntity) {
        Long id = couponCodeEntity.getId();
        if (id == null) {
            id = idGenerator.getAndIncrement();
        }
        CouponCodeEntity savedCouponCodeEntity =
                new CouponCodeEntity(
                        id,
                        couponCodeEntity.getCode(),
                        couponCodeEntity.getDiscountAmount(),
                        couponCodeEntity.getUsedAt(),
                        couponCodeEntity.getUsedBy());
        store.put(id, savedCouponCodeEntity);
        return savedCouponCodeEntity;
    }
}
```

#### Phase 1 테스트 — `CouponCodeEntityTest` (순수 JUnit 5)

```java
package pghd.coupon.domain;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.time.Instant;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import pghd.coupon.CouponCodeFixture;

class CouponCodeEntityTest {

    private static final Instant REDEEMED_AT = Instant.parse("2026-11-13T12:00:00Z");

    @Test
    @DisplayName("코드와 할인 금액으로 생성하면 id, 사용 시각, 사용자가 비어 있는 미사용 쿠폰이 된다")
    void of_codeAndDiscount_createsUnusedCoupon() {
        // Given & When
        CouponCodeEntity couponCodeEntity = CouponCodeEntity.of("SAVE5000", 5000L);

        // Then
        assertThat(couponCodeEntity.getId()).isNull();
        assertThat(couponCodeEntity.getCode()).isEqualTo("SAVE5000");
        assertThat(couponCodeEntity.getDiscountAmount()).isEqualTo(5000L);
        assertThat(couponCodeEntity.isUsed()).isFalse();
    }

    @Test
    @DisplayName("코드가 null 이면 NullPointerException 이 발생한다")
    void of_nullCode_throwsNullPointerException() {
        // When & Then
        assertThatThrownBy(() -> CouponCodeEntity.of(null, 5000L))
                .isInstanceOf(NullPointerException.class)
                .hasMessage("code must not be null");
    }

    @Test
    @DisplayName("할인 금액이 음수이면 IllegalArgumentException 이 발생한다")
    void of_negativeDiscountAmount_throwsIllegalArgumentException() {
        // When & Then
        assertThatThrownBy(() -> CouponCodeEntity.of("SAVE5000", -1L))
                .isInstanceOf(IllegalArgumentException.class);
    }

    @Test
    @DisplayName("사용 시각만 있고 사용자가 없으면 IllegalArgumentException 이 발생한다")
    void constructor_usedAtWithoutUsedBy_throwsIllegalArgumentException() {
        // When & Then
        assertThatThrownBy(
                        () -> new CouponCodeEntity(1L, "SAVE5000", 5000L, REDEEMED_AT, null))
                .isInstanceOf(IllegalArgumentException.class);
    }

    @Test
    @DisplayName("미사용 쿠폰을 사용 처리하면 사용 시각과 사용자가 설정되고 코드와 할인 금액은 유지된다")
    void redeem_unusedCoupon_setsUsedAtAndUsedBy() {
        // Given
        CouponCodeEntity couponCodeEntity = CouponCodeFixture.create();

        // When
        CouponCodeEntity redeemedCouponCodeEntity = couponCodeEntity.redeem(42L, REDEEMED_AT);

        // Then
        assertThat(redeemedCouponCodeEntity.getUsedAt()).isEqualTo(REDEEMED_AT);
        assertThat(redeemedCouponCodeEntity.getUsedBy()).isEqualTo(42L);
        assertThat(redeemedCouponCodeEntity.getCode()).isEqualTo(CouponCodeFixture.DEFAULT_CODE);
        assertThat(redeemedCouponCodeEntity.getDiscountAmount())
                .isEqualTo(CouponCodeFixture.DEFAULT_DISCOUNT_AMOUNT);
    }

    @Test
    @DisplayName("사용 처리해도 원본 쿠폰 객체는 미사용 상태로 남는다")
    void redeem_unusedCoupon_keepsOriginalUnused() {
        // Given
        CouponCodeEntity couponCodeEntity = CouponCodeFixture.create();

        // When
        couponCodeEntity.redeem(42L, REDEEMED_AT);

        // Then
        assertThat(couponCodeEntity.isUsed()).isFalse();
    }

    @Test
    @DisplayName("이미 사용된 쿠폰을 다시 사용 처리하면 IllegalStateException 이 발생한다")
    void redeem_usedCoupon_throwsIllegalStateException() {
        // Given
        CouponCodeEntity usedCouponCodeEntity = CouponCodeFixture.createUsed();

        // When & Then
        assertThatThrownBy(() -> usedCouponCodeEntity.redeem(42L, REDEEMED_AT))
                .isInstanceOf(IllegalStateException.class)
                .hasMessage("이미 사용된 쿠폰입니다.");
    }
}
```

#### Phase 2 테스트 — `CouponCodeRepositoryImplTest` (`@DataJpaTest` + Testcontainers MySQL, H2 금지)

DB 왕복 정밀도 때문에 시각은 고정값(`Instant.parse`)을 씁니다. `Instant.now()` 는 나노초를 가져 DATETIME(6) 에서 잘려 비교가 어긋납니다. 1차 캐시 때문에 거짓 통과하지 않도록 `flush` + `clear` 후 재조회합니다.

```java
package pghd.coupon.infrastructure;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.time.Instant;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.test.context.ActiveProfiles;
import pghd.coupon.CouponCodeFixture;
import pghd.coupon.domain.CouponCodeEntity;

@DataJpaTest
@ActiveProfiles("test")
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
class CouponCodeRepositoryImplTest {

    private static final Instant REDEEMED_AT = Instant.parse("2026-11-13T12:00:00Z");

    @Autowired private TestEntityManager testEntityManager;

    private CouponCodeRepositoryImpl couponCodeRepositoryImpl;

    @BeforeEach
    void setUp(@Autowired CouponCodeJpaRepository couponCodeJpaRepository) {
        couponCodeRepositoryImpl = new CouponCodeRepositoryImpl(couponCodeJpaRepository);
    }

    @Test
    @DisplayName("새 쿠폰을 저장하면 id 가 발급되고 코드로 조회한 할인 금액이 일치한다")
    void save_newCoupon_assignsIdAndFindsByCode() {
        // Given
        CouponCodeEntity savedCouponCodeEntity =
                couponCodeRepositoryImpl.save(CouponCodeFixture.create());
        testEntityManager.flush();
        testEntityManager.clear();

        // When
        Optional<CouponCodeEntity> couponCodeEntityOptional =
                couponCodeRepositoryImpl.findByCode(CouponCodeFixture.DEFAULT_CODE);

        // Then
        assertThat(savedCouponCodeEntity.getId()).isNotNull();
        assertThat(couponCodeEntityOptional).isPresent();
        assertThat(couponCodeEntityOptional.get().getDiscountAmount())
                .isEqualTo(CouponCodeFixture.DEFAULT_DISCOUNT_AMOUNT);
    }

    @Test
    @DisplayName("존재하지 않는 코드로 조회하면 빈 Optional 이 반환된다")
    void findByCode_unknownCode_returnsEmpty() {
        // When
        Optional<CouponCodeEntity> couponCodeEntityOptional =
                couponCodeRepositoryImpl.findByCode("UNKNOWN");

        // Then
        assertThat(couponCodeEntityOptional).isEmpty();
    }

    @Test
    @DisplayName("사용 처리한 쿠폰을 저장하면 재조회 시 사용 시각과 사용자가 유지된다")
    void save_redeemedCoupon_persistsUsedAtAndUsedBy() {
        // Given
        CouponCodeEntity savedCouponCodeEntity =
                couponCodeRepositoryImpl.save(CouponCodeFixture.create());
        couponCodeRepositoryImpl.save(savedCouponCodeEntity.redeem(42L, REDEEMED_AT));
        testEntityManager.flush();
        testEntityManager.clear();

        // When
        CouponCodeEntity foundCouponCodeEntity =
                couponCodeRepositoryImpl.findByCode(CouponCodeFixture.DEFAULT_CODE).orElseThrow();

        // Then
        assertThat(foundCouponCodeEntity.getId()).isEqualTo(savedCouponCodeEntity.getId());
        assertThat(foundCouponCodeEntity.getUsedAt()).isEqualTo(REDEEMED_AT);
        assertThat(foundCouponCodeEntity.getUsedBy()).isEqualTo(42L);
    }

    @Test
    @DisplayName("같은 코드의 쿠폰을 두 번 저장하면 유니크 제약으로 DataIntegrityViolationException 이 발생한다")
    void save_duplicateCode_throwsDataIntegrityViolationException() {
        // Given
        couponCodeRepositoryImpl.save(CouponCodeFixture.create());

        // When & Then
        assertThatThrownBy(() -> couponCodeRepositoryImpl.save(CouponCodeFixture.create()))
                .isInstanceOf(DataIntegrityViolationException.class);
    }
}
```

#### Phase 3 테스트 — `CouponRedeemServiceTest` (Fake Repository, Mockito 미사용)

```java
package pghd.coupon.application;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.time.Instant;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import pghd.coupon.CouponCodeFixture;
import pghd.coupon.FakeCouponCodeRepository;
import pghd.coupon.application.exception.CouponAlreadyUsedException;
import pghd.coupon.application.exception.CouponNotFoundException;
import pghd.coupon.domain.CouponCodeEntity;

class CouponRedeemServiceTest {

    private FakeCouponCodeRepository fakeCouponCodeRepository;
    private CouponRedeemService couponRedeemService;

    @BeforeEach
    void setUp() {
        fakeCouponCodeRepository = new FakeCouponCodeRepository();
        couponRedeemService = new CouponRedeemService(fakeCouponCodeRepository);
    }

    @Test
    @DisplayName("미사용 쿠폰 코드로 사용 처리하면 할인 금액과 요청 시점의 사용 시각이 반환된다")
    void redeemCoupon_unusedCode_returnsOutDtoWithDiscountAndUsedAt() {
        // Given
        fakeCouponCodeRepository.save(CouponCodeFixture.create());
        Instant requestedBeforeAt = Instant.now();

        // When
        CouponRedeemOutDto couponRedeemOutDto =
                couponRedeemService.redeemCoupon(CouponRedeemInDto.of("SAVE5000", 42L));
        Instant requestedAfterAt = Instant.now();

        // Then
        assertThat(couponRedeemOutDto.code()).isEqualTo("SAVE5000");
        assertThat(couponRedeemOutDto.discountAmount()).isEqualTo(5000L);
        assertThat(couponRedeemOutDto.usedAt()).isBetween(requestedBeforeAt, requestedAfterAt);
    }

    @Test
    @DisplayName("사용 처리 후 저장소의 쿠폰은 요청한 사용자가 사용한 상태로 저장된다")
    void redeemCoupon_unusedCode_persistsUsedByRequestedUser() {
        // Given
        fakeCouponCodeRepository.save(CouponCodeFixture.create());

        // When
        couponRedeemService.redeemCoupon(CouponRedeemInDto.of("SAVE5000", 42L));

        // Then
        CouponCodeEntity foundCouponCodeEntity =
                fakeCouponCodeRepository.findByCode("SAVE5000").orElseThrow();
        assertThat(foundCouponCodeEntity.isUsed()).isTrue();
        assertThat(foundCouponCodeEntity.getUsedBy()).isEqualTo(42L);
    }

    @Test
    @DisplayName("존재하지 않는 쿠폰 코드를 입력하면 CouponNotFoundException 이 발생한다")
    void redeemCoupon_unknownCode_throwsCouponNotFoundException() {
        // When & Then
        assertThatThrownBy(
                        () -> couponRedeemService.redeemCoupon(CouponRedeemInDto.of("UNKNOWN", 1L)))
                .isInstanceOf(CouponNotFoundException.class);
    }

    @Test
    @DisplayName("이미 사용된 쿠폰을 다시 사용하면 CouponAlreadyUsedException 이 발생하고 기존 사용자 정보는 바뀌지 않는다")
    void redeemCoupon_usedCode_throwsCouponAlreadyUsedExceptionAndKeepsOriginalUser() {
        // Given
        fakeCouponCodeRepository.save(CouponCodeFixture.createUsed());

        // When & Then
        assertThatThrownBy(
                        () -> couponRedeemService.redeemCoupon(CouponRedeemInDto.of("SAVE5000", 42L)))
                .isInstanceOf(CouponAlreadyUsedException.class);
        CouponCodeEntity foundCouponCodeEntity =
                fakeCouponCodeRepository.findByCode("SAVE5000").orElseThrow();
        assertThat(foundCouponCodeEntity.getUsedBy()).isEqualTo(CouponCodeFixture.DEFAULT_USED_BY);
        assertThat(foundCouponCodeEntity.getUsedAt()).isEqualTo(CouponCodeFixture.DEFAULT_USED_AT);
    }
}
```

#### Phase 4 테스트 — `CouponRedeemControllerTest` (`@WebMvcTest` + MockMvc)

Service 는 외부 경계 역할이라 `@MockBean` 허용 범위입니다 (Repository·UseCase·QueryService 가 아님). 스텁 인자를 `any()` 로 받으면 서비스에 잘못된 값이 넘어가도 통과하므로 `CouponRedeemInDto.of("SAVE5000", 42L)` 로 고정합니다. 사용자 id 는 `Authentication` principal 로 주입합니다. 스킬 샘플의 `webAppContextSetup` 직접 빌드 대신 자동 구성 `MockMvc` 를 써서 Security 필터와 `@AuthenticationPrincipal` 해석이 함께 동작하게 했습니다.

```java
package pghd.coupon.web;

import static org.mockito.BDDMockito.given;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.authentication;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.time.Instant;
import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.test.web.servlet.MockMvc;
import pghd.coupon.application.CouponRedeemInDto;
import pghd.coupon.application.CouponRedeemOutDto;
import pghd.coupon.application.CouponRedeemService;
import pghd.coupon.application.exception.CouponAlreadyUsedException;
import pghd.coupon.application.exception.CouponNotFoundException;

@WebMvcTest(CouponRedeemController.class)
class CouponRedeemControllerTest {

    private static final String REDEEM_URL = "/api/v1/coupons/redeem";
    private static final Instant USED_AT = Instant.parse("2026-11-13T03:00:00Z");
    private static final String VALID_BODY = "{\"code\": \"SAVE5000\"}";

    @Autowired private MockMvc mockMvc;

    @MockBean private CouponRedeemService couponRedeemService;

    private UsernamePasswordAuthenticationToken authenticatedUser() {
        return new UsernamePasswordAuthenticationToken(42L, null, List.of());
    }

    @Test
    @DisplayName("유효한 코드로 요청하면 200 과 쿠폰 코드, 할인 금액, 사용 시각을 반환한다")
    void redeemCoupon_validRequest_returnsOkWithDiscountAndUsedAt() throws Exception {
        // Given
        given(couponRedeemService.redeemCoupon(CouponRedeemInDto.of("SAVE5000", 42L)))
                .willReturn(new CouponRedeemOutDto("SAVE5000", 5000L, USED_AT));

        // When & Then
        mockMvc.perform(
                        post(REDEEM_URL)
                                .with(authentication(authenticatedUser()))
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(VALID_BODY))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value("SAVE5000"))
                .andExpect(jsonPath("$.discountAmount").value(5000))
                .andExpect(jsonPath("$.usedAt").value("2026-11-13T03:00:00Z"));
    }

    @Test
    @DisplayName("코드가 공백이면 서비스를 거치지 않고 400 을 반환한다")
    void redeemCoupon_blankCode_returnsBadRequest() throws Exception {
        // When & Then
        mockMvc.perform(
                        post(REDEEM_URL)
                                .with(authentication(authenticatedUser()))
                                .contentType(MediaType.APPLICATION_JSON)
                                .content("{\"code\": \" \"}"))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("존재하지 않는 쿠폰이면 404 를 반환한다")
    void redeemCoupon_unknownCoupon_returnsNotFound() throws Exception {
        // Given
        given(couponRedeemService.redeemCoupon(CouponRedeemInDto.of("SAVE5000", 42L)))
                .willThrow(new CouponNotFoundException());

        // When & Then
        mockMvc.perform(
                        post(REDEEM_URL)
                                .with(authentication(authenticatedUser()))
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(VALID_BODY))
                .andExpect(status().isNotFound());
    }

    @Test
    @DisplayName("이미 사용된 쿠폰이면 409 를 반환한다")
    void redeemCoupon_usedCoupon_returnsConflict() throws Exception {
        // Given
        given(couponRedeemService.redeemCoupon(CouponRedeemInDto.of("SAVE5000", 42L)))
                .willThrow(new CouponAlreadyUsedException());

        // When & Then
        mockMvc.perform(
                        post(REDEEM_URL)
                                .with(authentication(authenticatedUser()))
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(VALID_BODY))
                .andExpect(status().isConflict());
    }
}
```

공백 코드 테스트는 서비스를 스텁하지 않았습니다. 검증이 동작하지 않으면 서비스가 null 을 반환해 `CouponRedeemResponse.from(null)` 에서 500 이 나므로, 400 단언이 통과한다는 것이 검증 동작의 증거입니다.

---

## 6. 실행 명령과 가정 결과 (모드 A 5~8-1단계)

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 21)

# 5) 빌드 손상 확인 후 테스트 (--tests 필터 후 전체 재실행이면 cleanTest 를 앞에 붙임)
./gradlew :pasta-api:cleanTest :pasta-api:test --tests "pghd.coupon.*"
#   [가정] 1회차: 컴파일 통과, CouponCodeEntityTest 7, CouponCodeRepositoryImplTest 4,
#          CouponRedeemServiceTest 4, CouponRedeemControllerTest 4 = 19건 PASS (연속 실패 0회)
#   Infra 테스트는 8절 B 의 마이그레이션이 적용된 상태에서만 통과합니다.
#   마이그레이션 PR 이 먼저 머지되지 않으면 이 4건은 "relation not found" 로 실패합니다.

# 7) 포맷
./gradlew :pasta-api:spotlessApply
#   [가정] 포맷 변경 일부 적용

# 8) 설정 체크
grep -n "/api/v1/coupons/redeem" pasta-api/src/main/java/**/SecurityConstants.java
#   [가정] 1건 확인
grep -l "^error.coupon.not.found=" pasta-api/src/main/resources/message-shared*.properties | wc -l
#   [가정] 4

# 8-1) 리뷰 재발 방지 기계 검사 (RR-L)
python3 forge/common/review-lint.py
#   [가정] 위반 0건, 확인 항목 0건
#          (NAMING: 컬렉션 변수 없음, Instant 변수는 At 접미사 / RR-12: lenient·any() 스텁·doesNotExist 없음
#           RR-13: Collectors.toMap 없음 / LAYER: domain 이 예외·web 을 import 하지 않음 / FQCN·PII 없음)

# 완료 전 실물 확인 (DW-5, DW-7)
git status --short
git diff --stat
#   [가정] 신규 파일 + SecurityConstants·ExceptionConstants·message 4파일 수정만 보이고 의도하지 않은 변경 없음
```

일부러 깨뜨려 보는 확인(RR-12)의 예상 결과입니다. 모두 `[가정]` 이며 실제 실행 시 재확인합니다.

| 일부러 깨뜨린 지점 | 실패해야 하는 테스트 |
|--------------------|----------------------|
| 서비스의 `isUsed()` 분기 삭제 | `redeemCoupon_usedCode_...` (도메인 `IllegalStateException` 이 올라와 `CouponAlreadyUsedException` 단언 실패) |
| `redeem()` 이 `usedBy` 를 설정하지 않음 | 도메인 테스트와 서비스 `persistsUsedByRequestedUser` |
| `from()` 에서 `usedAt` 매핑 누락 | `save_redeemedCoupon_persistsUsedAtAndUsedBy` (고정 시각이라 기본값 null 과 구분됨) |
| 컨트롤러의 `@Valid` 제거 | `redeemCoupon_blankCode_returnsBadRequest` |
| airArray 등록 누락 | **단위 테스트로 잡히지 않습니다.** 통합 시점의 인증 확인이 필요합니다 (수동 확인 항목, 8절) |

---

## 7. TDD 체크박스 업데이트 (시뮬레이션, 실제 파일 수정 없음)

테스트 통과 후 `docs/tdd/coupon-redeem-tdd.md` 의 Phase 1~4 TODO 를 `- [ ]` 에서 `- [x]` 로 바꿉니다. 단 **Phase 2 의 `CouponCodeRepositoryImplTest` 는 마이그레이션 PR 머지 후 통과가 확인되기 전까지 체크하지 않습니다.** 확인하지 않은 항목을 완료로 표시하지 않습니다 (DW-7).

---

## 8. 사용자에게 필요한 후속 조치 / PR 본문 기재 사항

### 승인·결정 필요

1. 4절 A: 이중 사용 방지 방식 선택 (조건부 UPDATE 또는 비관적 락 권장).
2. 4절 B: `coupon_code` 마이그레이션 승인과 별도 PR 분리, `used_by` FK 여부.
3. 4절 C: 0 원 쿠폰, 이미 사용 시 상태 코드(409), 만료 개념 포함 여부.

### PR 본문에 적을 내용

- 기존 동작 변경: 없음 (신규 엔드포인트).
- 설계 결정 근거: 도메인 예외를 `IllegalStateException` 으로 두고 서비스가 `isUsed()` 로 위임 질의한 뒤 `application/exception` 예외로 번역 (domain 은 HTTP 예외 비참조 원칙).
- 알려진 위험: 동시 요청 이중 사용 (승인 후 반영 전까지 열려 있음).
- 시각 타입: `Instant`(UTC) 로 응답.
- 추가 요청 없이 포함한 것: `ExceptionConstants` 2건, i18n 4파일, 예외 클래스 2개.
- 가정 항목(2절)이 grep 결과와 다르면 import·상태코드를 조정.

### 수동 확인 항목

- 로컬 기동 후 인증 토큰 없이 `POST /api/v1/coupons/redeem` 호출 시 401 이 나오는지 (airArray 등록 검증).
- 동일 코드를 동시에 2회 호출했을 때의 결과 (4절 A 해결 전에는 둘 다 200 이 나올 수 있음).

---

## 9. 자기 검증 체크리스트 요약 (스킬 44항목 중 해당 항목)

| # | 항목 | 결과 |
|---|------|------|
| 1~3 | 패키지 flat / 의존 방향 / Domain 순수성 | 통과 (domain 에 Spring·JPA·HTTP 예외 없음, 첫 커밋부터 4계층 폴더) |
| 4 | Rich Domain | 통과 (`redeem`, `isUsed`, 불변식 모두 도메인 소유) |
| 5 | Repository 3단계 | 통과 (Domain 인터페이스 + JpaRepository + Impl) |
| 6~7 | record/class, Lombok | 통과 (`@Data`·`@Setter`·필드 `@Autowired` 없음, `@Builder` 생성자 레벨) |
| 8 | 네이밍 | 통과 (`var` 없음, 약어 없음, 시각 `*At`, 타입 반영 변수명) |
| 9~10 | 테스트 계층·스타일 | 통과 (Fake / MockMvc / Testcontainers, 한글 `@DisplayName`, Given-When-Then, AssertJ) |
| 11 | 설정 | airArray 등록, spotless 명령 포함, 환경변수 해당 없음 |
| 12 | 가드레일 | 커밋 안 함, H2 없음, stash 없음, 기존 마이그레이션 미수정 |
| 17, 24 | FQCN | 본문 패키지 경로 0건, 모든 외부 클래스 import |
| 18~20 | Phase 0 / 확인 vs 가정 / 인접 도메인 | 1절·2절에 기록, 인접 도메인 Repository 호출 없음 |
| 26~27 | i18n 4파일 / 위치 기반 | 4파일 동시 추가, 플레이스홀더 없음 |
| 28 | 싱글톤 mutable field | 서비스에 가변 필드 없음 |
| 42 | 작성 전 질문 5개 | 1절 표 |
| 43 | 이름 규칙 | 통과 (주석은 존댓말) |
| 44 | review-lint 위반 0건 | `[가정]` 0건, 실제 실행 필요 |
| DW-1~7 | 파괴적 쓰기 가드 | 신규 파일 위주, 기존 파일은 읽은 뒤 Edit, 완료 전 `git diff` 확인 명령 포함 |
| SC-1~5 | 범위 규율 | 마이그레이션·동시성 방식·정책 질문은 확정하지 않고 승인 요청 |
| RR-1~14 | 리뷰 재발 방지 | 4절·1절에 해당 항목 처리 (RR-2 정렬·RR-3 enum·RR-4 벌크·RR-9 대량 조회 해당 없음, RR-4 는 4절 A 선택지 1 채택 시 주의) |

해당 없음: admin 모듈 항목(13~16), 외부 API/WebClient, Soft-delete, 캐시, 아웃박스, 세션 오염 관련 항목. 단 4절 A 에서 DB 제약 위반을 catch 하는 방식을 택하게 되면 11-A/B (세션 재조회 금지, 에러코드 좁혀 판별)를 적용해야 합니다.
