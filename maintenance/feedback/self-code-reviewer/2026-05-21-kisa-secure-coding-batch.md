---
component: self-code-reviewer
source: pasta-japan-server
date: 2026-05-21
type: improvement
related_prs: 7884, 7882, 7881, 7880, 7877, 7879, 7885
severity: medium
---

## 증상

KISA 시큐어코딩 점검 결과 하루에 7개 PR 일괄 머지 — 자체 리뷰 단계에서 사전 검출 가능했던 패턴들이 외부 점검에서 무더기로 발견됨.

| PR | KISA 등급 | 패턴 |
|----|-----------|------|
| #7884 | Low | 빈 catch(ignored), `// no-op`, `// 무시` 단독 주석 17건 |
| #7882 | Medium | `public static` 변수에 `final` 누락 8건 |
| #7881 | High | CookieUtils CSRF 해시 MD5 → SHA-256 |
| #7880 | High | 테스트 yml 평문 비밀번호 → 환경변수 fallback |
| #7877 | KEV | Tomcat-embed 10.1.18 → 10.1.49 |
| #7879 | Critical | assertj-core 3.24.2 → 3.27.3 |
| #7885 | - | 토큰 검증 일원화 + jwks 기반 검증 추가 |

## 수정 내용

PR 단위로 일괄 처리되어 머지됨. self-code-reviewer는 이런 종류를 잡지 않음.

## 개선 제안 (self-code-reviewer v1.7 — KISA 시큐어코딩 검사 섹션 신설)

self-code-reviewer "특별 검사 항목" 아래에 KISA 카테고리를 신설하고, 변경 파일에서 다음을 검출:

### Low 등급 (디버그·오류 처리)

| 패턴 | 검출 룰 |
|------|---------|
| 빈 catch | `catch\s*\([^)]+\s+(ignored?|_)\)\s*\{\s*\}` |
| 단독 주석 | `^\s*//\s*(no-op\|무시\|TODO\|fixme)\s*$` (catch 블록 내부) |
| 변수 사전 선언 후 try 안 할당 | `\w+\s+\w+\s*=\s*null;\s*try\s*\{` (Optional/즉시 반환 권장) |

### Medium 등급

| 패턴 | 검출 룰 |
|------|---------|
| public static (non-final) | `public\s+static\s+(?!final\b)[A-Za-z<>\[\]]+\s+\w+` (불변 가능 여부 보고) |

### High 등급

| 패턴 | 검출 룰 |
|------|---------|
| 약한 해시 알고리즘 | `MessageDigest\.getInstance\(\s*"(MD5\|SHA-1\|SHA1)"\s*\)` 또는 hashAlgorithm 상수에 같은 값 |
| 평문 비밀번호 yml | `password:\s*[^$\s].*$` (yml 파일에서, `${ENV_VAR:-fallback}` 형태 아님) — 환경변수 fallback 권장 |

### KEV/Critical 등급

| 패턴 | 검출 룰 |
|------|---------|
| 의존성 버전 검사 | `build.gradle` 변경 시 KISA Critical/KEV 목록 대조 (정기 점검 — 즉시 검출은 불가, 매주 1회 권고) |

### 검출 시 보고 형식

```markdown
### KISA 시큐어코딩 검사

| 등급 | 위치 | 패턴 | 권장 수정 |
|------|------|------|----------|
| Low | LoggingFilter.java:42 | 빈 catch(ignored) | log.debug(맥락, e) 또는 // 사유 명시 주석 |
| Medium | GroupDirectNoticeList.java:12 | public static (non-final) | final 추가 (불변이면) |
| High | CookieUtils.java:33 | MD5 해시 사용 | SHA-256 이상 권장 |
```

### 가드 — false positive 회피

- 빈 catch 패턴은 **테스트 코드의 expected exception 패턴 (`assertThatThrownBy`)에서 발생할 수 없음** → main 디렉토리만 검사
- 평문 비밀번호 패턴은 **example/sample yml은 제외** (파일명에 `example` 포함 시 skip)
- public static 패턴은 **테스트 fixture / mock 클래스는 제외** (final 강제는 main 대상)

## 변경 파일 (참고 — 패턴 학습용)

- `api/src/main/java/.../filter/LoggingFilter.java` (Low — no-op 주석)
- `api/src/main/java/.../filter/TokenExpiredAndAudienceFilter.java` (Low — ignored)
- `notification/.../InvitationEventHandler.java` (Low — IOException ignore)
- `api/src/main/java/.../util/CookieUtils.java` (High — MD5)

## 누적 검토

self-code-reviewer 시큐어코딩 영역 신규 피드백. 본 건은 1건 누적이지만 다발성 (PR 7건)이라 단일 사례 이상의 무게.
