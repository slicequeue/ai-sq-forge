---
name: java-layered-unit-testing
description: "Java Spring Boot 계층별 단위 테스트 작성 전문가. 4-Tier 아키텍처(Web, Application, Domain, Infrastructure) 각 계층에 적합한 테스트 방식을 적용한다. Domain은 순수 JUnit 5, Application은 Fake 우선(외부 통신만 Spy·Mock), Web은 @WebMvcTest, Infrastructure는 @DataJpaTest + Testcontainers MySQL. 'テスト作成', '단위 테스트', 'unit test', '테스트 코드 작성', '계층별 테스트', 'Mockito', 'Testcontainers' 요청 시 사용한다."
version: "1.9"
last-modified: "2026-11-13"
changelog: "v1.9 — 2026-11-13 forge 하네스 첫 평가(신규 TC-6~8 + 회귀 TC-1·4) 감점 반영: (1) 자기 검증 #2 의 'App=Mockito' 잔재를 Fake 우선으로 정합화(TC-1 응답자가 충돌 지적), (2) v1.4 예시의 var·Mockito spy 를 명시 타입·손으로 쓴 Spy 로 교체(규칙 08 §2-2·v1.7 var 금지와 충돌), (3) 요청 범위가 예외 분기보다 좁아도 빠진 분기 작성(TC-6 NotFound 분기 제안만), (4) 스스로 찾은 결함은 제출 코드에서 수정(TC-4 이중 호출 결함을 설명만 붙여 제출), (5) 요청 변경 시 규칙 원본 인용(TC-4 규칙 07 미인용), 체크리스트 #22·#23 추가 | v1.8 — 2026-10-16 GLP-1 PR 리뷰 45건 반영: Application 계층 기본 방식을 Mockito → Fake 우선으로 교체(규칙 08 과 충돌하던 예시가 #789·#794 Mock 지적의 원인), 기본값과 다른 값 검증·모든 진입 경로 테스트·느슨한 JSON 단언 금지·이름 규칙·실패 격리 테스트 추가, review-lint.py 실행 단계 추가 | v1.7 — 2026-09-16 리뷰 피드백 전수 조사(PR 262건) 반영: RR-12 테스트 실효성 검사 추가 — 동어반복·위임만 검증·목표 경로 미실행·수동 나열 목록·경계값 픽스처·테스트 var 금지 | v1.6 — 2026-09-16 사이클 7 감사 반영: 파괴적 쓰기 가드 참조 연결 — 기존 테스트 파일은 먼저 읽고 Edit 로 추가, 통째 덮기 금지(DW-3). 근거: 2026-09-01 UserDeviceTest.java 기존 테스트 3건 삭제 | v1.5 — 2026-07-09 pasta #633 후속 반영: Testcontainers 통합 테스트 사용 기준 명시 — 동시성 경합·트랜잭션 격리·JPA Session 관련 로직은 단위 테스트로 커버 불가, `@SpringBootTest` + Testcontainers MySQL로 실제 DB 제약과 세션 오염 회귀 검증 필수. | v1.4 — 2026-07-07 pasta PR 리뷰 반영 2건: (1) Mockito verify vs Spy 선택 기준 명시 (side-effect 관찰 필요 시 Spy 콜카운트). (2) application·domain 테스트에서 infra 구현체 직접 참조 금지, domain 인터페이스 Fake 사용 (4-Tier 격리). AUTO FAIL 후보: `.infrastructure.`/`.persistence.`/`.cache.impl.` 클래스 직접 참조. | v1.3 — 2026-05-21 pasta 사례 반영: (1) @MockBean(name=...) 빈 이름 매직 스트링 금지 — 빈 등록자가 제공한 상수 import 강제. (2) enum 인라인 FQCN 패턴 명시 — `.stateInfo(com.x.y.State.NORMAL)` 같은 빌더 인자도 검사 대상. | v1.2 — blueprint v2.0 패턴 이식. v1.1 — FQCN 직접 사용 금지. v1.0 — pasta 역수입"
---

# java-layered-unit-testing — 계층별 단위 테스트 작성

> 원칙: **계층이 다르면 테스트 방식도 다르다.** Domain은 순수하게, Infrastructure는 실제 DB로.

**범위**: Java Spring Boot 4-Tier 아키텍처의 계층별 단위 테스트 작성
**비범위**: 통합 테스트, E2E 테스트, 프론트엔드 테스트

---

## Phase 0. 사전 확인 (코드 작성 전 필수)

1. **대상 클래스 계층 식별**: Web / Application / Domain / Infrastructure 중 어디에 해당?
2. **기존 테스트 패턴 탐색**: 같은 패키지의 기존 `*Test` 파일을 읽어 프로젝트 관례 파악
3. **JDK 버전 확인**: JDK 21 기준
4. **모듈 확인**: `pasta-api`, `admin` 등 어느 모듈의 테스트인지 확인

---

## 계층별 테스트 전략

### 1) Domain Layer (`domain/`) — 순수 JUnit 5

| 항목 | 규칙 |
|------|------|
| 테스트 유형 | Pure JUnit 5 unit test |
| 의존성 | 없음 또는 최소 mock |
| 초점 | 비즈니스 로직, 상태 전이, 검증, 도메인 규칙 |
| Spring 의존 | **금지** — @SpringBootTest, @ExtendWith(SpringExtension) 사용하지 않음 |

```java
class MyPlanNutrientRatioTest {
    @Test
    @DisplayName("목표 감량치가 주당 0.5kg이면 일일 적자 칼로리는 500kcal이다")
    void calculateDailyDeficit() {
        MyPlanNutrientRatio ratio = new MyPlanNutrientRatio(2000, false);
        assertThat(ratio.getCarbohydrateGram()).isEqualTo(200.0f);
    }
}
```

### 2) Application Layer (`application/`) — Fake 우선, 외부 통신만 Spy·Mock

규칙 08(`.claude/rules/08-test-code-convention.md` §2)의 **Fake → Stub/Spy → Mock** 순서를 따른다. 이 순서를 어겨 Repository·UseCase 를 `@Mock` 으로 두면 리뷰에서 반드시 지적된다(#789·#794).

| 협력 객체 | 테스트 더블 | 검증 |
|-----------|-------------|------|
| 상태를 가진 것: `*Repository`, 다른 도메인 `*UseCase`·`*QueryService` | **Fake** — 인메모리 컬렉션 + 실제와 같은 조건(기간·사용자·삭제 여부) | `save` 로 넣고 서비스 호출 → **반환값·Fake 상태**만 본다 |
| 외부 통신·void 부수효과: `*Client`, 푸시·태스크 enqueue | **Spy** — 호출 이력 기록, 필요하면 n번째 호출에서 예외 | `getCallCount()`, `getLastCall()` |
| Fake·Spy 로 대체할 수 없는 복잡한 외부 라이브러리 | Mock (제한적) | 사유를 테스트 클래스 주석에 한 줄 |

- Fake 는 `src/test/` 의 같은 도메인 패키지에 `Fake{Interface}` 로 둔다. 이미 있으면 재사용하고 없을 때만 만든다(`find . -name "Fake*"` 로 먼저 확인).
- 같은 패키지 기존 테스트가 Mock 위주여도 **새 테스트는 Fake 로 쓴다.** 기존 테스트를 고칠 범위가 아니면 그대로 둔다.
- `@Mock` 을 꼭 써야 하면 핵심 인자를 `any()` 대신 값·`isNull()` 로 고정하고, 공통 setUp 의 `lenient` 스텁이 예외 분기를 가리지 않게 예외 테스트에서 스텁을 덮어쓴다.

```java
class Glp1InjectionPlanQueryServiceTest {
    private FakeGlp1InjectionPlanRepository fakeGlp1InjectionPlanRepository;
    private FakeGlp1GroupRepository fakeGlp1GroupRepository;
    private Glp1InjectionPlanQueryService glp1InjectionPlanQueryService;

    @BeforeEach
    void setUp() {
        fakeGlp1InjectionPlanRepository = new FakeGlp1InjectionPlanRepository();
        fakeGlp1GroupRepository = new FakeGlp1GroupRepository();
        glp1InjectionPlanQueryService =
            new Glp1InjectionPlanQueryService(fakeGlp1InjectionPlanRepository, fakeGlp1GroupRepository);
    }

    @Test
    @DisplayName("일정이 기록 없는 그룹을 가리키면 일정 없음으로 응답한다")
    void getCurrent_planTargetsEmptyGroup_returnsEmpty() {
        // Given
        Glp1GroupEntity emptyGroup = fakeGlp1GroupRepository.save(groupWithoutRecords());
        fakeGlp1InjectionPlanRepository.save(planTargeting(emptyGroup));

        // When
        Glp1InjectionPlanAndRecordOutDto glp1InjectionPlanAndRecordOutDto =
            glp1InjectionPlanQueryService.getCurrent(USER_ID, CURRENT_AT);

        // Then
        assertThat(glp1InjectionPlanAndRecordOutDto.plan()).isNull();
    }
}
```

### 3) Web Layer (`web/`) — Mockito 또는 @WebMvcTest

| 항목 | 규칙 |
|------|------|
| 테스트 유형 | @WebMvcTest + `@MockBean` UseCase (규칙 08 §3 Web Unit Test 허용 범위) 또는 Mockito 단위 테스트 |
| 초점 | 컨트롤러 로직, 요청 매핑, 상태 코드, DTO 사용 |

### 4) Infrastructure Layer (`infrastructure/`) — @DataJpaTest + Testcontainers

| 항목 | 규칙 |
|------|------|
| 테스트 유형 | `@DataJpaTest` |
| DB | **Testcontainers MySQL 필수** — H2 절대 금지 |
| 초점 | 쿼리 정확성, 매핑 정확성, DB 제약조건 |

```java
@DataJpaTest
@AutoConfigurationPackage(basePackages = {"com.kakaohealthcare..."})
class MyRepositoryTest {
    @Autowired private MyJpaRepository repository;
    @Autowired private TestEntityManager em;

    @Test
    @DisplayName("특정 사용자의 활성 레이스를 조회한다")
    void findByUserIdAndStatus() {
        // Given
        em.persistAndFlush(entity);
        // When
        Optional<MyEntity> result = repository.findFirstByUserIdAndStatusOrderByCreatedAtDesc(1L, ACTIVE);
        // Then
        assertThat(result).isPresent();
    }
}
```

### 5) 통합 테스트 (`@SpringBootTest` + Testcontainers) — 동시성·세션 오염 검증 (v1.5)

`@DataJpaTest`(4계층)와 별개로, **아래 조건 중 하나라도 해당하면 통합 테스트 필수**. 단위 테스트로는 회귀 검증 불가한 영역.

| 트리거 | 이유 |
|--------|------|
| 동시 이벤트 처리 경합 (예: 뱃지 중복 발급, 리더보드 갱신) | 동일 Session 안 unique violation → AssertionFailure 회귀. Mockito로 재현 불가 |
| 트랜잭션 propagation 격리 (`REQUIRES_NEW` 등) | 실제 커밋·롤백 경계 검증 필요 |
| Hibernate Session 오염 회귀 (java-spring-coder v1.11-A/B/C 관련) | Session 상태 전이는 실제 EntityManager 없이 재현 불가 |
| DB 제약(UNIQUE·CHECK·FK) 위반 시 앱 행동 | 실제 MySQL 에러 코드(1062 등) 반환 검증 |
| 다중 인스턴스 pub-sub 메시지 흐름 | Redis Testcontainer 조합 |

**규칙**:
- Testcontainers MySQL 사용 (H2 절대 금지 — MySQL 8.0.13+ Functional Unique Index 등 방언 차이)
- 통합 테스트 파일명 `*IntegrationTest.java`로 구분, `@Tag("integration")`로 실행 그룹 분리
- 클래스 상단에 트리거 사유를 `@DisplayName` 또는 클래스 주석으로 명시 (예: "미션 뱃지 동시 발급 경합 회귀 방지")
- 2026-07-08 #633 미션 뱃지 사고 최종 리팩터에서 Testcontainers 통합 테스트 추가 사례

---

## 코딩 컨벤션

| 항목 | 규칙 |
|------|------|
| 클래스명 | `{ClassName}Test` |
| 메서드명 | 서술적 이름 또는 `whenX_thenY` |
| @DisplayName | **필수** — 한국어 설명 |
| Assertion | AssertJ `assertThat()` 필수 |
| 포매팅 | `./gradlew :{module}:spotlessApply` 실행 |
| 테스트 데이터 | 반복 데이터는 Constants로 추출 |

---

## 절대 금지 / 반드시 수행

### 파괴적 쓰기 가드 (공통 자원 참조)

> 원본: `forge/common/destructive-write-guard.md` (배포본: `.claude/shared/destructive-write-guard.md`)

- **기존 테스트 파일을 반드시 먼저 읽고 `Edit` 로 추가한다** — `cat >` · Write 로 통째 덮지 않는다 (DW-3). 2026-09-01 `UserDeviceTest.java` 를 덮어써 기존 테스트 3건을 삭제한 사고가 리뷰에서 발견됐다. 테스트 파일은 기존 메서드가 있을 확률이 가장 높은 파일 유형이다
- **덮어쓰기 전 `git status --short <경로>` 로 미커밋 변경 확인** (DW-1)
- **작업 후 `git status` / `git log <base>..HEAD --name-only` 로 의도치 않은 삭제가 없는지 확인** (DW-5)

### 리뷰 재발 방지 가드 — 테스트가 실제로 무엇을 잡는가 (공통 자원 참조)

> 원본: `forge/common/review-recurrence-guard.md`(배포본 `.claude/shared/review-recurrence-guard.md`) RR-12

- **동어반복 테스트 금지** — 검사 대상과 검사 기준이 같은 상수·같은 정규식이면 테스트는 항상 참이다. 오타를 넣어도 통과한다면 아무것도 잡지 못한다
- **위임만 검증하는 테스트 금지** — 서비스가 리포지토리 결과를 그대로 반환하는데 mock 반환값이 그대로 나오는지만 보면 깨질 수 없다
- **목표 경로가 실제로 실행되는지 확인** — 선검사(`exists`)로 early-return 하면 잡으려던 예외 경로가 한 번도 실행되지 않을 수 있다
- **수동 나열 목록 대신 스캔** — 대상을 손으로 나열하면 추가 시 갱신을 잊어 안전망이 조용히 빈다. 패키지·리플렉션 스캔으로 대체하고, 스캔 범위가 실제 대상 전체를 덮는지 확인한다
- **경계값 픽스처** — `limit`·임계값 로직은 경계를 **넘는** 픽스처를 쓴다. 상위 5건 로직을 3건으로 테스트하면 경계를 지나가지 않는다. 임계값 바로 옆 픽스처는 임계값이 조금만 바뀌어도 의도와 다른 이유로 실패한다
- **검증 방법** — 검증하려는 동작을 일부러 깨뜨렸을 때 테스트가 실패하는지 확인한다. 실패하지 않으면 회귀를 막지 못한다
- **테스트 코드에도 `var` 금지** — 명시 타입이 컨벤션이다. 같은 파일 기존 테스트가 `var` 를 써도 따라가지 않는다
- **기본값과 다른 값으로 검증** — 필드 기본값이 `true` 인데 `true` 로 요청하면 매핑을 빼도 통과한다(#791). false→true, true→false 둘 다 본다
- **새 검증·분기는 모든 진입 경로에서** — 등록(POST)·수정(PUT)에 같은 검증이 붙으면 둘 다 예외 테스트를 쓴다. 단위 테스트에는 "규칙 위반 시 예외 + 저장 미호출"을 넣는다(#800)
- **(v1.9) 요청 범위가 분기보다 좁아도 예외 분기는 작성** — "정상이랑 X 예외 두 개면 돼"처럼 요청된 케이스가 대상 메서드의 예외 분기(소유 확인 실패·존재하지 않음 등)보다 적으면, 빠진 분기 테스트를 **작성하고** `// 요청 외 추가: {분기} — 이 분기를 깨도 잡는 테스트가 없어서` 주석으로 표시한다. "원하시면 넣겠다"는 제안만으로 끝내지 않는다. 지우기는 쉽고, 빠진 분기는 아무도 실행하지 않는다(RR-14)
- **느슨한 JSON 단언 금지** — 키 부재는 `doesNotHaveJsonPath()`(`doesNotExist()` 는 JSON null 도 통과), 불리언은 `isBoolean()` 확인 뒤 값(`asBoolean()` 은 null 도 false), null 계약은 `value(nullValue())`(`isEmpty()` 는 빈 객체도 통과)(#801·#786)
- **이름 규칙** — 컬렉션은 `glp1InjectionRecordEntityList` 처럼 요소 타입+`List`, 시각은 `currentAt` 처럼 `At` 접미사, 대상·결과 변수도 `service`·`result` 대신 타입이 드러나게(#789·#791·#792)
- **실패 격리 테스트** — 여러 소스를 조립하는 서비스는 "한 소스가 예외를 내도 나머지가 반환된다"를 테스트한다. 트랜잭션 rollback-only 전파는 Mock 으로 재현되지 않으므로 실제 프록시(`@SpringBootTest`)로 확인한다(#793, RR-13)

### 절대 금지
- **H2 DB 사용** — Testcontainers MySQL 필수 (Infrastructure 계층)
- **Domain 테스트에 Spring 컨텍스트 로드** — 순수 JUnit 5만
- **계층 구분 없이 일괄 @SpringBootTest** — 계층별 적절한 방식 선택
- **@DisplayName 없는 테스트 메서드**
- **Mockito.any() 남용** — 가능하면 구체적 값으로 검증
- **테스트에서 실제 외부 API 호출**
- **FQCN(Fully Qualified Class Name) 직접 사용** — 테스트 코드 본문에 `com.x.y.Z` 형태 패키지 경로 박지 말 것. 무조건 파일 상단 `import` 추가 후 단순 클래스명 사용. 가장 자주 누수되는 두 패턴(PR #527 사례):

  ```java
  // ❌ 금지 — mock willThrow에서 패키지 경로 인라인
  given(repo.save(entity))
      .willThrow(new org.springframework.dao.DataIntegrityViolationException("duplicate"));

  // ❌ 금지 — assertThatThrownBy.isInstanceOf .class 리터럴
  assertThatThrownBy(() -> service.register(data))
      .isInstanceOf(org.springframework.dao.DataIntegrityViolationException.class);

  // ✅ 올바름 — import 추가 후 단순 클래스명
  import org.springframework.dao.DataIntegrityViolationException;
  ...
  given(repo.save(entity))
      .willThrow(new DataIntegrityViolationException("duplicate"));
  assertThatThrownBy(() -> service.register(data))
      .isInstanceOf(DataIntegrityViolationException.class);
  ```

  검사 대상: `new x.y.Z()`, `x.y.Z.class`, 변수·매개변수·제네릭 타입, 캐치 절. **"테스트라 한 번만 쓰니까 인라인으로"는 금지** — 휴먼 리뷰가 반드시 잡아낸다(휴먼 리뷰어 지적 1회 = 스킬 결함).

  **(v1.3 확장)** 빌더 인자의 enum 상수 접근도 검사 대상:
  ```java
  // ❌ 금지 (2026-05-21 commit a6b72daa82 사례)
  User.builder()
      .stateInfo(com.kakaohealthcare.moneyball.user.entity.State.NORMAL)
      ...

  // ✅ 올바름
  import com.kakaohealthcare.moneyball.user.entity.State;
  ...
  User.builder()
      .stateInfo(State.NORMAL)
      ...
  ```

- **(v1.3) @MockBean 빈 이름 매직 스트링 금지** — `@MockBean(name = "...")`, `@Qualifier("...")`에 빈 이름 문자열 인라인 금지. 빈 등록자(`*Configuration`)가 제공한 상수를 import해 사용. 등록자에 상수가 없으면 **본 스킬에서 정의하지 않고** 등록자 측에 상수 추가를 요청 (테스트 코드가 빈 이름의 SSOT 되면 안 됨).

  ```java
  // ❌ 금지 (2026-05-21 사례 — 8곳 매직 스트링)
  @MockBean(name = "dexcomAuthorizedClientManager")
  private OAuth2AuthorizedClientManager mgr;

  // ✅ 올바름 — 등록자가 제공한 상수 import
  import static com.x.shared.constant.DexcomBeanNameConstants.DEXCOM_AUTHORIZED_CLIENT_MANAGER;
  ...
  @MockBean(name = DEXCOM_AUTHORIZED_CLIENT_MANAGER)
  private OAuth2AuthorizedClientManager mgr;
  ```

- **(v1.4) application·domain 테스트에서 infra 구현체 직접 참조 금지** — `.infrastructure.`/`.persistence.`/`.cache.impl.` 등 infra 패키지 클래스를 도메인 계약(interface) 대신 테스트에서 직접 임포트·인스턴스화하지 말 것. domain 인터페이스의 **테스트용 Fake**를 `src/test/` 하위(`FakeXxxRepository`, `FakeXxxCache` 등)에 배치해 사용. Fake는 인메모리 컬렉션 기반 최소 구현이며, infra의 실제 로직(Redis 명령·JDBC 쿼리 등)을 재현하지 않는다. 이유: 계층 경계 위반 테스트는 infra 리팩터에 취약해 도메인 테스트가 쉽게 깨진다 (2026-07-07 `PricingQueryServiceTest`가 `InMemoryPricingRuleCache` 직접 참조 → `PricingRuleCache` 인터페이스 Fake로 전환된 사례).

  ```java
  // ❌ 금지 — application 테스트에서 infra 구현체 직접 참조
  import com.x.pricing.infrastructure.cache.InMemoryPricingRuleCache;
  ...
  InMemoryPricingRuleCache inMemoryPricingRuleCache = new InMemoryPricingRuleCache();
  PricingQueryService pricingQueryService = new PricingQueryService(inMemoryPricingRuleCache);

  // ✅ 올바름 — domain 인터페이스의 Fake를 test/ 하위에 배치해 사용
  // src/test/java/.../pricing/domain/FakePricingRuleCache.java
  class FakePricingRuleCache implements PricingRuleCache { ... }  // 인메모리 최소 구현

  // 테스트 본문
  PricingRuleCache fakePricingRuleCache = new FakePricingRuleCache();
  PricingQueryService pricingQueryService = new PricingQueryService(fakePricingRuleCache);
  ```

- **(v1.4, v1.9 정합화) 호출 검증은 손으로 쓴 Spy 우선, Mockito `verify` 는 Mock 이 불가피할 때만** — 규칙 08 §2-2 "피할 것"에 따라 호출 이력은 `Spy{Interface}`(JDK 컬렉션으로 이력 기록, Mockito 미사용)의 `getCallCount()`·`getLastCall()` 로 본다. 발행 실패 흡수·재시도처럼 **실제 로직이 돌아야 하는 경로**를 `verify(mock, times(1))` 로만 보면 흡수 경로가 커버되지 않는다 (2026-07-07 `PricingChangePublisherTest` 사례).

  | 목적 | 선택 | 이유 |
  |------|------|------|
  | 외부 통신·void 부수효과의 호출 여부·인자 | 손으로 쓴 `Spy{Interface}` + `getCallCount()`/`getLastCall()` | 규칙 08 기본. 테스트가 Mockito 에 묶이지 않음 |
  | 발행 실패 흡수·재시도 관찰 | 실제 구현 + 하위 협력 객체를 Spy(n번째 호출 예외 설정) | 실제 로직이 돌아야 흡수/재시도 경로가 커버됨 |
  | Fake·Spy 로 대체할 수 없는 외부 라이브러리 | Mockito `mock` + `verify` (사유 주석 한 줄, 핵심 인자는 값 고정) | 예외적 허용 |

  ```java
  // ❌ 부적합 — 발행 실패 흡수 로직인데 mock으로 verify만
  verify(publisher, times(1)).publish(any());  // 흡수 경로 커버 못함, any() 로 인자도 안 봄

  // ✅ 적합 — 실제 발행 로직 + 하위 전송 클라이언트 Spy
  SpyRedisMessageSender spyRedisMessageSender = new SpyRedisMessageSender();
  spyRedisMessageSender.failOnCall(1);                     // 첫 전송 실패 → 흡수·재시도 경로 실행
  PricingChangePublisher pricingChangePublisher = new PricingChangePublisher(spyRedisMessageSender);
  PricingCommandService pricingCommandService = new PricingCommandService(pricingChangePublisher);

  pricingCommandService.invalidateAll();

  assertThat(spyRedisMessageSender.getCallCount()).isEqualTo(2);
  ```

### 반드시 수행
1. Phase 0 사전 확인 (계층 식별 + 기존 패턴 확인)
2. 계층에 맞는 테스트 방식 선택
3. Given-When-Then 구조 적용
4. @DisplayName 한국어 설명 작성
5. 테스트 실행 및 통과 확인: `./gradlew :{module}:test --tests {ClassName}`
6. `python3 forge/common/review-lint.py` 실행 — 위반 0건, 확인 항목은 해당 여부 판단 (RR-L)
7. **(v1.9) 스스로 찾은 결함은 최종 코드에서 고친 뒤 보고** — 검토 중 "이 테스트는 목표 경로를 안 탄다"·"두 번 호출해 fallback 이 아닌 선조회 경로를 본다" 같은 결함을 발견하면, 결함 있는 코드에 "고쳐야 할 점" 설명을 덧붙여 내지 않고 **제출 코드 자체를 고친다**. 제출된 코드가 그대로 복사돼 들어가기 때문이다
8. **(v1.9) 사용자 요청을 규칙 때문에 바꿨다면 규칙 원본을 인용** — FQCN 인라인 거부는 규칙 07 `Explicit Imports`(`forge/common/pasta-rules/07-general-project-convention.md`, 배포본 `.claude/rules/07-...`), Repository·UseCase `@Mock` 거부는 규칙 08 §2, POST 만 테스트 요청 보정은 RR-14 를 근거로 적는다. 스킬 내부 번호(AUTO FAIL n)만 대면 사용자가 확인할 원본이 없다

---

## 자기 검증 체크리스트

| # | 등급 | 항목 |
|---|------|------|
| 1 | B | 대상 클래스 계층 정확히 식별했는가? |
| 2 | B | 계층에 맞는 테스트 방식을 적용했는가? (Domain=순수, App=Fake 우선·외부 통신만 Spy, Web=@WebMvcTest, Infra=Testcontainers) |
| 3 | B | H2 사용하지 않았는가? (Infrastructure 계층) |
| 4 | B | @DisplayName 한국어 설명이 모든 테스트에 있는가? |
| 5 | B | 테스트가 통과하는가? |
| 6 | R | Given-When-Then 구조를 따르는가? |
| 7 | R | @Nested로 메서드별 그룹핑했는가? (Application 계층) |
| 8 | R | AssertJ assertThat()을 사용했는가? |
| 9 | R | 기존 테스트 패턴과 일관성이 있는가? |
| 10 | R | spotlessApply를 실행했는가? |
| 11 | B | FQCN 직접 사용 없는가? — `new x.y.Z()` / `isInstanceOf(x.y.Z.class)` / 변수·매개변수 모두 import + 단순 클래스명? |
| 12 | R | **(v1.2) 계층 식별 근거 명시** — 대상 클래스의 패키지 경로 / 의존성으로 계층을 확정했는가? 추정 시 "추정" 표기? |
| 13 | R | **(v1.2) Fixture 가정 표기** — 비즈니스 의미 없는 임의값(예: `"test@test.com"`)이 아니라 실제 도메인에서 유효한 값을 사용했는가? 가정값은 주석으로 표기? |
| 14 | R | **(v1.2) 기존 테스트 스타일 정렬** — 동일 패키지의 기존 테스트와 `@Nested` 그룹핑·`@DisplayName` 한국어 톤·AssertJ 사용 패턴이 일치하는가? |
| 15 | B | **(v1.3) @MockBean 빈 이름 상수화** — `@MockBean(name = "...")` / `@Qualifier("...")` 매직 스트링 0건? 등록자 상수 import 사용? |
| 16 | B | **(v1.3) enum 인라인 FQCN 확장** — 빌더 인자·메서드 호출에 `com.x.y.Z.ENUM_CONST` 형태 인라인 0건? (`.stateInfo(State.NORMAL)`로 정리) |
| 17 | B | **(v1.4) infra 직접 참조 금지** — application·domain 계층 테스트에서 `.infrastructure.`/`.persistence.`/`.cache.impl.` 클래스 직접 참조 0건? domain 인터페이스 Fake 사용? |
| 18 | R | **(v1.4) verify vs Spy 선택 근거** — side-effect(예외 흡수·재시도) 관찰이 필요한 지점에서 `verify()`가 아닌 Spy 콜카운트를 사용했는가? 순수 상호작용 검증에는 `verify()`를 유지? |
| 19 | B | **(v1.8) 상태 저장소 Fake** — Application 단위 테스트에서 Repository·UseCase·QueryService 를 `@Mock` 으로 두지 않았는가? (규칙 08, RR-F14) |
| 20 | B | **(v1.8) 깨뜨리면 실패하는가** — 기본값과 다른 값으로 매핑을 검증했는가? 새 검증을 모든 진입 경로에서 테스트했는가? 느슨한 JSON 단언(`doesNotExist`·`asBoolean`·`isEmpty`)이 없는가? |
| 21 | B | **(v1.8) review-lint 위반 0건** — `review-lint.py` 를 실행했는가? |
| 22 | B | **(v1.9) 빠진 예외 분기** — 대상 메서드의 예외 분기(소유 확인·미존재·규칙 위반)마다 테스트가 있는가? 요청 외 추가분은 주석으로 표시했는가? |
| 23 | B | **(v1.9) 제출 코드 = 최종 코드** — 스스로 발견한 결함을 "고쳐야 할 점"으로 남기지 않고 코드에서 고쳤는가? 요청을 바꾼 지점마다 규칙 원본(07·08·RR-n)을 인용했는가? |

**표기**: B = 블로커 (미충족 시 FAIL), R = 권장

---

## 작업 종료 출력 템플릿

1. **대상 클래스**: 클래스명 + 계층
2. **테스트 방식**: 순수 JUnit / Fake·Spy / @WebMvcTest / @DataJpaTest (Mock 을 썼다면 사유)
3. **Self-check 결과표**: PASS/FAIL/N/A
4. **테스트 실행 결과**: 통과/실패
5. **남은 리스크**: 0~3개
