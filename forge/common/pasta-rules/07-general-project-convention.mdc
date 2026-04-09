---
description: 프로젝트 전역 아키텍처, 공통 기술 스택 및 코딩 스타일
globs:
alwaysApply: true
---
# Project Context & Persona
당신은 **Clean Architecture**와 **Hexagonal Architecture**를 엄격히 준수하는 시니어 Java Spring Boot 개발자입니다.
우리 프로젝트는 비즈니스 로직의 순수성을 지키기 위해 **Domain Layer**와 **Infrastructure Layer**를 철저히 분리합니다.

# Core Technology Stack
- **Language**: Java 17+
- **Framework**: Spring Boot 3.x
- **Persistence**: Spring Data JPA, QueryDSL
- **Utils**: Lombok (제한적 사용 - 각 레이어별 규칙 준수)
- **Documentation**: Swagger (OAS 3)

# General Principles
1. **Domain Purity**: `domain` 패키지는 Spring이나 JPA 의존성을 가지지 않도록 노력합니다.
2. **Immutability**: 가능하면 불변 객체를 지향합니다. DTO/값 객체는 `record`, 도메인 엔티티는 `final` 필드의 `class` 사용 (domain-entity-convention 참고).
3. **Separation of Concerns**: 기술적인 구현(DB, Web)은 비즈니스 로직(Domain)에 침투하지 않아야 합니다.
4. **YAGNI**: 실제 사용되지 않는 코드는 미리 작성하지 않습니다.

# Code Style & Convention

## 1. Import Convention
- ✅ **Explicit Imports**: 클래스 사용 시 `import`로 선언하여 간단한 클래스명 사용. 전체 패키지 경로 직접 사용 금지.
- ✅ **Static Imports**: 자주 사용하는 상수나 유틸리티 메서드는 정적 임포트 허용.
- ❌ **No Wildcards**: `import java.util.*` 금지.

## 2. Logging
- ✅ **Use Slf4j**: `@Log4j2` 또는 `@Slf4j` 사용.
- ✅ **Levels**:
    - `ERROR`: 시스템 장애, 핸들링되지 않은 예외 (반드시 Stack Trace 포함)
    - `WARN`: 잠재적 문제, 비즈니스 예외 (Stack Trace 불필요)
    - `INFO`: 주요 비즈니스 이벤트 (개인정보 마스킹 필수)
    - `DEBUG`: 개발용 상세 정보
- ❌ **No PII**: 개인정보(userId, 전화번호 등) 로깅 절대 금지. userId는 MDC에 포함되어 있으므로 로그 본문에 넣지 않는다.
- ✅ **메시지 형식**: `[ClassName.methodName] 설명: key1={}, key2={}` 형식을 사용한다.
  - 접두사 `[ClassName.methodName]`으로 로그 발생 위치를 명시한다.
  - 비즈니스 식별자(couponCodeId, redemptionId 등)는 파라미터로 포함 가능하다.
  - 이미 메서드 내 객체에서 접근 가능한 값은 별도 파라미터로 중복 전달하지 않는다.
  ```java
  // ✅ 좋은 예
  log.warn("[CouponRedeemService.save] 쿠폰 중복 사용 시도: couponCodeId={}, code={}",
      couponCode.getId(), couponCode.getCode());

  // ❌ 나쁜 예: 접두사 없음, userId(PII) 포함
  log.warn("쿠폰 중복 사용 시도: userId={}, couponCodeId={}", userId, couponCode.getId());
  ```

## 3. Programming Style
- **Early Return**: `else` 사용을 지양하고 조건이 맞지 않으면 즉시 반환하여 들여쓰기를 줄입니다.
- **Constants**: 하드코딩된 값은 상수로 추출.

### 3.1 JavaDoc & 주석 (Comments)

- **JavaDoc**: 외부 계약이 드러나는 공개 API 중 **부작용·선행조건·비명확한 동작**을 설명해야 할 때만 작성한다. Getter/Setter, private 필드, 단순 값 객체 필드에 대한 **자명한 설명**은 쓰지 않는다.
- **금지**: `{@code 파라미터명}` 등으로 **시그니처를 한글로 반복**하는 JavaDoc, 코드와 동일한 내용의 인라인 주석(“오늘 기록 조회”, “이전 값 계산” 등 이름으로 충분한 경우).
- **허용(인라인)**: 비즈니스 규칙·예외 케이스·**왜(why)** 이렇게 구현했는지처럼 **코드만으로 전달되지 않는 맥락**만 짧게 남긴다.
- **API 문서 우선**: HTTP/스키마 설명은 가능하면 `@Schema(description = "...")`, DB 코멘트는 `@Comment("...")` 등 **선언부 메타데이터**에 두고, 본문 주석으로 중복하지 않는다.
- **Clean code**: 의미 없는 주석은 쓰지 않는다. 설명이 필요하면 **이름 리팩터링·메서드 분리**를 먼저 검토한다.

## 4. ThreadLocal 유틸리티 사용 규칙

프로젝트 전반에서 요청 스레드에 바인딩된 유틸리티를 사용합니다. 각 유틸리티의 역할과 사용 위치를 준수합니다.

| 유틸리티 | 역할 | 사용 위치 | 비고 |
|---------|------|----------|------|
| `TimeZoneContext.getZoneId()` | 요청 헤더 기반 타임존 (`ZoneId`) | **Web(Controller)** | 인터셉터가 자동 세팅. Service에는 `ZoneId` 파라미터로 전달 |
| `MessageUtil.getMessage(key)` | i18n 메시지 조회 (내부에서 `LocaleContextHolder` 사용) | **Application 이하** | `MessageSource` 직접 주입 대신 정적 메서드 사용 |
| `LocaleContextHolder.getLocale()` | 현재 요청 로케일 | **Infrastructure(외부 API 호출)** | Application/Web에서는 직접 사용하지 않음. 메시지 조회는 `MessageUtil`로 대체 |

- ✅ **Controller**: `TimeZoneContext.getZoneId()`로 타임존을 얻어 Service 파라미터로 전달.
- ✅ **Application/Support**: i18n 메시지가 필요하면 `MessageUtil.getMessage(key)` 사용. `MessageSource` 빈 주입 불필요.
- ✅ **Infrastructure**: 외부 API 호출 시 로케일이 필요하면 `LocaleContextHolder.getLocale()` 직접 사용.
- ❌ **Service 파라미터로 `Locale` 전달 금지**: `MessageUtil`이 내부에서 `LocaleContextHolder`를 사용하므로, Service 메서드에 `Locale`을 파라미터로 넘기지 않습니다.
- 📝 **테스트**: `TimeZoneContext`는 `@BeforeEach`에서 `addTimeZone()`, `@AfterEach`에서 `clear()` 호출. `MessageUtil`은 `MockedStatic<MessageUtil>`로 모킹.

## 5. Service Method Naming Convention

- ✅ **Client Service / Query Service 메서드 네이밍 규칙**:
  - **여러 개 조회**: `getAll*` 패턴 사용 (예: `getAllMealRecordsByUserIdAndDateAndTimeZone`)
  - **단일 조회 (null 가능)**: `get*OrElseNull` 패턴 사용 (예: `getMealRecordByIdOrElseNull`)
  - **단일 조회 (Optional 반환)**: `find*` 패턴 사용 (예: `findById`, `findLastRecorded`)
  - **존재 여부 확인**: `exist*` 또는 `has*` 패턴 사용 (예: `existWeightRecords`)
  - **카운트 조회**: `get*CountBy` 패턴 사용 (예: `getInjectionRecordCountBy`)

- ❌ **금지 사항**:
  - 여러 개 조회에 `find*` 사용 금지 (예: `findMealRecordsBy*` → `getAllMealRecordsBy*`)
  - 단일 조회(null 가능)에 `find*` 사용 금지 (예: `findMealRecordById` → `getMealRecordByIdOrElseNull`)

- 📝 **참고**: Repository 인터페이스는 Spring Data JPA 컨벤션을 따르므로 `find*` 패턴을 사용합니다. 페이징 조회를 반환하는 메서드는 가독성 위해 `getPage*` 패턴 사용을 권장합니다 (예: `getPageByUserIdAndIds`).

- ✅ **Application Service 내부 private 메서드 네이밍** (외부 노출되지 않는 헬퍼):
  - **여러 개 조회**: `getAll*By*` 패턴으로 조회 대상·조건을 명시 (예: `getAllRecentWorkoutTypesByUserId`).
  - **단일 변환 (null 반환 가능)**: `to*OrNull` 접미사 사용 (예: `toItemDtoOrNull`). null을 반환할 수 있는 변환 메서드는 `to*` 대신 `to*OrNull`로 구분합니다.
  - **매핑·그룹핑 변환**: `map*To*` 패턴으로 의도 표현 (예: `mapTypesToCategories`). `build*`보다 변환 결과가 명확합니다.

## 6. 정렬 (Comparator)

- ✅ **단순 비교**: 정렬 기준이 단일 필드(예: id)일 때는 `Comparator.comparing(Entity::getId)` 등으로 충분합니다.
- ❌ **불필요한 복잡도 지양**: 로케일 기반 문자열 정렬이 필요하지 않으면 `Locale`, `Collator`, `LocaleContextHolder` 등 도입하지 않습니다. 요구사항에 맞는 최소 구현을 유지합니다.

## 7. Copyright

- ✅ **연도 기준**: 파일 최상단 Copyright 연도는 **해당 파일이 최초 생성된 연도**를 사용합니다. 프로젝트 또는 리포지터리 생성 연도가 아닌, 파일 단위 생성 시점을 기준으로 합니다.
- ✅ **신규 생성 파일**: 새로 생성하는 파일은 반드시 **생성 시점의 연도(현재 연도)**를 Copyright에 사용합니다. 기존 파일을 복사해 만든 경우에도, 새 파일로 최초 생성된 시점의 연도를 씁니다.

## 8. Build & Test Convention

- ✅ **JDK 21 필수**: 모든 빌드 및 테스트는 JDK 21로 실행해야 합니다 (`export JAVA_HOME=$(/usr/libexec/java_home -v 21)`).
- ✅ **빌드 전 체크리스트**: 코드 수정 후 다음 순서로 확인
  1. JDK 21 설정 확인
  2. **spotless 포맷팅**:
     - **pasta-api 모듈**: 커밋/푸시 전 **항상** 자동 적용 (`./gradlew :pasta-api:spotlessApply`)
     - **그 외 모듈**: 필요 시 수동 적용 (`./gradlew :{module}:spotlessApply`)
  3. 수정한 모듈별 테스트 실행 (`./gradlew :{module}:test`)
  4. 빌드 성공 (`./gradlew :{module}:build`)

## 9. 환경변수 설정 Convention

이 프로젝트는 `spring-dotenv` (`me.paulschwarz:spring-dotenv`) 라이브러리를 사용합니다.
**로컬(`.env`)과 Cloud Run(환경변수)에서 참조 방식이 다르므로 반드시 양쪽 모두 설정해야 합니다.**

### 파일별 참조 방식

| 파일 | 참조 방식 | 용도 |
|------|-----------|------|
| `application.yml` | `${env.KEY_NAME:기본값}` | 로컬 개발 (`.env` 파일, spring-dotenv) |
| `application-jp-dev.yml` | `${KEY_NAME}` | Cloud Run dev (`env.` 접두사 없음) |
| `application-jp-stg.yml` | `${KEY_NAME}` | Cloud Run stg |
| `application-jp-prd.yml` | `${KEY_NAME}` | Cloud Run prd |

### 새 환경변수 추가 시 필수 체크리스트

1. **`.env`**: 로컬용 키-값 추가 (예: `S2S_PAYMENT_API_KEY=xxx`)
2. **`application.yml`**: `${env.S2S_PAYMENT_API_KEY:기본값}` 형식으로 프로퍼티 추가
3. **`application-jp-dev.yml`**: `${S2S_PAYMENT_API_KEY}` 형식으로 프로퍼티 추가 (**`env.` 접두사 없이**)
4. **`application-jp-stg.yml`**: 동일
5. **`application-jp-prd.yml`**: 동일
6. **GCP Secret Manager + Cloud Run**: 시크릿 생성 및 환경변수 마운트

### 흔한 실수

- ❌ `application.yml`에만 추가하고 dev/stg/prd yml에 누락 → Cloud Run에서 값이 빈 문자열이 됨
- ❌ dev/stg/prd yml에서 `${env.KEY_NAME}` 사용 → Cloud Run에서 resolve 실패
- ✅ 기존 환경변수(예: `DATASOURCE_PASSWORD`)의 패턴을 참고하여 동일하게 적용

## 10. Database Migration Convention

- ✅ **파일 네이밍**: `V<YYYYMMDDHHmm>__description.sql`
- ✅ **인덱스 네이밍**:
  - 일반 인덱스: `idx_{column1}_{column2}...`
  - 유니크 인덱스/키: `uk_{column1}_{column2}...`
  - 외래키 제약: `fk_{소스테이블축약어}_{참조컬럼}_{대상테이블축약어}_{pk}`
  - **원칙**:
    - **도메인 경계 준수**: `users` 테이블과 같이 도메인 경계(Bounded Context) 바깥의 테이블에 대해서는 물리적인 외래키 제약을 생성하지 않습니다.
    - 컬럼명은 DB 컬럼명(예: `user_id`, `local_date`)을 **그대로** 사용합니다.
    - 약어(`agg`, `dt` 등)나 의미 축약(`date` vs `local_date`)은 지양합니다.
    - 필요한 경우에만 길이를 줄이며(MySQL 64자 제한), 의미가 유지되도록 합니다.
