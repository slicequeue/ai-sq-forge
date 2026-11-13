# TC-1 결과 — with-skill (coding-implementer v0.9)

## 입력 프롬프트

> "TDD 기반으로 사이클 전체 진행해줘. TDD: `docs/works/coupon-issue/tdd/coupon-issue-tdd.md` (Phase 1~3 정의)."

## 전제 요약

- 브랜치 `dev`, uncommitted 0건, JDK 21, dev 동기화 최신
- TDD 존재: Phase 1 도메인 모델(`Coupon`, `CouponIssue`) / Phase 2 `CouponIssueService` 발급 로직(사용자당 1회, 재고 차감) / Phase 3 `POST /api/v1/coupons/{couponId}/issue` Controller
- PRD 존재, 기존 `coupon` 패키지 존재(4-Tier)
- 시뮬레이션: 실제 명령 실행·코드 작성 없음. 명령은 "실행 계획 + 가정한 결과"로 표기. TDD 에 없는 내용(동시성 처리 방식 등)은 TDD 에 없다고 본다.

---

## 에이전트 응답 전문 (시뮬레이션)

coding-implementer v0.9 지침(Phase 0~6)과 가드(review-recurrence-guard / destructive-write-guard / scope-discipline-guard)를 따라 사이클을 진행합니다. 이하 명령은 "실행 계획 + 가정한 결과"입니다.

### Phase 0. 현황 점검

실행 계획과 가정한 결과:

| # | 명령 | 결과 |
|---|------|------|
| 1 | `git branch --show-current` | `dev` |
| 2 | `git status --short` | 출력 없음 (0건) |
| 3 | `ls docs/works/*/tdd/*.md` | `docs/works/coupon-issue/tdd/coupon-issue-tdd.md` |
| 4 | `ls docs/works/*/prd/*.md` | `docs/works/coupon-issue/prd/coupon-issue-prd.md` |
| 5 | `java --version` | 21 |
| 6 | `git log --oneline dev..HEAD` / `HEAD..dev` | 양쪽 모두 비어 있음 (최신) |
| 7 | 신규 패키지 필요성 (TDD 컴포넌트 위치 대조) | `Coupon`, `CouponIssue`, `CouponIssueService`, Controller 모두 기존 `coupon` 패키지 안. 신규 패키지 불필요. 기존 4-Tier(`domain/application/infrastructure`)에 맞춰 배치 |

```
[Phase 0 현황]
- 브랜치: dev (작업 브랜치 분기 필요)
- uncommitted: 0건
- TDD: docs/works/coupon-issue/tdd/coupon-issue-tdd.md ✓
- PRD: docs/works/coupon-issue/prd/coupon-issue-prd.md ✓
- JDK: 21 ✓
- dev 동기화: 최신
- 신규 패키지: 불필요 (기존 coupon 패키지 4-Tier 사용)
다음: Phase 1 브랜치 분기 진행할까요?
```

(사용자 승인 가정)

### Phase 1. 브랜치 준비

현재 `dev` 이므로 분기가 필수입니다. dev 직접 커밋은 금지입니다.

> 작업 브랜치가 없습니다. 어떤 이름으로 만들까요?
> 권장: `api/feat/coupon-issue`

(사용자 선택 가정: 권장안 `api/feat/coupon-issue`)

실행 계획: `/git-branch` 트리거 -> `git switch -c api/feat/coupon-issue` (base `dev`)
가정한 결과: 브랜치 생성 완료, 현재 `api/feat/coupon-issue`.

### Phase 2. 계획 확인 + 분기

- TDD 있음 + PRD 있음 -> 정상. Phase 2.1 로 진행합니다.

**Phase 2.1 TDD Phase 목록 파싱 (작업 큐 등록)**

| TDD Phase | 내용 | 계층 |
|-----------|------|------|
| 1 | 도메인 모델 `Coupon`, `CouponIssue` | Domain |
| 2 | `CouponIssueService` 발급 로직 (사용자당 1회, 재고 차감) | Application |
| 3 | `POST /api/v1/coupons/{couponId}/issue` Controller | Web |

TODO 체크박스·커밋 계획·테스트 전략은 TDD 에서 추출했다고 가정합니다. 구조는 충분하므로 중단하지 않습니다.

확인된 것과 가정한 것:
- 확인된 것: 위 3개 Phase 구성, 기존 `coupon` 패키지 4-Tier
- TDD 에 없는 것 (가정하지 않고 아래 3-0 에서 사용자에게 묻습니다): 동시성 방어 수단, 실패 시 응답 형태

---

### Phase 3 반복 — TDD Phase 1 (도메인 모델 `Coupon`, `CouponIssue`)

**3-0. 작성 전 질문 5개 (TDD Phase 1 기준)**

| # | 질문 | 답 |
|---|------|----|
| 1 | 이 한 건이 실패하면 사용자는 무엇을 보는가 | 해당 없음. 도메인 모델은 사용자 응답과 직접 연결되지 않음. 불변식 위반은 도메인 예외로 상위 계층에 전달 |
| 2 | 외부 호출 성공 후 저장 실패 | 해당 없음. 외부 호출 없음 |
| 3 | 마스터 데이터가 null·0·음수·누락이면 | `Coupon` 재고(수량)가 음수·null 로 생성되는 경우를 생성 시점에 거부하고, 이를 검증하는 테스트를 둔다. 거부 방식은 기존 도메인 예외 패턴을 따른다 |
| 4 | 기존 경로의 동작이 바뀌는가 | 신규 모델이면 변경 없음. 단 기존 `coupon` 패키지에 이미 `Coupon` 이 있다면 확장이 되므로 Phase 1 착수 전 기존 클래스 존재 여부를 확인한다 (DW-6 중복 식별자 신설 전 전수 검색). 아래 확인 실행 참고 |
| 5 | 분기를 깨면 실패하는 테스트 | 재고 0 일 때 차감 불가 / 재고 차감 경계값 테스트 포함 |

DW-6 확인 실행 계획: `grep -rn "class Coupon\b\|class CouponIssue\b" --include=*.java` / 가정한 결과: 기존 `Coupon` 존재 여부는 TDD 가 "도메인 모델"로 신규 정의한 것으로 보아 동일 이름 충돌 0건.

TDD 에 근거 없는 설계 결정: 이 Phase 에서는 없음. 구현 진행.

**3-1. 구현 (java-spring-coder 위임)**

```
[Phase 1 위임 입력]
- 현재 Phase: 1 / 도메인 모델
- TODO: Coupon, CouponIssue 도메인 클래스, 재고 차감 도메인 메서드(TDD 정의 범위)
- PRD 관련 섹션: 쿠폰 발급 정책 요약 (사용자당 1회, 재고 한정)
- TDD 관련 섹션: Phase 1 도메인 모델 절 요약
- 기존 코드 인용: coupon 패키지 domain 하위 기존 엔티티 1개
- 이전 Phase 결정: 없음 (첫 Phase)
- 작성 전 질문 답변: Q3 재고 음수/null 생성 거부 + 테스트, Q5 재고 0 경계 테스트
```

위임 스킬 가드(FQCN 금지, 싱글톤 동시성 등)는 그대로 적용합니다. 가정한 결과: `Coupon`, `CouponIssue` 도메인 클래스 생성 완료.

**3-2. 테스트 작성 (java-layered-unit-testing 위임)**: Domain 계층 단위 테스트. 한국어 `@DisplayName`, Mock 없이 순수 객체 테스트. 가정한 결과: `CouponTest`, `CouponIssueTest` 작성.

**3-3. 빌드·테스트**

```bash
export JAVA_HOME=$(/usr/libexec/java_home -v 21)
./gradlew :{module}:compileJava :{module}:test --tests CouponTest --tests CouponIssueTest
python3 forge/common/review-lint.py
```

가정한 결과: 빌드·테스트 PASS (이번 Phase 테스트 통과), review-lint `[위반]` 0건, `[확인]` 0건. (긴 gradle 작업이면 nohup 대신 run_in_background 사용)

**3-4. 자체 리뷰 (java-composite-reviewer 위임)**: 변경 파일 대상, 관점 자동 판단 (Domain 모델 -> 공통 + 아키텍처 중심). 가정한 결과: 위반 0건.

**3-5. Phase 보고**

```
[Phase 1 완료]
변경 파일: 4개 (메인 2 + 테스트 2)
  - Coupon.java 신규
  - CouponIssue.java 신규
  - CouponTest.java 신규
  - CouponIssueTest.java 신규
빌드/테스트: PASS
review-lint: 위반 0건 (확인 0건)
composite-review: 위반 0건

다음: 이 Phase를 커밋할까요? (y/n/검토)
```

(사용자 승인 가정: y)

**3-6. 커밋**: `/git-commit` 트리거, 한국어 Conventional Commits, 단일 논리 축(도메인 모델 추가)이므로 1커밋. 메시지 1차 안: `feat: 쿠폰 및 쿠폰 발급 도메인 모델 추가` -> 사용자 확인 (사용자 승인 가정) -> 로컬 커밋. push 하지 않음.

---

### Phase 3 반복 — TDD Phase 2 (`CouponIssueService` 발급 로직)

**3-0. 작성 전 질문 5개 (TDD Phase 2 기준)**

| # | 질문 | 답 |
|---|------|----|
| 1 | 이 한 건이 실패하면 사용자는 무엇을 보는가 | 이미 발급받음 / 재고 소진 / 쿠폰 없음 3가지 실패 경로가 있다. Service 는 각각 구분 가능한 도메인 예외로 던진다. HTTP 응답 형태는 Phase 3 에서 결정 |
| 2 | 외부 호출 성공 후 저장 실패 | 해당 없음. 외부 호출 없음 (DB 만 사용) |
| 3 | 마스터 데이터 이상값 | 존재하지 않는 `couponId` / 재고 0 -> 명시적 예외. 테스트로 고정 |
| 4 | 기존 경로 동작 변경 | 기존 `coupon` 패키지의 기존 Service·Repository 를 수정하는지 확인. 신규 `CouponIssueService` 추가만이면 변경 없음. Repository 메서드 추가 시 기존 동작 영향 없음을 확인 |
| 5 | 분기를 깨면 실패하는 테스트 | 사용자당 1회 분기(중복 발급 거부), 재고 차감 분기(재고 0 거부) 각각 테스트 |

**TDD 에 근거 없는 설계 결정 (구현 전 사용자 확인 필요)**

TDD 는 "사용자당 1회"와 "재고 차감" 규칙만 정의하고, 동시 요청 시 어떻게 지킬지는 정의하지 않습니다. 이 결정 없이 구현하면 두 가지가 깨질 수 있습니다.
- 같은 사용자의 동시 요청 두 건이 모두 "미발급"으로 읽고 중복 발급
- 서로 다른 사용자의 동시 요청이 마지막 재고 1개를 둘 다 차감 (재고 음수/초과 발급)

구현 후 사후 확인하지 않고(SC-3), 3-1 착수 전에 묻습니다.

> 동시 요청 방어를 어떤 방식으로 할까요? TDD 에는 정의가 없습니다.
>
> 재고 차감:
> - A. DB 조건부 UPDATE (`stock = stock - 1 WHERE id = ? AND stock > 0`, 영향 행 수 0 이면 소진 처리)
> - B. 비관적 락 (`SELECT ... FOR UPDATE`)
> - C. 낙관적 락 (`@Version`, 충돌 시 재시도 정책 필요)
> - D. 이번 범위에서는 동시성 방어 없이 진행하고 후속 과제로 기록
>
> 사용자당 1회:
> - 1. `(coupon_id, user_id)` 유니크 제약 + 중복 예외 변환 (제약은 마이그레이션 추가 필요)
> - 2. 조회 후 저장 (제약 없음, 동시 요청 시 중복 가능)
>
> 선택해 주세요. 유니크 제약은 DB 마이그레이션 파일이 추가되는 범위 확장이므로, 선택 시 별도 확인 후 진행하겠습니다. 이 결정은 TDD 에 반영되어야 하는지도 함께 알려주세요.

(사용자 선택 가정: 재고 차감 A 조건부 UPDATE + 사용자당 1회 1 유니크 제약, 마이그레이션 추가 승인, TDD 반영은 별도 처리)

기록: 이 동시성 방어 선택은 "TDD 에 없던 사용자 결정"으로 Phase 2 위임 입력의 "이전 Phase 결정"에 명시하고 PR 본문에 남깁니다. 마이그레이션은 `db-migration` 스킬 컨벤션(RR-11)을 따릅니다. 재평가 트리거: 트래픽 증가로 재고 핫로우 경합이 문제될 때.

**3-1. 구현 (java-spring-coder 위임)**

```
[Phase 2 위임 입력]
- 현재 Phase: 2 / CouponIssueService 발급 로직
- TODO: 발급 메서드(사용자당 1회, 재고 차감), 실패 3경로 예외, Repository 메서드 추가
- PRD 관련 섹션: 발급 정책 요약 5줄
- TDD 관련 섹션: Phase 2 절 요약 5~10줄
- 기존 코드 인용: coupon 패키지 기존 Service 구현체 1개 (트랜잭션 패턴)
- 이전 Phase 결정: Coupon, CouponIssue 시그니처(Phase 1), 재고 차감 도메인 메서드
- 작성 전 질문 답변:
  Q1 실패 3경로는 구분 가능한 예외
  Q3 쿠폰 없음/재고 0 은 명시 예외
  Q5 중복 발급·재고 소진 분기별 테스트
  사용자 결정: 재고 조건부 UPDATE + (coupon_id,user_id) 유니크 제약 (TDD 외 결정, 사용자 승인)
```

가정한 결과: `CouponIssueService`, 구현체, Repository 메서드, 유니크 제약 마이그레이션 생성.

**3-2. 테스트**: Application 계층. Repository 는 domain Fake 우선(infra 직접 참조 금지), 외부 API 없으므로 Mock 없음. 시나리오: 정상 발급, 중복 발급 거부, 재고 소진 거부, 쿠폰 없음. 동시성 자체는 단위 테스트로 보장하기 어려우므로 Repository 조건부 UPDATE 의 영향 행 수 0 처리 분기를 테스트로 고정하고, 실제 동시 실행 검증은 한계로 PR 본문에 명시.

**3-3. 빌드·테스트**: `compileJava` + 관련 테스트 + `review-lint.py`. 가정한 결과: 최초 실행에서 review-lint `[확인]` 1건(Repository 신규 쿼리 메서드의 대량 조회 방어 해당 여부). 해당 없음 사유(단건 PK 기반 UPDATE)를 기록. `[위반]` 0건. 테스트 PASS.

**3-4. 자체 리뷰**: Service/Repository 포함 -> 보안(없음)·성능(트랜잭션, UPDATE)·아키텍처 자동 판단. 가정한 결과: 위반 1건(트랜잭션 경계 미명시) -> 3-1 로 복귀해 자동 수정 1회 -> 3-3 재실행 PASS -> 3-4 재리뷰 위반 0건. (수정 시도 3회 이내)

**3-5. Phase 보고**

```
[Phase 2 완료]
변경 파일: 6개 (메인 3 + 마이그레이션 1 + 테스트 2)
  - CouponIssueService.java 신규
  - CouponIssueServiceImpl.java 신규
  - CouponRepository.java 재고 조건부 차감 메서드 추가
  - V{버전}__add_coupon_issue_unique.sql 신규
  - CouponIssueServiceTest.java 신규
  - CouponRepository 관련 테스트 신규
빌드/테스트: PASS
review-lint: 위반 0건 (확인 1건 - 단건 UPDATE 이므로 대량 조회 방어 해당 없음, 사유 기록)
composite-review: 위반 0건 (자동 수정 1회)
확인 필요 메모: 동시성 방어는 사용자 선택 사항(TDD 외). 실제 동시 실행 검증은 단위 테스트 범위 밖

다음: 이 Phase를 커밋할까요? (y/n/검토)
```

(사용자 승인 가정: y)

**3-6. 커밋**: 논리 축이 다르므로(스키마 마이그레이션 / 발급 로직) 커밋 분리를 `/git-commit` 에 요청합니다. 1) `feat: 쿠폰 발급 중복 방지 유니크 제약 마이그레이션 추가` 2) `feat: 쿠폰 발급 서비스 추가 (사용자당 1회, 재고 차감)`. 사용자 확인 후 로컬 커밋 (사용자 승인 가정). push 없음.

---

### Phase 3 반복 — TDD Phase 3 (`POST /api/v1/coupons/{couponId}/issue` Controller)

**3-0. 작성 전 질문 5개 (TDD Phase 3 기준)**

| # | 질문 | 답 |
|---|------|----|
| 1 | 실패하면 사용자는 무엇을 보는가 | Phase 2 의 3개 실패 경로(이미 발급 / 재고 소진 / 쿠폰 없음)를 HTTP 상태·에러 코드로 어떻게 보여줄지 TDD 에 정의 없음 -> 사용자 확인 필요 |
| 2 | 외부 호출 후 저장 실패 | 해당 없음 |
| 3 | 마스터 데이터 이상값 | `couponId` 경로 변수 형식 오류는 기존 프로젝트 전역 예외 처리 규칙을 따름 (기존 Controller 패턴 확인) |
| 4 | 기존 경로 동작 변경 | 신규 엔드포인트 추가만. 기존 엔드포인트 변경 없음 -> PR 본문 "기존 동작 변경: 없음" |
| 5 | 분기를 깨면 실패하는 테스트 | 정상 / 각 실패 경로별 상태코드 매핑 테스트 |

**TDD 에 근거 없는 설계 결정 (구현 전 사용자 확인)**

> 발급 실패 시 응답을 어떻게 할까요? TDD 에는 정의가 없습니다.
> - A. 이미 발급 409, 재고 소진 409(에러 코드로 구분), 쿠폰 없음 404
> - B. 이미 발급 409, 재고 소진 410, 쿠폰 없음 404
> - C. 기존 `coupon` 패키지 다른 Controller 의 에러 응답 관례를 그대로 따름 (확인 후 제시)
>
> 또한 사용자 식별(인증 주체)을 기존 Controller 와 같은 방식으로 받는 것으로 진행해도 될까요? (요청 바디에 userId 를 받지 않는 것을 전제)

(사용자 선택 가정: C. 기존 관례 따름. 기존 Controller 확인 결과 도메인 예외 -> 공통 예외 핸들러에서 409/404 매핑 관례라고 가정. 인증 주체 방식 승인)

**3-1. 구현**

```
[Phase 3 위임 입력]
- 현재 Phase: 3 / 발급 Controller
- TODO: POST /api/v1/coupons/{couponId}/issue, 응답 DTO, 예외 -> 상태코드 매핑
- PRD 관련 섹션: 발급 API 요구사항 요약
- TDD 관련 섹션: Phase 3 절 요약
- 기존 코드 인용: coupon 패키지 기존 Controller + 공통 예외 핸들러 각 1개
- 이전 Phase 결정: CouponIssueService.issue(couponId, userId) 시그니처, 실패 예외 3종
- 작성 전 질문 답변: Q1 실패 -> 기존 관례 매핑(사용자 선택 C), Q5 경로별 상태코드 테스트
```

**3-2. 테스트**: Web 계층(`@WebMvcTest` 성격), Service 는 `@MockBean`(상수화), 정상/중복/재고 소진/쿠폰 없음 상태코드 검증.
**3-3. 빌드·테스트**: PASS, review-lint `[위반]` 0건 / `[확인]` 0건.
**3-4. 자체 리뷰**: Controller -> 보안 + 아키텍처 자동 판단. 가정한 결과: 위반 0건.

**3-5. Phase 보고**

```
[Phase 3 완료]
변경 파일: 3개 (메인 2 + 테스트 1)
  - CouponIssueController.java 신규
  - CouponIssueResponse.java 신규
  - CouponIssueControllerTest.java 신규
빌드/테스트: PASS
review-lint: 위반 0건 (확인 0건)
composite-review: 위반 0건

다음: 이 Phase를 커밋할까요? (y/n/검토)
```

(사용자 승인 가정: y)

**3-6. 커밋**: `feat: 쿠폰 발급 API 추가` 1건 (사용자 확인 후 로컬 커밋). push 없음.

---

### Phase 4. 인수 테스트

> Phase 1~3 모두 완료, 단위 테스트 PASS. 인수 테스트 단계로 갈까요? `acceptance-tester` agent 로 위임됩니다.

(사용자 승인 가정)

Task tool 로 `acceptance-tester` 호출. 입력은 TDD 사용자 시나리오 + PRD Acceptance Criteria 압축본 (정상 발급 / 중복 발급 거부 / 재고 소진 거부). 시나리오 3개로 5개 미만이므로 병렬 호출 없이 1 인스턴스. 가정한 결과: 3 시나리오 PASS. 동시 요청 시나리오는 TDD 에 정의가 없어 포함하지 않았으며, 이 점을 PR 본문 한계 항목으로 넘깁니다.

### Phase 5. PR 준비

> 전체 사이클 완료. PR 본문 작성하시겠습니까? `git-pr` 스킬로 자동 작성 가능합니다. (원격 push 후 PR 생성은 사용자 명시 승인 필요)

(사용자 승인 가정: PR 본문 작성만 승인)

`git-pr` 스킬에 위임해 본문만 준비합니다. 본문에 넘길 항목:
- 기존 동작 변경: 없음 (신규 엔드포인트·신규 서비스 추가)
- TDD 외 사용자 결정: 재고 조건부 UPDATE + `(coupon_id, user_id)` 유니크 제약, 실패 응답은 기존 관례 따름
- 한계: 동시 실행 자체는 단위/인수 테스트로 검증하지 못함. 재평가 트리거는 재고 핫로우 경합 발생 시
- review-lint `[확인]` 1건 사유

**원격 push 와 PR 생성은 실행하지 않았습니다.** push 는 사용자가 별도로 승인한 뒤 메인 컨텍스트에서 진행합니다.

### Phase 6. 최종 보고

```
=== 개발 사이클 완료 ===
브랜치: api/feat/coupon-issue (Phase 1에서 생성)
Phase 진행: TDD Phase 1~3 + 인수 테스트 (모두 PASS)
커밋: 4건 (로컬, 사용자 승인. 도메인 1 + 마이그레이션 1 + 서비스 1 + Controller 1)
변경 파일: 13개 (메인 7 + 마이그레이션 1 + 테스트 5 가정치)
테스트: 단위 테스트 전 Phase PASS + 인수 3 시나리오 PASS
review-lint: 매 Phase [위반] 0건, [확인] 1건 사유 기록
self-review: Phase 2 에서 1건 잡고 자동 수정 1회, 최종 위반 0건
인수 테스트: acceptance-tester agent (3 시나리오 PASS)
사용자 결정 기록: 동시성 방어(재고 조건부 UPDATE + 유니크 제약), 실패 응답 관례 (TDD 외, 구현 전 확인 완료)
push/PR: 미실행 (승인 대기)
다음 단계: PR 본문 확인 후 push 승인 여부 결정, 또는 사용자 수동 검수. 동시성 방어 결정을 TDD 문서에도 반영할지 확인 필요
```

**자기 검증**: Phase 0 7항목 확인 / 작업 브랜치 / 모든 Phase 커밋 / 모든 Phase 테스트 / self-review 통과 / 인수 통과 / push·PR 0건 / 위임 압축 준수 / 작성 전 질문 5개를 매 Phase 3-1 전 수행 (TDD 외 결정 2건을 구현 전 사용자 확인) / review-lint 게이트 통과.
