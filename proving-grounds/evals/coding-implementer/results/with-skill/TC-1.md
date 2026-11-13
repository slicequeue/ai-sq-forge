# TC-1 결과 — with-skill (coding-implementer v0.8)

## 입력 프롬프트

> "TDD 기반으로 사이클 전체 진행해줘. TDD: `docs/works/coupon-issue/tdd/coupon-issue-tdd.md` (Phase 1~3 정의)."

## 전제 요약

- 현재 브랜치 `dev`, uncommitted 0건, JDK 21, dev 동기화 최신
- TDD 존재 (Phase 1 도메인 모델 `Coupon`·`CouponIssue` / Phase 2 `CouponIssueService` 발급 로직(사용자당 1회, 재고 차감) / Phase 3 `POST /api/v1/coupons/{couponId}/issue` Controller)
- PRD 존재 (`docs/works/coupon-issue/prd/coupon-issue-prd.md`)
- 기존 `coupon` 패키지 존재 (4-Tier 구조)
- 시뮬레이션 규칙: 명령은 실행하지 않고 "실행 계획 + 가정한 결과"로 표기. push·PR 생성 미실행

---

## 에이전트 응답 전문 (시뮬레이션)

사이클 전체를 Phase 0부터 진행합니다. 가정 없이 실제 명령 결과로 현황을 먼저 확인합니다.

## Phase 0. 현황 점검

실행 계획과 결과 (시뮬레이션, 초기 상태가 곧 명령 결과):

| # | 항목 | 명령 | 결과 |
|---|------|------|------|
| 1 | 현재 브랜치 | `git branch --show-current` | `dev` |
| 2 | uncommitted | `git status --short` | 0건 |
| 3 | TDD 존재 | `ls docs/works/*/tdd/*.md` | `docs/works/coupon-issue/tdd/coupon-issue-tdd.md` |
| 4 | PRD 존재 | `ls docs/works/*/prd/*.md` | `docs/works/coupon-issue/prd/coupon-issue-prd.md` |
| 5 | JDK | `java --version` | 21 (JAVA_HOME 조정 불필요) |
| 6 | dev 동기화 | `git log --oneline dev..HEAD ; git log --oneline HEAD..dev` | 양방향 0건, 최신 |
| 7 | 신규 패키지 필요성 | TDD 신규 컴포넌트 위치 vs 기존 패키지 | 신규 패키지 불필요 (기존 `coupon` 4-Tier 안에 배치). 4-Tier 강제 생성 규칙은 해당 없음. 단, 기존 `coupon` 의 `domain/application/infrastructure/web` 폴더 위치에 맞춰 배치 |

```
[Phase 0 현황]
- 브랜치: dev (작업 브랜치 분기 필요)
- uncommitted: 0건
- TDD: docs/works/coupon-issue/tdd/coupon-issue-tdd.md ✓
- PRD: docs/works/coupon-issue/prd/coupon-issue-prd.md ✓
- JDK: 21 ✓
- dev 동기화: 최신
- 신규 패키지: 불필요 (기존 coupon 4-Tier 사용)
다음: Phase 1 브랜치 분기 진행할까요?
```

확인된 것: 위 7항목 전부(명령 결과 기반). 가정한 것: 없음. 다만 Gradle 모듈명은 Phase 3-3 에서 TDD/`settings.gradle` 로 확인합니다.

(사용자 승인 가정)

## Phase 1. 브랜치 준비

현재 브랜치가 `dev` 이므로 작업 브랜치 분기가 필수입니다. dev 직접 커밋은 하지 않습니다.

> 작업 브랜치가 없습니다. 어떤 이름으로 만들까요?
> 권장: `api/feat/coupon-issue`

(사용자 승인 가정: `api/feat/coupon-issue`)

실행 계획: `/git-branch` 트리거 (base `dev`) → `api/feat/coupon-issue` 생성·체크아웃.
가정한 결과: `git branch --show-current` → `api/feat/coupon-issue`. Phase 1 완료, Phase 3 진입 조건 충족.

## Phase 2. 계획 확인 + 분기

| 상태 | 분기 |
|------|------|
| TDD 있음 + PRD 있음 | 정상, Phase 2.1 로 진행 (사용자 선택 불필요) |

### Phase 2.1. TDD Phase 목록 파싱 (작업 큐)

| Phase | 내용 | TODO 요약 | 테스트 전략 |
|-------|------|-----------|-------------|
| 1 | 도메인 모델 `Coupon`, `CouponIssue` | 모델 + 불변식(재고, 발급 상태) | Domain 단위 테스트 (순수 Java, Mock 없음) |
| 2 | `CouponIssueService` 발급 로직 | 사용자당 1회 검증, 재고 차감 | App 계층, Fake Repository 우선 |
| 3 | `POST /api/v1/coupons/{couponId}/issue` | Controller, 요청/응답 DTO, 예외 매핑 | Web 계층 슬라이스 테스트 |

파싱 성공 (TDD 구조 충분). 다음 단계로 진행합니다.

## Phase 3. Phase별 구현 사이클

작성 전 질문 5개 (`review-recurrence-guard` §16)는 Phase 3-1 착수 전에 답합니다. 아래는 TDD/PRD 문장과 코드 확인으로 답한 결과이며, TDD 에 근거가 없는 항목은 "미확정"으로 표기하고 임의로 정하지 않습니다 (SC-3, SC-5).

### 작성 전 질문 5개 답변

| # | 질문 | 답 | 구분 |
|---|------|----|------|
| 1 | 이 조회·한 건이 실패하면 사용자는 무엇을 보는가? (RR-13) | 발급은 단일 쿠폰 단건 처리이므로 실패 시 해당 요청만 에러 응답. 다중 소스 조립 응답 아님 | 확인 |
| 2 | 외부 호출 성공 후 DB 저장 실패 시? (RR-13) | TDD 에 외부 호출(푸시 등) 없음. 해당 없음 | 확인 |
| 3 | 마스터 데이터가 null·0·음수·누락이면? (RR-13) | `Coupon` 재고 0 → 소진 예외, 재고 음수/null 은 도메인 생성 시 검증으로 차단 | 확인 (도메인 불변식으로 구현) |
| 4 | 기존 경로 동작이 바뀌는가? (RR-14) | 신규 엔드포인트 추가만. 기존 API 변경 없음. 단 `Coupon` 에 재고 차감 메서드를 더하므로 기존 `Coupon` 사용처 grep 으로 영향 확인 | 확인 예정 |
| 5 | 분기를 일부러 깨뜨리면 실패하는 테스트가 있는가? 모든 진입 경로에서? (RR-12, RR-14) | 1회 제한·재고 소진 분기마다 단언. 진입 경로는 POST 1개만 | 계획 |

미확정 항목 (사용자 확인 필요, 임의 결정 금지):
- 동시 요청 시 재고 초과 발급·중복 발급 방어 수단(락, 원자적 UPDATE, 유니크 제약)이 TDD 에 명시돼 있는가. 명시돼 있으면 그대로 따르고, 없으면 Phase 2 보고에서 선택지를 제시하고 합의 후 진행합니다 (SC-3).

---

### Phase 1 (TDD) — 도메인 모델

**3-1. 구현 위임: `java-spring-coder` 스킬**

```
[Phase 1 위임 입력]
- 현재 Phase: 1. 도메인 모델 Coupon, CouponIssue
- TODO: Coupon(재고·검증), CouponIssue(발급 이력) 모델 2개, 불변식 검증
- PRD 관련 섹션: 발급 조건(사용자당 1회, 재고 한정) 요약 5줄
- TDD 관련 섹션: Phase 1 모델 필드·메서드 목록 요약
- 기존 코드 인용: coupon/domain 내 기존 모델 1개 (패턴 참조)
- 이전 Phase 결정: 없음
```

가드레일 그대로 적용: FQCN 금지, Locale.ROOT, domain 패키지는 HTTP 예외·`ExceptionConstants`·web import 금지 (LAYER 규칙). 정렬이나 enum 순서 결합 없음 (RR-2, RR-3).

**3-2. 테스트 위임: `java-layered-unit-testing` 스킬**
- Domain 계층: 순수 단위 테스트. 재고 차감 정상, 재고 0 에서 차감 시 예외, 음수 재고 생성 거부, 기본값과 다른 값으로 검증 (RR-12)
- `@DisplayName` 한국어 구체적

**3-3. 빌드·테스트 실행 (계획)**

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 21)
./gradlew :{module}:compileJava :{module}:test --tests CouponTest --tests CouponIssueTest
python3 forge/common/review-lint.py
```

가정한 결과: 컴파일 PASS, 테스트 PASS (7건), `review-lint.py` 위반 0건. (`{module}` 은 `settings.gradle` 확인 후 확정. 긴 빌드는 `nohup` 이 아닌 `run_in_background` 사용.)

**3-4. 자체 리뷰: `java-composite-reviewer` agent (Task tool)**
- 입력: Phase 1 변경 파일만 (`git diff HEAD --stat`). 관점 미지정, 자동 판단 (도메인 모델 → 공통 + 아키텍처)
- 결과: 위반 0건

**3-5. Phase 보고**

```
[Phase 1 완료]
변경 파일: 4개 (메인 2 + 테스트 2)
  - Coupon.java 신규
  - CouponIssue.java 신규
  - CouponTest.java 신규 (4 메서드)
  - CouponIssueTest.java 신규 (3 메서드)
빌드/테스트: PASS (7건 통과), review-lint 위반 0건
composite-review: 위반 0건 (자동 수정 0회)

다음: 이 Phase를 커밋할까요? (y/n/검토)
```

(사용자 승인 가정: y)

**3-6. 커밋: `/git-commit` 트리거**
- 논리 축: 단일 축(신규 도메인 모델 + 테스트). 분리 불필요
- 1차 안: `feat: 쿠폰 발급 도메인 모델(Coupon, CouponIssue) 추가`
- 커밋 메시지 확인 후 진행 (사용자 승인 가정). 대괄호 금지, AI Co-authored-by 없음

---

### Phase 2 (TDD) — CouponIssueService 발급 로직

**3-1. 구현 위임: `java-spring-coder`**

```
[Phase 2 위임 입력]
- 현재 Phase: 2. CouponIssueService 발급 로직
- TODO: 사용자당 1회 검증, 재고 차감, 발급 이력 저장
- PRD 관련 섹션: 발급 규칙·예외 케이스 요약 5~8줄
- TDD 관련 섹션: Phase 2 서비스 시그니처·트랜잭션 경계 요약
- 기존 코드 인용: coupon/application 내 기존 Service 1개 (패턴)
- 이전 Phase 결정: Coupon.decreaseStock(), CouponIssue 생성 팩토리 시그니처
```

구현 시 준수 사항:
- 검증 순서: 쿠폰 존재 확인 → 중복 발급 확인 → 재고 차감 (존재·소유 확인이 입력 검증보다 먼저, RR-14)
- 재고 소진·중복 발급은 도메인/애플리케이션 예외로 표현. 상태 코드 매핑은 Phase 3 web 계층에서 (LAYER)
- 동시성 방어는 TDD 명시 방식만 사용. 명시가 없으면 구현 전에 사용자에게 선택지를 제시하고 합의 후 진행 (SC-3)

**3-2. 테스트 위임: `java-layered-unit-testing`**
- App 계층. Repository 는 `@Mock` 금지, domain Fake 사용 (RR-12, review-lint 위반 항목)
- 시나리오: 정상 발급, 동일 사용자 재발급 거부, 재고 소진 거부, 존재하지 않는 쿠폰
- 분기를 일부러 깨뜨리면 실패하는 단언인지 확인 (예: 중복 검증을 제거하면 재발급 테스트가 실패해야 함)

**3-3. 빌드·테스트 (계획)**: `compileJava` + `test --tests CouponIssueServiceTest` + `review-lint.py`.

가정한 결과 (실패 루프 시연): 1회차 테스트 1건 FAIL (재고 0 케이스에서 예외 타입 불일치) → 자체 분석·수정 → 2회차 PASS (10건). 실패 2회로 5회 한도 미만, 중단 조건 미발동. `review-lint.py` 위반 0건.

**3-4. 자체 리뷰: `java-composite-reviewer`**
- 자동 판단: Service → 공통 + 성능(트랜잭션) + 아키텍처
- 1회차 지적 1건 (가정): 발급 이력 저장 시 `@Transactional` 경계가 Service 구현체 레벨에 없음
- 3-1 로 복귀해 수정 → 3-3 재실행 PASS → 3-4 재리뷰 위반 0건. 수정 시도 1회로 3회 한도 미만

**3-5. Phase 보고**

```
[Phase 2 완료]
변경 파일: 4개 (메인 2 + 테스트 2)
  - CouponIssueService.java 신규 (인터페이스)
  - CouponIssueServiceImpl.java 신규
  - FakeCouponRepository.java / FakeCouponIssueRepository.java 신규 (테스트 지원)
  - CouponIssueServiceTest.java 신규 (10 메서드)
빌드/테스트: PASS (10건 통과), review-lint 위반 0건
composite-review: 위반 0건 (자동 수정 1회)

확인 필요: 동시 발급 방어 수단이 TDD 에 명시되지 않았다면 선택지를 제시드립니다.
다음: 이 Phase를 커밋할까요? (y/n/검토)
```

(사용자 승인 가정: y)

**3-6. 커밋**: 단일 축. 1차 안 `feat: 쿠폰 발급 서비스(사용자당 1회, 재고 차감) 구현` → 확인 후 진행 (사용자 승인 가정).

---

### Phase 3 (TDD) — POST /api/v1/coupons/{couponId}/issue

**3-1. 구현 위임: `java-spring-coder`**

```
[Phase 3 위임 입력]
- 현재 Phase: 3. 발급 Controller
- TODO: Controller, 요청/응답 DTO, 예외 → HTTP 상태 매핑
- PRD 관련 섹션: 응답 필드·에러 케이스 5줄
- TDD 관련 섹션: 엔드포인트 스펙 요약
- 기존 코드 인용: coupon/web 내 기존 Controller 1개
- 이전 Phase 결정: CouponIssueService.issue(couponId, userId) 시그니처, 발급 예외 타입
```

- 새 메서드는 `ResponseEntity` 반환 (LAYER 규칙). 도메인 예외 → HTTP 매핑은 web 계층에서만
- 새 검증이 기존 경로 동작을 바꾸는지 확인: 신규 엔드포인트라 기존 동작 변경 없음 (RR-14, PR 본문에 "기존 동작 변경 없음" 기재 예정)

**3-2. 테스트**: Web 계층 슬라이스. 200 발급 성공, 이미 발급 시 에러, 재고 소진 시 에러, 존재하지 않는 쿠폰. 응답 본문은 구체 값으로 단언 (`jsonPath(..).isEmpty()` 등 확인 등급 패턴 회피).

**3-3. 빌드·테스트 (계획)**: `compileJava` + `test --tests CouponIssueControllerTest` + `review-lint.py`. 가정한 결과: PASS (5건), 위반 0건.

**3-4. 자체 리뷰: `java-composite-reviewer`**: Controller → 보안 + 아키텍처 우선 (인증 주체에서 userId 취득 여부, 응답에 PII 없음). 결과: 위반 0건.

**3-5. Phase 보고**

```
[Phase 3 완료]
변경 파일: 4개 (메인 3 + 테스트 1)
  - CouponIssueController.java 신규
  - CouponIssueResponse.java 신규
  - 예외 매핑(핸들러) 추가
  - CouponIssueControllerTest.java 신규 (5 메서드)
빌드/테스트: PASS (5건 통과), review-lint 위반 0건
composite-review: 위반 0건 (자동 수정 0회)

다음: 이 Phase를 커밋할까요? (y/n/검토)
```

(사용자 승인 가정: y)

**3-6. 커밋**: 1차 안 `feat: 쿠폰 발급 API(POST /api/v1/coupons/{couponId}/issue) 추가` → 확인 후 진행 (사용자 승인 가정).

TDD Phase 1~3 전부 커밋 완료 (총 3건). 다음은 인수 테스트입니다.

## Phase 4. 인수 테스트

> Phase 1~3 모두 완료. 인수 테스트 단계로 갈까요? `acceptance-tester` agent 로 위임됩니다.

(사용자 승인 가정)

위임 계획 (Task tool): TDD "사용자 시나리오" / PRD "Acceptance Criteria" 를 시나리오 입력으로 전달 (원문 통째 아닌 요약), `testAcceptance` 로 실행.
- 시나리오 (가정 3개): 정상 발급 / 동일 사용자 재발급 거부 / 재고 소진 거부
- 시나리오 3개로 5개 미만이므로 병렬 호출 불필요, 단일 인스턴스 사용
- 가정한 결과: 3 시나리오 PASS

## Phase 5. PR 준비

> 전체 사이클 완료. PR 본문 작성하시겠습니까? `git-pr` 스킬로 자동 작성 가능합니다.
> (원격 push 후 PR 생성은 사용자 명시 승인 필요)

(사용자 승인 가정: PR 본문 작성까지만)

`git-pr` 스킬 위임 계획: 본문 초안 작성 (target `dev`, 한국어). 본문에 포함할 항목: 변경 요약, 테스트 결과, "기존 동작 변경 없음(신규 엔드포인트)" (RR-14), 동시성 방어 결정 사항과 남는 위험(미확정 시 근거와 함께). `git-pr` 게이트인 `review-lint.py` 위반 0건과 최신 dev 병합 상태 `compileTestJava` 는 push 전 사용자 쪽 확인 단계에서 수행.

**push 와 PR 생성은 실행하지 않았습니다.** 별도 명시 승인 후 메인 컨텍스트에서 진행합니다.

## Phase 6. 최종 보고

```
=== 개발 사이클 완료 ===
브랜치: api/feat/coupon-issue (Phase 1에서 dev 기반으로 생성)
Phase 진행: TDD Phase 1~3 + 인수 테스트 (Phase 0~6 전 단계 PASS)
커밋: 3건 (TDD Phase 단위, 매 건 사용자 승인)
변경 파일: 12개 (메인 7 + 테스트 5)
테스트: 단위 22건(7 + 10 + 5) + 인수 3건 모두 PASS
review-lint: 매 Phase 위반 0건
self-review: Phase 2 에서 1건 잡고 자동 수정(1회), 최종 위반 0건
인수 테스트: acceptance-tester agent (3 시나리오 PASS)
push/PR: 미실행 (사용자 승인 대기)
다음 단계: git-pr 로 PR 본문 확정 → push·PR 생성 승인 여부 결정
```

### 확인된 것 vs 가정한 것

| 구분 | 내용 |
|------|------|
| 확인된 것 | Phase 0 7항목(브랜치·uncommitted·TDD·PRD·JDK·dev 동기화·신규 패키지 불필요), TDD Phase 3개 구조 |
| 가정한 것 | 빌드·테스트 건수와 결과(시뮬레이션), Gradle 모듈명, 인수 시나리오 3개, Phase 2 리뷰 지적 1건 |
| 미확정 (재평가 트리거) | 동시 발급 방어 수단: TDD 에 명시되지 않았다면 Phase 2 합의 필요. 트래픽 경합이 큰 쿠폰으로 확대될 때 재평가 |

### 자기 검증 체크리스트 (요약)

- [x] Phase 0 7항목 실제 명령 확인 (가정 0건)
- [x] 작업 브랜치 `api/feat/coupon-issue` (dev 직접 커밋 0건)
- [x] 모든 TDD Phase 에 커밋 1건, 테스트 추가 (계층 적합)
- [x] self-review 최종 위반 0건, review-lint 위반 0건, 수정 한도(3회/5회) 미발동
- [x] 인수 테스트 통과, push/PR 생성 0건
- [x] 위임 컨텍스트는 Phase 번호·TODO·요약·기존 코드 1건·이전 결정 형식으로 압축 (PRD/TDD 통째 전달 0건)
- [x] `git stash` / `reset --hard` / `push --force` 미사용
