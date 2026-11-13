# 조직 코딩 컨벤션 적용 가이드 (virtualcare/coding-conventions)

코드를 쓰거나 리뷰하는 컴포넌트가 조직 컨벤션을 언제, 어떤 순서로 적용하는지 정한다. 규칙 본문은 원문(`vc-conventions/*.md`)에 있고, 이 문서는 적용 판정만 다룬다.

- 원문 위치: forge `forge/common/vc-conventions/` (배포본 `.claude/shared/vc-conventions/`)
- 원문은 사내 internal 저장소 문서라 forge 저장소에 커밋하지 않는다. forge 저장소의 `vc-conventions-sync.sh` 로 받고, 프로젝트에는 forge-deploy 가 원문 폴더째 배포한다
- 버전: 0.1 (2026-11-13)

## 1. 기준 버전

| 항목 | 값 |
|------|-----|
| 저장소 | `virtualcare/coding-conventions` |
| 기준 | PR #7 `convention/align-review-rules` 커밋 `7cc266d` (2026-11-13 미병합, 항목별 팀 합의 진행 중) |
| 받은 시각 | 원문 폴더의 `SOURCE` 파일 |
| MySQL | `mysql-convention.md` 는 PR #7 이 건드리지 않았다(PR #6 개편 중). main 기준 |

PR #7 이 병합되거나 항목이 되돌려지면 `VC_CONV_REF` 를 바꿔 다시 받고 이 표를 고친다. 되돌려진 항목은 3절 판정에서도 지운다.

## 2. 적용 대상 판정

1. `.claude/shared/vc-conventions-guide.md` 가 있으면 조직 컨벤션 적용 프로젝트다. **forge 저장소 자체는 비적용**이다(이 파일이 `forge/common/` 에 있어도 forge 커밋·코드는 forge 규칙을 따른다). forge 에서 컴포넌트를 평가할 때는 TC 가 명시한 프로젝트 맥락으로 판정한다.
2. 없으면 조직 컨벤션을 적용하지 않고 프로젝트 규칙(`.claude/rules/`)만 따른다. 없다는 이유로 원문을 다른 곳에서 찾아 적용하지 않는다.
3. 원문 폴더가 비어 있으면(동기화 안 됨) 작업을 멈추지 않는다. 이 가이드 4절 요약으로 적용하고 보고에 "조직 컨벤션 원문 미확인"을 적는다.

배포 대상: virtualcare 조직 저장소(pasta-japan-server, moneyball). 조직 밖 저장소(poc-meal-recommender 등)에는 배포하지 않는다.

## 3. 우선순위

신규로 쓰는 코드와 이번 작업에서 바꾸는 코드에 적용한다. **기존 코드를 일괄로 바꾸지 않는다**(PR #7 전제).

1. 하드 가드레일 — `destructive-write-guard`, `scope-discipline-guard`, `review-recurrence-guard`, 프로젝트 규칙 09(가드레일)
2. 조직 컨벤션 — `vc-conventions/*.md`
3. 프로젝트 규칙의 스타일 항목 — `.claude/rules/` 01~08, 11
4. 같은 파일·패키지의 기존 관례

**사용자가 명시한 API 계약(경로·HTTP 메서드·요청/응답 필드명)은 조직 컨벤션 적용 대상이 아니다.** 기존 관례와 다르면 바꾸지 말고 결정 요청으로 남긴다.

2와 3이 충돌하면 아래 표의 판정을 따르고 다시 묻지 않는다. 표에 없는 충돌은 구현 전에 사용자에게 묻되 권장안은 조직 컨벤션 우선으로 제시한다. 물을 수 없는 흐름(자동 실행 등)이면 조직 컨벤션을 따르고 PR 본문에 "표에 없는 충돌, 조직 컨벤션 우선 적용"을 적는다.

| 항목 | 조직 컨벤션 | 프로젝트 규칙·기존 스킬 | 실측 (2026-11-13, pasta / moneyball) | 판정 |
|------|-------------|------------------------|--------------------------------------|------|
| 정적 팩토리 | 생성자 직접 호출·생성자 `@Builder`. `from`/`of` 는 복잡한 변환일 때만, 이름은 자기 타입 반환 시만 | 규칙 02·03·05 가 `of`/`from` 필수 | 최근 60일 추가 12건 / 324건 | 신규 클래스는 조직 컨벤션. 이미 `from()` 이 있는 클래스에 필드만 더할 때는 기존 메서드를 고쳐 쓰고 새 팩토리를 만들지 않는다 |
| 커밋·PR 제목 | `[핵심키워드] 명사형 요약`, 이슈 키는 요약 앞, `feat:` 등 접두어 금지 | 규칙 11·`git-commit` 이 `feat:`·`refac:` | `[키워드]` 140:34 / 564:85. 대부분 squash 머지 제목(=PR 제목)이고, pasta 브랜치 개별 커밋은 아직 `fix:`·`perf:` 가 많다 | 조직 컨벤션 (PR 제목·개별 커밋 모두) |
| 이슈 키 위치 | 요약 앞 (`[건강나이] CF-12100 ...`) | 규정 없음 | moneyball 요약 앞 1 : 끝 괄호 `(CORE-1522)` 68 | 원문(요약 앞)을 따른다. PR #7 #9 합의에서 끝 괄호로 정해지면 이 행을 바꾼다. 남의 커밋의 끝 괄호는 지적하지 않는다 |
| 테스트 DB | H2 기본, MySQL 호환 필요 시 Testcontainers | 규칙 09 가 Testcontainers 원칙·H2 전환 금지 | 두 저장소 모두 모듈별 혼재 | **모듈의 기존 테스트 DB 설정을 따른다.** 어느 쪽으로도 전환하지 않는다(규칙 09 가드레일) |
| `@SpringBootTest` | 인수 테스트(E2E)에만 | RR-13 rollback-only 는 실제 프록시로 검증 | 46 / 56개 파일 | E2E 에만. 트랜잭션 전파(rollback-only)처럼 슬라이스로 재현되지 않는 검증만 예외로 두고 테스트 주석과 PR 본문에 사유를 적는다 |
| Controller 이름 | 변경 `{Domain}CommandController` / 조회 `{Domain}QueryController` | 규정 없음 | 15/236, 15/264 | 신규 Controller 부터. 기존 Controller 에 엔드포인트를 더할 때는 그 Controller 에 둔다 |
| Service 이름 | `{Domain}Service`(4-Tier), `{Action}{Domain}Service`(헥사고날) | java-spring-coder 는 `{Domain}{Action}Service` | pasta 기존 Service 대부분 Action 형 | 같은 패키지 기존 Service 이름 형식을 따른다. 새 도메인 패키지는 조직 컨벤션 |
| 테스트 메서드명 | 영어 또는 한글 | 규칙 08 은 영어 | - | 같은 테스트 클래스의 기존 관례. 새 클래스는 영어 메서드명 + 한국어 `@DisplayName` |

## 4. 컴포넌트별로 읽을 원문

| 컴포넌트 | 읽을 원문 | 확인 포인트 요약 |
|----------|-----------|------------------|
| java-spring-coder, coding-implementer | naming, pkg-structure, entity, dto, lombok, etc | 아래 4-1 |
| java-layered-unit-testing | testcode, naming(변수명) | 아래 4-2 |
| java-architecture-reviewer | pkg-structure, entity, dto, lombok, naming | 4-1 위반 여부를 리뷰 항목으로 |
| git-commit, git-pr | commit-message | `[핵심키워드] 명사형 요약` |
| db-migration | mysql | main 기준(PR #6 진행 중) |

### 4-1. 프로덕션 코드 요약

- 계층 이름: web `Request`/`Response`, application `InDto`/`OutDto`(헥사고날 `Command`/`Result`), `~Dto` 단독 금지. JPA `@Entity` 는 `{Domain}JpaEntity`(infrastructure), domain 은 id 있으면 `{Domain}Entity`, 없으면 `{Domain}`. Persistence 구현은 `{Domain}RepositoryImpl`
- 의존 방향 `web → application → domain ← infrastructure`. Repository 인터페이스는 domain. application 은 흐름 조합만, 비즈니스 판단(if/else)은 domain. scheduler 는 infrastructure. 패키지명 `presentation` 대신 `web`
- web DTO 는 application 으로 넘기지 않는다. Controller 가 `Request → InDto`, `OutDto → Response`
- DTO 는 record. `@Setter` 전면 금지. JPA Entity 는 `@NoArgsConstructor(access = PROTECTED)` + 직접 선언한 생성자에 `@Builder`. 상태 변경은 `change{Field}()`
- domain 객체에 JPA·Spring 어노테이션 금지(`jakarta.annotation.Nullable` 만 허용)
- 이름은 줄이지 않는다: `req`·`res`·`dto`·`e`·`cnt`·`msg`·`tmp` 금지, 변수명은 타입명 전체(`UserEntity userEntity`). 컬렉션은 요소 클래스명 반영(`orderItems`), Map 은 `{값 복수형}By{키}`(`ordersById`), `list`·`dataList`·`resultMap` 금지
- `var`, 와일드카드 import, `System.out`, `printStackTrace()` 금지. TODO/FIXME 는 이슈 번호와 함께
- 조회 메서드: `get~`(없으면 `OrThrowException`/`OrNull`/`OrDefault` 명시), `find~` 는 Optional

### 4-2. 테스트 코드 요약

- 단위 테스트는 Fixture + Fake 우선. Fake 이름은 `Fake*`(`Stub*` 금지). `@Mock` 은 Fake 를 만들기 어려울 때(Controller 의 `@MockitoBean`)만
- 대상별: Domain=Fixture만, Service·Facade=Fake Repository, Controller=`@WebMvcTest`(원문의 `@MockitoBean` 은 Spring Boot 3.4+. 2026-11 기준 pasta·moneyball 은 3.2.2 라 `@MockBean` 을 쓴다), Repository=`@DataJpaTest`, E2E=`@SpringBootTest(RANDOM_PORT)` + `TestRestTemplate`
- `@DisplayName` 한국어 필수, "정상"·"성공" 대신 구체적 행동과 결과. Given-When-Then 주석 필수
- 테스트 간 상태 공유 금지(`@BeforeEach` 초기화, `@BeforeAll` 공유 데이터 금지). `Thread.sleep` 금지(Awaitility). 메서드 1개짜리 `@Nested` 금지
- AssertJ 만(JUnit `assertEquals` 금지). 한 테스트에 논리적 검증 하나(시나리오·인수 테스트 제외)

## 5. 기계 검사 연동

`review-lint.py` 가 조직 컨벤션 중 기계로 판정되는 항목을 검사한다(`review-recurrence-guard.md` §15 RR-L 표의 "VC" 행). 판정이 애매한 항목(정적 팩토리, 축약 변수명, `@SpringBootTest`)은 `[확인]` 으로만 내고 사람이 판단한다.

## 6. 보고

- 조직 컨벤션 때문에 사용자 요청이나 프로젝트 규칙과 다르게 구현했으면 원문 파일과 3절 판정을 인용한다
- 기존 코드가 조직 컨벤션과 다르다는 이유만으로 고치지 않는다. 고칠 가치가 있으면 보고에 "범위 밖 제안"으로 적는다(SC-1)

## 변경 이력

| 날짜 | 버전 | 내용 |
|------|------|------|
| 2026-11-13 | 0.1 | PR #7(7cc266d) 기준 신설. pasta·moneyball 실측으로 충돌 7건 판정(이슈 키 위치·squash 제목 근거는 git-commit 평가에서 추가), forge 자체 비적용 명시 |
