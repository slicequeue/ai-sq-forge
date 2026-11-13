# TC-1 with-skill (java-spring-coder v1.18, 조직 컨벤션 비적용)

쿠폰 사용(Redeem) API 4계층 구현 완료 (로컬 미반영 시뮬레이션, 테스트 미실행, 커밋 전)

- Domain·Infrastructure·Application·Web 4계층 main 13개 파일과 계층별 테스트 5종을 작성했다.
- 조직 컨벤션 판정: 비적용(`.claude/shared/vc-conventions-guide.md` 없음). 프로젝트 규칙 02·03·05 그대로 따랐다. JpaEntity `from()`/`toEntity()`, DTO `of()`/`from()` 정적 팩토리를 쓴다.
- 테스트·review-lint·spotlessApply 는 이 시뮬레이션에서 돌리지 않았다. 아래 "실행 예정 명령"에 적었다.
- 반영 전에 결정이 필요한 충돌 3건이 있다(아래 "확인 필요"). 3건이 풀리기 전에는 저장소에 적용하면 안 된다.

## 확인 필요 (적용 전 결정)

Phase 0 현황 파악에서 실제 저장소(`pasta-japan-server`, 읽기 전용)를 확인한 결과다.

1. **동일 엔드포인트가 이미 있다.** `pasta-api` 의 `com.kakaohealthcare.vc.pasta.coupon` 패키지에 `CouponCommandController` 의 `POST /api/v1/coupons/redeem` 가 이미 구현돼 있다(`CouponCommandService`, `CouponCode`, `CouponRedemption`, `CouponCodeRepository`, `Fake*Repository` 포함). TDD 의 `CouponRedeemController` 를 그대로 추가하면 같은 매핑이 둘이 되어 기동 시 `Ambiguous mapping` 으로 실패한다. 새 엔드포인트 도입은 승인 사안이라(SC-3) 임의로 기존 코드를 지우거나 덮지 않았다.
2. **테이블 `coupon_code` 가 이미 있다.** 기존 `CouponCodeJpaEntity` 가 `coupon_code`(policy, expiry_date, status 등) 를 쓴다. TDD 의 필드(id, code, discountAmount, usedAt, usedBy)는 이 스키마와 다르다. 아래 코드는 충돌을 피하려고 임시로 `coupon_redeem_code` 를 썼다. 이 이름은 내가 정한 가정이다. Flyway 마이그레이션은 TDD 에 없어서 만들지 않았다(SC-3). 마이그레이션 담당과 테이블명 확정이 필요하다.
3. **패키지 루트.** TDD 는 `pghd/coupon/...` 이라고만 적었다. `pasta-api` 의 루트는 `com.kakaohealthcare.vc.pasta` 이므로 `com.kakaohealthcare.vc.pasta.pghd.coupon` 로 풀었다. 기존 `...pasta.coupon` 패키지와 클래스 충돌은 없다. 다만 도메인이 둘로 갈라진다.

권장: 1번이 "기존 기능 재구현" 이면 TDD 를 기존 `coupon` 도메인 기준으로 다시 쓰는 편이 맞다. 아래 코드는 TDD 를 그대로 구현한 결과이며, 사용자가 결정을 내리면 폐기하거나 이식할 수 있다.

### 확인된 것 / 가정한 것

| 구분 | 내용 |
|------|------|
| 확인됨 | `pasta-api` 루트 `com.kakaohealthcare.vc.pasta`, 파일 머리 Copyright 헤더, 2칸 들여쓰기(google-java-format), `@AuthenticationPrincipal Long userId` 패턴 |
| 확인됨 | `/api/v1/coupons/**` 가 `SecurityConstants.airArray` 에 이미 있다(`api` 모듈 `SecurityConstants.java` 63행). 새로 등록할 항목 없음 |
| 확인됨 | `ExceptionConstants.ERROR_COUPON_NOT_FOUND`(404150), `ERROR_COUPON_ALREADY_REDEEMED`(400151) 가 이미 있다. 새 에러 코드를 만들지 않고 재사용 |
| 확인됨 | Spring Boot 3.2.2 라서 `@MockBean` 사용 가능. 컨트롤러 테스트는 기존처럼 `SecurityAutoConfiguration` 제외 |
| 확인됨 | `docs/plans`·`docs/tdd` 에 이번 쿠폰 사용 TDD 파일은 없다. 요청에 붙은 TDD 로 모드 A 진행. 갱신할 체크박스 없음 |
| 가정됨 | 테스트 DB 는 과제 전제대로 모듈 기존 Testcontainers MySQL 설정. 실제 `pasta-api/src/test/resources/application.yml` 은 H2(`jdbc:h2:mem`) 로 보였으나, 과제 전제를 따라 테스트 DB 설정은 건드리지 않았다. 재평가 트리거: 첫 `./gradlew :pasta-api:test` 실행 결과 |
| 가정됨 | 메시지 키 `error.coupon.not.found`, `error.coupon.already.used` 는 기존 쿠폰 예외가 쓰는 키를 재사용했다. 키 정의 파일 위치는 확인하지 못했다 |
| 가정됨 | 동시 사용(같은 코드 두 요청) 방어는 TDD 에 없다. 아래 "작성 전 질문 5개" 2번 참고 |

## 작성 전 질문 5개 (RR-13·14)

1. 조회가 실패하면 사용자는 무엇을 보나: 코드가 없으면 404(`CouponNotFoundException`), 이미 사용했으면 400(`CouponAlreadyUsedException`). 단건 흐름이라 격리할 하위 조회는 없다.
2. 저장이 실패하면: `@Transactional` 한 건이라 롤백된다. 외부 호출은 없다. **같은 코드를 동시에 두 요청이 쓰면 둘 다 `usedAt == null` 을 읽고 둘 다 저장해 마지막 쓰기가 이긴다(중복 사용).** TDD 는 낙관 락·비관 락·조건부 UPDATE 를 정하지 않았다. `@Version` 컬럼 추가(스키마 변경) 또는 `findByCode` 에 `PESSIMISTIC_WRITE` 잠금 중 선택이 필요하다. 합의 없이 넣지 않았다(SC-3). 결정 전에는 이 위험이 열려 있다.
3. 마스터 데이터가 이상하면: `discountAmount` 음수는 도메인 생성자에서 `IllegalArgumentException`, `code` null 은 `requireNonNull` 로 즉시 실패.
4. 기존 경로 동작이 바뀌나: 새 엔드포인트라 기존 동작 변경은 없다. 단 위 1번 충돌이 실제 변경 지점이다.
5. 분기를 깨뜨리면 실패하는 테스트: 미사용 성공, 이미 사용됨, 코드 없음, 빈 코드 검증 400 을 각 계층에 뒀다.

## TDD 비판적 검증 결과

- TDD 는 서비스가 `isUsed()` 판단을 하는지 정하지 않았다. 도메인 `redeem()` 이 `IllegalStateException` 으로 방어하되, 도메인은 `BadRequestException` 을 참조할 수 없다(규칙 06). 그래서 서비스가 `couponCodeEntity.isUsed()` 로 위임 질의 후 `CouponAlreadyUsedException` 을 던진다. 판단 로직은 엔티티에 있고 서비스는 변환만 한다.
- TDD 에 예외 핸들러가 없다. `application/exception` 의 예외를 404/400 으로 바꿀 `web/exception/CouponRedeemExceptionHandler` 를 TDD 밖 파일로 추가했다. 기존 `CouponExceptionHandler` 는 `...pasta.coupon.web` 패키지에만 적용돼 새 패키지를 처리하지 못한다.
- 응답 시각은 `Instant` 로 했다(`*At` 규칙, 기존 쿠폰 코드와 동일).

## 만들 파일 (pasta-api, 루트 `pasta-api/src/main/java/com/kakaohealthcare/vc/pasta/pghd/coupon/`)

### Phase 1. Domain

`domain/CouponCodeEntity.java`

```java
// Copyright 2026 Kakao Healthcare Corp. All Rights Reserved.
package com.kakaohealthcare.vc.pasta.pghd.coupon.domain;

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

  // 쿠폰 코드는 민감 정보라 toString 출력에서 제외합니다.
  @ToString.Exclude private final String code;

  private final long discountAmount;
  private final Instant usedAt;
  private final Long usedBy;

  public CouponCodeEntity(Long id, String code, long discountAmount, Instant usedAt, Long usedBy) {
    Objects.requireNonNull(code, "code must not be null");
    if (discountAmount < 0) {
      throw new IllegalArgumentException("discountAmount must not be negative");
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

  public CouponCodeEntity redeem(Long userId, Instant redeemedAt) {
    Objects.requireNonNull(userId, "userId must not be null");
    Objects.requireNonNull(redeemedAt, "redeemedAt must not be null");
    if (isUsed()) {
      throw new IllegalStateException("이미 사용된 쿠폰 코드입니다.");
    }
    return new CouponCodeEntity(id, code, discountAmount, redeemedAt, userId);
  }

  public boolean isUsed() {
    return usedAt != null;
  }
}
```

`domain/CouponCodeRepository.java`

```java
// Copyright 2026 Kakao Healthcare Corp. All Rights Reserved.
package com.kakaohealthcare.vc.pasta.pghd.coupon.domain;

import java.util.Optional;

public interface CouponCodeRepository {

  Optional<CouponCodeEntity> findByCode(String code);

  CouponCodeEntity save(CouponCodeEntity couponCodeEntity);
}
```

### Phase 2. Infrastructure

`infrastructure/CouponCodeJpaEntity.java`

```java
// Copyright 2026 Kakao Healthcare Corp. All Rights Reserved.
package com.kakaohealthcare.vc.pasta.pghd.coupon.infrastructure;

import java.time.Instant;

import org.hibernate.annotations.Comment;

import com.kakaohealthcare.vc.pasta.pghd.coupon.domain.CouponCodeEntity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.validation.constraints.NotNull;
import lombok.AccessLevel;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

// 기존 coupon_code 테이블과 스키마가 달라 임시 테이블명을 썼습니다. 확정은 마이그레이션 합의 후에 합니다.
@Entity
@Table(name = "coupon_redeem_code")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class CouponCodeJpaEntity {

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  @Comment("쿠폰 코드 일련번호")
  private Long id;

  @NotNull
  @Comment("쿠폰 코드")
  @Column(name = "code", nullable = false, unique = true, length = 100)
  private String code;

  @Comment("할인 금액")
  @Column(name = "discount_amount", nullable = false)
  private long discountAmount;

  @Comment("사용 시각")
  @Column(name = "used_at")
  private Instant usedAt;

  @Comment("사용한 사용자 일련번호")
  @Column(name = "used_by")
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

`infrastructure/CouponCodeJpaRepository.java`

```java
// Copyright 2026 Kakao Healthcare Corp. All Rights Reserved.
package com.kakaohealthcare.vc.pasta.pghd.coupon.infrastructure;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

public interface CouponCodeJpaRepository extends JpaRepository<CouponCodeJpaEntity, Long> {

  Optional<CouponCodeJpaEntity> findByCode(String code);
}
```

`infrastructure/CouponCodeRepositoryImpl.java`

```java
// Copyright 2026 Kakao Healthcare Corp. All Rights Reserved.
package com.kakaohealthcare.vc.pasta.pghd.coupon.infrastructure;

import java.util.Optional;

import org.springframework.stereotype.Repository;

import com.kakaohealthcare.vc.pasta.pghd.coupon.domain.CouponCodeEntity;
import com.kakaohealthcare.vc.pasta.pghd.coupon.domain.CouponCodeRepository;

import lombok.RequiredArgsConstructor;

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

### Phase 3. Application

`application/exception/CouponNotFoundException.java`

```java
// Copyright 2026 Kakao Healthcare Corp. All Rights Reserved.
package com.kakaohealthcare.vc.pasta.pghd.coupon.application.exception;

import com.kakaohealthcare.moneyball.shared.exception.ExceptionConstants;
import com.kakaohealthcare.moneyball.shared.exception.NotFoundException;

public class CouponNotFoundException extends NotFoundException {

  public CouponNotFoundException() {
    super(ExceptionConstants.ERROR_COUPON_NOT_FOUND, "error.coupon.not.found");
  }
}
```

`application/exception/CouponAlreadyUsedException.java`

```java
// Copyright 2026 Kakao Healthcare Corp. All Rights Reserved.
package com.kakaohealthcare.vc.pasta.pghd.coupon.application.exception;

import com.kakaohealthcare.moneyball.shared.exception.BadRequestException;
import com.kakaohealthcare.moneyball.shared.exception.ExceptionConstants;

public class CouponAlreadyUsedException extends BadRequestException {

  public CouponAlreadyUsedException() {
    super(ExceptionConstants.ERROR_COUPON_ALREADY_REDEEMED, "error.coupon.already.used");
  }
}
```

(참고: 기존 `CouponNotFoundException` 은 코드 문자열을 메시지 인자로 넘기지만, 새 예외는 쿠폰 코드를 메시지·로그에 싣지 않도록 인자를 뺐다. 메시지 키가 `{0}` 를 요구하면 이 가정이 깨진다. 미확인.)

`application/CouponRedeemInDto.java`

```java
// Copyright 2026 Kakao Healthcare Corp. All Rights Reserved.
package com.kakaohealthcare.vc.pasta.pghd.coupon.application;

public record CouponRedeemInDto(String code, Long userId) {

  public static CouponRedeemInDto of(String code, Long userId) {
    return new CouponRedeemInDto(code, userId);
  }
}
```

`application/CouponRedeemOutDto.java`

```java
// Copyright 2026 Kakao Healthcare Corp. All Rights Reserved.
package com.kakaohealthcare.vc.pasta.pghd.coupon.application;

import java.time.Instant;

import com.kakaohealthcare.vc.pasta.pghd.coupon.domain.CouponCodeEntity;

public record CouponRedeemOutDto(long discountAmount, Instant usedAt) {

  public static CouponRedeemOutDto from(CouponCodeEntity couponCodeEntity) {
    return new CouponRedeemOutDto(
        couponCodeEntity.getDiscountAmount(), couponCodeEntity.getUsedAt());
  }
}
```

응답에서 쿠폰 코드는 뺐다. 요청자가 이미 알고 있는 값이라 응답 필드로 되돌릴 이유가 없다(YAGNI, 민감 정보 노출 최소화). TDD 는 응답 필드를 정하지 않았다.

`application/CouponRedeemService.java`

```java
// Copyright 2026 Kakao Healthcare Corp. All Rights Reserved.
package com.kakaohealthcare.vc.pasta.pghd.coupon.application;

import java.time.Instant;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.kakaohealthcare.vc.pasta.pghd.coupon.application.exception.CouponAlreadyUsedException;
import com.kakaohealthcare.vc.pasta.pghd.coupon.application.exception.CouponNotFoundException;
import com.kakaohealthcare.vc.pasta.pghd.coupon.domain.CouponCodeEntity;
import com.kakaohealthcare.vc.pasta.pghd.coupon.domain.CouponCodeRepository;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Service
@RequiredArgsConstructor
public class CouponRedeemService {

  private final CouponCodeRepository couponCodeRepository;

  @Transactional
  public CouponRedeemOutDto redeem(CouponRedeemInDto couponRedeemInDto) {
    Instant currentAt = Instant.now();

    CouponCodeEntity couponCodeEntity =
        couponCodeRepository
            .findByCode(couponRedeemInDto.code())
            .orElseThrow(CouponNotFoundException::new);

    // 사용 여부 판단은 엔티티에 위임하고, 서비스는 예외 변환만 합니다.
    if (couponCodeEntity.isUsed()) {
      throw new CouponAlreadyUsedException();
    }

    CouponCodeEntity redeemedCouponCodeEntity =
        couponCodeEntity.redeem(couponRedeemInDto.userId(), currentAt);
    CouponCodeEntity savedCouponCodeEntity = couponCodeRepository.save(redeemedCouponCodeEntity);

    log.info(
        "[CouponRedeemService.redeem] 쿠폰 사용 완료: couponCodeId={}",
        savedCouponCodeEntity.getId());
    return CouponRedeemOutDto.from(savedCouponCodeEntity);
  }
}
```

로그에는 사용자 식별자와 쿠폰 코드를 넣지 않고 비즈니스 식별자(`couponCodeId`)만 남겼다.

### Phase 4. Web

`web/CouponRedeemRequest.java`

```java
// Copyright 2026 Kakao Healthcare Corp. All Rights Reserved.
package com.kakaohealthcare.vc.pasta.pghd.coupon.web;

import com.kakaohealthcare.vc.pasta.pghd.coupon.application.CouponRedeemInDto;

import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.validation.constraints.NotBlank;

public record CouponRedeemRequest(@Schema(description = "쿠폰 코드") @NotBlank String code) {

  public CouponRedeemInDto toInDto(Long userId) {
    return CouponRedeemInDto.of(code, userId);
  }
}
```

`web/CouponRedeemResponse.java`

```java
// Copyright 2026 Kakao Healthcare Corp. All Rights Reserved.
package com.kakaohealthcare.vc.pasta.pghd.coupon.web;

import java.time.Instant;

import com.kakaohealthcare.vc.pasta.pghd.coupon.application.CouponRedeemOutDto;

import io.swagger.v3.oas.annotations.media.Schema;

public record CouponRedeemResponse(
    @Schema(description = "할인 금액") long discountAmount,
    @Schema(description = "사용 시각") Instant usedAt) {

  public static CouponRedeemResponse from(CouponRedeemOutDto couponRedeemOutDto) {
    return new CouponRedeemResponse(couponRedeemOutDto.discountAmount(), couponRedeemOutDto.usedAt());
  }
}
```

`web/CouponRedeemController.java`

```java
// Copyright 2026 Kakao Healthcare Corp. All Rights Reserved.
package com.kakaohealthcare.vc.pasta.pghd.coupon.web;

import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.kakaohealthcare.moneyball.shared.dto.BaseErrorResponse;
import com.kakaohealthcare.vc.pasta.pghd.coupon.application.CouponRedeemOutDto;
import com.kakaohealthcare.vc.pasta.pghd.coupon.application.CouponRedeemService;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/coupons")
@Tag(name = "Coupon Redeem API", description = "쿠폰 사용 API")
public class CouponRedeemController {

  private final CouponRedeemService couponRedeemService;

  @PostMapping("/redeem")
  @Operation(summary = "쿠폰 사용", description = "쿠폰 코드를 입력해 사용 처리하고 할인 금액과 사용 시각을 반환합니다.")
  @ApiResponse(responseCode = "200", description = "쿠폰 사용 성공")
  @ApiResponse(
      responseCode = "400",
      description = "**400151** (ERROR_COUPON_ALREADY_REDEEMED): 이미 사용된 쿠폰 코드",
      content =
          @Content(
              mediaType = "application/json",
              schema = @Schema(implementation = BaseErrorResponse.class)))
  @ApiResponse(
      responseCode = "404",
      description = "**404150** (ERROR_COUPON_NOT_FOUND): 존재하지 않는 쿠폰 코드",
      content =
          @Content(
              mediaType = "application/json",
              schema = @Schema(implementation = BaseErrorResponse.class)))
  public ResponseEntity<CouponRedeemResponse> redeem(
      @AuthenticationPrincipal Long userId,
      @RequestBody @Valid CouponRedeemRequest couponRedeemRequest) {
    CouponRedeemOutDto couponRedeemOutDto =
        couponRedeemService.redeem(couponRedeemRequest.toInDto(userId));
    return ResponseEntity.ok(CouponRedeemResponse.from(couponRedeemOutDto));
  }
}
```

`web/exception/CouponRedeemExceptionHandler.java` (TDD 밖 추가)

```java
// Copyright 2026 Kakao Healthcare Corp. All Rights Reserved.
package com.kakaohealthcare.vc.pasta.pghd.coupon.web.exception;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import com.kakaohealthcare.moneyball.shared.dto.BaseErrorResponse;
import com.kakaohealthcare.vc.pasta.pghd.coupon.application.exception.CouponAlreadyUsedException;
import com.kakaohealthcare.vc.pasta.pghd.coupon.application.exception.CouponNotFoundException;

import lombok.extern.log4j.Log4j2;

@RestControllerAdvice(basePackages = "com.kakaohealthcare.vc.pasta.pghd.coupon.web")
@Log4j2
public class CouponRedeemExceptionHandler {

  @ExceptionHandler(CouponNotFoundException.class)
  public ResponseEntity<BaseErrorResponse> handleCouponNotFoundException(
      CouponNotFoundException couponNotFoundException) {
    log.warn("[CouponRedeemExceptionHandler.handleCouponNotFoundException] 존재하지 않는 쿠폰 코드 요청");
    return new ResponseEntity<>(couponNotFoundException.toErrorResponse(), HttpStatus.NOT_FOUND);
  }

  @ExceptionHandler(CouponAlreadyUsedException.class)
  public ResponseEntity<BaseErrorResponse> handleCouponAlreadyUsedException(
      CouponAlreadyUsedException couponAlreadyUsedException) {
    log.warn("[CouponRedeemExceptionHandler.handleCouponAlreadyUsedException] 이미 사용된 쿠폰 코드 요청");
    return new ResponseEntity<>(
        couponAlreadyUsedException.toErrorResponse(), HttpStatus.BAD_REQUEST);
  }
}
```

### 설정

- `SecurityConstants.airArray`: `/api/v1/coupons/**` 가 이미 등록돼 있어 변경하지 않았다.
- 새 환경변수·외부 API 없음. 환경별 yml 4곳 변경 없음.
- Flyway 마이그레이션: 위 "확인 필요" 2번 때문에 만들지 않았다.

## 테스트 (루트 `pasta-api/src/test/java/com/kakaohealthcare/vc/pasta/pghd/coupon/`)

`domain/CouponCodeFixture.java`

```java
// Copyright 2026 Kakao Healthcare Corp. All Rights Reserved.
package com.kakaohealthcare.vc.pasta.pghd.coupon.domain;

import java.time.Instant;

public class CouponCodeFixture {

  public static final String DEFAULT_CODE = "SAVE5000";
  public static final long DEFAULT_DISCOUNT_AMOUNT = 5000L;
  public static final Long DEFAULT_USER_ID = 1L;
  public static final Instant DEFAULT_USED_AT = Instant.parse("2026-11-13T00:00:00Z");

  private CouponCodeFixture() {}

  public static CouponCodeEntity createUnused() {
    return CouponCodeEntity.of(DEFAULT_CODE, DEFAULT_DISCOUNT_AMOUNT);
  }

  public static CouponCodeEntity createUsed() {
    return new CouponCodeEntity(
        null, DEFAULT_CODE, DEFAULT_DISCOUNT_AMOUNT, DEFAULT_USED_AT, DEFAULT_USER_ID);
  }
}
```

`domain/FakeCouponCodeRepository.java`

```java
// Copyright 2026 Kakao Healthcare Corp. All Rights Reserved.
package com.kakaohealthcare.vc.pasta.pghd.coupon.domain;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class FakeCouponCodeRepository implements CouponCodeRepository {

  private final Map<String, CouponCodeEntity> couponCodeEntityByCode = new HashMap<>();
  private long nextId = 1L;

  @Override
  public Optional<CouponCodeEntity> findByCode(String code) {
    return Optional.ofNullable(couponCodeEntityByCode.get(code));
  }

  @Override
  public CouponCodeEntity save(CouponCodeEntity couponCodeEntity) {
    Long id = couponCodeEntity.getId() != null ? couponCodeEntity.getId() : nextId++;
    CouponCodeEntity savedCouponCodeEntity =
        new CouponCodeEntity(
            id,
            couponCodeEntity.getCode(),
            couponCodeEntity.getDiscountAmount(),
            couponCodeEntity.getUsedAt(),
            couponCodeEntity.getUsedBy());
    couponCodeEntityByCode.put(savedCouponCodeEntity.getCode(), savedCouponCodeEntity);
    return savedCouponCodeEntity;
  }
}
```

`domain/CouponCodeEntityTest.java`

```java
// Copyright 2026 Kakao Healthcare Corp. All Rights Reserved.
package com.kakaohealthcare.vc.pasta.pghd.coupon.domain;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.time.Instant;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("CouponCodeEntity 테스트")
class CouponCodeEntityTest {

  @Test
  @DisplayName("코드와 할인 금액으로 생성하면 미사용 상태이고 사용 시각과 사용자가 비어 있다")
  void of_codeAndDiscountAmount_createsUnusedEntity() {
    // Given & When
    CouponCodeEntity couponCodeEntity = CouponCodeEntity.of("SAVE5000", 5000L);

    // Then
    assertThat(couponCodeEntity.isUsed()).isFalse();
    assertThat(couponCodeEntity.getUsedAt()).isNull();
    assertThat(couponCodeEntity.getUsedBy()).isNull();
    assertThat(couponCodeEntity.getDiscountAmount()).isEqualTo(5000L);
  }

  @Test
  @DisplayName("미사용 쿠폰을 사용 처리하면 사용 시각과 사용자가 채워진 새 엔티티가 반환된다")
  void redeem_unusedCoupon_returnsRedeemedEntity() {
    // Given
    CouponCodeEntity couponCodeEntity = CouponCodeFixture.createUnused();
    Instant redeemedAt = Instant.parse("2026-11-13T01:00:00Z");

    // When
    CouponCodeEntity redeemedCouponCodeEntity = couponCodeEntity.redeem(7L, redeemedAt);

    // Then
    assertThat(redeemedCouponCodeEntity.isUsed()).isTrue();
    assertThat(redeemedCouponCodeEntity.getUsedAt()).isEqualTo(redeemedAt);
    assertThat(redeemedCouponCodeEntity.getUsedBy()).isEqualTo(7L);
    assertThat(couponCodeEntity.isUsed()).isFalse();
  }

  @Test
  @DisplayName("이미 사용된 쿠폰을 다시 사용 처리하면 IllegalStateException 이 발생한다")
  void redeem_usedCoupon_throwsIllegalStateException() {
    // Given
    CouponCodeEntity usedCouponCodeEntity = CouponCodeFixture.createUsed();

    // When & Then
    assertThatThrownBy(() -> usedCouponCodeEntity.redeem(2L, Instant.now()))
        .isInstanceOf(IllegalStateException.class);
  }

  @Test
  @DisplayName("코드가 null 이면 생성 시점에 NullPointerException 이 발생한다")
  void of_nullCode_throwsNullPointerException() {
    // When & Then
    assertThatThrownBy(() -> CouponCodeEntity.of(null, 5000L))
        .isInstanceOf(NullPointerException.class);
  }

  @Test
  @DisplayName("할인 금액이 음수이면 생성 시점에 IllegalArgumentException 이 발생한다")
  void of_negativeDiscountAmount_throwsIllegalArgumentException() {
    // When & Then
    assertThatThrownBy(() -> CouponCodeEntity.of("SAVE5000", -1L))
        .isInstanceOf(IllegalArgumentException.class);
  }

  @Test
  @DisplayName("toString 출력에 쿠폰 코드가 포함되지 않는다")
  void toString_excludesCouponCode() {
    // Given
    CouponCodeEntity couponCodeEntity = CouponCodeFixture.createUnused();

    // When & Then
    assertThat(couponCodeEntity.toString()).doesNotContain(CouponCodeFixture.DEFAULT_CODE);
  }
}
```

`infrastructure/CouponCodeRepositoryImplTest.java`

```java
// Copyright 2026 Kakao Healthcare Corp. All Rights Reserved.
package com.kakaohealthcare.vc.pasta.pghd.coupon.infrastructure;

import static org.assertj.core.api.Assertions.assertThat;

import java.time.Instant;
import java.util.Optional;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ActiveProfiles;

import com.kakaohealthcare.vc.pasta.pghd.coupon.domain.CouponCodeEntity;
import com.kakaohealthcare.vc.pasta.pghd.coupon.domain.CouponCodeFixture;

// 테스트 DB 는 모듈의 기존 Testcontainers 설정을 그대로 사용하므로 임베디드 DB 로 교체하지 않습니다.
@DataJpaTest
@ActiveProfiles("test")
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Import(CouponCodeRepositoryImpl.class)
@DisplayName("CouponCodeRepositoryImpl 테스트")
class CouponCodeRepositoryImplTest {

  @Autowired private CouponCodeRepositoryImpl couponCodeRepositoryImpl;

  @Test
  @DisplayName("저장한 쿠폰 코드를 코드로 조회하면 같은 값의 도메인 엔티티가 반환된다")
  void findByCode_savedCode_returnsEntity() {
    // Given
    couponCodeRepositoryImpl.save(CouponCodeFixture.createUnused());

    // When
    Optional<CouponCodeEntity> foundCouponCodeEntity =
        couponCodeRepositoryImpl.findByCode(CouponCodeFixture.DEFAULT_CODE);

    // Then
    assertThat(foundCouponCodeEntity).isPresent();
    assertThat(foundCouponCodeEntity.get().getId()).isNotNull();
    assertThat(foundCouponCodeEntity.get().getDiscountAmount())
        .isEqualTo(CouponCodeFixture.DEFAULT_DISCOUNT_AMOUNT);
  }

  @Test
  @DisplayName("존재하지 않는 코드로 조회하면 빈 Optional 이 반환된다")
  void findByCode_unknownCode_returnsEmpty() {
    // When
    Optional<CouponCodeEntity> foundCouponCodeEntity =
        couponCodeRepositoryImpl.findByCode("UNKNOWN");

    // Then
    assertThat(foundCouponCodeEntity).isEmpty();
  }

  @Test
  @DisplayName("사용 처리한 엔티티를 저장하면 사용 시각과 사용자가 영속화된다")
  void save_redeemedEntity_persistsUsedAtAndUsedBy() {
    // Given
    CouponCodeEntity savedCouponCodeEntity =
        couponCodeRepositoryImpl.save(CouponCodeFixture.createUnused());
    Instant redeemedAt = Instant.parse("2026-11-13T01:00:00Z");

    // When
    couponCodeRepositoryImpl.save(savedCouponCodeEntity.redeem(9L, redeemedAt));
    CouponCodeEntity foundCouponCodeEntity =
        couponCodeRepositoryImpl.findByCode(CouponCodeFixture.DEFAULT_CODE).orElseThrow();

    // Then
    assertThat(foundCouponCodeEntity.isUsed()).isTrue();
    assertThat(foundCouponCodeEntity.getUsedBy()).isEqualTo(9L);
    assertThat(foundCouponCodeEntity.getUsedAt()).isEqualTo(redeemedAt);
  }
}
```

`application/CouponRedeemServiceTest.java`

```java
// Copyright 2026 Kakao Healthcare Corp. All Rights Reserved.
package com.kakaohealthcare.vc.pasta.pghd.coupon.application;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import com.kakaohealthcare.vc.pasta.pghd.coupon.application.exception.CouponAlreadyUsedException;
import com.kakaohealthcare.vc.pasta.pghd.coupon.application.exception.CouponNotFoundException;
import com.kakaohealthcare.vc.pasta.pghd.coupon.domain.CouponCodeEntity;
import com.kakaohealthcare.vc.pasta.pghd.coupon.domain.CouponCodeFixture;
import com.kakaohealthcare.vc.pasta.pghd.coupon.domain.FakeCouponCodeRepository;

@DisplayName("CouponRedeemService 테스트")
class CouponRedeemServiceTest {

  private FakeCouponCodeRepository fakeCouponCodeRepository;
  private CouponRedeemService couponRedeemService;

  @BeforeEach
  void setUp() {
    fakeCouponCodeRepository = new FakeCouponCodeRepository();
    couponRedeemService = new CouponRedeemService(fakeCouponCodeRepository);
  }

  @Test
  @DisplayName("미사용 쿠폰 코드로 사용 요청하면 할인 금액과 사용 시각이 반환된다")
  void redeem_unusedCode_returnsOutDto() {
    // Given
    fakeCouponCodeRepository.save(CouponCodeFixture.createUnused());
    CouponRedeemInDto couponRedeemInDto =
        CouponRedeemInDto.of(CouponCodeFixture.DEFAULT_CODE, CouponCodeFixture.DEFAULT_USER_ID);

    // When
    CouponRedeemOutDto couponRedeemOutDto = couponRedeemService.redeem(couponRedeemInDto);

    // Then
    assertThat(couponRedeemOutDto.discountAmount())
        .isEqualTo(CouponCodeFixture.DEFAULT_DISCOUNT_AMOUNT);
    assertThat(couponRedeemOutDto.usedAt()).isNotNull();
  }

  @Test
  @DisplayName("사용 요청이 성공하면 저장소의 쿠폰이 요청 사용자로 사용 처리된다")
  void redeem_unusedCode_marksStoredCouponAsUsedByUser() {
    // Given
    fakeCouponCodeRepository.save(CouponCodeFixture.createUnused());

    // When
    couponRedeemService.redeem(CouponRedeemInDto.of(CouponCodeFixture.DEFAULT_CODE, 5L));

    // Then
    CouponCodeEntity storedCouponCodeEntity =
        fakeCouponCodeRepository.findByCode(CouponCodeFixture.DEFAULT_CODE).orElseThrow();
    assertThat(storedCouponCodeEntity.isUsed()).isTrue();
    assertThat(storedCouponCodeEntity.getUsedBy()).isEqualTo(5L);
  }

  @Test
  @DisplayName("존재하지 않는 쿠폰 코드로 요청하면 CouponNotFoundException 이 발생한다")
  void redeem_unknownCode_throwsCouponNotFoundException() {
    // Given
    CouponRedeemInDto couponRedeemInDto = CouponRedeemInDto.of("UNKNOWN", 1L);

    // When & Then
    assertThatThrownBy(() -> couponRedeemService.redeem(couponRedeemInDto))
        .isInstanceOf(CouponNotFoundException.class);
  }

  @Test
  @DisplayName("이미 사용된 쿠폰 코드로 요청하면 CouponAlreadyUsedException 이 발생하고 기존 사용 정보는 바뀌지 않는다")
  void redeem_usedCode_throwsCouponAlreadyUsedExceptionAndKeepsUsage() {
    // Given
    fakeCouponCodeRepository.save(CouponCodeFixture.createUsed());
    CouponRedeemInDto couponRedeemInDto = CouponRedeemInDto.of(CouponCodeFixture.DEFAULT_CODE, 99L);

    // When & Then
    assertThatThrownBy(() -> couponRedeemService.redeem(couponRedeemInDto))
        .isInstanceOf(CouponAlreadyUsedException.class);
    CouponCodeEntity storedCouponCodeEntity =
        fakeCouponCodeRepository.findByCode(CouponCodeFixture.DEFAULT_CODE).orElseThrow();
    assertThat(storedCouponCodeEntity.getUsedBy()).isEqualTo(CouponCodeFixture.DEFAULT_USER_ID);
  }
}
```

`web/CouponRedeemControllerTest.java`

```java
// Copyright 2026 Kakao Healthcare Corp. All Rights Reserved.
package com.kakaohealthcare.vc.pasta.pghd.coupon.web;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.time.Instant;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.context.ContextConfiguration;
import org.springframework.test.web.servlet.MockMvc;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.kakaohealthcare.vc.pasta.pghd.coupon.application.CouponRedeemOutDto;
import com.kakaohealthcare.vc.pasta.pghd.coupon.application.CouponRedeemService;
import com.kakaohealthcare.vc.pasta.pghd.coupon.application.exception.CouponAlreadyUsedException;
import com.kakaohealthcare.vc.pasta.pghd.coupon.application.exception.CouponNotFoundException;
import com.kakaohealthcare.vc.pasta.pghd.coupon.web.exception.CouponRedeemExceptionHandler;

@WebMvcTest(
    controllers = CouponRedeemController.class,
    excludeAutoConfiguration = SecurityAutoConfiguration.class)
@ContextConfiguration(classes = {CouponRedeemController.class, CouponRedeemExceptionHandler.class})
@DisplayName("CouponRedeemController 테스트")
class CouponRedeemControllerTest {

  private static final String REDEEM_URL = "/api/v1/coupons/redeem";

  @Autowired private MockMvc mockMvc;

  @Autowired private ObjectMapper objectMapper;

  @MockBean private CouponRedeemService couponRedeemService;

  @Test
  @DisplayName("유효한 쿠폰 코드로 요청하면 200 과 할인 금액·사용 시각이 응답된다")
  void redeem_validRequest_returnsOk() throws Exception {
    // Given
    Instant usedAt = Instant.parse("2026-11-13T00:00:00Z");
    given(couponRedeemService.redeem(any())).willReturn(new CouponRedeemOutDto(5000L, usedAt));

    // When & Then
    mockMvc
        .perform(
            post(REDEEM_URL)
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(new CouponRedeemRequest("SAVE5000"))))
        .andExpect(status().isOk())
        .andExpect(jsonPath("$.discountAmount").value(5000));
  }

  @Test
  @DisplayName("쿠폰 코드가 공백이면 400 이 응답되고 서비스는 호출되지 않는다")
  void redeem_blankCode_returnsBadRequest() throws Exception {
    // When & Then
    mockMvc
        .perform(
            post(REDEEM_URL)
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(new CouponRedeemRequest(" "))))
        .andExpect(status().isBadRequest());
    verify(couponRedeemService, never()).redeem(any());
  }

  @Test
  @DisplayName("존재하지 않는 쿠폰 코드면 404 가 응답된다")
  void redeem_unknownCode_returnsNotFound() throws Exception {
    // Given
    given(couponRedeemService.redeem(any())).willThrow(new CouponNotFoundException());

    // When & Then
    mockMvc
        .perform(
            post(REDEEM_URL)
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(new CouponRedeemRequest("UNKNOWN"))))
        .andExpect(status().isNotFound());
  }

  @Test
  @DisplayName("이미 사용된 쿠폰 코드면 400 이 응답된다")
  void redeem_usedCode_returnsBadRequest() throws Exception {
    // Given
    given(couponRedeemService.redeem(any())).willThrow(new CouponAlreadyUsedException());

    // When & Then
    mockMvc
        .perform(
            post(REDEEM_URL)
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(new CouponRedeemRequest("SAVE5000"))))
        .andExpect(status().isBadRequest());
  }
}
```

## 실행 예정 명령 (모두 미실행)

```bash
cd /Users/kakao/workplace-kakao/global/pasta-japan/server/pasta-japan-server
git status --short pasta-api/src/main/java/com/kakaohealthcare/vc/pasta/pghd pasta-api/src/test/java/com/kakaohealthcare/vc/pasta/pghd   # DW-1 신규 경로 충돌 확인
export JAVA_HOME=$(/usr/libexec/java_home -v 21)
./gradlew :pasta-api:spotlessApply
./gradlew :pasta-api:cleanTest :pasta-api:test --tests "*pghd.coupon*"   # Docker 실행 필요(Testcontainers)
python3 forge/common/review-lint.py
```

`review-lint.py` 는 출력 마지막 줄이 "조직 컨벤션 검사 꺼짐" 인지 확인한다(비적용 판정과 일치해야 함).

## 자기 검증 (작성한 코드 기준, 실행 검증 아님)

- 계층: Domain 은 Lombok·JDK 만 쓰고 JPA/Spring 이 없다. Application 은 Domain 인터페이스와 `application/exception` 만 참조한다. Web 은 Application 만 참조한다. 의존 방향 위반 없음.
- Lombok: Domain `@Getter`·`@ToString`·`@EqualsAndHashCode` 모두 사용, `@Setter`·`@Data` 없음. JPA 는 생성자 레벨 `@Builder`.
- JPA NOT NULL: `code` 에 `@Column(nullable=false)` + `@NotNull` 병행. `long discountAmount` 는 primitive 라 `@NotNull` 생략.
- `var`, 와일드카드 import, FQCN 인라인 없음. 테스트의 mock 예외도 import 후 단순 이름.
- 주석 문체: 코드 블록 주석 줄만 훑었다. `// 쿠폰 코드는 ... 제외합니다.`, `// 기존 coupon_code ... 합니다.`, `// 사용 여부 판단은 ... 합니다.`, `// 테스트 DB 는 ... 않습니다.` 모두 존댓말이고 `한다.`·`된다.` 끝맺음 0건. `// Given`·`// When & Then` 은 구분 표지다.
- 로그: 접두사 `[ClassName.method]`, userId·쿠폰 코드 미포함.
- 테스트 스타일: `@DisplayName` 한글 구체 시나리오, Given-When-Then, AssertJ only. Domain/Application 은 Fake, Web 은 MockMvc, Infra 는 모듈 기존 테스트 DB 설정 유지(H2 전환·설정 변경 없음).
- 커밋·stash·마이그레이션 파일 변경 없음.

미확인:
- 모든 테스트 통과 여부, `spotlessApply` 후 포맷 차이, `review-lint` 위반 0건 여부.
- `@DataJpaTest` 가 실제로 Testcontainers MySQL 에 붙는지(`@AutoConfigureTestDatabase(replace = NONE)` 는 내가 넣은 가정).
- 컨트롤러 테스트에서 `@AuthenticationPrincipal Long userId` 는 `SecurityAutoConfiguration` 제외로 바인딩되지 않아(null) 서비스에 넘어간 사용자 식별자는 검증하지 못한다. 인증 주체 바인딩은 보안 통합 테스트 범위다.
- 메시지 키 2개의 정의 위치와 `{0}` 인자 유무.

## 범위 밖 제안 (고치지 않음)

- 기존 `...pasta.coupon` 도메인과 이번 `...pasta.pghd.coupon` 도메인의 통합 또는 폐기 결정.
- 동시 사용 방어(`@Version` 또는 비관적 락) 도입 여부.
