# 조직 컨벤션 적용 시 테스트 규칙 (v1.10)

SKILL.md Phase 0-5 에서 **조직 컨벤션 적용 프로젝트**로 판정됐을 때만 읽는다. 비적용 프로젝트는 이 파일을 쓰지 않고 SKILL.md 본문(규칙 08·09)대로 한다.

- 판정·우선순위·충돌 표: `forge/common/vc-conventions-guide.md`(배포본 `.claude/shared/vc-conventions-guide.md`) 2·3절, 4-2절
- 원문: `forge/common/vc-conventions/testcode-convention.md`(배포본 `.claude/shared/vc-conventions/testcode-convention.md`), 변수명은 `naming-convention.md`
- 원문 폴더가 비어 있으면 가이드 4-2절 요약으로 적용하고 보고에 "조직 컨벤션 원문 미확인"을 적는다
- **신규·이번 작업에서 바꾸는 테스트에만 적용한다.** 같은 파일의 기존 테스트가 다르게 써 있어도 고치지 않는다(가이드 3절, SC-1). 고칠 가치가 있으면 보고에 "범위 밖 제안"

## 1. 대상별 테스트 더블 (원문 3절 표)

| 대상 | 테스트 더블 | Spring Context |
|------|-------------|----------------|
| Domain | Fixture 만 | 없음 |
| Service·Facade | Fixture + `Fake*` Repository·UseCase | 없음 |
| Controller | `@MockitoBean` UseCase + Fixture | `@WebMvcTest` |
| Repository·쿼리 | 실제 DB + Fixture | `@DataJpaTest` |
| 인수 테스트(E2E) | 실제 Bean | `@SpringBootTest(RANDOM_PORT)` + `TestRestTemplate`, **여기에만** |

- `@MockitoBean` 은 Spring Boot 3.4 부터 있다. 모듈이 3.4 미만이면(2026-11-13 실측 pasta·moneyball 모두 3.2.2) `@MockBean` 을 그대로 쓰고 보고에 한 줄 적는다. 없는 어노테이션을 써서 컴파일을 깨뜨리지 않는다
- 외부 통신 호출 기록용 손으로 쓴 `Spy*` 는 그대로 쓴다(원문이 금지한 이름은 `Stub*` 뿐). 인메모리 저장소 대역은 반드시 `Fake*`

## 2. `@SpringBootTest` 예외

E2E 가 아닌데 `@SpringBootTest` 가 필요한 경우는 **슬라이스(`@DataJpaTest`·`@WebMvcTest`)나 Fake 조합으로 재현되지 않는 검증**뿐이다(가이드 3절 판정).

| 검증 | 방식 |
|------|------|
| DB 제약 위반(UNIQUE·FK) 시 예외, Hibernate Session 상태 | `@DataJpaTest` 로 먼저 시도 (실제 EntityManager·DB 가 뜬다) |
| 트랜잭션 전파(rollback-only, `REQUIRES_NEW`)처럼 **서비스 프록시 경계**를 넘는 동작 | 예외 허용: `@SpringBootTest` |
| 여러 트랜잭션이 동시에 도는 경합 | 예외 허용: `@SpringBootTest` |

예외를 쓸 때는 두 곳에 사유를 남긴다.

```java
// @SpringBootTest 예외: rollback-only 전파는 서비스 프록시 경계를 넘어야 재현된다.
// @DataJpaTest·Fake 로는 재현 안 됨 (vc-conventions-guide 3절, RR-13)
@SpringBootTest
@Tag("integration")
class Glp1HomeCardQueryServiceIntegrationTest {
```

PR 본문에도 "`@SpringBootTest` 예외 사유: …" 한 줄.

## 3. 테스트 DB

**모듈의 기존 테스트 DB 설정을 따른다.** Testcontainers 모듈을 H2 로, H2 모듈을 Testcontainers 로 바꾸지 않는다(규칙 09 가드레일이 조직 컨벤션보다 우선, 가이드 3절).

- 확인 순서: 같은 테스트 클래스 → 같은 패키지 이웃 테스트(`@ActiveProfiles`·`@AutoConfigureTestDatabase`) → 모듈 `src/test/resources/application*.yml`
- 한 모듈 안에서도 섞여 있다. 2026-11-13 moneyball `analysis`: `application.yml` 은 H2(`MODE=MySQL`), `application-test.yml` 은 Testcontainers(`jdbc:tc:mysql`). `@ActiveProfiles("test")` 가 붙은 Repository 테스트 4개는 Testcontainers, 안 붙은 3개(`PGHDActivityWorkoutRecordGlucoseMap*`)는 H2
- 기존 클래스에 메서드를 더하면 그 클래스 설정을 그대로 쓴다. `@ActiveProfiles` 를 더하거나 빼지 않는다
- 새 클래스는 같은 패키지에서 같은 테이블·쿼리를 다루는 테스트의 설정을 따르고, 근거를 보고에 적는다
- H2 에서 돌지 않는 MySQL 전용 쿼리(예: `ON DUPLICATE KEY UPDATE`, JSON 함수)를 만나면 쿼리를 H2 용으로 고치지 않고, DB 설정도 바꾸지 않는다. 막힌 지점을 보고하고 사용자에게 선택지를 묻는다
- 모듈에 테스트 DB 설정이 아예 없으면 혼자 정하지 않고 사용자에게 묻는다(SC-3)

## 4. 작성 규칙 체크

| 항목 | 규칙 |
|------|------|
| Fake 이름 | `Fake{Interface}`. `Stub*` 이름 금지. 사용자가 "Stub 으로"라고 해도 `Fake*` 로 짓고 근거(원문 4절)를 적는다 |
| `@DisplayName` | 한국어, 구체적인 행동과 결과. "정상", "성공", "실패", "테스트" 만으로 끝내지 않는다. 예: "만료된 쿠폰을 사용하면 CouponExpiredException 이 발생한다" |
| 구조 | `// Given` `// When` `// Then` 주석 필수(예외 단언은 `// When & Then` 허용) |
| 메서드명 | 새 클래스는 영어 `{상황}_{기대결과}` + 한국어 `@DisplayName`. 기존 클래스에 더할 때는 그 클래스 관례(가이드 3절) |
| 상태 공유 | `@BeforeEach` 로 초기화. `@BeforeAll`·`static` 필드에 테스트가 바꾸는 데이터를 두지 않는다. `@TestMethodOrder`·`@Order` 로 순서에 기대는 테스트를 새로 만들지 않는다 |
| 비동기 대기 | `Thread.sleep` 금지. Awaitility `await().atMost(…).untilAsserted(…)` |
| `@Nested` | 안에 테스트 메서드가 1개뿐이면 묶지 않는다. 2개 이상일 때만 메서드·상황별로 묶는다 |
| 단언 | AssertJ 만. `org.junit.jupiter.api.Assertions` import 금지 |
| 검증 개수 | 한 테스트에 논리적 검증 하나(단위·통합). 같은 대상의 여러 필드를 보는 것은 하나로 본다(`extracting(...).containsExactly(...)`). 반환값 + 저장 미호출처럼 성격이 다른 검증은 테스트를 나눈다. 시나리오·인수 테스트는 예외 |
| 변수명 | 타입명 전체(`glp1InjectionRecordEntity`), `result`·`dto`·`res`·`e` 금지 (naming 원문) |

## 5. 보고

- 판정 결과 한 줄: "조직 컨벤션 적용 (`.claude/shared/vc-conventions-guide.md` 있음)" 또는 "비적용 (가이드 없음) — 프로젝트 규칙 08·09 기준"
- 사용자 요청을 조직 컨벤션 때문에 바꿨으면 원문 파일과 절, 가이드 3절 판정을 인용한다
- `review-lint.py` 는 가이드가 옆에 있으면 VC 검사가 자동으로 켜진다. `Thread.sleep`·JUnit Assertions 는 `[위반]`, `Stub*`·모호한 `@DisplayName`·`@BeforeAll`·`@SpringBootTest` 는 `[확인]` 으로 나온다
