---
description: 아키텍처 패키지 구조 및 네이밍 규칙
globs: **/*.java
alwaysApply: true
---
# Architecture Structure

**구조**: 핵심 규칙은 본문 상단(계층·의존성·네이밍), 예시·예외는 하단. 에이전트는 상단부터 참조하면 된다.

프로젝트는 도메인을 기준으로 모듈화되어 있으며, 각 도메인은 아래 4가지 계층을 가집니다.

## 1. Web Layer (`web`)
- **역할**: 외부 요청 처리, DTO 변환, 공통 응답 포맷팅
- **구성요소**: `*Controller`, `*Request`, `*Response`
- **위치**: `pghd/{domain}/web/`

## 2. Application Layer (`application`)
- **역할**: 유스케이스 흐름 제어, 트랜잭션 관리, 도메인 객체와 DTO 간 변환
- **구성요소**: `*Service`, `*UseCase`, `*InDto`, `*OutDto`
- **위치**: `pghd/{domain}/application/`

## 3. Domain Layer (`domain`)
- **역할**: 핵심 비즈니스 로직, 상태 변경 검증 (외부 의존성 없음)
- **구성요소**:
  - `*Entity`: 순수 도메인 객체. **`class` 사용** (domain-entity-convention 준수. DTO와 구분을 위해 record 금지)
  - `*Repository`: 리포지토리 **인터페이스**
  - `*Service`: 도메인 로직 서비스 (필요시)
  - `*ClientService`: 다른 도메인/외부 시스템 데이터 조회 시 사용하는 **인터페이스**
  - `*PaginatedResult`, `*SortSpec`: 페이징·정렬이 필요한 도메인 전용 값 객체 (도메인 간 공유 금지). **`class` 사용** (domain-entity-convention 준수)
- **위치**: `pghd/{domain}/domain/`

## 4. Infrastructure Layer (`infrastructure`)
- **역할**: 기술적 구현 (DB, 외부 API, File System)
- **구성요소**:
  - `*JpaEntity`: DB 테이블 매핑 객체
  - `*JpaRepository`: Spring Data JPA 인터페이스
  - `*RepositoryImpl`: Domain Repository의 구현체
  - `*Client`: **다른 도메인의 서비스** 호출 (리포지토리/Infrastructure 직접 접근 금지). 단순 변환만 필요하면 `*ClientService` 직접 구현 가능.
  - `*ClientServiceImpl`: **가공이 필요할 때만** 둠. ACL(Anti-Corruption Layer)로 여러 Client 조합·데이터 enrichment·복잡한 변환 수행.
- **위치**: `pghd/{domain}/infrastructure/`

# Layer Dependency Rules (계층 간 의존성 규칙)

## 의존성 방향
```
Web → Application → Domain ← Infrastructure
```

## 핵심 규칙
- **Domain**: 다른 레이어 참조 금지 (Java 표준 라이브러리만)
- **Application**: Domain만 참조, Domain → DTO 변환 담당
- **Infrastructure**: Domain만 참조, Domain Repository 인터페이스 구현
- **Web**: Application만 참조, Application DTO → Web DTO 변환

## 위반 예시
```java
// ❌ Domain이 Application DTO 참조
public interface Service {
  Page<ApplicationDto> find(...); // 금지
}

// ✅ Domain 객체만 사용
public interface Service {
  Page<DomainEntity> find(...); // 허용
}

// ❌ Infrastructure Client가 Web/Application DTO 직접 생성
public class S2sPghdMealRecordClient {
  MealRecordItemResponse toResponse(...); // 금지 - Web DTO 참조
}

// ❌ 다른 도메인 리포지토리/Infrastructure 직접 접근 (도메인 경계 위반)
public class S2sPghdMealRecordClient {
  private final PghdMealRecordJpaRepository repository; // 금지
}

// ✅ Client는 다른 도메인 서비스를 호출
public class S2sPghdMealRecordClient {
  private final MealRecordQueryService pghdMealRecordQueryService; // 허용 - 서비스 호출
}
```

# Naming Convention

- **JPA Entity**: `*JpaEntity` (예: `Glp1InjectionRecordJpaEntity`)
- **Domain Entity**: `*Entity` 또는 도메인명 그대로 (예: `Glp1InjectionRecordEntity`, `BloodPressureEntity`)
- **Domain Repository**: `*Repository` (Interface)
- **Infra Repository**: `*RepositoryImpl` (Implementation)

## Spring Bean Naming (빈 이름 충돌 방지)

- **클래스명에 도메인/서비스 접두사 필수**: 같은 이름의 클래스가 여러 도메인에 존재할 수 있으므로 클래스명 자체에 도메인/서비스 접두사를 포함합니다.
- **S2S API**: 클래스명에 `S2s` 접두사 사용 (예: `S2sObesityRoutineRaceClient`). 빈 이름은 클래스명 기반 자동 생성이므로 별도 지정 불필요.
- **다른 도메인**: 도메인명을 클래스명 접두사로 사용 (예: `PghdRoutineRaceClient`, `ReportRoutineRaceClient`).
- **클래스명 변경 우선**: 빈 이름만 변경하는 것보다 클래스명 자체를 변경하는 것이 더 명확하고 import 충돌도 방지합니다.

## Domain Object Naming (다른 도메인 객체 재사용 시)

- **다른 도메인에서 데이터를 가져와 자체 도메인 객체로 구현할 때**: 객체명 앞에 **사용하는 쪽 도메인 prefix**를 붙입니다.
- **예**: S2S에서 obesity의 `RoutineRace`를 가져와 사용 → `S2sObesityRoutineRace` (prefix: S2s + 도메인 Obesity + 원본명).
- **목적**: 다른 도메인과 이름 중복 방지, import/타입 구분 명확화.
- **원본과 동일한 이름 사용 금지**: `RoutineRace`만 사용하면 moneyball.obesity의 `RoutineRace`와 혼동 가능.

## Client / ClientService Pattern (다른 도메인·외부 시스템 데이터 조회 시)

다른 도메인 또는 외부 시스템 데이터를 조회할 때 계층 의존성을 지키기 위해 다음 패턴을 따릅니다. **pasta-api 모듈 전체에 적용됩니다.**

### 기본 원칙: 다른 도메인 서비스 호출

- **Client는 다른 도메인의 서비스(Application)를 호출**합니다. 다른 도메인의 리포지토리/Infrastructure에 직접 접근하는 것은 **금지**입니다.
- **이유**: 리포지토리 직접 접근은 도메인 경계 위반, 결합도 증가, 변경 영향도 확대로 이어져 위험합니다.

### 기본 구조

- **Domain**: `*ClientService` 인터페이스 정의. 도메인 모델 반환.
- **Infrastructure `*Client`**: **다른 도메인 서비스** 호출. 서비스 응답 → 도메인 모델 변환. Web/Application DTO 참조 금지.
- **Application**: `*ClientService` 인터페이스에 의존. 도메인 모델 → Application DTO 변환 담당.

### ACL(Anti-Corruption Layer) 개요

**ACL의 목적**: 외부 도메인의 모델/API가 내부 도메인을 "오염(corruption)"시키지 않도록, 변환·가공 계층을 두어 **자체 도메인 모델로만** 소비합니다. DDD의 Bounded Context 간 통신 패턴입니다.

- **핵심**: 다른 도메인 서비스 응답을 그대로 노출하지 않고, **사용하는 쪽 도메인 모델**(예: `S2sFood`, `S2sPghdMealRecord`)로 변환하여 반환합니다.
- **단순 변환 vs 가공**: 변환만 하면 Client가 직접 구현, 여러 소스 병합·enrichment가 필요하면 `*ClientServiceImpl`(ACL)을 둡니다.

### 구현체 선택: Client 직접 구현 vs ClientServiceImpl(ACL)

| 상황 | 구현 방식 | 판단 기준 |
|------|-----------|-----------|
| **단순 변환** | `*Client`가 `*ClientService` 직접 구현 | 단일 서비스 호출, 1:1 매핑, 추가 조회·병합 없음 |
| **가공 필요** | `*ClientServiceImpl`(ACL) 별도 구현 | 여러 Client 조합, 여러 소스 병합, 데이터 enrichment, 복잡한 변환·가공 |

**단순 변환 예시**: `UserModel` → `User` (단일 서비스, 필드 매핑·계산만), `Food` → `S2sFood` (1:1 매핑)

**가공 필요 예시**: MealRecord + Image 병합, RoutineRace + WeightLossGoal 조합 후 `weeklyWeightLossGoalKg` 계산

```java
// Domain: 인터페이스만 정의
public interface FoodClientService {
  List<S2sFood> getAllFoodsByIds(List<Long> ids);
}

// 단순 변환: Client가 ClientService 직접 구현 (ACL 불필요)
public class S2sFoodClient implements FoodClientService {
  private final FoodQueryService foodQueryService;
  /* Food → S2sFood 1:1 변환 (단일 서비스) */
}

// 가공 필요: 내부 Client 분리 + ClientServiceImpl(ACL) 구현
public class S2sPghdMealRecordClient { /* MealRecord 서비스 호출, raw 데이터 반환 */ }
public class S2sPghdImageClient { /* Image 서비스 호출 */ }
public class S2sMealRecordClientServiceImpl implements S2sMealRecordClientService {
  /* MealRecordClient + ImageClient 조합, enrichment 후 S2sPghdMealRecord 반환 */
}
```

## Domain PaginatedResult / SortSpec (도메인별 페이징·정렬)

페이징·정렬이 필요한 도메인은 domain 패키지에 **자체** `*PaginatedResult`, `*SortSpec`을 둡니다. **pasta-api 모듈 전체에 적용됩니다.**

- **도메인 간 공유 금지**: 공용 `PaginatedResult` 사용 금지. 각 도메인은 `MealRecordPaginatedResult`, `RoutineRacePaginatedResult` 등 도메인 prefix를 붙인 타입을 사용합니다.
- **정렬 규격**: `*SortSpec`은 도메인 내부에 정의. Application에서 파싱 후 Spring `Sort` 생성.

# S2S API URL Design Convention
- **적용 범위**: S2S (Server-to-Server) API에만 적용됩니다. 기존 API는 기존 URL 패턴을 유지합니다.
- **URL 구조**: `/{service}/{service_version}/{domain}/{api_version}/{resource}`
  - `service`: 서비스 식별자 (예: `s2s`)
  - `service_version`: API Gateway에서 분기를 위한 버전 (예: `v1`)
  - `domain`: 도메인명 (복수형 사용, 예: `pghds`, `users`)
  - `api_version`: API 버전 (예: `v1`)
  - `resource`: 리소스명 (복수형 사용, 예: `foods`, `meal-records`)
- **예시**: `/s2s/v1/pghds/v1/foods`, `/s2s/v1/pghds/v1/meal-records`
- **RESTful 원칙**: 리소스명은 복수형을 사용합니다 (예: `pghd` → `pghds`)
