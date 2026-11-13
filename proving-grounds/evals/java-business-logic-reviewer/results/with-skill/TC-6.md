# 비즈니스 로직 리뷰 리포트 — `api/feat/badge-issue`

> 대상: 뱃지 발급 기능 (PRD·TDD 대비 구현 정합성). 읽기 전용 리뷰이며 코드는 수정하지 않았다.
> 이 리포트는 불변식 위반 2건(AUTO FAIL)을 포함한다. 머지 전 반드시 해소가 필요하다.

---

## Phase 0. 문서 확보

- PRD: 요청에 인라인으로 제공됨 ("뱃지 발급 기능 PRD"). 저장소 파일 경로(`docs/prd/...`) 또는 Jira 링크는 제공되지 않음.
- TDD: 요청에 인라인으로 제공됨 (Domain / Service / Exception 3줄). 파일 경로·Confluence 링크는 제공되지 않음.
- 판단: 인라인 본문을 요건 원문으로 사용해 진행한다. 정식 문서와 다를 수 있으므로 원본 위치를 알려주시면 재대조하겠다.
- 한계: 입력에는 변경 코드 2개 파일(`BadgeIssueService.java`, `Badge.java`)의 발췌만 있다. 호출부(미션 달성 이벤트)·Controller·Repository·마이그레이션은 diff에 없어, 그 영역은 "확인 불가"로 표기하고 단정하지 않는다.

## Phase 1. 요건 추출

### 1.1 PRD 수용 기준

| # | 원문 인용 |
|---|-----------|
| AC-1 | "특정 미션 달성 시 자동 뱃지 발급" |
| AC-2 | "관리자는 수동 뱃지 부여 가능" |

### 1.2 TDD 시그니처

| # | 계층 | 원문 인용 |
|---|------|-----------|
| T-1 | Domain | "Badge — status(ISSUED, REVOKED), 재발급 방지" |
| T-2 | Service | "BadgeIssueService.issue(userId, badgeType)" |
| T-3 | Exception | "DuplicateBadgeException" |

- 엔드포인트·HTTP status 매핑: TDD에 명시 없음. 중복 시 응답 status(예: 409)가 TDD에 정의되지 않았다. 아래 확인 요청에 포함한다.

### 1.3 도메인 불변식 (격리)

| # | 원문 인용 | 코드 대응 위치 |
|---|-----------|----------------|
| INV-1 | "동일 사용자에게 동일 뱃지 중복 발급 절대 불가 (unique constraint: user_id + badge_type)" | `BadgeIssueService.java:20` (issue), `Badge.java:15` (status 필드) |
| INV-2 | "뱃지 발급 실패해도 미션 달성 기록은 보존 (별도 트랜잭션)" | `BadgeIssueService.java:20` (`@Transactional`) |

---

## 🟠 불변식 위반 (최우선)

### [BIZ-INVARIANT] INV-1 중복 발급 방지 미반영 — `BadgeIssueService.java:20`, `Badge.java:15`

- 요건: "동일 사용자에게 동일 뱃지 중복 발급 절대 불가" / TDD "재발급 방지" / `DuplicateBadgeException`
- 실제:
  - `issue()` 가 사전 중복 검사(`status == ISSUED` 확인, 기존 뱃지 존재 조회) 없이 `new Badge(...)` 후 곧바로 `save()` 한다 (`BadgeIssueService.java:20` 이후 본문).
  - `Badge.java:15` 의 `status` 필드에는 상태 전이 검증 메서드가 없고, 재발급 시도 시 `IllegalStateException` 도 발생하지 않는다. TDD의 "재발급 방지"가 도메인에 구현되지 않았다.
  - 방어선이 DB unique constraint 하나뿐이다. 그런데 이 constraint 가 이번 diff 어디에도 없어, 실제로 존재하는지 확인되지 않았다 (마이그레이션 파일 미포함). constraint 가 없다면 중복 발급이 그대로 저장된다.
  - constraint 가 있더라도 위반 시 `DataIntegrityViolationException` 이 그대로 전파된다. `DuplicateBadgeException` 으로 변환되지 않아 사용자에게는 일반 500 으로 노출될 수 있다.
  - 동시성: 사전 검사를 추가하더라도 check-then-save 사이에 경합이 가능하다. 최종 방어선은 DB unique constraint 이고, 그 위반을 예외 변환으로 처리해야 한다.
- 등급: **AUTO FAIL / Critical**
- 실전 사고 참조: MISSION #633 (도메인 불변식 위반 사고) 와 동일 유형. 불변식을 코드·예외 변환 없이 DB 에 맡긴 구조다.

### [BIZ-INVARIANT] INV-2 별도 트랜잭션 격리 없음 — `BadgeIssueService.java:20`

- 요건: "뱃지 발급 실패해도 미션 달성 기록은 보존 (별도 트랜잭션)"
- 실제: `issue()` 에 `@Transactional` 만 선언되어 기본 전파 `REQUIRED` 다. 미션 달성 처리 트랜잭션 안에서 호출되면 같은 트랜잭션에 참여한다. 뱃지 저장이 실패(예: 중복으로 인한 예외)하면 호출 트랜잭션이 rollback-only 로 표시되어 미션 달성 기록까지 함께 롤백된다. 요건과 정반대 동작이다.
- 확인 불가 범위: 호출부 코드가 diff 에 없어 미션 달성 처리와 같은 트랜잭션인지는 직접 확인하지 못했다. 다만 `REQUIRES_NEW` 또는 비동기/이벤트 분리가 없으므로 요건을 보장하는 코드는 존재하지 않는다. 호출부가 트랜잭션 밖이라 해도 그건 우연이며 불변식을 보장하지 않는다.
- 등급: **AUTO FAIL / Critical**

### 수정 방향 제안 (코드 수정은 하지 않음, 3건)

1. 도메인 검증: `Badge` 에 상태 전이·재발급 방지 검증을 두고(예: 이미 `ISSUED` 인 뱃지에 재발급 시 도메인 예외), `BadgeIssueService.issue()` 가 저장 전에 `(userId, badgeType)` 기존 뱃지를 조회해 `ISSUED` 이면 `DuplicateBadgeException` 을 던진다.
2. 예외 변환: DB unique constraint 가 마이그레이션에 있는지 확인하고(없으면 추가), `save` 시 `DataIntegrityViolationException` 을 `DuplicateBadgeException` 으로 변환해 경합 상황의 최종 방어선으로 삼는다. HTTP status 매핑(예: 409)은 아래 확인 요청 후 확정한다.
3. 트랜잭션 격리: 뱃지 발급을 미션 달성 트랜잭션과 분리한다(`Propagation.REQUIRES_NEW`, 또는 커밋 후 이벤트 처리). 이때 발급 실패 시 로그·지표를 남겨 침묵 실패가 되지 않게 한다 (RR-1, RR-13).

---

## 🔴 미구현

- [BIZ-MISSING] AC-2 "관리자는 수동 뱃지 부여 가능"
  - 예상 위치: 관리자 Controller / 수동 부여 Service 메서드
  - 결과: 제공된 변경 코드에 관리자 부여 경로가 없다. `issue(userId, type)` 하나뿐이며 관리자 권한 검증도 보이지 않는다. 다른 PR·기존 코드에 있는지는 diff 만으로 확인 불가이므로, 있다면 위치를 알려 달라.
  - 등급: High
- [BIZ-MISSING] T-3 `DuplicateBadgeException`
  - 예상 위치: 예외 클래스 및 `@ExceptionHandler`/`@RestControllerAdvice`
  - 결과: diff 에 예외 클래스 정의도 throw 지점도 없다. 코드 주석대로 `DataIntegrityViolationException` 이 그대로 전파된다.
  - 등급: High

## 🟡 사각지대

- [BIZ-EDGE] 동시 발급 경합 — `BadgeIssueService.java:20`
  - 같은 사용자·같은 뱃지의 동시 요청(예: 미션 이벤트 중복 수신, 자동 발급과 관리자 수동 발급 동시 실행)에서 사전 검사만으로는 막을 수 없다. DB constraint + 예외 변환이 필요하다 (INV-1 수정안 2 와 동일).
  - 등급: High
- [BIZ-EDGE] `REVOKED` 상태 뱃지의 재처리 — `Badge.java:15`
  - `status(ISSUED, REVOKED)` 가 있으나 `REVOKED` 이후 동일 `(userId, badgeType)` 을 다시 발급할 수 있는지가 요건에서 불명확하다. unique constraint 가 `status` 를 포함하지 않으면 `REVOKED` 뒤 재발급은 constraint 위반이 된다. 아래 확인 요청 1번.
  - 등급: Medium
- [BIZ-EDGE] `issue(Long userId, BadgeType type)` 입력 null 처리 없음 — `BadgeIssueService.java:20`
  - null 입력 시 처리 방침이 요건에 없다. 요건 확정 후 판단 필요.
  - 등급: Low

## ⚠️ 부분 매핑

- [BIZ-PARTIAL] AC-1 "특정 미션 달성 시 자동 뱃지 발급"
  - 매핑된 부분: 발급 실행 단위 `BadgeIssueService.issue()` (`BadgeIssueService.java:20`).
  - 누락/확인 불가: "특정 미션 달성" 을 감지해 `issue()` 를 호출하는 호출 지점이 diff 에 없다. 어떤 미션이 어떤 뱃지에 대응하는지도 PRD 문구("특정 미션")만으로는 정해지지 않는다 (아래 확인 요청 2번). 그리고 INV-2 때문에 호출 방식이 요건을 깨뜨릴 수 있다.
  - 등급: Medium
- [BIZ-PARTIAL] T-1 `Badge` 도메인 — `Badge.java:15`
  - 매핑된 부분: `status` 필드 존재(`Badge.java:15`). ISSUED/REVOKED enum 정의 자체는 diff 에서 확인되지 않았다.
  - 누락: "재발급 방지" 도메인 로직·상태 전이 검증이 없다 (INV-1 참조).
  - 등급: High

## ✅ 매핑됨 (요약)

- T-2 `BadgeIssueService.issue(userId, badgeType)`: 시그니처가 TDD 와 일치한다 — `BadgeIssueService.java:20` (`issue(Long userId, BadgeType type)`). 내부 동작의 정합성은 위 불변식 항목에서 별도로 지적했다.

---

## 리뷰 재발 방지 검사 (RR)

| 검사 | 결과 |
|------|------|
| 장애 시 동작 (RR-1) | 발급 실패 시 열림/닫힘 정책이 코드·주석에 없고, 실패를 로그·지표로 남기는 처리도 없음. INV-2 수정안 3 에서 함께 처리 필요 |
| 실패 격리 (RR-13) | 뱃지 실패가 핵심 정보(미션 달성 기록)까지 되돌릴 수 있는 구조. INV-2 와 동일 |
| 동작 변경·판정 기준 (RR-14) | 존재 확인이 저장보다 먼저여야 하는데 반대. INV-1 과 동일 |
| 결정성·enum 순서·벌크 연산·응답 단위 (RR-2/3/4/6) | 해당 코드 없음 |

## 📊 통계

- 총 요건 7건 (수용 기준 2 + TDD 3 + 불변식 2). 불변식 2건은 코드 대응 위치로 판정했고 TDD T-1 과 중복 관점이다.
- 상태: 매핑됨 1 (T-2) / 부분 매핑 2 (AC-1, T-1) / 미구현 2 (AC-2, T-3) / 불변식 위반 2 (INV-1, INV-2)
- 요건 외 사각지대 3건 (동시 발급 경합, REVOKED 재처리, null 입력)
- 판정: 불변식 위반 2건으로 **머지 불가 (AUTO FAIL)**

---

## 사용자 확인 요청 (임의 해석하지 않음, BIZ-HG-2)

1. `REVOKED` 된 뱃지에 동일 사용자가 같은 종류를 다시 받을 수 있는가? PRD 는 "중복 발급 절대 불가" 이고 TDD 는 "재발급 방지" 라 `REVOKED` 후 재부여가 허용인지 금지인지 문서로 정해지지 않았다. 답에 따라 unique constraint 범위와 도메인 규칙이 달라진다.
2. AC-1 의 "특정 미션" 은 어떤 미션과 뱃지의 대응인가? 매핑 정의 위치(PRD 부록, 코드 enum 등)를 알려 달라.
3. 중복 발급 시 사용자·관리자에게 어떤 응답을 줄 것인가 (HTTP status, 메시지)? TDD 에 매핑이 없다. 자동 발급 경로에서는 중복을 에러가 아닌 무시(멱등)로 볼지도 정해야 한다.
4. 정식 PRD/TDD 문서 위치(경로 또는 링크)와, DB unique constraint(user_id + badge_type)가 정의된 마이그레이션 위치를 알려 달라.

## 다른 리뷰어 위임 안내 (스코프 밖)

이 리포트는 요건·불변식 관점만 다뤘다. 다음은 판정에 넣지 않고 위임한다.

- 보안(관리자 수동 부여 API 의 권한 검증 등): `java-secure-coding-reviewer`
- 성능(`REQUIRES_NEW` 도입 시 커넥션 점유·트랜잭션 비용): `java-performance-reviewer`
- 아키텍처(계층·예외 계층 위치·컨벤션): `java-architecture-reviewer`
- 공통 룰: `self-code-reviewer`
- 다관점 일괄 검토가 필요하면 `java-composite-reviewer` 조합 호출을 권장한다.
- PRD↔TDD 문서 간 불일치(위 확인 요청 1번의 문구 불명확 포함)가 의심되면 `prd-plan-designer` 재호출을 안내한다.

## 자기 검증

1. Phase 0 문서 위치 확인 및 미제공 사실 명시: 완료
2. 수용 기준 번호 + 원문 인용: 완료
3. 불변식 별도 리스트: 완료 (INV-1, INV-2)
4. 매핑 판정에 파일:라인 근거: 완료 (diff 에 있는 라인만 인용, 없는 영역은 확인 불가로 표기)
5. 5분류 아이콘: 완료
6. 불변식 위반 최상단 배치: 완료
7. 모호 문구 임의 해석 금지: 확인 요청으로 분리
8. 스코프 밖 위임 안내: 완료
9. 코드 수정 없음: 완료
10. 통계 포함: 완료
