---
component: java-layered-unit-testing
source: pasta-japan-server
date: 2026-05-21
type: convention-mismatch
related_commits: a6b72daa82
severity: low
---

## 증상

테스트 코드에서 `@MockBean(name = "dexcomAuthorizedClientManager")` 매직 스트링 반복 사용. PR 리뷰에서 상수화 지적.

또한 같은 커밋에서 enum 인라인 FQCN(`com.x.y.State.NORMAL`) 패턴이 테스트 fixture 빌더에서 발견됨 — v1.2 자기 검증 #11(FQCN 인라인 금지)이 잡았어야 하나 비대상으로 누수.

## 수정 내용

```java
// before
@MockBean(name = "dexcomAuthorizedClientManager")
private OAuth2AuthorizedClientManager mgr;

// after
import static com.x.shared.constant.DexcomBeanNameConstants.DEXCOM_AUTHORIZED_CLIENT_MANAGER;
@MockBean(name = DEXCOM_AUTHORIZED_CLIENT_MANAGER)
private OAuth2AuthorizedClientManager mgr;
```

## 개선 제안 (java-layered-unit-testing v1.3 가드레일)

### A. @MockBean 빈 이름 상수 강제

자기 검증 체크리스트에 추가:
- [ ] `@MockBean(name = "...")` / `@Qualifier("...")` 의 빈 이름이 다른 곳에서도 사용되면 상수 import로 통일했는가?
- [ ] 빈 등록자(Configuration)에서 상수를 제공하지 않으면 → 작업 보류 후 등록자 측에 상수 추가 요청 (이 스킬 단독으로 빈 이름을 정의하지 않음)

### B. enum FQCN 인라인 금지 — 패턴 확장

v1.2 #11이 mock 예외/.class 리터럴 중심이라 enum 인라인 누수. 패턴 확장:
- 기존: `new x.y.Z()`, `isInstanceOf(x.y.Z.class)`
- **추가**: `.stateInfo(x.y.Z.ENUM_CONST)`, `EnumSet.of(x.y.Z.A, x.y.Z.B)` 등 enum 상수 접근 인라인 FQCN

자기 검증 체크리스트:
- [ ] 테스트 빌더/fixture에서 enum 상수 접근 시 `import` + 단순 클래스명 사용했는가? `com.x.y.State.NORMAL` 같은 인라인 FQCN 0건?

## 변경 파일 (참고)

- `api/src/test/.../PGHDWorkoutNudgingMessageAcceptanceTest.java`
- `api/src/test/.../DashboardStaffPrescriptionAcceptanceTest.java`

## 누적 검토

java-layered-unit-testing FQCN 관련:
- 2026-04-28: PR #527 — mock 예외/.class 리터럴 (v1.1 가드레일 추가)
- 2026-05-21: 본 건 — enum 인라인 + @MockBean 이름 매직 스트링 (v1.3 추가)

**2건 누적**. 동일 영역 재발이지만 패턴이 매번 미세하게 달라 정규식만으로는 완전 차단 어려움. 셀프 리뷰 단계와 코드 작성 단계 양쪽에서 다층 방어 권고.
