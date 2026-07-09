---
name: java-spring-coder
description: "Java Spring Boot 4-Tier 아키텍처 코드 생성 전문가. Java 코드 구현, Spring Boot 개발, 단위 테스트 작성, 기능 개발, TDD 계획서 기반 구현 요청 시 사용. Use proactively when implementing features, writing unit tests, or executing tasks from a plan document."
version: "1.11"
last-modified: "2026-07-09"
changelog: "v1.11 — 2026-07-09 7월 pasta 사고 4건 흡수: (1) Hibernate Session 오염 회귀 방지 3연타 하드 가드레일 — unique violation catch 후 같은 세션 재조회 금지 / DataIntegrityViolationException 광범위 catch 금지 (SQL 에러코드로 좁혀 판별) / 방어 조회는 REQUIRES_NEW 격리 (#633 미션 뱃지 사고, moneyball 저장소에서 이미 겪은 사고의 재발). (2) 설정 게이팅 @ConditionalOnBean 회피 — 환경별 게이팅은 @Profile 선호, Bean 로드 순서 취약성 (584ced0b97 GLOB-566 사례). (3) 캐시 pub-sub 즉시 무효화 + 폴링 백스톱 + 발행 실패 흡수 (v1.10 3층 폴백의 진화형, GLOB-566 시리즈). (4) 어노테이션 + 인터셉터 조합 패턴 — @ApiGroup 등 마킹 기반 선택 적용 (GLOB-549 유료화 인터셉터). | v1.10 — 2026-07-02 6월 pasta 사고 5건 흡수: (1) 외부 API DTO 시간 필드 방어 파싱 — DateTimeFormatterBuilder + optional 필드, 미사용 필드는 String 유지 (a122fc1152 #581 / 641b72ab49 #582 Dexcom EGV 하루 두 번 hotfix). (2) 공용 모듈 JPA @Entity 스캔 충돌 회피 — 다른 애플리케이션 모듈이 의존하는 공용 모듈에는 @Entity 두지 말고 JdbcClient Reader 사용 (7abea8f2f0 admin 기동 실패 → JPA→JDBC 교체). (3) 권한/보안 캐시 3층 폴백 + write-through 전체 재작성 + 워밍업 임계 (2d0bae1344 GLOB-566 / 10f7c711a6 GLOB-569 이용권한 패턴). (4) 신규 패키지 첫 커밋부터 4-Tier 강제 (82e7ee8ec9 access 사후 재편 사례). (5) 예외 로깅 표준 — JsonTemplateLayout exceptionRootCause 전용 필드 + maxStringLength 32KB (6529b3593d #625 스택 16KB 절단으로 원인 못 봄). | v1.9 — 싱글톤 mutable field / Soft-delete Functional Unique / WebClient timeout+retry. v1.8 — Locale.ROOT + i18n 4파일. v1.7 — Bean 이름 상수 + REQUIRES_NEW + 약한 해시 금지"
---

# java-spring-coder — Java Spring Boot 구현 스킬

> 프로젝트 규칙: `.claude/rules/` (인덱스: `00-rules-index.md`)

---

## Phase 0. 사전 확인

코드 작성 전 반드시 확인. 확인 없이 구현하지 않는다.

1. **작업 계획서 탐색**: `docs/plans/*.md` 또는 `docs/tdd/*.md`에 TDD 문서가 있는지 확인
2. **동작 모드 결정**: TDD 있으면 모드 A / 없으면 모드 B / 테스트만 요청이면 모드 C
3. **프로젝트 규칙 로드**: `.claude/rules/` 하위 규칙 파일을 Read 도구로 참조
4. **기존 코드 패턴 파악**: 같은 도메인의 기존 Entity/Service/Controller 구조 확인
5. **JDK 21 확인**: `export JAVA_HOME=$(/usr/libexec/java_home -v 21)`
6. **admin 모듈 여부 확인**: 작업 대상이 `admin/` 패키지인가?
   - **YES** → 13~16 규칙 추가 로드. 4-Tier 대신 레이어 혼합형, `@Controller`(NOT `@RestController`) 적용
   - **NO** → 기존 01~12 규칙 적용

---

## 아키텍처 원칙

### 4-Tier 계층 구조

```
Web → Application → Domain ← Infrastructure
```

> **(v1.10) 신규 패키지는 첫 커밋부터 계층 폴더 강제**
> 새 도메인·기능 패키지 생성 시 `domain/` · `application/` · `infrastructure/`(및 필요 시 `web/`) 폴더를 **첫 커밋에** 함께 만든다. 계층 없이 만들었다가 후속으로 재편하는 대형 리팩토링 사고 이력이 있다 (2026-07-01 `common/access` 재편). 도메인 로직·계약은 `domain/`, 오케스트레이션은 `application/`, 어댑터·리포지토리 구현은 `infrastructure/`.

### Rich Domain, Lean Service

- **Domain이 모든 비즈니스 로직을 소유**한다. Service는 흐름 제어(오케스트레이션)만.
- Domain Entity에 상태 변경 메서드를 둔다: `redeem()`, `expire()`, `decreaseRemainCount()`
- Service에서 `if (entity.getStatus() == EXPIRED)` 같은 판단 금지 → `entity.isExpired()`로 위임

### 패키지 구조 (도메인 기반 flat)

```
pghd/{domain}/domain/          ← Entity, Repository(I), ClientService(I) — flat
pghd/{domain}/infrastructure/  ← JpaEntity, JpaRepository, RepositoryImpl, Client
pghd/{domain}/application/     ← Service, InDto, OutDto
pghd/{domain}/web/             ← Controller, Request, Response
```

**금지**: `domain/coupon/entity/`, `domain/coupon/repository/` 같은 기능 기반 하위 패키지 분리

### admin 모듈 예외 (Phase 0에서 admin 확인 시에만 적용)

admin 모듈은 pasta-api의 4-Tier와 다른 **레이어 혼합형 SSR 구조**를 따른다.

- `@Controller` 사용 (NOT `@RestController`), Thymeleaf 뷰 반환
- 패키지: `controllers`, `service`, `repository` 등 직접 배치 (4-Tier X)
- `AdminHistoryService` 주입·호출로 감사 로그 기록 (15 규칙)
- Thymeleaf 레이아웃: `layout:decorate`, URL-View-File 정합 (14 규칙)
- 페이지별 JS 파일 생성 (16 규칙)
- 새 `@PreAuthorize` authority 추가 시 → SUPER_ADMIN permission에 해당 authority를 포함하는 마이그레이션 자동 포함
- Bootstrap 버전 확인 필수 — **BS5이면 `data-bs-*` 문법, `bootstrap.Modal` API 사용. BS4(`data-toggle` 등) 문법 절대 금지**
- 마이그레이션 SQL에서 스키마 접두사(`pasta.`) 절대 금지, JSON 컬럼 수정은 `JSON_ARRAY_APPEND` 패턴 사용
- 상세: `.claude/rules/13-admin-module-overview.md` ~ `16-admin-static-assets-convention.md` 참조

### 의존성 규칙

| 계층 | 참조 가능 | 참조 금지 |
|------|-----------|-----------|
| Domain | Java 표준, Lombok | Spring, JPA, 다른 레이어 |
| Application | Domain | Infrastructure 구체 클래스 |
| Infrastructure | Domain | Application, Web |
| Web | Application | Domain 직접, Infrastructure |

> **(v1.10) 공용 모듈에는 `@Entity` 두지 말 것**
> 여러 애플리케이션 모듈(api, admin, batch 등)이 의존하는 공용 모듈에 `@Entity`를 두면, 소비 모듈의 `@EntityScan` 경계와 충돌해 기동 실패로 이어진다 (2026-07-01 admin 기동 실패 → `ServiceAccessPatternJpaEntity`를 `JdbcClient` 기반 Reader로 교체). 공용 모듈에서는 **JDBC 기반 read-only Repository** 또는 **인터페이스 + 각 애플리케이션 모듈의 구현체** 패턴을 사용한다.

> **(v1.11) 설정 게이팅은 `@Profile` 선호, `@ConditionalOnBean` 회피**
> 환경별 Config on/off는 `@Profile("!test")` 등 `@Profile` 기반으로 게이팅한다. `@ConditionalOnBean(RedisTemplate.class)` 같은 Bean 존재 조건은 Bean 로드 순서에 취약해, 순서 지정이 어려운 상황에서 사고 재현 가능 (2026-07-07 `PricingCacheRedisConfig` `@ConditionalOnBean` → `@Profile` 전환 사례).
> `@ConditionalOnBean`을 써야 하는 경우는 **진짜 다른 Bean의 존재/부재에 의존하는 라이브러리성 auto-configuration**일 때만. 그 외에는 `@Profile`이 안전.

---

## 네이밍 컨벤션

### 금지 단어 (메서드명)

| 금지 | 대안 | 이유 |
|------|------|------|
| `execute`, `process`, `run`, `do` | 구체적 동사 (`redeem`, `expire`, `calculate`) | 의미 불명확 |
| `check`, `handle`, `manage` | `validate`, `resolve`, `orchestrate` | 과도한 추상화 |
| `get` (커맨드에서) | `create`, `update`, `delete` | 조회와 혼동 |
| `set` (도메인에서) | `change{Field}()`, `update{Field}()` | Setter 패턴 금지 |

### 클래스 네이밍

| 계층 | 패턴 | 예시 |
|------|------|------|
| Domain Entity | `{Domain}Entity` (class) | `CouponCodeEntity` |
| Domain Repository | `{Domain}Repository` (interface) | `CouponCodeRepository` |
| Domain ClientService | `{Domain}ClientService` (interface) | `FoodClientService` |
| JPA Entity | `{Domain}JpaEntity` | `CouponCodeJpaEntity` |
| RepositoryImpl | `{Domain}RepositoryImpl` | `CouponCodeRepositoryImpl` |
| Client | `{Prefix}{Domain}Client` | `S2sFoodClient` |
| Service | `{Domain}{Action}Service` | `CouponRedeemService` |
| Controller | `{Domain}{Action}Controller` | `CouponRedeemController` |

### 서비스 메서드 네이밍

| 패턴 | 용도 | 예시 |
|------|------|------|
| `getAll*By*` | 복수 조회 | `getAllCouponsByUserId` |
| `get*OrElseNull` | 단일 조회 (null) | `getCouponByIdOrElseNull` |
| `find*` | 단일 조회 (Optional) | `findById` |
| `exist*` / `has*` | 존재 여부 | `existCouponByCode` |
| `getPage*` | 페이징 조회 | `getPageByUserIdAndIds` |

### 변수 네이밍

- **약어 금지**: `cnt` → `count`, `amt` → `amount`, `dt` → `date`
- **타입 반영**: `couponEntityList` (not `coupons`), `couponEntityMap` (not `map`)
- **`var` 키워드 금지**: 항상 명시적 타입 선언

---

## 코드 생성 프로토콜

### 동작 모드

| 모드 | 조건 | 동작 |
|------|------|------|
| **A: TDD 전체 구현** | `docs/plans/` 또는 `docs/tdd/`에 TDD 있음 | Phase 1~N 일괄 구현 + 테스트 + 보고 |
| **B: 단순 구현** | TDD 없음, 코드+테스트 요청 | 기존 패턴 파악 → 구현 + 테스트 + 보고 |
| **C: 테스트만 추가** | 기존 코드에 테스트만 요청 | 코드 분석 → 테스트만 생성 |

### 코드 생성 순서 (모드 A/B 공통)

```
1. Domain       → Entity, Repository(I), ClientService(I), VO
2. Infrastructure → JpaEntity, JpaRepository, RepositoryImpl, Client
3. Application  → Service, InDto/OutDto
4. Web          → Controller, Request/Response
5. 설정         → SecurityConstants, 환경변수
6. Test Double  → Fake Repository, Spy Client
7. Test         → Domain → Application → Web → Infrastructure 순
```

### 파일 생성 계획 (4-Tier)

| # | 파일 | 계층 | 설명 |
|---|------|------|------|
| 1 | `{Domain}Entity.java` | Domain | 비즈니스 로직 소유, JPA 금지 |
| 2 | `{Domain}Repository.java` | Domain | 인터페이스, 도메인 모델만 |
| 3 | `{Domain}JpaEntity.java` | Infra | `toEntity()`, `from()` 변환 |
| 4 | `{Domain}JpaRepository.java` | Infra | Spring Data JPA |
| 5 | `{Domain}RepositoryImpl.java` | Infra | 3단계 Repository 구현 |
| 6 | `{Domain}{Action}Service.java` | App | 오케스트레이션 |
| 7 | `{Action}InDto.java` / `OutDto.java` | App | record 타입 |
| 8 | `{Domain}{Action}Controller.java` | Web | Swagger + REST |
| 9 | `{Action}Request.java` / `Response.java` | Web | record 타입 |
| 10 | `Fake{Domain}Repository.java` | Test | HashMap 기반 |
| 11 | 계층별 `*Test.java` | Test | Fake/MockMvc/Testcontainers |

상세 계층별 코드 패턴은 `references/four-tier-patterns.md` 참조.

---

## 코드 컨벤션

### record / class 정책

| 대상 | 타입 | 이유 |
|------|------|------|
| Domain Entity | **class** 필수 | 행위 메서드, 상태 변경 필요 |
| Domain VO | record 허용 | 값 동등성 |
| Application InDto/OutDto | **record** | 불변 데이터 전달 |
| Web Request/Response | **record** | 불변 데이터 전달 |
| JPA Entity | **class** 필수 | JPA 프록시 요구 |

### Lombok 정책

| 계층 | 허용 | 금지 |
|------|------|------|
| Domain Entity | `@Getter`, `@ToString`, `@EqualsAndHashCode` (**둘 다 필수**) | `@Setter`, `@Data`, `@Builder`(10필드 미만) |
| JPA Entity | `@Getter`, `@NoArgsConstructor(PROTECTED)`, `@Builder`(생성자 레벨) | `@Setter`, `@Data` |

> **JPA Entity NOT NULL 컬럼 어노테이션 규칙**
> - `@Column(nullable = false)`와 `@NotNull`(jakarta.validation.constraints)을 **반드시 병행** 사용
> - `@Column(nullable = false)`만 단독 사용 금지 — 프로젝트 기존 패턴과 일관성 유지 필수
| Service | `@RequiredArgsConstructor`, `@Log4j2`/`@Slf4j` | `@Data` |
| Controller | `@RequiredArgsConstructor` | `@Data` |

### 전역 금지

- `@Data`, `@AllArgsConstructor`, `@Value` (Lombok)
- `@Autowired` 필드 주입 → 생성자 주입
- `@Setter` 클래스 레벨
- `var` 키워드 → 명시적 타입
- 와일드카드 import (`import java.util.*`)
- `System.out.println` / `printStackTrace`

### 정적 팩토리 메서드 규칙

| 메서드 | 용도 | 위치 |
|--------|------|------|
| `of(필드들)` | 새 인스턴스 생성 | Domain Entity, VO |

> **도메인 엔티티 생성자/팩토리 검증 규칙**
> - 생성자에서 NOT NULL 필수 필드는 `Objects.requireNonNull(field, "field must not be null")`로 검증 필수
> - `of()` 팩토리 메서드에서도 동일하게 입력 검증 필수 — null이 들어오면 즉시 실패해야 한다

| `from(source)` | 다른 객체 → 이 객체 변환 | DTO, JpaEntity |
| `toEntity()` | JpaEntity → Domain Entity | JpaEntity |
| `to{Target}()` | 이 객체 → 다른 객체 변환 | DTO |
| `forXxx()` | 특정 목적 생성 | DTO |

### 로깅 규칙

- **로그 접두사**: `[ClassName.methodName]` 형식 필수 — 예: `log.info("[CouponRedeemService.redeem] 쿠폰 사용 완료")`
- **PII(userId 등) 로그 본문 포함 금지** — MDC에 이미 존재하므로 중복·유출 방지
- **비즈니스 식별자**(couponCodeId, orderId 등)는 로그 본문에 포함 허용
- **민감 정보 평문 INFO 로그 금지** — 쿠폰 코드 등은 반드시 마스킹 처리 (`****ABCD` 등)

---

## 실행 프로토콜

### 모드 A: TDD 전체 구현

> **Phase별 분리 호출 금지. 한 번에 전체 Phase를 구현한다.**

1. **기존 코드 패턴 확인** — 같은 도메인 기존 Entity/Service/Controller를 읽어 예외 처리, 응답 포맷, 타입 관례 파악
2. **TDD 비판적 검증** — TDD 문서를 무비판적으로 수용하지 않는다. 구현 시점에서 프로젝트 규칙(CQRS 분리, 도메인 풍부화, 상위 클래스 활용 등)과 대조하여 TDD 설계가 규칙에 위배되면 능동적으로 수정·보고한다
3. TDD 문서의 모든 Phase TODO를 순서대로 한번에 구현
4. 테스트도 모든 Phase 것을 함께 작성
5. 전체 구현 완료 후 테스트 실행
   ```bash
   export JAVA_HOME=$(/usr/libexec/java_home -v 21)
   ./gradlew :{module}:test
   ```
6. 테스트 실패 시 자동 수정 (5회 미만). **5회 이상 → 즉시 중단, 보고**
7. pasta-api 모듈이면 `./gradlew :pasta-api:spotlessApply`
8. **설정 체크** — 새 API 엔드포인트 → SecurityConstants airArray 등록, 새 환경변수 → 4곳 설정
9. TDD 체크박스 업데이트 (`- [ ]` → `- [x]`)
10. 변경 사항 보고 — **커밋하지 않음**

### 모드 B: 단순 구현

1. **기존 코드 패턴 파악** — 같은 도메인 기존 Entity/Service/Controller, 예외 처리 패턴(`MoneyballException`, `ExceptionConstants`), 응답 포맷 확인
2. 코드 생성 순서에 따라 구현
3. 계층별 테스트 작성
4. **설정 체크** — 새 API 엔드포인트 → SecurityConstants airArray 등록, 새 환경변수 → 4곳 설정
5. 테스트 실행 → 보고 — **커밋은 사용자 요청 시에만**

### 모드 C: 테스트만 추가

1. 기존 코드 분석 (계층, 의존성 파악)
2. 테스트 대상 선정 및 Test Double 결정
3. 테스트 작성 → 실행 → 보고

상세 워크플로는 `references/implementation-workflow.md` 참조.

---

## 가드레일

### 하드 가드레일 (절대 위반 불가)

- **Testcontainers(MySQL) 필수** — H2 전환 금지
- **사용자 명시적 요청 없이 커밋 금지** — 변경 사항 보고만
- **기존 obesity 마이그레이션 파일 수정/삭제 금지** — `myplan/` 하위만 수정
- **git stash / stash drop / stash pop 절대 금지** — 데이터 유실 사고 이력
- **Application에서 Infrastructure 구체 클래스 직접 import 금지**
- **Domain에 JPA/Spring 어노테이션 금지** — 순수 도메인 유지
- **테스트 5회 이상 연속 실패 시 즉시 중단, 보고**
- **Non-bean 클래스에 `@Transactional` 금지** — Spring AOP 프록시 기반이므로 Spring Bean(`@Component`/`@Service`/`@Repository` 등)에서만 동작. Non-bean이면 어노테이션 제거 + Javadoc에 "프록시 미적용으로 트랜잭션 없음" 명시. 필요하면 내부에서 `SimpleJpaRepository` 단일 연산(자체 트랜잭션 보장)만 사용하거나 Bean으로 승격
- **OAuth2 Client 커스터마이징 클래스를 `@Component`/`@Service`로 무분별하게 등록 금지** — Spring이 모든 OAuth2 Provider 플로우(Google OIDC 포함)에 자동 편입시켜 타 Provider 로그인이 깨진다. Provider 전용이면 non-bean + `AuthorizedClientServiceOAuth2AuthorizedClientManager` 내부 주입 방식 사용
- **admin 세션 중 `SecurityContextHolder.setAuthentication(...)` 호출 금지** — 외부 OAuth2 토큰이 admin 인증을 덮어 이후 요청 403 유발. 호출이 불가피하면 controller에서 save/finally-restore 패턴 필수
- **FQCN(Fully Qualified Class Name) 직접 사용 금지** — 모든 외부 클래스는 파일 상단 `import` 선언 후 단순 클래스명 사용. **메인+테스트 코드 동일 적용**. 검사 대상: 변수 선언, 매개변수, 제네릭, 예외 인스턴스 생성(`new x.y.Z()`), `.class` 리터럴, 캐치 절, 어노테이션. 가장 자주 누수되는 패턴은 **테스트 mock 예외**:
  ```java
  // ❌ 금지 (PR #527 사례)
  .willThrow(new org.springframework.dao.DataIntegrityViolationException("duplicate"));
  .isInstanceOf(org.springframework.dao.DataIntegrityViolationException.class)

  // ✅ 올바름
  import org.springframework.dao.DataIntegrityViolationException;
  ...
  .willThrow(new DataIntegrityViolationException("duplicate"));
  .isInstanceOf(DataIntegrityViolationException.class)
  ```
  예외: 어노테이션 인자 문자열, SpEL 표현식, JPQL/SQL 쿼리, 로그 메시지 본문은 검사 대상 아님. **"한 번만 쓰는 거니까 인라인으로"는 절대 금지** — 무조건 import 추가 후 단순 클래스명.

  **(v1.7 추가)** enum 상수 접근 / 표준 라이브러리도 동일 적용:
  ```java
  // ❌ 금지 (2026-05-21 commit a6b72daa82 사례)
  .stateInfo(com.kakaohealthcare.moneyball.user.entity.State.NORMAL)
  java.lang.reflect.Field field = ...

  // ✅ 올바름
  import com.kakaohealthcare.moneyball.user.entity.State;
  import java.lang.reflect.Field;
  ...
  .stateInfo(State.NORMAL)
  Field field = ...
  ```

- **(v1.7) Bean 이름 매직 스트링 금지** — `@Bean`, `@Qualifier`, `@MockBean(name=...)`, `@DependsOn`, `BeanFactory#getBean` 등에 같은 빈 이름 리터럴이 3회 이상 반복되면 **반드시** 상수화. 오타 시 런타임 NoSuchBeanDefinitionException 위험.
  - **상수 위치 결정 트리**:
    - 빈 등록자와 모든 소비자가 **같은 모듈** → 등록자 `*Configuration` 클래스 내 `public static final String`
    - 등록자(A 모듈) ↔ 소비자(B 모듈)가 **다른 모듈** → `shared/.../constant/{Domain}BeanNameConstants` 신설 (config → config 의존 외관 회피)
  - **2026-05-21 사례** (commit a6b72daa82 → 후속 0fc9b52338):
    ```java
    // ❌ 금지 — 8곳에 매직 스트링 반복
    @Bean
    public OAuth2AuthorizedClientManager dexcomAuthorizedClientManager(...) { ... }
    @Qualifier("dexcomAuthorizedClientManager") OAuth2AuthorizedClientManager mgr
    @MockBean(name = "dexcomAuthorizedClientManager") OAuth2AuthorizedClientManager mgr

    // ✅ 올바름 — shared 모듈 상수
    // shared/.../constant/DexcomBeanNameConstants.java
    public final class DexcomBeanNameConstants {
        public static final String DEXCOM_AUTHORIZED_CLIENT_MANAGER = "dexcomAuthorizedClientManager";
        private DexcomBeanNameConstants() {}
    }

    // api 모듈
    @Bean(DEXCOM_AUTHORIZED_CLIENT_MANAGER)
    public OAuth2AuthorizedClientManager dexcomAuthorizedClientManager(...) { ... }
    ```

- **(v1.7) TransactionTemplate 전파 명시 의무** — `new TransactionTemplate(...)` 생성 시 **즉시** `setPropagationBehavior(...)` 호출. 기본값(REQUIRED) 의도 시에도 주석으로 명시.
  - **REQUIRES_NEW 권장 케이스**:
    - 외부 시스템(Cloud Task, SQS 등) 호출 실패 후 **실패 상태 마킹**이 호출 측 트랜잭션 결과와 독립적으로 커밋되어야 할 때
    - 감사 로그·이력 기록이 호출 측 롤백과 무관하게 남아야 할 때
    - 알림 발송 큐 enqueue 실패 후 retry 큐 적재
  - **2026-05-21 사례** (commit 1066af4f54):
    ```java
    // ❌ 위험 — 호출 측 롤백 시 FAILED 마킹도 함께 롤백
    this.transactionTemplate = new TransactionTemplate(platformTransactionManager);

    // ✅ 올바름 — enqueue 실패 마킹은 호출 측과 독립 커밋
    this.transactionTemplate = new TransactionTemplate(platformTransactionManager);
    this.transactionTemplate.setPropagationBehavior(TransactionDefinition.PROPAGATION_REQUIRES_NEW);
    ```

- **(v1.7) 약한 해시 알고리즘 금지** — `MessageDigest.getInstance("MD5"|"SHA-1"|"SHA1")` 금지. CSRF/세션ID/토큰 같은 보안 용도면 **SHA-256 이상** 강제. 2026-05-21 commit f1d959badf 사례(CookieUtils CSRF MD5→SHA-256 KISA High 지적).

- **(v1.8) Locale.ROOT 강제** — 다음 호출에 `Locale.ROOT` 인자 명시 의무. 터키 locale 등 JVM 기본 Locale 의존으로 인한 국제화 버그 차단.
  ```java
  // ❌ 위험 (2026-05-15 commit a1a425ecb2 CodeRabbit 지적)
  String key = "TITLE".toLowerCase();
  String msg = String.format("user-%s", id);  // 내부 키용

  // ✅ 올바름
  String key = "TITLE".toLowerCase(Locale.ROOT);
  String msg = String.format(Locale.ROOT, "user-%s", id);
  ```
  **적용 범위**:
  - `String#toLowerCase()` / `toUpperCase()` 단독 호출 (예외: 사용자 화면 표시용으로 사용자 locale을 의도적으로 적용하는 경우만 — 의도 주석 필수)
  - `String#format` 결과가 내부 키·로그·API 응답 본문이면 `Locale.ROOT` 명시. 사용자 표시용이면 `Locale.getDefault()` 또는 사용자 locale.

- **(v1.8) i18n 키 사용 시 위치 기반 placeholder** — `messages.getMessage(...)` 호출 시 `{0}`, `{1}` 위치 기반만 사용. 명명 기반(`{name}`)은 일부 라이브러리만 지원해 호환성 깨질 위험.
  ```java
  // ✅ 올바름
  messages.getMessage("myplan.guide.meal.v2.description", new Object[]{kcal}, locale);
  // properties — en: Breakfast/lunch/dinner for a daily target of {0} kcal
  ```

- **(v1.8) i18n 키 추가 시 4파일 동기화** — `message-shared*.properties` 신규 키 추가는 항상 4파일(default/ko/en/ja) 동시. 단일 파일만 추가 금지. 추가 후 tolgee 스킬로 콘솔 push 권장.

- **(v1.9) @Service 싱글톤에 mutable instance field 금지** — Spring Bean은 기본적으로 싱글톤. instance field에 가변 상태가 있으면 모든 요청이 공유 → 세션 간 값 혼용 위험 (KISA Medium 진단 사례).
  ```java
  // ❌ 위험 (2026-05-21 KbsmcEhrClient KISA 진단 — 세션 간 token 혼용)
  @Service
  public class KbsmcEhrClient {
      private String token;       // ← 싱글톤 공유 mutable
      private Long tokenExpiry;
      // ...
  }

  // ✅ 올바름 — 방식 A: AtomicReference + immutable record
  @Service
  public class KbsmcEhrClient {
      private final AtomicReference<TokenSnapshot> tokenCache = new AtomicReference<>();
      private record TokenSnapshot(String token, Instant expiry) {}
  }

  // ✅ 올바름 — 방식 B: 메서드 인수 전달 (지역 변수화)
  public Response verify(Request req) {
      String token = getValidToken();      // 지역 변수
      return verifyWithToken(req, token);  // 인수로 전달
  }
  ```
  **판단 가이드**:
  - 캐시 가치가 있으면(매번 fetch 비싸면) → `AtomicReference<record>` 방식
  - 단순 일회성이면 → 메서드 인수 전달
  - 금지: `private String token;` 같은 raw mutable instance field

- **(v1.9) Soft-delete + unique 제약 — MySQL Functional Unique Index** — `deleted_at` 컬럼으로 soft-delete를 쓰면서 동시에 unique 제약이 필요한 경우, MySQL 8.0.13+ Functional Unique Index 사용.
  ```sql
  -- ❌ 위험 — 일반 UNIQUE는 soft-deleted 행과 alive 행이 충돌
  CREATE UNIQUE INDEX uk_email ON users (email);

  -- ✅ 올바름 (2026-05-21 GLOB-366 commit de480fe266 사례)
  ALTER TABLE users
    ADD UNIQUE INDEX uk_email_for_login_active (
      (CASE WHEN deleted_at IS NULL THEN email ELSE NULL END)
    );
  ```
  **선택 기준**:
  - alive 행끼리만 unique 보장 필요 → Functional Unique Index
  - 영구 unique 필요 (재가입 막기) → 별도 history 테이블 또는 soft-delete 시 email 마스킹

- **(v1.9) WebClient 외부 호출 timeout 명시 + 재시도 필터** — 외부 시스템 호출 시 connect/read timeout을 반드시 명시. 재시도는 일시 장애 한정.
  ```java
  // ✅ 올바름 (2026-05-21 commit f5ed7dd757 / 2dc6614cd2 Dexcom OAuth 사례)
  WebClient.builder()
      .clientConnector(new ReactorClientHttpConnector(
          HttpClient.create()
              .responseTimeout(Duration.ofSeconds(10))
              .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, 5_000)
      ))
      .build();

  // 재시도는 일시 장애만 — 4xx 영구 오류는 제외
  Retry.fixedDelay(3, Duration.ofSeconds(2))
      .filter(throwable ->
          throwable instanceof ReadTimeoutException
          || throwable instanceof ConnectTimeoutException
          || (throwable instanceof WebClientResponseException ex
              && ex.getStatusCode().is5xxServerError())
      );
  ```

- **(v1.10) 외부 API DTO 시간 필드 방어 파싱** — 외부 API 응답에서 `Instant`/`OffsetDateTime` 등 강타입 시간 필드는 초·밀리초·오프셋 존재 여부가 응답마다 달라질 수 있다. 표준 ISO 파서로 받으면 hotfix 반복 사고 확정.
  ```java
  // ❌ 위험 (2026-06-08 #581·#582 Dexcom EGV 하루 두 번 hotfix)
  public record DexcomEgvRecord(
      String recordId,
      Instant systemTime,                          // 초 생략 응답에서 파싱 실패
      @JsonProperty("displayTime") OffsetDateTime displayTime,  // 오프셋 다양성에서 재실패
      ...
  ) {}

  // ✅ 올바름 — 실사용 필드는 견고 파서, 미사용 필드는 String
  static final DateTimeFormatter FLEXIBLE_OFFSET =
      DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm[:ss][.SSS]X");

  public record DexcomEgvRecord(
      String recordId,
      @JsonDeserialize(using = DexcomInstantDeserializer.class) Instant systemTime,
      @JsonProperty("displayTime") String displayTime,   // 비즈니스 미사용 → String 유지
      ...
  ) {}
  ```
  **규칙**:
  - 외부 API 시간 필드 강타입 파싱 시 `DateTimeFormatterBuilder` 또는 optional pattern(`[:ss][.SSS]`) 사용 필수
  - **비즈니스 로직에서 실제로 사용하지 않는 시간 필드는 강타입 파싱 금지, String으로 유지**
  - `@JsonDeserialize(using = ...)` 커스텀 deserializer는 **실 사용 필드에만** 부착 (미사용 필드는 파싱 실패 리스크만 남는다)
  - "완벽 파서" 만들려다 실패한 사례 반복 금지 — 애매하면 String 후퇴가 안전

- **(v1.10) 권한/보안 관련 캐시 3층 폴백 + write-through 전체 재작성** — 이용권한·과금 등 사고 시 무료 개방으로 이어지는 캐시는 **Redis → DB → 하드코딩 기본값** 3층 폴백 필수.
  ```java
  // ✅ 올바름 (2026-07-01 GLOB-566 이용권한 패턴 로더)
  public Set<String> load(ServiceAccessPatternType type) {
      try {
          Set<String> fromRedis = redisTemplate.opsForSet().members(redisKey(type));
          if (!fromRedis.isEmpty()) return fromRedis;
      } catch (Exception e) { log.warn(...); }         // 예외 삼킴
      try {
          Set<String> fromDb = patternDbReader.findActive(type);
          if (!fromDb.isEmpty()) return fromDb;
      } catch (Exception e) { log.warn(...); }         // 예외 삼킴
      return ServiceAccessPatternDefaults.of(type);    // 하드코딩 기본값
  }
  ```
  **규칙**:
  - 어느 계층도 **예외를 상위로 전파하지 않는다** — 무료 개방 사고 방지가 최우선
  - CRUD write-through는 **유형별 전체 재작성**(부분 갱신 금지) — 캐시 드리프트 원천 차단
  - 기동 시 워밍업 + **임계값 검증**(카운트가 예상보다 적으면 경보 이벤트 발행). WarmupRunner가 운영 모드를 인식해 알람 강도 조정
  - 대상: 접근 제어 패턴, 요금제·플랜 상태, 기능 플래그 등 **틀리면 무료 개방·과금 누락**으로 이어지는 정책성 데이터

  **(v1.11) Redis pub-sub 즉시 무효화 + 폴링 백스톱 + 발행 실패 흡수** — 3층 폴백의 진화형. 어드민 CRUD가 다른 인스턴스의 로컬 캐시까지 즉시 무효화하는 요구에 대응.
  - **커밋 후 발행**: pub-sub 발행은 트랜잭션 커밋 후 실행 (커밋 전 발행 금지 — 상위 롤백 시 잘못된 무효화 발생). `@TransactionalEventListener(phase = AFTER_COMMIT)` 또는 커밋 확인 후 명시적 호출
  - **발행 실패 흡수**: Redis 발행 실패 시 로그 후 무시 → 어드민 CRUD API 자체는 성공 유지. 원본 데이터는 이미 커밋되어 있고, 폴링 백스톱이 자가 치유
  - **폴링 백스톱**: pub-sub이 놓친 리스너를 위해 30초~1분 저빈도 폴링으로 캐시 재작성. pub-sub 실패가 곧 데이터 유실이 되지 않게 하는 안전망
  - **발행 실패 로그 레벨**: 초회 WARN → 연속 실패 ERROR + 스택트레이스 (v1.10 예외 로깅 표준 적용)
  - 2026-07-07 GLOB-566 `PricingChangePublisher`/`PricingCacheInvalidationListener` 사례

- **(v1.10) 예외 로깅 표준** — JsonTemplateLayout 사용 시 스택트레이스가 절단되어 근본 원인을 못 보는 사고 방지.
  ```yaml
  # ✅ 올바름 (2026-06-30 #625 사례)
  # log4j2-*.yml
  maxStringLength: 32768   # 16KB는 스택 절단 사고 발생, 최소 32KB
  # CustomLogJsonLayoutV1.json 등에 exceptionRootCause 전용 필드 추가
  ```
  **규칙**:
  - JsonTemplateLayout 사용 시 `exceptionRootCause` 전용 필드 필수 (`${json:exception:rootCauseFirst}` 등)
  - `maxStringLength`는 **32KB 이상** — 16KB는 스택 절단으로 원인 못 보는 사고 이력
  - 로그 본문 PII(userId 등) 금지, sensorId·eventId·orderId 같은 안전한 비즈니스 식별자만 (기존 로깅 규칙 재확인)

- **(v1.11-A) unique/제약 위반 catch 후 같은 Hibernate Session 재조회 절대 금지** — `DataIntegrityViolationException` 등 제약 위반 예외가 던져진 순간 Session은 이미 rollback-only 상태다. 같은 Session/EntityManager로 재조회하면 `AssertionFailure`가 튀며, 앞서 저장된 다른 엔티티(예: 미션 달성 기록)까지 상위 트랜잭션과 함께 롤백된다. **예외는 최상단에서만 잡고 세션에서 이탈**하는 게 원칙.
  ```java
  // ❌ 금지 (2026-07-08 #633 미션 뱃지 사고, 한국 moneyball 저장소에서 이미 겪은 사고의 재발)
  try {
    session.persist(badge);
  } catch (DataIntegrityViolationException e) {
    Badge existing = session.find(Badge.class, key);  // ← Session 오염 상태에서 조회 → AssertionFailure
    return existing;
  }

  // ✅ 올바름 — 세션 이탈, 필요 시 상위에서 새 트랜잭션으로 재조회
  try {
    session.persist(badge);
  } catch (DataIntegrityViolationException e) {
    if (isDuplicateKey(e)) {                          // (v1.11-B) SQL 에러코드로 좁혀 판별
      log.info("Badge already exists, skipping: {}", key);
      return;                                         // 세션 이탈
    }
    throw e;
  }
  ```

- **(v1.11-B) `DataIntegrityViolationException` 광범위 catch 금지, SQL 에러코드로 좁혀 판별** — `DataIntegrityViolationException`을 무조건 삼키면 unique 위반뿐 아니라 **NOT NULL / FK 위반 같은 실제 결함도 은폐**된다. 반드시 SQL 에러코드로 좁혀 판별.
  ```java
  // ✅ 올바름 — MySQL 중복 키(1062=ER_DUP_ENTRY)만 좁혀 판별
  static boolean isDuplicateKey(DataIntegrityViolationException e) {
    Throwable cause = e.getMostSpecificCause();
    if (cause instanceof SQLIntegrityConstraintViolationException sqlEx) {
      return sqlEx.getErrorCode() == 1062;   // ER_DUP_ENTRY
    }
    return false;
  }
  ```
  다른 DB를 쓰면 해당 DB의 SQLState/에러코드로 판별. 판별 실패면 `throw`로 전파해서 실제 결함이 로그에 남게 한다.

- **(v1.11-C) 방어 조회·중복 검사가 필요한 도메인 이벤트 처리는 `REQUIRES_NEW` 별도 트랜잭션 격리** — 뱃지 발급·감사 로그처럼 상위 트랜잭션 롤백과 무관하게 커밋되어야 하는 처리는 별도 트랜잭션으로 격리한다. 상위 롤백이 이 처리까지 감아버리지 않게. (v1.7 TransactionTemplate 전파 명시 의무의 자연스러운 연장선).
  - 대상: 뱃지 발급, 미션 달성 이력, 감사 로그, 알림 큐 enqueue 실패 마킹 등
  - 구현: `@Transactional(propagation = Propagation.REQUIRES_NEW)` 또는 `TransactionTemplate.setPropagationBehavior(PROPAGATION_REQUIRES_NEW)`
  - 2026-07-08 #633 사례에서 뱃지 발급을 별도 트랜잭션으로 격리 + Testcontainers 통합테스트 추가로 재발 방지

- **(v1.11) 어노테이션 + 인터셉터 조합 패턴** — 인터셉터는 전체 호출 경로에 걸리지만, `HandlerMethod.getMethodAnnotation(...)`으로 마킹된 API에만 로직 적용.
  ```java
  // shared 모듈 — 어노테이션 정의
  @Target(ElementType.METHOD)
  @Retention(RetentionPolicy.RUNTIME)
  public @interface ApiGroup { ApiGroupType value(); }

  // api 모듈 — 인터셉터
  public boolean preHandle(HttpServletRequest req, HttpServletResponse res, Object handler) {
    if (!(handler instanceof HandlerMethod hm)) return true;
    ApiGroup marker = hm.getMethodAnnotation(ApiGroup.class);
    if (marker == null) return true;                 // 마킹 안 된 API는 통과
    return pricingGate.check(marker.value(), req);
  }
  ```
  **규칙**:
  - 어노테이션은 **shared 모듈**에 정의(모든 모듈에서 부착 가능), 인터셉터·게이트 로직은 **api 모듈**에 배치 (4-Tier 유지)
  - 어노테이션 파라미터는 **enum** 사용, 문자열 리터럴 금지 — 리네임 시 컴파일러 지원 확보 (safe-mass-rename 스킬과 연계)
  - 2026-07-07 GLOB-549 `@ApiGroup` 유료화 인터셉터 사례

### 소프트 가드레일

- Fake 우선, Mockito는 외부 API 등 Fake가 복잡한 경우만
- DTO는 record, Domain Entity는 class
- `var` 키워드 금지 — 명시적 타입 선언
- 와일드카드 import 금지
- `@DisplayName` 한글, 구체적 시나리오 ("`성공한다`" 금지 → "`할인 금액과 사용 시각이 반환된다`")
- `JOIN FETCH` + `Page` 조합 시 반드시 `countQuery` 분리 — 안 하면 메모리 내 페이지네이션 발생
- `@RequestParam(required = false) String`의 빈 문자열 → 컨트롤러에서 `isBlank() → null` 정규화 처리
- 서비스 시그니처 변경 시 테스트의 mock 호출도 반드시 동기화 업데이트
- 외부 API 의존성 추가 시 **환경별 yml 4곳**(`application.yml`, `application-jp-dev.yml`, `application-jp-stg.yml`, `application-jp-prd.yml`) override 일치 확인 — 누락 시 prd가 sandbox URL 호출하는 사고 발생
- DB 컬럼 참조 전 실제 스키마/마이그레이션 파일 grep 확인 — 추측성 컬럼명(`transmitter_id` 대신 `sensor_id`) 사용하지 말 것

---

## 자기 검증 체크리스트

작업 완료 후 반드시 12항목 확인:

1. [ ] **패키지 구조**: 도메인 기반 flat 구조인가? (기능 기반 하위 분리 없음)
2. [ ] **의존성 방향**: Web→App→Domain←Infra 위반 없는가?
3. [ ] **Domain 순수성**: Domain에 JPA/Spring 어노테이션 없는가?
4. [ ] **Rich Domain**: 비즈니스 로직이 Domain Entity에 있는가? (Service에 판단 로직 없음)
5. [ ] **Repository 3단계**: Domain Interface + JPA Interface + RepositoryImpl 구조인가?
6. [ ] **record/class 정책**: DTO는 record, Entity는 class인가?
7. [ ] **Lombok 정책**: `@Data`, `@AllArgsConstructor`, 필드 `@Autowired` 없는가?
8. [ ] **네이밍**: 금지 단어 미사용, 약어 없음, `var` 없음, 서비스 메서드 패턴 준수?
9. [ ] **테스트 계층**: Fake(Domain/App), MockMvc(Web), Testcontainers(Infra)?
10. [ ] **테스트 스타일**: `@DisplayName` 한글 구체적, Given-When-Then, AssertJ only?
11. [ ] **설정**: SecurityConstants airArray, 환경변수 4곳, spotless?
12. [ ] **가드레일**: 커밋 안 함, H2 없음, 마이그레이션 보호, stash 없음?
13. [ ] **admin 모듈**: admin 작업이면 13~16 규칙 참조했는가? (@Controller, AdminHistory, Thymeleaf 레이아웃)
14. [ ] **Spring Bean/AOP**: Non-bean 클래스에 `@Transactional` 같은 AOP 어노테이션 붙이지 않았는가? OAuth2 Client 커스터마이징은 non-bean + `AuthorizedClientServiceOAuth2AuthorizedClientManager` 패턴 준수?
15. [ ] **SecurityContext 격리**: 외부 OAuth2/API 호출이 admin 세션을 오염시키지 않는가? (save/restore 또는 setAuthentication 제거)
16. [ ] **외부 API 환경 설정**: 신규 외부 의존성의 endpoint/credential을 local/dev/stg/prd yml 4곳에 모두 override 했는가?
17. [ ] **FQCN 검사**: 메인+테스트 코드 본문(import 외)에 `com.x.y.Z` 형태 패키지 경로가 직접 박혀 있지 않은가? 특히 mock 예외(`new x.y.Z()`)와 `.class` 리터럴(`isInstanceOf(x.y.Z.class)`) 점검?
18. [ ] **(v1.6) Phase 0 현황 파악 실행**: 작업 계획서 탐색·기존 도메인 코드 탐색·JDK/admin 모듈 확인을 실제로 수행했는가? (생략하고 가정으로 구현 진행 금지)
19. [ ] **(v1.6) 확인 vs 가정 분리**: TDD가 없어 코드만 보고 시그니처를 결정한 경우, 결정 근거(기존 도메인의 어느 패턴을 따랐는지)를 커밋 메시지 또는 PR 본문에 명시했는가?
20. [ ] **(v1.6) 도메인 외부 컬럼/메서드 가정 금지**: 인접 도메인의 Repository·Entity를 호출하지 않고, 자체 Service에서 데이터 가공했는가? (19-architecture-boundaries 위반 자가 점검)
21. [ ] **(v1.7) Bean 이름 상수화 + 위치**: `@Bean`/`@Qualifier`/`@MockBean` 빈 이름이 3회 이상 반복되면 상수화했는가? 다중 모듈 공유 시 shared 모듈에 두었는가? (config→config 의존 외관 회피)
22. [ ] **(v1.7) TransactionTemplate 전파**: 새로 생성한 `TransactionTemplate`에 `setPropagationBehavior(...)` 명시했는가? 외부 enqueue 실패 마킹/감사 로그 등 독립 커밋 필요 케이스면 `REQUIRES_NEW`?
23. [ ] **(v1.7) 보안 알고리즘**: 해시 알고리즘 사용 시 MD5/SHA-1 없는가? SHA-256 이상?
24. [ ] **(v1.7) enum/표준라이브러리 FQCN**: `.stateInfo(com.x.y.State.NORMAL)` 같은 enum 인라인 / `java.lang.reflect.*` 표준라이브러리 인라인 모두 import + 단순 클래스명으로 변환?
25. [ ] **(v1.8) Locale.ROOT 명시**: `toLowerCase()`/`toUpperCase()`/내부용 `String.format` 호출에 Locale.ROOT 인자 명시했는가? 사용자 화면용이면 의도 주석?
26. [ ] **(v1.8) i18n 4파일 동기화**: `message-shared*.properties` 신규 키가 default+ko+en+ja 4파일 모두에 추가되었는가? `grep -l "^{키}=" message-shared*.properties` 결과 4건?
27. [ ] **(v1.8) i18n placeholder 위치 기반**: `messages.getMessage(...)` 인자가 위치 기반(`{0}`,`{1}`)인가? 명명 기반(`{name}`) 0건?
28. [ ] **(v1.9) 싱글톤 동시성**: 새로 추가한 `@Service`/`@Component`/`@Repository` 클래스에 mutable instance field 0건? 캐시 필요하면 `AtomicReference<record>`, 일회성이면 메서드 인수 전달?
29. [ ] **(v1.9) Soft-delete unique**: 신규 unique 제약 필요한 컬럼에 `deleted_at` 소프트 삭제가 있으면 Functional Unique Index 사용했는가? (일반 UNIQUE는 soft-deleted 행과 충돌)
30. [ ] **(v1.9) WebClient timeout/retry**: 새 외부 호출에 connect/read timeout 명시했는가? 재시도 필터가 ReadTimeout/ConnectTimeout/5xx만 잡고 4xx는 제외하는가?
31. [ ] **(v1.10) 외부 API DTO 시간 필드**: 강타입(`Instant`/`OffsetDateTime`) 필드에 `DateTimeFormatterBuilder`나 optional pattern deserializer가 붙어 있는가? 비즈니스 미사용 시간 필드는 `String`으로 남겨 파싱 리스크를 없앴는가?
32. [ ] **(v1.10) 공용 모듈 JPA 회피**: 다른 애플리케이션 모듈이 의존하는 공용 모듈에 `@Entity`/`@Table` 클래스가 신규 추가되지 않았는가? 공용 read-only 경로는 `JdbcClient`/`NamedParameterJdbcTemplate` 기반인가?
33. [ ] **(v1.10) 신규 패키지 4-Tier 첫 커밋 강제**: 새 도메인·기능 패키지가 `domain/application/infrastructure` 폴더를 **첫 커밋에** 포함하는가? 계층 없이 만들고 후속 재편으로 미루지 않았는가?
34. [ ] **(v1.10) 정책성 캐시 3층 폴백**: 이용권한·요금제·기능 플래그 같은 정책성 데이터 캐시가 Redis → DB → 하드코딩 3층 폴백이고 어느 계층도 예외를 상위 전파하지 않는가? CRUD write-through가 유형별 전체 재작성인가? 기동 워밍업 + 임계값 경보를 포함하는가?
35. [ ] **(v1.10) 예외 로깅**: log4j2 설정에 `exceptionRootCause` 전용 필드 + `maxStringLength ≥ 32768`이 반영되어 있는가? 로그 본문에 userId 등 PII를 넣지 않았는가?
36. [ ] **(v1.11) Hibernate Session 오염 방지**: 신규/수정 코드에 `DataIntegrityViolationException` 등 제약 위반 catch가 있으면, catch 블록 안에서 같은 Session/EntityManager로 재조회하지 않는가? (예외 catch 이후에는 세션 이탈)
37. [ ] **(v1.11) 예외 좁혀 판별**: `DataIntegrityViolationException`을 조건 없이 삼키지 않고 `SQLIntegrityConstraintViolationException` errorCode(예: MySQL 1062)로 좁혀 판별하는가? 판별 실패는 `throw`로 전파?
38. [ ] **(v1.11) 방어 조회 트랜잭션 격리**: 뱃지 발급·미션 이력·감사 로그 같은 상위 롤백과 독립 커밋 필요 처리에 `REQUIRES_NEW` 격리가 적용되어 있는가?
39. [ ] **(v1.11) 설정 게이팅 @Profile 선호**: 신규 `@Configuration`이 환경별 on/off라면 `@Profile`을 썼는가? `@ConditionalOnBean`을 썼다면 진짜 auto-configuration 요건인지 근거 명시?
40. [ ] **(v1.11) 캐시 pub-sub 무효화 안전성**: pub-sub 발행이 트랜잭션 커밋 후에 실행되고(커밋 전 발행 아님), 발행 실패는 흡수되며, 폴링 백스톱이 붙어 있는가?
41. [ ] **(v1.11) 어노테이션+인터셉터 배치**: 마킹 어노테이션이 shared 모듈에 있고 인터셉터가 api 모듈에 있는가? 어노테이션 파라미터가 enum(문자열 리터럴 금지)인가?

---

## 참조 인덱스

| 파일 | 내용 |
|------|------|
| `references/four-tier-patterns.md` | 4-Tier 계층별 코드 패턴 (Entity, Repository, Service, Controller) |
| `references/layer-code-patterns.md` | 계층별 상세 구현 패턴 (Domain Entity, VO, JPA Entity, DTO, 예외, Client) |
| `references/test-double-patterns.md` | 테스트 더블 패턴 (Fake/Spy/Fixture, BDD 스타일, 계층별 테스트) |
| `references/implementation-workflow.md` | 구현 워크플로 상세 (모드 A/B/C, 테스트 루프, 커밋 분리) |
| `references/evaluation-rubric.md` | 평가 루브릭 (100점, AUTO FAIL 조건) |
