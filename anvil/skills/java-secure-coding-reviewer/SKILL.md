---
name: java-secure-coding-reviewer
description: "백엔드 Java Spring Boot 보안 리뷰 전용 스킬 — KISA 시큐어코딩·OWASP Top 10·PII 처리·시크릿 노출 방지·의존성 CVE. 보안 관점 요청 시 자동 트리거, java-composite-reviewer 에이전트 안에서도 조합 가능. Use proactively when reviewing security, KISA, OWASP, secret leak, PII exposure, or CVE concerns."
version: "0.1"
last-modified: "2026-07-09"
changelog: "v0.1 — 2026-07-09 self-code-reviewer v1.11의 KISA 시큐어코딩 섹션을 이관·분리하여 신설. self v1.7 KISA 5등급 룰 원본 그대로 이관 후 OWASP Top 10·PII 처리·시크릿 노출·CVE 의존성 확장. self-code-reviewer는 공통 룰(FQCN·@Profile·Hibernate Session·임시 로그 등)만 잔존, 도메인 특수 보안 관점은 이 스킬 담당."
harness-status: pending
---

# java-secure-coding-reviewer — 보안 관점 코드 리뷰 스킬

> 백엔드 Java Spring Boot 코드의 **보안 리뷰 전용**. self-code-reviewer가 담당하던 KISA 섹션을 이관·확장하며, OWASP·PII·시크릿·CVE 4개 축을 추가로 커버한다.

---

## 트리거 조건

- 사용자가 "보안 리뷰", "KISA 점검", "OWASP 검토", "시크릿 노출", "PII 처리", "취약점", "CVE" 등을 언급
- java-composite-reviewer 에이전트가 보안 관점을 요청
- PR 리뷰 요청에 보안 태그가 명시

---

## 스코프

### In-Scope

| 축 | 커버 |
|----|------|
| KISA 시큐어코딩 | Low/Medium/High/KEV/Critical 5등급 (2026-05 KISA 점검 일괄 머지 경험 반영) |
| OWASP Top 10 | SQL Injection · XSS · CSRF · 인증/인가 · 세션 관리 · 암호화 실패 · 안전하지 않은 역직렬화 · SSRF · 로깅·모니터링 실패 · 취약 컴포넌트 |
| PII·민감정보 | 로그·저장·전송 시 PII(userId·사번·병원명·전화·이메일) 노출 방지, 마스킹 |
| 시크릿 노출 | 하드코딩 API 키·비밀번호·토큰·Firebase 키·JWT secret 리터럴 |
| 의존성 CVE | Gradle/Maven 의존성 CVE 매칭 (SBOM·Snyk·dependency-check 준수) |

### Out-of-Scope (다른 리뷰어 담당)

| 관점 | 담당 |
|------|------|
| 성능 (N+1·캐시·트랜잭션·스레드) | java-performance-reviewer |
| 4-Tier 계층·모듈 관계·Bean 등록·컨벤션 | java-architecture-reviewer |
| Hibernate Session 오염 / @Profile 문법 / FQCN / 임시 로그 등 도메인 무관 공통 룰 | self-code-reviewer |
| Locale.ROOT / i18n 4파일 동기화 | self-code-reviewer + tolgee |

---

## 하드 가드레일 (AUTO FAIL)

| # | 카테고리 | 검출 | 등급 |
|---|---------|------|------|
| SEC-HG-1 | SQL Injection | 문자열 concat 쿼리 (`String.format`으로 SQL 생성, `+`로 조립) — `PreparedStatement`/JPA `@Query` 파라미터 바인딩 미사용 | **AUTO FAIL** |
| SEC-HG-2 | 하드코딩 시크릿 | API 키·비밀번호·JWT secret·Firebase private key·OAuth client secret 리터럴이 소스에 박혀 있음 | **AUTO FAIL** |
| SEC-HG-3 | PII 로그 본문 | userId·사번·병원명·환자명·전화번호·이메일 리터럴이 `log.*(...)` 본문에 노출 (마스킹 없이) | **AUTO FAIL** |
| SEC-HG-4 | 약한 해시로 인증·서명 | `MessageDigest.getInstance("MD5"\|"SHA-1")` 를 인증·세션·서명·CSRF 토큰에 사용 (self v1.7 High 룰 이관) | **AUTO FAIL** |
| SEC-HG-5 | 평문 비밀번호 yml | `application-*.yml`에 `password:\s*[^$]` (환경변수 fallback 아님). `example`/`sample`/`template` 파일은 skip | **AUTO FAIL** |

---

## KISA 5등급 검사 (self v1.7 이관)

2026-05-21 KISA 점검 일괄 머지(PR #7877~#7885) 경험 반영. 변경 파일에서 사전 검출.

### Low 등급 — 디버그·오류 처리

| 패턴 | 검출 | 권장 수정 |
|------|------|----------|
| 빈 catch (변수명 ignored/ignore/_) | `catch\s*\([^)]+\s+(ignored?\|_)\)\s*\{\s*\}` | `log.debug/warn(맥락, e)` 또는 `// 사유 명시` 한국어 주석 |
| 단독 무사유 주석 | catch 블록 안에 `^\s*//\s*(no-op\|무시\|TODO\|fixme)\s*$` 만 존재 | "왜 무시해도 되는가" 한 줄 설명 추가 |
| try 전 null 사전 선언 | `\w+\s+\w+\s*=\s*null;\s*try\s*\{` | `Optional<T>` 변환 또는 try 안에서 즉시 반환 |

### Medium 등급 — 불변성·싱글톤

| 패턴 | 검출 | 권장 수정 |
|------|------|----------|
| public static (non-final) | `public\s+static\s+(?!final\b)[A-Za-z<>\[\]]+\s+\w+\s*=` | 불변 가능하면 `final` 추가. mutable 사유 있으면 주석 |
| @Service 싱글톤 mutable instance field | `@Service\|@Component\|@Repository` + `private\s+(?!static\s+)(?!final\s+)[A-Za-z<>\[\]]+\s+\w+;` (필드) | `AtomicReference<record>` 또는 메서드 인수 전달 |

### High 등급 — 보안 알고리즘·시크릿

| 패턴 | 검출 | 권장 수정 |
|------|------|----------|
| 약한 해시 알고리즘 | `MessageDigest\.getInstance\(\s*"(MD5\|SHA-1\|SHA1)"\s*\)` 또는 상수 값 | SHA-256 이상. CSRF/세션 ID/서명 용도면 즉시 교체 (SEC-HG-4 AUTO FAIL) |
| 평문 비밀번호 yml | `password:\s*[^$\s]` (환경변수 fallback 아님) | `${DB_PASSWORD:-fallback}` 패턴. 샘플 파일 제외 (SEC-HG-5 AUTO FAIL) |

### KEV/Critical 등급 — 의존성

| 패턴 | 검출 | 권장 수정 |
|------|------|----------|
| build.gradle 의존성 변경 | `build.gradle\|*.gradle.kts` 변경 시 | KISA Critical/KEV 목록 대조 권장 (자동 검출 어려움 — 사용자 확인 요청) |

### False positive 회피

- 빈 catch: 테스트 코드는 expected exception 패턴이라 skip
- 평문 비번 yml: `example`/`sample`/`local-template` 포함 시 skip
- public static (non-final): 테스트 fixture/mock 클래스(`*Fixture.java`, `Fake*.java`) skip

---

## OWASP Top 10 검사

### A01. Broken Access Control

- `@PreAuthorize`/`@Secured` 없이 `@RestController` 메서드 노출 → 인증 우회 위험
- `SecurityConstants.airArray` 등록 누락 (self-code-reviewer 공통 룰과 연계 — 여기서는 인증·인가 관점만)
- 리소스 소유권 검증 누락 (`user.id != resource.ownerId` 검사 없이 조회·수정)

### A02. Cryptographic Failures

- 약한 해시(MD5/SHA-1) — High 등급 SEC-HG-4 참조
- HTTPS 미강제 (WebClient/RestTemplate에서 `http://` 하드코딩)
- 대칭키 하드코딩 (SEC-HG-2 AUTO FAIL)

### A03. Injection

- SQL Injection: `String.format`/`+`로 SQL 조립 → SEC-HG-1 AUTO FAIL
- JPQL Injection: `@Query(value = "... " + variable + " ...")` 파라미터 바인딩 미사용
- Command Injection: `Runtime.exec(userInput)`, `ProcessBuilder(userInput)` 사용
- LDAP/XPath Injection: 외부 입력을 필터·쿼리에 직접 삽입

### A04. Insecure Design

- 요율 제한(Rate Limiting) 없는 인증·로그인 엔드포인트
- 예측 가능한 ID(순차 정수) — UUID/ULID 사용 권장

### A05. Security Misconfiguration

- 기본 계정·기본 비밀번호 잔존
- Spring Security 설정에서 `permitAll()` 광범위 적용
- Actuator 엔드포인트가 `/actuator/**` permitAll (info·health 외 노출 위험)

### A06. Vulnerable and Outdated Components → CVE 섹션 참조

### A07. Identification and Authentication Failures

- JWT secret 하드코딩 (SEC-HG-2)
- 토큰 만료 시간 무한대(`exp` 없음)
- 로그인 실패 로그에 비밀번호 원문 노출 (SEC-HG-3)
- 세션 fixation — 로그인 후 세션 재발급 없음

### A08. Software and Data Integrity Failures

- 안전하지 않은 역직렬화: `ObjectInputStream` 신뢰할 수 없는 소스에서 사용
- Jackson `enableDefaultTyping()` 활성화 (RCE 위험)

### A09. Security Logging and Monitoring Failures

- 인증·인가 실패에 로그 없음 (감사 추적 불가)
- **PII 로그 본문 노출** (SEC-HG-3 AUTO FAIL) — 감사 로그가 오히려 유출 경로

### A10. Server-Side Request Forgery (SSRF)

- 사용자 입력 URL을 WebClient/HttpClient가 직접 호출
- 내부 네트워크 IP(10.x, 192.168.x, 169.254.169.254) 필터링 없음

---

## PII·민감정보 처리 룰

### 로그 본문 PII 노출 (SEC-HG-3 AUTO FAIL)

| 필드 유형 | 검출 | 권장 수정 |
|----------|------|----------|
| 사용자 식별자 | `log\.(info\|debug\|warn\|error)\(.*\b(userId\|user_id\|memberId\|patientId)\s*[:=]\s*[^,)]+` (마스킹 없이) | ID 해시화 또는 마지막 4자리만 노출 |
| 사번 | `log.*(employeeId\|empNo\|사번)` 리터럴 | 마스킹 (앞 2자 + `****`) |
| 병원명·환자명·이름 | `log.*(patientName\|userName\|hospitalName)` | 이니셜만 or 완전 제거 |
| 전화·이메일 | `log.*(phone\|phoneNumber\|email)` | 마스킹 (`010-****-1234`, `xxx@example.com`) |
| 주민등록번호·사업자번호 | `log.*(ssn\|residentNumber\|businessNumber)` | 뒷자리 마스킹 필수 |
| 카드번호·계좌번호 | `log.*(cardNumber\|accountNumber)` | 처음 4자리 + 마지막 4자리만 |

### 로그 요약 원칙 (PR #594 반영)

- 페이로드 전체 로깅 금지: 호출자·건수·요약 3요소만
- 예: `log.info("Dexcom devices called by {} — {} records fetched", callerId, deviceCount)`
- 사유별 WARN 로깅으로 구분 (미등록 sensorId / 미연결 사용자)

### 저장·전송 시 PII

- DB 컬럼에 PII 저장 시 → 암호화 컬럼(`@Convert(converter = ...)`) 또는 마스킹 저장
- 외부 API 전송 시 → 필요 최소 필드만. 전체 사용자 객체 통째 전송 금지

---

## 시크릿 노출 검출

### 하드코딩 시크릿 (SEC-HG-2 AUTO FAIL)

**grep 패턴** (변경 파일 대상):

| 카테고리 | 정규식 | 예시 |
|---------|--------|------|
| API 키 | `["'](sk_\|pk_\|AIza\|AKIA\|ghp_\|ghs_)[A-Za-z0-9]{20,}["']` | Stripe·Google·AWS·GitHub 토큰 리터럴 |
| JWT secret | `jwtSecret\|jwt\.secret\|JWT_SECRET\s*=\s*["'][^$"']{16,}["']` | 환경변수 아닌 리터럴 |
| Firebase 키 | `["']-----BEGIN PRIVATE KEY-----` | private key 통째 박음 |
| 비밀번호 필드 | `password\s*=\s*["'][^$"'][^"']{4,}["']` (환경변수 fallback 아님) | 소스 하드코딩 |
| OAuth client secret | `clientSecret\|client_secret\s*=\s*["'][^$"']{16,}["']` | OAuth 자격증명 |

### 통과 예 (환경변수 fallback)

```yaml
password: ${DB_PASSWORD:-}
jwt.secret: ${JWT_SECRET:-}
```

```java
@Value("${jwt.secret}")
private String jwtSecret;
```

### False positive 회피

- 테스트 픽스처(`test/resources/`)의 더미 값은 skip. 단 실 값과 유사한 형식(`sk_live_...`)은 예외
- `application-example.yml`, `application-local-template.yml` skip
- 주석 처리된 리터럴은 skip (하지만 커밋 전에 삭제 권장)

---

## CVE 의존성 검사

### Gradle·Maven 변경 감지

변경 파일에 `build.gradle`/`build.gradle.kts`/`pom.xml`이 있으면:

1. 변경된 dependency 라인 추출
2. 각 dependency의 CVE 매칭 (자동 검출 어려움 → 사용자에게 확인 요청)
3. SBOM·Snyk·dependency-check 결과 파일이 프로젝트에 있으면 참조

### 알려진 취약 라이브러리 카탈로그 (KISA KEV 대비 예시)

| 라이브러리 | 취약 버전 | 권장 |
|-----------|----------|------|
| log4j-core | < 2.17.1 (Log4Shell) | 2.17.1+ |
| jackson-databind | < 2.14.0 (다수) | 최신 |
| spring-boot | < 2.7.18 / < 3.1.5 (Actuator·Web 취약점) | 최신 patch |
| commons-text | < 1.10.0 (CVE-2022-42889) | 1.10.0+ |

**검출 시 등급**: 리터럴 매치 → 필수 수정. 사용자 CVE 추가 확인 필요 → Info 등급 안내.

### 리포트 형식

```markdown
### CVE 의존성 검사

| 라이브러리 | 현재 버전 | 취약 CVE | 권장 |
|-----------|----------|---------|------|
| log4j-core | 2.14.1 | CVE-2021-44228 (Log4Shell) | 2.17.1+ |
```

---

## 리포트 형식 (self-code-reviewer와 동일)

```markdown
## 보안 코드 리뷰 결과

**브랜치**: {현재 브랜치}
**비교 기준**: dev
**변경 파일**: {N}개
**보안 관점 검사**: KISA / OWASP Top 10 / PII / 시크릿 / CVE

### AUTO FAIL (즉시 수정 필수)

| # | 파일:위치 | 유형 | 위반 | 수정 방향 |
|---|----------|------|------|-----------|
| 1 | api/.../XxxService.java:42 | SEC-HG-1 (SQL Injection) | `String.format("SELECT ... WHERE id=%s", userId)` | `@Query(nativeQuery=true)` + 파라미터 바인딩 |

### 필수 수정 (Critical / High)

| # | 파일:위치 | 유형 | 등급 | 내용 | 수정 방향 |
|---|----------|------|------|------|-----------|

### 권장 개선 (Medium / Low)

| # | 파일:위치 | 유형 | 등급 | 내용 | 개선 방향 |
|---|----------|------|------|------|-----------|

### 검사 통과 항목

- KISA Low: OK
- KISA Medium: OK
- OWASP A01 Broken Access Control: OK
- PII 로그 노출: OK
- 시크릿 하드코딩: OK
- CVE 의존성: 변경 없음
```

**유형 코드**:

| 코드 | 의미 |
|------|------|
| `SEC-KISA-{L\|M\|H\|K\|C}` | KISA 5등급 |
| `SEC-OWASP-A0{N}` | OWASP Top 10 |
| `SEC-PII` | PII 노출 |
| `SEC-SECRET` | 시크릿 하드코딩 |
| `SEC-CVE` | 의존성 취약점 |
| `SEC-HG-{N}` | 하드 가드레일 AUTO FAIL |

**등급**: `AUTO FAIL` / `Critical` / `High` / `Medium` / `Low` / `Info`

---

## 가드레일

### 하드 가드레일 (절대 위반 불가)

- **코드 변경 금지** — 이 스킬은 **읽기 전용**. 코드를 수정하지 않는다
- **커밋/push 금지** — 리뷰 결과 보고만
- **시크릿 리포트 마스킹** — 발견한 시크릿 리터럴을 리포트에 원본 그대로 노출하지 말 것. `sk_live_****` 형태로 마스킹 후 파일:라인만 정확히 안내

### 소프트 가드레일

- False positive 회피 룰 우선 적용 (테스트 픽스처·샘플 파일 skip)
- KISA/OWASP 판정 애매하면 "검토 권장" 등급으로 사용자 결정 요청
- CVE는 자동 검출 한계 명시 — 사용자에게 SBOM·Snyk 결과 파일 요청 병기

---

## 자기 검증 체크리스트

리뷰 완료 후 반드시 확인:

1. [ ] **범위**: 변경된 파일만 대상으로 했는가? (dev 기준 diff)
2. [ ] **KISA 5등급**: Low/Medium/High/KEV/Critical 각 패턴을 명시적으로 검사했는가?
3. [ ] **OWASP Top 10**: A01~A10 각 축을 순회했는가? 미해당은 "검사 통과"로 명시?
4. [ ] **PII 로그 검사**: userId·사번·이름·전화·이메일 리터럴이 log 본문에 있는지 grep했는가? SEC-HG-3 AUTO FAIL 우선 처리?
5. [ ] **시크릿 grep**: API 키·JWT secret·비밀번호·Firebase 키 5종 정규식으로 검색했는가? 하드코딩 발견 시 마스킹 후 보고?
6. [ ] **CVE 대조**: `build.gradle`·`pom.xml` 변경 있으면 알려진 취약 라이브러리 카탈로그와 대조하고, 사용자에게 SBOM 결과 요청했는가?
7. [ ] **AUTO FAIL 분리**: SEC-HG-1~5 위반을 별도 섹션으로 최상단에 배치했는가?
8. [ ] **False positive**: 테스트 픽스처·샘플 yml·주석 처리 코드에 대한 skip 룰 적용했는가?
9. [ ] **시크릿 마스킹**: 리포트에 발견한 시크릿 값 자체를 노출하지 않고 파일:라인만 안내했는가?
10. [ ] **스코프 밖 이관**: 성능·아키텍처·공통 룰(Hibernate Session·@Profile·FQCN·i18n) 관점에서 발견한 것은 별도 리뷰어에게 위임 안내했는가? (java-performance-reviewer / java-architecture-reviewer / self-code-reviewer)

---

## 참조 인덱스

| 파일 | 상태 | 내용 |
|------|------|------|
| `references/evaluation-rubric.md` | **미작성** (harness-status: pending) | 평가 루브릭 (100점, AUTO FAIL 조건) |

**정본 참조**:
- self-code-reviewer v1.11 — 공통 룰(FQCN·@Profile·Hibernate Session·임시 로그·i18n·Locale·Bean Qualifier 등)
- java-spring-coder v1.11 — 하드 가드레일 v1.11-A/B/C (Session 오염·SQL 에러코드·REQUIRES_NEW)
- java-performance-reviewer — 성능 관점
- java-architecture-reviewer — 4-Tier·모듈·컨벤션
- java-composite-reviewer (agent) — 4개 리뷰어 조합 오케스트레이션
