---
name: java-layered-unit-testing
description: "Java Spring Boot 계층별 단위 테스트 작성 전문가. 4-Tier 아키텍처(Web, Application, Domain, Infrastructure) 각 계층에 적합한 테스트 방식을 적용한다. Domain은 순수 JUnit 5, Application/Web은 Mockito, Infrastructure는 @DataJpaTest + Testcontainers MySQL. 'テスト作成', '단위 테스트', 'unit test', '테스트 코드 작성', '계층별 테스트', 'Mockito', 'Testcontainers' 요청 시 사용한다."
version: "1.3"
last-modified: "2026-05-21"
changelog: "v1.3 — 2026-05-21 pasta 사례 반영: (1) @MockBean(name=...) 빈 이름 매직 스트링 금지 — 빈 등록자가 제공한 상수 import 강제. (2) enum 인라인 FQCN 패턴 명시 — `.stateInfo(com.x.y.State.NORMAL)` 같은 빌더 인자도 검사 대상. | v1.2 — blueprint v2.0 패턴 이식. v1.1 — FQCN 직접 사용 금지. v1.0 — pasta 역수입"
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

### 2) Application Layer (`application/`) — Mockito

| 항목 | 규칙 |
|------|------|
| 테스트 유형 | Mockito-based unit test |
| 어노테이션 | `@ExtendWith(MockitoExtension.class)`, `@Mock`, `@InjectMocks` |
| 초점 | 유스케이스 조율, DTO 변환, Repository 인터페이스 호출 |
| 구조 | `@Nested`로 메서드별 그룹핑, Given-When-Then |

```java
@ExtendWith(MockitoExtension.class)
class MyPlanRoutineRaceQueryServiceTest {
    @Mock private MyPlanRoutineRaceRepository repository;
    @InjectMocks private MyPlanRoutineRaceQueryService service;

    @Nested
    @DisplayName("getRoutineRace")
    class GetRoutineRace {
        @Test
        @DisplayName("레이스가 존재하면 QueryResult를 반환한다")
        void returnsQueryResult_whenRaceExists() {
            // Given
            when(repository.findById(1L)).thenReturn(Optional.of(mockRace));
            // When
            var result = service.getRoutineRace(new MyPlanRoutineRaceIdInDto(1L));
            // Then
            assertThat(result.routineRaceId()).isEqualTo(1L);
        }
    }
}
```

### 3) Web Layer (`web/`) — Mockito 또는 @WebMvcTest

| 항목 | 규칙 |
|------|------|
| 테스트 유형 | Mockito 단위 테스트 (기본) 또는 @WebMvcTest (MVC 통합 필요 시) |
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

### 반드시 수행
1. Phase 0 사전 확인 (계층 식별 + 기존 패턴 확인)
2. 계층에 맞는 테스트 방식 선택
3. Given-When-Then 구조 적용
4. @DisplayName 한국어 설명 작성
5. 테스트 실행 및 통과 확인: `./gradlew :{module}:test --tests {ClassName}`

---

## 자기 검증 체크리스트

| # | 등급 | 항목 |
|---|------|------|
| 1 | B | 대상 클래스 계층 정확히 식별했는가? |
| 2 | B | 계층에 맞는 테스트 방식을 적용했는가? (Domain=순수, App=Mockito, Infra=Testcontainers) |
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

**표기**: B = 블로커 (미충족 시 FAIL), R = 권장

---

## 작업 종료 출력 템플릿

1. **대상 클래스**: 클래스명 + 계층
2. **테스트 방식**: 순수 JUnit / Mockito / @DataJpaTest
3. **Self-check 결과표**: PASS/FAIL/N/A
4. **테스트 실행 결과**: 통과/실패
5. **남은 리스크**: 0~3개
