---
name: self-code-reviewer
description: "dev 브랜치 기준으로 변경 코드를 프로젝트 규칙(.claude/rules/)과 대조하여 위반/개선점을 보고하는 자체 코드 리뷰 스킬. 코드 리뷰, 품질 검사, self review, 규칙 준수 검사 요청 시 사용. Use proactively when the user asks for code review, quality check, or rule compliance review."
version: "1.10"
last-modified: "2026-07-02"
changelog: "v1.10 — 2026-07-02 6월 pasta 사고 3건 흡수: (1) Bean Qualifier cross-module 검증 — 3회 재발(5월 api → 6/16 batch·batch-app #593 → 6/19 admin #588) 방지, 다른 모듈이 같은 상수 참조하는데 미준수 케이스 AUTO FAIL 확장. (2) 인터페이스 구현체 모듈별 등록 확인 — #597 UserDiabetesTypeService 누락 기동 실패 방지. (3) 임시 진단 로그 후속 제거 강제 — #616 대시보드 403 진단 로그 부채화 방지. | v1.9 — 2026-05-21 이번 주 추가 패턴: (1) catch 블록 부가 주석 검출 — 'ACL 변환 실패 시 빈 리스트로 fallback' 같은 부가 설명 주석은 log 메시지로 흡수, 주석은 제거 (commit f3b85a79d0 KISA 리뷰 반영 사례). (2) @Service 싱글톤 mutable instance field 검출 (KISA Medium 진단). (3) WebClient 외부 호출 timeout 누락 / 재시도 필터 4xx 포함 위험 검출. (4) Soft-delete + UNIQUE 충돌 패턴. | v1.8 — Locale.ROOT 누락 검출. v1.7 — Bean 매직 스트링 + KISA 시큐어코딩 섹션. v1.6 — blueprint v2.0"
---

# self-code-reviewer — 자체 코드 리뷰 스킬

> 프로젝트 규칙: `.claude/rules/` (인덱스: `00-rules-index.md`)

---

## Phase 0. 사전 확인

1. **현재 브랜치 확인**: `git branch --show-current` — dev/main이면 리뷰 대상 없음, 안내
2. **비교 기준 확인**: 기본 `dev`. 사용자가 다른 브랜치를 지정하면 해당 브랜치 사용
3. **변경 범위 파악**: `git log dev..HEAD --oneline` + `git diff dev...HEAD --stat`
4. **변경 파일 없으면**: 리뷰 대상 없음 안내
5. **admin 모듈 포함 여부**: 변경 파일에 `admin/` 경로가 있는가?
   - **YES** → 13~16 규칙 추가 로드. 01-architecture의 4-Tier를 admin에 적용하여 위반으로 오판하지 않도록 주의
   - **NO** → 기존 01~12 규칙 적용

---

## 핵심 규칙

### 리뷰 대상

- `dev` 브랜치 이후 **추가·변경된 코드만** 리뷰
- 변경되지 않은 기존 코드는 리뷰하지 않음
- 삭제된 코드는 "삭제가 적절한지"만 확인

### 리뷰 관점 (우선순위 순)

| 우선순위 | 관점 | 설명 |
|---------|------|------|
| 1 | **가드레일 위반** | 하드 가드레일 위반 여부 (즉시 수정 필요). **Domain에 JPA 어노테이션(@Entity, @Table 등) 존재도 이 등급** |
| 2 | **아키텍처 위반** | 의존성 방향, Repository 패턴, Service JPA Entity 노출, **타 도메인 경계 위반** |
| 3 | **컨벤션 위반** | 네이밍, Lombok, record/class, import 규칙 |
| 4 | **설정 누락** | SecurityConstants, 환경변수 4곳, 마이그레이션 |
| 5 | **테스트 품질** | 계층별 테스트, Fake/Spy, Testcontainers |
| 6 | **권장 개선** | 가독성, 일관성, 유지보수 (위반은 아님) |

---

## 실행 프로토콜

### Step 1. 변경 범위 수집

```bash
# 커밋 목록
git log dev..HEAD --oneline

# 변경 파일 통계
git diff dev...HEAD --stat

# 변경 내용 상세 (파일별)
git diff dev...HEAD -- {path}
```

### Step 2. 규칙 로드

`.claude/rules/` 하위 규칙 파일을 Read 도구로 참조:

| 규칙 파일 | 검사 대상 |
|-----------|-----------|
| `01-architecture-convention.md` | 의존성 방향, 패키지 구조, Client 패턴 |
| `19-architecture-boundaries.md` | 타 도메인 Repository import 금지, 삭제 전 사용처 확인, Qualifier |
| `02-domain-entity-convention.md` | Domain Entity class, Lombok, primitive/Wrapper |
| `03-jpa-entity-convention.md` | JPA Entity, Builder, 변환 메서드 |
| `04-repository-pattern-convention.md` | 3단계 Repository 패턴 |
| `05-dto-web-layer-convention.md` | DTO record, 팩토리 메서드, Controller |
| `06-exception-handling-convention.md` | MoneyballException, ExceptionConstants |
| `07-general-project-convention.md` | 네이밍, 로깅, Import, 환경변수, DB 마이그레이션 |
| `08-test-code-convention.md` | TDD, Fake/Spy, 계층별 테스트 |
| `09-guardrails.md` | Testcontainers, 커밋 보호, 마이그레이션 보호 |
| `12-multipart-image-validation.md` | 이미지 업로드 검증 |
| `13-admin-module-overview.md` | admin 모듈 구조, 4-Tier 예외 (admin/** 변경 시) |
| `14-admin-thymeleaf-layout-convention.md` | Thymeleaf 레이아웃, URL-View-File 정합 (admin/** 변경 시) |
| `15-admin-security-history-convention.md` | @PreAuthorize, AdminHistory 감사 로그 (admin/** 변경 시) |
| `16-admin-static-assets-convention.md` | 페이지별 JS, sidebar, static 자산 (admin/** 변경 시) |

### Step 3. 항목별 검사

변경된 각 파일에 대해 해당하는 규칙을 대조. 상세 체크리스트는 `references/review-checklist.md` 참조.

#### 특별 검사 항목

- **환경변수 검사**: `application.yml`에 `${env.KEY}` 추가 시 → `application-jp-dev/stg/prd.yml`에 `${KEY}` 존재 확인
- **시큐리티 경로 검사**: 새 API 엔드포인트 추가 시 → `SecurityConstants.airArray` 등록 확인
- **마이그레이션 검사**: `obesity/` 하위 기존 파일 수정/삭제 여부 확인
- **도메인 엔티티 NOT NULL 검증**: 생성자에서 NOT NULL 필드에 `Objects.requireNonNull` 검증 여부
- **도메인 엔티티 Lombok**: `@Getter` + `@EqualsAndHashCode` 필수 적용 여부
- **로깅 형식 검사**: `[ClassName.methodName]` 접두사 사용 여부, PII 금지, 민감정보 마스킹 여부
- **Service 반환 타입 검사**: JPA 엔티티를 Service 밖으로 직접 노출하는지 여부
- **타 도메인 Repository import 검사**: 다른 도메인의 `*JpaRepository`, `*JpaEntity`, `*RepositoryImpl`을 직접 import하는지 (19-architecture-boundaries 위반)
- **Qualifier 주입 검사**: 동일 인터페이스 구현체가 여러 개일 때 `@Qualifier`로 명시적 주입하는지
- **삭제 안전성 검사**: Service/Client/유틸리티 클래스 삭제 시 전체 프로젝트에서 사용처 잔존 여부
- **재시도 로직 검증**: 재시도 로직이 있으면 실제 catch/retry가 동작하는지 로직 흐름 검증
- **JPQL 페이지네이션 검사**: `JOIN FETCH` + `Page` 사용 시 `countQuery` 분리 여부
- **페이지네이션 필터 파라미터 검사**: 페이지네이션 링크에 현재 필터 파라미터가 모두 포함되었는지
- **민감정보 로깅 검사**: 쿠폰 코드 등 민감 정보가 INFO 로그에 평문으로 노출되는지
- **FQCN(Fully Qualified Class Name) 검출**: 코드 본문(import 문 외)에 `com.x.y.Z` 형태 패키지 경로가 직접 박혀 있는지 검사. **메인+테스트 코드 모두 대상**. 가장 자주 누수되는 패턴(PR #527 사례):
  - `new x.y.Z("...")` — 예외/객체 인스턴스 생성을 인라인으로
  - `isInstanceOf(x.y.Z.class)` / `MyClass.class` 형태의 `.class` 리터럴
  - `x.y.Z variable = ...` / 매개변수 / 제네릭 타입 인자 / 캐치 절
  - **(v1.7)** `x.y.Z.ENUM_CONST` 형태 — enum 상수 접근 인라인 FQCN. 예: `.stateInfo(com.x.y.State.NORMAL)`. import + 단순 클래스명 사용 권장
  - **(v1.7)** `java.x.y.Z` 표준 라이브러리 인라인 — 예: `java.lang.reflect.Field`, `java.util.concurrent.TimeUnit`. import 누락 케이스로 검출
  - **검사 룰 (개념)**: 정규식 `\b[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+\.[A-Z][A-Za-z0-9_]*(\.[A-Z][A-Z0-9_]*)?\b` 매칭이 import 문이 아닌 코드 본문에 등장하는지 (마지막 그룹은 enum 상수 옵션)
  - **검사 제외**: 어노테이션 인자 문자열, SpEL 표현식, JPQL/SQL 쿼리 문자열, 로그 메시지 본문은 false positive — 무시
  - **검출 시 등급**: 필수 수정 (07-general-project-convention "Explicit Imports" 명시 위반). 테스트 파일도 동일 적용 — "테스트라 한 번만 쓰니까"는 면죄부 아님

- **(v1.7) Bean 이름 매직 스트링 검출**: 동일 빈 이름 문자열 리터럴이 변경 파일 군집에서 3회 이상 등장하면 → "상수화 권장" 보고
  - 검사 위치: `@Bean(...)`, `@Bean(name=...)`, `@Qualifier("...")`, `@MockBean(name=...)`, `@DependsOn("...")`, `BeanFactory#getBean("...")`, `ApplicationContext#getBean("...")`
  - **검출 정규식**: 위 위치들의 인자 문자열을 추출 → 동일 값 3회 이상 → 보고
  - **권장 위치 판단**:
    - 빈 등록자(A) + 소비자(B)가 **같은 모듈** → 등록자 클래스 내 `public static final String` 상수
    - **다른 모듈** → `shared/.../constant/{Domain}BeanNameConstants` 신설 권장 (config → config 의존 외관 회피)
  - **출처**: 2026-05-21 commit a6b72daa82 (dexcomAuthorizedClientManager 8회 반복 PR 리뷰 지적) / 후속 0fc9b52338 (shared 모듈 이동)
  - **보고 형식**: `Bean 이름 "{값}"이(가) {파일:라인} 등 {N}곳에 매직 스트링으로 반복. {등록자Class}에 public static final 상수 추출 권장. 모듈 공유 시 shared 위치 검토.`

#### (v1.7) KISA 시큐어코딩 검사

2026-05-21 KISA 점검 일괄 머지(PR #7877~#7885) 경험 반영. 변경 파일에서 다음 패턴을 사전 검출하여 외부 점검에 무더기 발견되는 상황을 차단한다.

**Low 등급 — 디버그·오류 처리**

| 패턴 | 검출 | 권장 수정 |
|------|------|----------|
| 빈 catch (변수명 ignored/ignore/_) | `catch\s*\([^)]+\s+(ignored?|_)\)\s*\{\s*\}` | `log.debug/warn(맥락, e)` 또는 `// 사유 명시` 한국어 주석 |
| 단독 무사유 주석 | catch 블록 안에 `^\s*//\s*(no-op\|무시\|TODO\|fixme)\s*$` 만 존재 | "왜 무시해도 되는가" 한 줄 설명 추가 |
| try 전 null 사전 선언 | `\w+\s+\w+\s*=\s*null;\s*try\s*\{` | `Optional<T>`로 변환 또는 try 안에서 즉시 반환 |

**Medium 등급 — 불변성**

| 패턴 | 검출 | 권장 수정 |
|------|------|----------|
| public static (non-final) | `public\s+static\s+(?!final\b)[A-Za-z<>\[\]]+\s+\w+\s*=` | 불변 가능하면 `final` 추가. mutable 사유 있으면 주석 |

**High 등급 — 보안 알고리즘·시크릿**

| 패턴 | 검출 | 권장 수정 |
|------|------|----------|
| 약한 해시 알고리즘 | `MessageDigest\.getInstance\(\s*"(MD5\|SHA-1\|SHA1)"\s*\)` 또는 상수 값 | SHA-256 이상. CSRF/세션 ID 같은 보안 용도면 즉시 교체 |
| 평문 비밀번호 yml | yml 파일에서 `password:\s*[^$\s]` (`${ENV:-fb}` 형태 아님) | 환경변수 fallback 패턴 적용. 단 `application-example.yml` 같은 샘플 파일은 제외 |

**KEV/Critical 등급 — 의존성**

| 패턴 | 검출 | 권장 수정 |
|------|------|----------|
| build.gradle 의존성 변경 | `build.gradle\\|*.gradle.kts` 변경 시 KISA Critical/KEV 목록 대조 | 즉시 자동 검출은 불가. 변경 보고에 "KISA 목록 대조 권장" 표시 |

**보고 형식 (KISA 검사 결과 섹션)**

검출 시 리뷰 결과에 별도 섹션:

```markdown
### KISA 시큐어코딩 검사

| 등급 | 위치 | 패턴 | 권장 수정 |
|------|------|------|----------|
| Low | api/.../LoggingFilter.java:42 | 빈 catch(ignored) | log.debug + 한국어 사유 |
| High | api/.../CookieUtils.java:33 | MD5 hashAlgorithm 상수 | SHA-256 |
| Medium | .../GroupDirectNoticeList.java:12 | public static (non-final) | final 추가 (불변 가능) |
```

**False positive 회피**
- 빈 catch 패턴: 메인 코드만 검사 (테스트 코드는 expected exception 패턴이라 false positive 多)
- 평문 비번 yml: 파일명에 `example`/`sample`/`local-template` 포함 시 skip
- public static (non-final): 테스트 fixture/mock 클래스(`*Fixture.java`, `Fake*.java`)는 skip

**검출 시 등급**: 권장 개선 (Low/Medium) 또는 필수 수정 (High/KEV/Critical). 일괄 PR 권장.

#### (v1.9) catch 블록 부가 주석 검출

2026-05-21 commit f3b85a79d0 (PghdRecordMapAcl 리뷰 반영) 사례. catch 블록의 **부가 설명 주석**은 log 메시지로 흡수하고 주석은 제거 권장.

```java
// ❌ 검출 — 주석 + log가 동일 정보 중복
} catch (Exception e) {
  // ACL 변환 실패 시 빈 리스트로 fallback — 채널 피드 노출이 중단되지 않도록 방어적으로 처리
  log.error("Failed to get PGHD by recordMapId: {}", pghdRecordMapId, e);
  return Collections.emptyList();
}

// ✅ 권장 — log 메시지에 의도 포함, 주석 제거
} catch (Exception e) {
  log.error("ACL 변환 실패 — recordMapId {} fallback empty list. {}", pghdRecordMapId, e);
  return Collections.emptyList();
}
```

**검출 룰**: catch 블록 안에 `//` 한국어 주석 + `log.*(...)` 호출이 모두 있고, 주석 내용과 log 메시지가 의미 중복이면 → "주석은 제거, log 메시지로 의도 흡수" 권장.

**예외**: catch에 log가 없는데 주석만 있으면 → v1.7 "단독 무사유 주석" 검출 대상 (제거가 아니라 log 추가).

#### (v1.9) @Service 싱글톤 mutable instance field 검출

2026-05-21 commit 2adbd26c26 (KbsmcEhrClient KISA Medium 진단) 사례. `@Service`/`@Component`/`@Repository` 클래스에 mutable instance field가 있으면 모든 요청 간 공유 → 세션 간 값 혼용 위험.

| 패턴 | 검출 | 권장 수정 |
|------|------|----------|
| `@Service` + non-final non-static instance field | 클래스에 `@Service\|@Component\|@Repository` 어노테이션 + `private\s+(?!static\s+)(?!final\s+)[A-Za-z<>\[\]]+\s+\w+;` (필드 선언) | `AtomicReference<record>` 또는 메서드 인수 전달 |

**False positive 회피**: 
- `@Autowired`, `@Value`, `@PersistenceContext` 등으로 주입되는 필드는 Spring이 안전하게 관리 → 제외
- `final` 필드는 immutable이라 안전 → 제외

**보고 형식**:
```markdown
### 싱글톤 동시성 검사 (v1.9)

| 위치 | 필드 | 위험 | 권장 수정 |
|------|------|------|----------|
| KbsmcEhrClient.java:30 | `private String token` | 세션 간 token 혼용 | `AtomicReference<TokenSnapshot>` |
```

#### (v1.9) WebClient 외부 호출 timeout / 재시도 필터 검출

| 패턴 | 검출 | 권장 수정 |
|------|------|----------|
| WebClient 생성에 timeout 누락 | `WebClient\.builder\(\)\..*?\.build\(\)` 전체에 `responseTimeout\|CONNECT_TIMEOUT_MILLIS` 없음 | connect/read timeout 명시 |
| Retry 필터에 4xx 포함 위험 | `Retry\.[a-zA-Z]+\(.*?\)\.filter\(` 본문에 `WebClientResponseException`만 있고 5xx 한정자 없음 | 4xx 영구 오류 제외 필터 |

#### (v1.9) Soft-delete + UNIQUE 충돌 검출

마이그레이션 SQL 파일에서:
| 패턴 | 검출 | 권장 수정 |
|------|------|----------|
| `deleted_at` 컬럼 존재 + 일반 UNIQUE | `(deleted_at|is_deleted)` 컬럼 + `UNIQUE INDEX` (Functional 아님) | MySQL 8.0.13+ Functional Unique Index (`CASE WHEN deleted_at IS NULL THEN col ELSE NULL END`) |

#### (v1.10) Bean Qualifier cross-module 검증 — **3회 재발 방지 우선 룰**

2026-05월 api → 2026-06-16 batch·batch-app (#593) → 2026-06-19 admin (#588). **세 번 반복 재발**. 기존 v1.7 "Bean 이름 매직 스트링" 룰이 있음에도 신규 모듈이 들어올 때마다 `No qualifying bean` 기동 실패가 재현됐다. 룰을 **cross-module 정합성 검증**으로 확장한다.

**증상 패턴**:
```java
// cgm 모듈 (요구자)
@Qualifier(DEXCOM_AUTHORIZED_CLIENT_MANAGER) OAuth2AuthorizedClientManager manager

// batch 모듈 (등록자) — 메서드명 기반 → 상수 미준수
@Bean
public OAuth2AuthorizedClientManager authorizedClientManager(...) { ... }  // ❌ 기동 실패
```

**검사 룰**:
1. `@Qualifier("리터럴문자열")` 사용 시 → 반드시 상수 참조로 변경 요구 (v1.7 강화 재확인)
2. `@Qualifier(CONST)` 형태로 사용된 상수는 → 해당 상수를 **참조하는 모든 애플리케이션 모듈**(api/batch/batch-app/admin 등)에 `@Bean(CONST)` 정의가 있는지 grep 검증
3. 신규 모듈에 OAuth2/WebClient/AuthorizedClientManager 등 shared Bean 관련 Configuration 추가 시 → 기존 Qualifier 상수와 매칭 확인. 메서드명 기반 등록만 있으면 → 사고 재발 경고

**검출 절차 (concrete)**:
```bash
# 1. 변경 파일에서 새 @Bean/@Qualifier 위치 추출
# 2. 상수 이름 확인 (예: DEXCOM_AUTHORIZED_CLIENT_MANAGER)
# 3. 전체 모듈 grep — 이 상수를 @Qualifier로 참조하는 모듈 목록 수집
grep -rn "DEXCOM_AUTHORIZED_CLIENT_MANAGER" --include="*.java"
# 4. 참조 모듈 각각에 대해 @Bean(CONST) 정의 존재 여부 확인
# 5. 하나라도 없으면 → 필수 수정 보고
```

**AUTO FAIL 확장** (기존 v1.7 "Bean 매직 스트링" AUTO FAIL의 sub-case):
- **AUTO FAIL 조건**: 다른 모듈이 `@Qualifier(CONST)`로 참조하는 상수인데, 이 모듈의 `@Bean`이 메서드명 기반(상수 미명시) → 기동 실패 확정 → 리뷰 통과 불가

**보고 형식**:
```markdown
### Bean Qualifier cross-module 검증 (v1.10)

| 위치 | 상수 | 다른 모듈 참조 | 이 모듈 등록 | 등급 |
|------|------|---------------|-------------|------|
| batch/BatchOAuth2Configuration.java:63 | DEXCOM_AUTHORIZED_CLIENT_MANAGER | cgm/DexcomWebClientConfiguration.java:31 | @Bean (메서드명 authorizedClientManager) | **AUTO FAIL** — 기동 실패 예상 |

권장: `@Bean(DEXCOM_AUTHORIZED_CLIENT_MANAGER)` 명시 + 메서드명을 상수와 일치시켜 `dexcomAuthorizedClientManager`로 변경.
```

**False positive 회피**:
- `@Primary`로 표시된 Bean은 Qualifier 없어도 매칭 → skip
- 테스트 코드 `@MockBean` 은 별도 v1.3 룰로 처리

#### (v1.10) 인터페이스 구현체 모듈별 등록 확인

2026-06-18 batch (#597) 사례. `UserDiabetesTypeService` 인터페이스만 있고 batch 모듈에 구현체 Bean 없어 `NoSuchBeanDefinitionException` 기동 실패.

| 패턴 | 검출 | 권장 수정 |
|------|------|----------|
| 인터페이스 주입받는데 모듈 내 구현체 없음 | `@RequiredArgsConstructor` 또는 `@Autowired`로 인터페이스 주입, 해당 모듈 `@ComponentScan` 범위 내 `@Service`/`@Component` 구현체 미존재 | 해당 모듈에 `*ServiceImpl` 등록 or 공용 configuration에 @Bean 노출 |

**검사 절차**: 변경 파일이 새 인터페이스 도입/사용 시 → 인터페이스를 주입받는 모든 애플리케이션 모듈의 스캔 경로에서 `implements {InterfaceName}` 존재 여부 grep. 없으면 필수 수정 보고.

#### (v1.10) 임시 진단 로그 후속 제거 강제

2026-06-23 (#616) 사례. 대시보드 403 원인 진단용 임시 로그를 SecurityConfiguration에 추가한 후 제거 커밋이 없어 기술 부채화.

| 패턴 | 검출 | 권장 수정 |
|------|------|----------|
| 임시 진단 목적 로그 | log 문구 또는 근처 주석에 "임시\|진단\|temp\|diagnostic\|for debug" 키워드 | TODO 태그 + JIRA/이슈 링크 필수 (`// TODO(GLOB-XXX): 원인 확인 후 제거`) |
| 커밋 메시지에 "임시" 명시 | 임시 로그 추가 commit은 message에도 "임시\|diagnostic\|진단용" 포함 | 후속 제거 커밋 추적 가능 |

**리뷰 시 이전 이력 확인**: `git log dev..HEAD -S"임시" -- '*.java'`로 임시 로그가 이전 커밋에서 추가됐는지 확인. 있는데 제거 커밋 없으면 "제거 여부 확인" 알림.

**False positive 회피**: `log.trace/debug` 로 남긴 정상 디버깅 로그 중 "임시" 키워드 미포함은 skip.

#### (v1.8) i18n / Locale 함정 검사

2026-05-15 commit a1a425ecb2 (CodeRabbit 지적) 반영. 변경 파일에서 다음 패턴 검출:

| 패턴 | 정규식 | 권장 수정 | 등급 |
|------|--------|----------|------|
| `toLowerCase()` 단독 | `\.toLowerCase\s*\(\s*\)` | `.toLowerCase(Locale.ROOT)` 명시 | 필수 |
| `toUpperCase()` 단독 | `\.toUpperCase\s*\(\s*\)` | `.toUpperCase(Locale.ROOT)` 명시 | 필수 |
| `String.format` 로케일 누락 (내부 키·로그·API용) | `String\.format\s*\(\s*"` (첫 인자가 Locale 아님) | `String.format(Locale.ROOT, ...)` — 사용자 화면용이면 예외 | 권장 |
| ja 카피에서 `\\n` split | ja 파일 또는 ja Locale 처리 코드에서 `split\s*\(\s*"\\\\n"`  | ja는 줄바꿈 미사용 정책 — split 대상 부적절 | 권장 |

**False positive 회피**: 
- 사용자 화면 출력용 `String.format` (예: i18n 메시지 본문 변환)은 Locale 명시 필요 없음. 단, **내부 키 생성·로그·API 응답 본문**이면 `Locale.ROOT` 강제.
- 판단 어려우면 "검토 권장" 등급으로 보고하고 사용자 결정 받기.

**보고 형식**:

```markdown
### i18n / Locale 함정 검사

| 위치 | 패턴 | 위험 | 권장 수정 |
|------|------|------|----------|
| MyPlanMealMenu.java:47 | `.toLowerCase()` 단독 | 터키 locale에서 점 없는 i 변환 | `.toLowerCase(Locale.ROOT)` |
| RoutineKey.java:23 | `String.format("user-%s", id).toLowerCase()` | 내부 키 — locale 의존 위험 | Locale.ROOT 명시 |
```

#### admin 모듈 검사 (admin/** 변경 시에만)

변경 파일이 admin 모듈이면 01~09 규칙 대신 13~16 규칙을 우선 적용:

- **아키텍처**: 레이어 혼합형 구조가 정상 (4-Tier 위반으로 잘못 판단하지 않을 것)
- **컨트롤러**: `@Controller` + Thymeleaf 뷰 반환 (NOT `@RestController`)
- **템플릿**: `layout:decorate` 사용, URL-View-File 정합 (14 규칙)
- **보안**: `@PreAuthorize` 어노테이션, `AdminHistoryService` 감사 로그 호출 (15 규칙)
- **정적 자산**: 페이지별 JS 파일, sidebar 메뉴 정합 (16 규칙)
- **sidebar 링크 정합**: 컨트롤러 `@GetMapping`과 sidebar 링크가 1:1 대응하는지 대조
- **권한 마이그레이션**: `@PreAuthorize` 추가 시 SUPER_ADMIN permission 마이그레이션 존재 여부 검사

### Step 4. 리뷰 결과 보고

```markdown
## 자체 코드 리뷰 결과

**브랜치**: {현재 브랜치}
**비교 기준**: dev
**커밋 수**: {N}개
**변경 파일**: {N}개

### 필수 수정 (규칙 위반)

| # | 파일:위치 | 위반 규칙 | 내용 | 수정 방향 |
|---|----------|-----------|------|-----------|
| 1 | {path}:{line} | {규칙} | {위반 내용} | {수정 제안} |

### 권장 개선

| # | 파일:위치 | 내용 | 개선 방향 |
|---|----------|------|-----------|
| 1 | {path}:{line} | {개선 내용} | {개선 제안} |

### 검사 통과 항목
- 아키텍처 의존성: OK
- SecurityConstants: OK
- 환경변수 설정: OK
- ...
```

---

## 가드레일

### 하드 가드레일 (절대 위반 불가)

- **코드 변경 금지** — 이 스킬은 **읽기 전용**. 코드를 수정하지 않는다
- **커밋/push 금지** — 리뷰 결과 보고만
- **git stash 금지** — 데이터 유실 방지

### 소프트 가드레일

- 변경되지 않은 기존 코드에 대한 리뷰 최소화 (변경 코드에 집중)
- 사소한 스타일 이슈는 "권장 개선"으로 분류 (필수 수정과 분리)

---

## 자기 검증 체크리스트

리뷰 완료 후 반드시 확인:

1. [ ] **범위 정확성**: dev 이후 변경 코드만 리뷰했는가?
2. [ ] **규칙 참조**: `.claude/rules/` 규칙을 실제로 Read하고 대조했는가?
3. [ ] **환경변수 검사**: 새 프로퍼티 추가 시 4곳 설정 확인했는가?
4. [ ] **SecurityConstants**: 새 API 엔드포인트의 airArray 등록 확인했는가?
5. [ ] **필수/권장 분리**: 위반(필수)과 개선(권장)을 올바르게 분류했는가?
6. [ ] **코드 미변경**: 리뷰만 하고 코드를 수정하지 않았는가?
7. [ ] **구체적 위치**: 위반 항목에 파일명:라인 번호를 포함했는가?
8. [ ] **admin 모듈**: admin 변경이 있으면 13~16 규칙을 Read하고 대조했는가? 4-Tier 위반으로 오판하지 않았는가?
9. [ ] **FQCN 검사**: 변경 파일(메인+테스트)의 코드 본문에 `com.x.y.Z` 형태 패키지 경로가 직접 박혀 있는지 명시적으로 확인했는가? mock 예외(`new x.y.Z()`)와 `.class` 리터럴(`isInstanceOf(x.y.Z.class)`) 점검?
10. [ ] **(v1.6) 확인 vs 가정 분리**: 리뷰 결과의 "수정 방향"이 (a) 규칙 본문에 명시된 것 / (b) 리뷰어 가정·추론 중 어느 것인지 분리 표기했는가? 추론 기반 수정 제안은 "근거: 리뷰어 판단" 명시.
11. [ ] **(v1.6) 변경 의도 파악 근거**: PR 제목·커밋 메시지·연결된 PRD/TDD 중 어느 것을 변경 의도 파악 근거로 썼는지 보고서 헤더에 명시했는가? (의도 미파악 시 리뷰가 표면적 컨벤션 위반 검사에 그칠 위험)
12. [ ] **(v1.7) Bean 이름 매직 스트링 검사**: `@Bean`/`@Qualifier`/`@MockBean(name=...)` 등의 빈 이름 문자열이 변경 파일 군집에서 3회 이상 등장하면 상수화 권장 보고했는가? 모듈 공유 시 shared 위치 검토?
13. [ ] **(v1.7) enum/표준라이브러리 FQCN**: `com.x.y.Z.ENUM_CONST`, `java.lang.reflect.*` 같은 인라인 FQCN을 검사했는가? (#9 FQCN 검사의 확장 패턴)
14. [ ] **(v1.7) KISA 시큐어코딩 검사**: 변경 파일에 빈 catch / MD5·SHA-1 / 평문 비번 yml / public static (non-final) 패턴이 있는지 검사했는가? 검출 시 별도 섹션으로 보고?
15. [ ] **(v1.8) i18n / Locale.ROOT 검사**: `.toLowerCase()` / `.toUpperCase()` 단독 호출, 내부용 `String.format` Locale 누락이 있는지 검사했는가? ja 카피 `\\n` split 등 ja 정책 위반?
16. [ ] **(v1.8) i18n 4파일 동기화 검사**: `message-shared*.properties` 변경 시 4파일(default/ko/en/ja)에 동일 키가 모두 존재하는가? 누락 시 보고?
17. [ ] **(v1.9) catch 부가 주석**: 변경된 catch 블록에 주석+log 의미 중복 검사했는가? 중복이면 "주석 제거, log 메시지로 의도 흡수" 권장?
18. [ ] **(v1.9) 싱글톤 동시성**: 신규/변경된 `@Service`/`@Component`/`@Repository` 클래스에 mutable instance field(`@Autowired`·`final`·`static` 제외) 검출했는가?
19. [ ] **(v1.9) WebClient timeout/retry**: 새 WebClient 생성에 connect/read timeout 명시? Retry 필터가 4xx 제외하는가?
20. [ ] **(v1.9) Soft-delete + UNIQUE**: 변경된 마이그레이션 SQL에 `deleted_at` + 일반 UNIQUE 충돌 검사? Functional Unique Index 권장?
21. [ ] **(v1.10) Bean Qualifier cross-module**: 변경 파일에 새 `@Bean` 또는 `@Qualifier(CONST)`가 있으면, 해당 상수를 참조하는 모든 모듈의 `@Bean(CONST)` 정의 존재 여부를 grep으로 확인했는가? 하나라도 미준수면 AUTO FAIL 보고?
22. [ ] **(v1.10) 인터페이스 구현체 모듈 등록**: 새 인터페이스 주입 코드가 있으면, 해당 모듈 스캔 경로에 구현체가 존재하는지 grep했는가? 없으면 필수 수정 보고?
23. [ ] **(v1.10) 임시 진단 로그**: 변경된 로그 문구 또는 근처 주석에 "임시/진단/temp/diagnostic/for debug" 키워드 있으면 TODO+이슈 링크 강제했는가? 이전 커밋의 임시 로그 잔존 여부도 `git log -S` 로 확인?

---

## 참조 인덱스

| 파일 | 내용 |
|------|------|
| `references/review-checklist.md` | 규칙별 상세 검사 항목 체크리스트 |
| `references/evaluation-rubric.md` | 평가 루브릭 (100점, AUTO FAIL 조건) |
