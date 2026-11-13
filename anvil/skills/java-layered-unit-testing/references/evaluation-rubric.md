# java-layered-unit-testing 평가 루브릭

- [평가 항목](#평가-항목)
- [AUTO FAIL 조건](#auto-fail-조건)
- [합격 기준](#합격-기준)
- [평가 실행 방법](#평가-실행-방법)

---

## 평가 항목

| # | 항목 | 배점 | 설명 |
|---|------|------|------|
| 1 | **계층별 테스트 방식 적합성** | 25 | Domain=순수 JUnit, App=**Fake 우선**(Repository·UseCase·QueryService 는 Fake, 외부 통신·void 부수효과는 Spy, Mock 은 사유 주석과 함께 제한적), Web=@WebMvcTest+@MockBean UseCase(적용 프로젝트는 @MockitoBean, Boot 3.4 미만이면 @MockBean), Infra=@DataJpaTest + 테스트 DB(비적용: Testcontainers, 적용: 모듈 기존 설정). (v1.8 정합화: 이전 기준 "App=Mockito" 는 규칙 08 §2 와 충돌해 #789·#794 지적을 낳았으므로 폐기) |
| 2 | **테스트 통과 여부** | 25 | 모든 테스트가 실제로 통과하는가 |
| 3 | **테스트 커버리지 / 품질** | 20 | 핵심 분기, 엣지 케이스, 실패 시나리오 포함 |
| 4 | **코딩 컨벤션 준수** | 15 | @DisplayName, Given-When-Then, AssertJ, @Nested. (v1.10) 적용 프로젝트는 vc-testcode.md 4절 포함, 완료 보고 share-writing-guard A 등급 |
| 5 | **기존 패턴 일관성** | 15 | 프로젝트 기존 테스트와 스타일 일관 |
| | **합계** | **100** | |

---

## AUTO FAIL 조건

1. **테스트 DB 전환·위반** — 비적용 프로젝트: H2 사용(Testcontainers MySQL 필수). 적용 프로젝트(v1.10): 모듈·클래스의 기존 테스트 DB 설정을 다른 쪽으로 전환(H2→Testcontainers, Testcontainers→H2, `@ActiveProfiles` 추가·제거로 DB 가 바뀌는 경우 포함). 적용 프로젝트의 H2 모듈에서 H2 를 유지한 것은 위반 아님
2. **Domain 계층 테스트에 @SpringBootTest 사용**
3. **테스트 전체 실패 (컴파일 에러 포함)**
4. **계층 무시하고 일괄 @SpringBootTest 적용**
5. **FQCN 직접 사용** — 테스트 코드 본문(import 외)에 `com.x.y.Z` 형태 패키지 경로 박힘. `new x.y.Z()` / `isInstanceOf(x.y.Z.class)` / 변수·매개변수·제네릭 모두 적용. PR #527 사례.
6. **(v1.8) 상태 저장소 Mock 정답 주입 (RR-F14)** — Application 단위 테스트에서 `*Repository`·`*UseCase`·`*QueryService` 를 `@Mock`/`mock()` + `given().willReturn()` 으로 둠. 사용자가 "기존처럼 Mock 으로" 요구해도 적용. Web 계층 `@WebMvcTest` 의 `@MockBean` UseCase 는 제외(규칙 08 §3 허용 범위).
7. **(v1.10, 적용 프로젝트) 조직 컨벤션 테스트 하드 위반** — 코드 블록에 `Thread.sleep`, 또는 E2E 가 아닌 테스트에 사유 주석 없는 `@SpringBootTest`. (카탈로그 N-3)
8. **(v1.10, 비적용 프로젝트) 조직 컨벤션 과잉 적용** — 가이드가 없는 프로젝트에서 조직 컨벤션을 근거로 규칙 08·09 와 다르게 구현(예: Testcontainers 필수인데 "조직 컨벤션은 H2 기본"이라며 H2 사용, 규칙 08 의 `@Nested` 그룹핑을 조직 컨벤션 근거로 거부). (카탈로그 N-1 AUTO FAIL 후반)

### 감점 기준 (v1.8 신설, 항목 3 "커버리지/품질" 에서 차감)

| 패턴 | 감점 |
|------|------|
| 기본값과 같은 값으로만 매핑 검증 (예: 기본 `true` 필드를 `true` 로만 요청) | -5 |
| 같은 검증이 붙은 진입 경로(POST·PUT 등) 중 일부만 예외 테스트 | -5 |
| 느슨한 JSON 단언 (`doesNotExist()` 로 null 계약, `asBoolean()` 단독, `jsonPath(..).isEmpty()` 로 null 계약) | -3/건 (최대 -6) |
| 규칙 위반 예외 테스트에 "저장 미호출" 확인 누락 | -3 |
| 다중 소스 조립 서비스에 실패 격리 테스트 누락, 또는 rollback-only 전파 위험을 Mock/Fake 만으로 검증 완료로 단정 | -5 |
| 이름 규칙 위반 (`service`·`result`·접미사 없는 컬렉션·`At` 없는 시각) — 항목 4 에서 차감 | -2/종류 (최대 -6) |
| `review-lint.py` 실행 단계 누락 — 항목 4 에서 차감 | -3 |
| (v1.10, 적용) `Stub*` 이름 — 항목 4 | -3 |
| (v1.10, 적용) "정상·성공"류 모호한 `@DisplayName`, GWT 주석 누락, 1개짜리 `@Nested`, JUnit `Assertions`, `@BeforeAll` 공유 데이터 — 항목 4 | -2/종류 (최대 -8) |
| (v1.10, 적용) 한 테스트에 성격이 다른 논리 검증 여럿 — 항목 3 | -2 |
| (v1.10, 적용) `@SpringBootTest` 예외에 테스트 주석 또는 PR 본문 사유 한쪽 누락 — 항목 1 | -3 |
| (v1.10) 조직 컨벤션 판정 결과 미보고 — 항목 5 | -3 |
| (v1.10) 완료 보고 share-writing-guard 위반(첫 줄 결론·단계 없음, 미실행 "통과", "없음" 줄) — 항목 4 | -2/건 (최대 -4) |

---

## 합격 기준

| 등급 | 점수 | 설명 |
|------|------|------|
| **EXCELLENT** | 90~100 | 계층별 방식 완벽, 전체 통과, 엣지 케이스 포함 |
| **PASS** | 75~89 | 계층별 방식 OK, 테스트 통과, 경미한 미흡 |
| **FAIL** | 0~74 | 계층 구분 미흡 또는 테스트 실패 |

---

## 평가 실행 방법

### 테스트 케이스 유형

| 유형 | 비율 | 예시 |
|------|------|------|
| Happy Path | 50% | Application Service 테스트 작성 요청 |
| Edge Case | 30% | Domain 복잡 로직 테스트, Repository 커스텀 쿼리 테스트 |
| Negative | 20% | H2 사용 유도, @SpringBootTest 유도, 계층 미구분 유도, Repository `@Mock` 유도(v1.8), 조직 컨벤션 이탈 유도 N-3(v1.10) |

### 변경 이력

| 날짜 | 내용 |
|------|------|
| 2026-11-13 | v1.10 — 항목 1·4 조직 컨벤션 조건 추가, AUTO FAIL 1 조건부(적용 프로젝트는 테스트 DB 전환이 위반), AUTO FAIL 7(N-3)·8(과잉 적용) 신설, v1.10 감점 기준 추가 |
| 2026-11-13 | v1.8 정합화 — 항목 1 의 Application 기준을 Mockito → Fake 우선으로 교체, AUTO FAIL 6(RR-F14) 추가, v1.8 감점 기준 신설. 사유: SKILL.md v1.8 이 Application 기본 방식을 Fake 우선으로 바꿨는데 루브릭은 Mockito 를 정답으로 채점하고 있어 스킬과 모순 |
