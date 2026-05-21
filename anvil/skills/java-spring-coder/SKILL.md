---
name: java-spring-coder
description: "Java Spring Boot 4-Tier 아키텍처 코드 생성 전문가. Java 코드 구현, Spring Boot 개발, 단위 테스트 작성, 기능 개발, TDD 계획서 기반 구현 요청 시 사용. Use proactively when implementing features, writing unit tests, or executing tasks from a plan document."
version: "1.8"
last-modified: "2026-05-21"
changelog: "v1.8 — 2026-05-21 i18n 사례 추가 (commit a1a425ecb2 CodeRabbit 지적): Locale.ROOT 강제 가드레일. `toLowerCase()`/`toUpperCase()`/내부용 `String.format`에 Locale.ROOT 명시. 터키 locale 등 JVM 기본 Locale 의존 버그 차단. i18n 키 사용 시 위치 기반 placeholder(`{0}`) 강제. | v1.7 — Bean 이름 상수 + REQUIRES_NEW + 약한 해시 금지. v1.6 — blueprint v2.0. v1.5 — FQCN 금지"
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

---

## 참조 인덱스

| 파일 | 내용 |
|------|------|
| `references/four-tier-patterns.md` | 4-Tier 계층별 코드 패턴 (Entity, Repository, Service, Controller) |
| `references/layer-code-patterns.md` | 계층별 상세 구현 패턴 (Domain Entity, VO, JPA Entity, DTO, 예외, Client) |
| `references/test-double-patterns.md` | 테스트 더블 패턴 (Fake/Spy/Fixture, BDD 스타일, 계층별 테스트) |
| `references/implementation-workflow.md` | 구현 워크플로 상세 (모드 A/B/C, 테스트 루프, 커밋 분리) |
| `references/evaluation-rubric.md` | 평가 루브릭 (100점, AUTO FAIL 조건) |
