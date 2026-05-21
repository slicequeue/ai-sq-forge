---
component: self-code-reviewer
source: pasta-japan-server
date: 2026-05-21
type: convention-mismatch
related_commits: a6b72daa82, 0fc9b52338
severity: medium
---

## 증상

PR #527 사고 이후 self-code-reviewer v1.5에 FQCN 검출 가드레일을 강화했음에도, 같은 부류 누수가 PR 리뷰 단계에서 다시 지적됨. 자체 리뷰 단계에서 사전 차단 실패.

구체 사례 (commit a6b72daa82, PR 리뷰 반영 후속 커밋):
1. **Bean 이름 매직 스트링 반복** — `"dexcomAuthorizedClientManager"` 문자열이 `@Bean`, `@Qualifier`, `@MockBean(name=...)` 총 8곳에 동일 리터럴로 박혀 있었음. 오타 발생 시 런타임 NoSuchBeanDefinitionException 위험.
2. **enum 인라인 FQCN** — 테스트 코드에서 `.stateInfo(com.kakaohealthcare.moneyball.user.entity.State.NORMAL)` 형태. State import + `.stateInfo(State.NORMAL)`로 정리 가능했지만 누락.
3. **표준 라이브러리 FQCN** — `java.lang.reflect.Field` 같은 표준 라이브러리도 인라인 잔존. import 누락 케이스로 검출 가능.

후속 커밋 0fc9b52338에서는 빈 이름 상수의 모듈 위치 문제도 별도로 지적되어 shared 모듈로 이동 — config → config 의존 외관 회피.

## 수정 내용

PR 리뷰어가 잡아 사용자가 직접 수정:
- `DexcomWebClientConfiguration.DEXCOM_AUTHORIZED_CLIENT_MANAGER` public static final 상수 정의 → 8곳 static import로 교체
- `com.x.y.State.NORMAL` → `import` + `State.NORMAL`
- 후속 커밋에서 빈 이름 상수를 `shared/.../constant/DexcomBeanNameConstants`로 이동

## 개선 제안 (self-code-reviewer v1.7 가드레일)

기존 FQCN 검출 룰은 main/test 코드 본문의 `com.x.y.Z` 패턴을 잡지만, 다음 3개 패턴이 누락되어 있음:

1. **Bean 이름 매직 스트링 반복 검출**: 동일 문자열 리터럴이 `@Bean(...)`, `@Qualifier(...)`, `@MockBean(name=...)`, `@DependsOn(...)`, `BeanFactory#getBean(...)` 등에 3회 이상 등장하면 → "빈 이름 상수화 권장" 보고
2. **enum FQCN 패턴 강화**: 기존 정규식 `com.x.y.Z`에 더해 `com.x.y.Z.ENUM_CONST` 형태(점 두 단계 이상 + UPPER_SNAKE_CASE 마지막 토큰)도 별도 분류로 검출
3. **표준 라이브러리 FQCN**: `java.*.*.*` (예: `java.lang.reflect.Field`, `java.util.concurrent.TimeUnit`) 인라인 검출. 단, JPQL/SQL 문자열·로그 메시지 본문은 false positive 제외 (v1.6과 동일 정책)

### 추가 검사 — Bean 이름 상수의 위치

빈 등록자(A 모듈)·소비자(B 모듈)·테스트 mock(여러 모듈)이 공유하는 빈 이름 상수가 A의 `*Configuration` 클래스에 있으면 → "다중 모듈 공유 contract이므로 shared/.../constant/* 위치 권장" 보고. config → config 의존 외관 회피.

판단 기준:
- 상수가 `*Configuration` 클래스에 있고, 그 상수를 import하는 클래스가 **다른 모듈**의 `*Configuration` 클래스라면 → shared 이동 권고

## 변경 파일 (참고)

- `api/src/main/java/com/kakaohealthcare/moneyball/api/common/config/DexcomAuth2Configuration.java`
- `api/src/test/java/.../acceptance/app/PGHDWorkoutNudgingMessageAcceptanceTest.java`
- `api/src/test/java/.../acceptance/dashboard/DashboardStaffPrescriptionAcceptanceTest.java`
- `cgm/.../DexcomWebClientConfiguration.java`
- `shared/.../constant/DexcomBeanNameConstants.java` (후속 신규)

## 누적 검토

self-code-reviewer FQCN 관련 피드백:
- 2026-04-28: PR #527 — mock 예외/.class 리터럴 인라인 FQCN (v1.5 가드레일 추가)
- 2026-05-21: 본 건 — Bean 매직 스트링 + enum FQCN + 표준 라이브러리 FQCN + 상수 위치 (v1.7 추가)

**2건 누적** — 동일 영역 재발이므로 정규식 룰 확장 + 분류 세분화 필요. 3건 누적 시 구조적 재설계 검토.
