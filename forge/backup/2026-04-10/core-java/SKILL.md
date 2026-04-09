---
name: code-java
description: Spring Boot 프로젝트에서 헥사고날/4-Tier 아키텍처 + CQRS/DDD/EDA를 적용한 코드와 테스트를 생성한다. '아키텍처 코드 생성', '헥사고날 구조 잡아줘', '4-Tier로 만들어줘', 'CQRS 적용', '이벤트 기반 아키텍처', 'code-java' 등의 요청에 사용. BDD 스타일 테스트, Test Double(Fixture, Fake)을 함께 생성한다.
---

# code-java - Spring Boot 아키텍처 코드 생성

> 사용자 프로파일, 출력 스타일, 정보 수집 원칙은 deep-dive 스킬의 `references/shared-context.md`를 Read 도구로 읽어 참조한다. 경로: `01. Management/Skills/Claude Code Skills/deep-dive/references/shared-context.md`


---


## Phase 0. 아키텍처 선택

스킬 실행 시 반드시 아래를 먼저 확인한다. 확인 없이 코드를 생성하지 않는다.

1. 아키텍처: 헥사고날 / 4-Tier
2. CQRS: 적용 / 미적용
3. EDA: 적용 / 미적용

### 선택 매트릭스

| 조합 | 아키텍처 | CQRS | EDA | Application 계층 핵심 | 외부 의존 추상화 |
|------|----------|------|-----|----------------------|-----------------|
| H+C | 헥사고날 | O | - | UseCase(Port In) + Port Out | Port Out 인터페이스 |
| H-C | 헥사고날 | X | - | UseCase(Port In) + Port Out | Port Out 인터페이스 |
| 4+C | 4-Tier | O | - | Service + Facade | Domain Repository 인터페이스 |
| 4-C | 4-Tier | X | - | Service + Facade | Domain Repository 인터페이스 |

EDA는 위 4가지 조합 어디에나 추가 가능하다. DDD(Rich Domain Model)는 항상 기본 적용된다.


---


## 공통 원칙

### 계층 책임 (Rich Domain, Lean Service)

도메인이 rich하고 서비스는 lean하다. 비즈니스 판단, 검증, 상태 변경 로직은 Domain 계층에 존재한다. Application 계층은 트랜잭션 경계와 도메인 조립(오케스트레이션)만 담당하며 if/else로 비즈니스 규칙을 판단하지 않는다.

| 계층 | 핵심 책임 | 금지 사항 |
|------|----------|----------|
| Domain | 모든 비즈니스 로직 소유. 판단, 검증, 상태 변경. copy & paste 가능 | Spring/JPA 프레임워크 의존, jakarta.validation 의존 |
| Application | 트랜잭션 경계, 도메인 조립, 오케스트레이션 | 비즈니스 판단 로직 (if/else 비즈니스 규칙) |
| Web / Adapter In | 표현 책임. Swagger, 화면 표시값 변환 | 비즈니스 로직, 직접 DB 접근 |
| Infrastructure / Adapter Out | 외부 시스템 연동. Domain 인터페이스 구현 | 비즈니스 로직 |

### 의존성 방향

```
헥사고날:  Adapter In -> Application(Port) -> Domain <- Adapter Out
4-Tier:   Web -> Application -> Domain <- Infrastructure
```

역방향 의존 절대 금지. Domain이 Application, Presentation, Infrastructure에 의존하면 안 된다.

### 패키지 구조 강제 규칙 (CRITICAL)

이 규칙은 가장 중요한 규칙이다. 이 규칙을 위반하는 코드는 생성하지 않는다. 패키지 구조를 확정한 후 코드를 작성한다.

모든 패키지는 도메인 단위로 하위 폴더를 구성한다. 기능 단위(entity/, repository/, vo/, adapter/ 등)로 하위 폴더를 만드는 것은 절대 금지한다.

절대 금지 (FORBIDDEN):
```
domain/coupon/entity/
domain/coupon/repository/
domain/coupon/vo/
adapter/out/persistence/coupon/entity/
```

올바른 구조 (CORRECT):
```
domain/coupon/
├── CouponEntity.java
├── CouponRepository.java    (4-Tier) 또는 없음 (헥사고날은 Port Out 사용)
├── CouponStatus.java        (Enum)
├── CouponPolicy.java        (VO)
└── Coupons.java             (일급 컬렉션)
```

### 네이밍 컨벤션

금지 단어와 대체어:

| 금지 단어 | 문제점 | 대체어 |
|-----------|--------|--------|
| execute | 무엇을 실행하는지 알 수 없음 | create, verify, approve, revoke |
| process | 가공/승인/정산 불분명 | settle, approve, reject, fulfill |
| check | 검증/조회/존재확인 불분명 | validate, isExpired, existsBy |
| handle | 무엇을 어떻게 처리하는지 알 수 없음 | route, dispatch, on{Event} |
| manage | CRUD 중 무엇인지 알 수 없음 | register, revoke, assign, release |
| do / run | 가장 포괄적, 의미 전달 불가 | migrate, sync, generate, calculate |
| get (Command 측) | 조회와 혼동 | load, fetch, resolve |
| set (Domain) | 의도와 행위를 파괴 | change{Field}() |

클래스/인터페이스 네이밍 표:

| 구분 | 헥사고날 | 4-Tier |
|------|----------|--------|
| Domain Entity | {Domain}Entity | {Domain}Entity |
| Domain VO | 도메인 용어 그대로 | 도메인 용어 그대로 |
| 일급 컬렉션 | {Domain}s | {Domain}s |
| Domain Repository | 없음 (Port Out 사용) | {Domain}Repository (interface) |
| Application Service | {Action}{Domain}Service | {Domain}Service |
| Facade | 없음 (UseCase로 대체) | {Action}{Domain}Facade |
| UseCase (Port In) | {Action}{Domain}UseCase | 없음 |
| Port Out (영속화) | Save{Domain}Port, Find{Domain}Port | 없음 (Repository 직접 주입) |
| Port Out (외부 API) | {Action}{Domain}Port | 없음 |
| Application DTO | {Action}{Domain}Command / Result | {Action}{Domain}InDto / OutDto |
| Controller | {Domain}CommandController / QueryController | {Domain}CommandController / QueryController |
| JPA Entity | {Domain}JpaEntity | {Domain}JpaEntity |
| Persistence Adapter | {Domain}PersistenceAdapter | {Domain}RepositoryImpl |
| JPA Repository | {Domain}CommandRepository / QueryRepository | {Domain}JpaRepository |
| Domain Exception | {Domain}{Reason}Exception | {Domain}{Reason}Exception |
| Fixture | {Domain}EntityFixture | {Domain}EntityFixture |
| Fake (헥사고날) | Fake{Domain}PersistencePort | - |
| Fake (4-Tier) | - | Fake{Domain}Repository |

메서드 네이밍:

- 헥사고날 UseCase: 클래스명의 Action 동사를 메서드명으로 사용 (CreateCouponUseCase.create())
- 4-Tier Service: 도메인 단위 CRUD 메서드 (CouponService.create(), findById(), expire())
- 4-Tier Facade: 액션 동사 (IssueCouponFacade.issue())
- Query 메서드 구분: findBy (Optional), getBy (throws), searchBy (list)
- 변환 메서드: toEntity(), toCommand()/toInDto(), toDomain(), fromDomain(), from() (static factory)
- 두문자어 규칙: 첫 글자만 대문자 (ApiResponse, EdaConfig, OAuthToken)

### 코드 컨벤션

record 사용 정책:

| 위치 | record 허용 여부 |
|------|----------------|
| Domain Entity | 금지 (class만 사용) |
| Domain 내 DTO | 금지 (class만 사용) |
| Domain VO (Money, CouponPolicy 등) | 허용 |
| Application DTO (Command/Result, InDto/OutDto) | 허용 (적극 사용) |
| Web DTO (Request, Response) | 허용 (적극 사용) |
| 일급 컬렉션 | 금지 (class만 사용) |

Lombok 정책:

| 계층 | 허용 | 금지 |
|------|------|------|
| Domain Entity | @Getter | @Setter, @Data, @Builder, @AllArgsConstructor |
| Domain VO (class) | @Getter | @Setter, @Data |
| Service/Facade | @RequiredArgsConstructor, @Slf4j | @Setter, @Data |
| Application DTO | 없음 (record 사용) | 모든 Lombok |
| Controller | @RequiredArgsConstructor, @Slf4j | @Setter, @Data |
| JPA Entity | @Getter, @NoArgsConstructor(PROTECTED), @Builder | @Setter, @Data, @AllArgsConstructor |

전역 금지: @Data, @AllArgsConstructor, @Value, @Autowired(필드 주입), @Setter(class-level)

변수 네이밍 정책:

변수명은 축약하지 않고 자료형과 클래스명을 그대로 반영한다. 변수명만 보고 타입을 유추할 수 있어야 한다.

| 선언 | 금지 (축약) | 올바른 변수명 |
|------|-----------|-------------|
| `List<OrderItem> ???` | items | orderItemList |
| `List<OrderItemInDto> ???` | items, dtos | orderItemInDtoList |
| `Map<Long, CouponEntity> ???` | store, map | couponEntityMap |
| `Set<String> ???` | tags, names | tagSet, couponNameSet |
| `Optional<MemberEntity> ???` | member, opt | memberEntityOptional |
| `CouponEntity ???` | coupon, entity | couponEntity |

컬렉션 변수는 `{ElementType}{CollectionType}` 형태를 따른다 (예: `orderItemList`, `couponEntityMap`, `memberIdSet`).
단일 객체 변수는 클래스명을 camelCase로 사용한다 (예: `couponEntity`, `createCouponCommand`).

기타:
- var 키워드 금지 (타입 명시)
- 와일드카드 import 금지
- System.out.println, printStackTrace() 금지 -> @Slf4j 사용
- Command Service/Facade: @Transactional
- Query Service: @Transactional(readOnly = true)
- 불필요한 public 지양 (package-private 권장)

DB 네이밍:

| 종류 | 접두사 | 예시 |
|------|--------|------|
| 일반 인덱스 | idx_{table}_{column} | idx_coupon_name |
| 유니크 인덱스 | uk_{table}_{column} | uk_coupon_name |
| 외래키 | fk_{table}_{ref_table} | fk_member_coupon_coupon |


---


## 아키텍처별 패키지 구조

### 헥사고날 +CQRS

```
{module}/src/main/java/{base-package}/{module}/
├── command/
│   ├── domain/{도메인}/                    # Entity, VO, Enum, 일급 컬렉션 (flat)
│   │   └── shared/                        # Shared Context VO
│   ├── application/{도메인}/
│   │   ├── port/in/                       # UseCase 인터페이스, Command DTO
│   │   ├── port/out/                      # Port Out 인터페이스
│   │   └── service/                       # UseCase 구현체
│   └── adapter/
│       ├── in/
│       │   ├── web/{도메인}/              # Controller + dto/
│       │   ├── scheduler/
│       │   └── event/
│       └── out/
│           ├── persistence/{도메인}/      # JpaEntity, Adapter, Repository (flat)
│           ├── messaging/
│           └── cache/
├── query/                                  # command와 동일 구조
└── support/
    ├── exception/                          # BusinessException + {도메인}/ 하위폴더
    ├── config/
    └── handler/
```

### 헥사고날 -CQRS

```
{module}/src/main/java/{base-package}/{module}/
├── domain/{도메인}/
│   └── shared/
├── application/{도메인}/
│   ├── port/in/
│   ├── port/out/
│   └── service/
├── adapter/
│   ├── in/web/{도메인}/
│   └── out/persistence/{도메인}/
└── support/
```

상세 구현(UseCase, Port, Adapter, Service, Test)은 `references/hexagonal-patterns.md` 참조.

### 4-Tier +CQRS

```
{module}/src/main/java/{base-package}/{module}/
├── command/
│   ├── web/{도메인}/                      # Controller + dto/
│   ├── application/{도메인}/
│   │   ├── facade/                        # Facade (여러 Service 조합)
│   │   ├── service/                       # Service (단일 도메인)
│   │   └── dto/
│   │       ├── in/                        # InDto
│   │       └── out/                       # OutDto
│   ├── domain/
│   │   ├── {도메인}/                      # Entity, VO, Repository 인터페이스, Enum (flat)
│   │   └── shared/                        # Shared Context VO
│   └── infrastructure/
│       ├── persistence/{도메인}/          # JpaEntity, JpaRepository, RepositoryImpl (flat)
│       ├── scheduler/                     # @Scheduled 스케줄러
│       ├── messaging/                     # Kafka Consumer/Producer
│       └── cache/
├── query/                                  # command와 동일 구조
└── support/
```

4-Tier에서 Controller가 위치하는 최상위 패키지는 `web`이다. `presentation`은 사용하지 않는다. Scheduler, Event Consumer, Kafka Listener 등은 HTTP 요청 처리가 아니므로 `web`이 아닌 `infrastructure` 하위에 위치한다.

### 4-Tier -CQRS

```
{module}/src/main/java/{base-package}/{module}/
├── web/{도메인}/                           # Controller + dto/
├── application/{도메인}/
│   ├── service/
│   ├── facade/
│   └── dto/
├── domain/{도메인}/
├── infrastructure/
│   ├── persistence/{도메인}/
│   ├── scheduler/
│   └── messaging/
└── support/
```

상세 구현(Facade, Service, InDto, OutDto, Repository, Test)은 `references/four-tier-patterns.md` 참조.

### EDA 옵션

EDA를 선택하면 아래 구조가 추가된다.

상세 구현(DomainEvent, Publisher, Listener, Async)은 `references/eda-patterns.md` 참조.

### 계층별 공통 코드 패턴

Domain Entity, VO, Exception, Presentation, Infrastructure의 코드 패턴은 `references/layer-code-patterns.md` 참조.

### Test Double 패턴

Fixture, Fake Repository/Port, Fake 외부 API의 코드 패턴은 `references/test-double-patterns.md` 참조.


---


## 멀티모듈 구조

### 모듈 네이밍

| 모듈 종류 | 패턴 | 예시 |
|-----------|------|------|
| Application (서버) | {국가}-{기능} | jp-api, kr-batch, api (kr 생략) |
| Application (국가별 Override) | {국가}-module-{기능} | jp-module-iap |
| Library (공통 모듈) | module-{기능} | module-iap, module-kafka |

국가 접두사: 단일 국가면 kr- 생략 가능. 2개국 이상이면 모든 국가 접두사 명시 (kr-api, jp-api).

모듈 의존성:
```
Application 모듈 -> Library 모듈 -> 외부 라이브러리
```

### 테스트 패키지 구조

```
{module}/src/test/java/{base-package}/{module}/
├── command/
│   ├── domain/{도메인}/                 # Domain 유닛 테스트
│   ├── application/{도메인}/service/    # Service 유닛 테스트
│   └── adapter/ 또는 infrastructure/   # 아키텍처에 따라
├── query/                               # 동일 구조
├── support/                             # Test Double 모음
│   ├── fixture/                         # Fixture 클래스
│   ├── fake/                            # Fake 구현체
│   └── base/                            # 테스트 베이스 클래스
├── integration/                         # 통합 테스트
└── acceptance/                          # E2E 인수 테스트
```


---


## 코드 생성 프로토콜

### 동작 모드

1. Full 생성: 도메인 + Application + Infrastructure/Adapter + Presentation + 전 계층 테스트
2. 코드 + 테스트 추가: 기존 도메인에 새 기능과 해당 테스트 추가
3. 테스트만 추가: 기존 코드에 누락된 테스트 보완 (Fixture, Fake 포함)

어떤 모드든 테스트 코드 없이 프로덕션 코드만 생성하지 않는다.

### 생성 순서

Domain -> Application -> Infrastructure/Adapter Out -> Presentation/Adapter In -> Test Double -> Tests

### 생성 계획 표

코드 작성 전 반드시 생성할 파일 목록을 표로 출력한다.

헥사고날 생성 계획 표:

| 구분 | 파일 | 위치 |
|------|------|------|
| Domain Entity | {Domain}Entity.java | command/domain/{도메인}/ |
| Domain VO | {Concept}.java | command/domain/{도메인}/ |
| 일급 컬렉션 | {Domain}s.java | command/domain/{도메인}/ |
| Domain Exception | {Domain}{Reason}Exception.java | support/exception/{도메인}/ |
| UseCase | {Action}{Domain}UseCase.java | command/application/{도메인}/port/in/ |
| Command DTO | {Action}{Domain}Command.java | command/application/{도메인}/port/in/ |
| Result DTO | {Action}{Domain}Result.java | command/application/{도메인}/port/in/ |
| Port Out | Save{Domain}Port.java | command/application/{도메인}/port/out/ |
| Service | {Action}{Domain}Service.java | command/application/{도메인}/service/ |
| Controller | {Domain}CommandController.java | command/adapter/in/web/{도메인}/ |
| Web Request DTO | {Action}{Domain}Request.java | command/adapter/in/web/{도메인}/dto/ |
| Web Response DTO | {Action}{Domain}Response.java | command/adapter/in/web/{도메인}/dto/ |
| JPA Entity | {Domain}JpaEntity.java | command/adapter/out/persistence/{도메인}/ |
| Persistence Adapter | {Domain}PersistenceAdapter.java | command/adapter/out/persistence/{도메인}/ |
| JPA Repository | {Domain}CommandRepository.java | command/adapter/out/persistence/{도메인}/ |
| Fixture | {Domain}EntityFixture.java | support/fixture/ |
| Fake Port | Fake{Domain}PersistencePort.java | support/fake/ |
| Domain Test | {Domain}EntityTest.java | command/domain/{도메인}/ |
| Service Test | {Action}{Domain}ServiceTest.java | command/application/{도메인}/service/ |
| Controller Test | {Domain}CommandControllerTest.java | command/adapter/in/web/{도메인}/ |

4-Tier 생성 계획 표:

| 구분 | 파일 | 위치 |
|------|------|------|
| Domain Entity | {Domain}Entity.java | command/domain/{도메인}/ |
| Domain Repository | {Domain}Repository.java | command/domain/{도메인}/ |
| Domain VO | {Concept}.java | command/domain/{도메인}/ |
| 일급 컬렉션 | {Domain}s.java | command/domain/{도메인}/ |
| Domain Exception | {Domain}{Reason}Exception.java | support/exception/{도메인}/ |
| InDto | {Action}{Domain}InDto.java | command/application/{도메인}/dto/in/ |
| OutDto | {Action}{Domain}OutDto.java | command/application/{도메인}/dto/out/ |
| Service | {Domain}Service.java | command/application/{도메인}/service/ |
| Facade | {Action}{Domain}Facade.java | command/application/{도메인}/facade/ |
| Controller | {Domain}CommandController.java | command/web/{도메인}/ |
| Web Request DTO | {Action}{Domain}Request.java | command/web/{도메인}/dto/ |
| Web Response DTO | {Action}{Domain}Response.java | command/web/{도메인}/dto/ |
| JPA Entity | {Domain}JpaEntity.java | command/infrastructure/persistence/{도메인}/ |
| JPA Repository | {Domain}JpaRepository.java | command/infrastructure/persistence/{도메인}/ |
| Repository Impl | {Domain}RepositoryImpl.java | command/infrastructure/persistence/{도메인}/ |
| Fixture | {Domain}EntityFixture.java | support/fixture/ |
| Fake Repository | Fake{Domain}Repository.java | support/fake/ |
| Domain Test | {Domain}EntityTest.java | command/domain/{도메인}/ |
| Service Test | {Domain}ServiceTest.java | command/application/{도메인}/service/ |
| Facade Test | {Action}{Domain}FacadeTest.java | command/application/{도메인}/facade/ |
| Controller Test | {Domain}CommandControllerTest.java | command/web/{도메인}/ |

### 자기 검증 체크리스트

코드 생성 후 반드시 아래를 확인한다:

1. 패키지 구조: domain-based flat 확인 (entity/, repository/, vo/ 하위폴더 없음)
2. 의존성 방향 위반 없음 (Domain이 Application/Infrastructure에 의존하지 않음)
3. 네이밍 컨벤션 준수 (금지 단어 미사용, 두문자어 규칙)
4. 테스트 코드 누락 없음
5. record/class 사용 정책 준수
6. Lombok 정책 준수 (@Data, @Setter 미사용)
7. var 키워드 미사용
8. @Setter 미사용, change{Field}() 사용 확인
9. @Nested 미사용 (테스트 클래스 flat 구조)
10. @DisplayName이 구체적 동작을 서술 (모호한 표현 "정상적으로", "올바르게", "성공한다" 금지)
11. 4-Tier 패키지에 presentation 미사용 (web 사용), scheduler/consumer는 infrastructure에 위치
12. 변수명이 자료형과 클래스명을 반영 (축약 금지, 예: items -> orderItemList)


---

### 커밋 메시지

```
<type>(<scope>): <변경 요약>

feat(coupon/command): CouponService 구현
test(coupon): CouponService 단위 테스트 추가
fix(member): 회원 조회 시 NPE 수정
```

