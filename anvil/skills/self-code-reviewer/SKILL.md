---
name: self-code-reviewer
description: "dev 브랜치 기준으로 변경 코드를 프로젝트 규칙(.claude/rules/)과 대조하여 공통 관점 위반/개선점을 보고하고, 보안·성능·아키텍처 관점 리뷰가 필요하면 각 관점 스킬로 안내하는 자체 코드 리뷰 스킬. 코드 리뷰, 품질 검사, self review, 규칙 준수 검사 요청 시 사용. Use proactively when the user asks for code review, quality check, or rule compliance review."
version: "2.0"
last-modified: "2026-07-09"
changelog: |
  v2.0 — 2026-07-09 관점별 리뷰 스킬 3개 분리 사이클에서 이관 완료:
    - KISA 시큐어코딩 섹션 → java-secure-coding-reviewer v0.1
    - WebClient timeout/재시도·싱글톤 mutable·Soft-delete UNIQUE → java-performance-reviewer v0.1
    - FQCN 인라인·Bean Qualifier cross-module·인터페이스 구현체 모듈 → java-architecture-reviewer v0.1
    잔존은 공통 룰(@Profile 문법·광범위 catch·Session 오염·입력 형식 검증·임시 로그·catch 부가 주석·i18n Locale) + java-composite-reviewer 오케스트레이션 안내. 489줄 → ~300줄 슬림화.
  v1.11 — 2026-07-09 7월 pasta 사고 4건 검출 룰: (1) Spring @Profile 문법 &&→& AUTO FAIL — GLOB-566 PricingCacheRedisConfig / GLOB-567 PricingAdminConfiguration 두 곳 동일 오류 재발(#49c513f596, #0df4473548). (2) DataIntegrityViolationException 광범위 catch 검출 — 미션 뱃지 사고(#633) CodeRabbit 피드백 반영. (3) Hibernate Session 오염 재조회 검출 — unique violation catch 이후 같은 세션 재조회 AUTO FAIL. (4) 입력 형식 검증 누락 검출 — #623 사번 형식 검증 재발 방지.
  v1.10 — 2026-07-02 6월 pasta 사고 3건 흡수: Bean Qualifier cross-module 3회 재발 방지 / 인터페이스 구현체 모듈별 등록 확인 / 임시 진단 로그 후속 제거 강제.
  v1.9 — 2026-05-21 이번 주 추가 패턴: catch 부가 주석 검출 / @Service 싱글톤 mutable / WebClient timeout·재시도 / Soft-delete UNIQUE.
  v1.8 — Locale.ROOT 누락 검출.
  v1.7 — Bean 매직 스트링 + KISA 시큐어코딩 섹션.
  v1.6 — blueprint v2.0.
---

# self-code-reviewer — 자체 코드 리뷰 스킬 (공통 룰 + 관점 오케스트레이션)

> 프로젝트 규칙: `.claude/rules/` (인덱스: `00-rules-index.md`)

**v2.0부터**: 이 스킬은 **도메인 무관 공통 룰**만 검사한다. 보안·성능·아키텍처 관점은 관점 스킬로 위임한다.

---

## 관점 리뷰 오케스트레이션 (v2.0)

리뷰 요청 시나리오별 진입점:

| 시나리오 | 처리 |
|---------|------|
| **공통 룰만** (문법·컨벤션 등 자체 스코프) | 이 스킬이 직접 실행 |
| **전체 리뷰** (관점 지정 없음) | **`java-composite-reviewer` 에이전트**로 위임 권장 |
| **특정 관점만** | 해당 관점 스킬 직접 호출 안내 |
| **관점 애매** | `java-composite-reviewer`가 자동 판단 |

### 관점 스킬 정본 위치

| 관점 | 스킬 | 스코프 |
|------|------|--------|
| 보안 | `skills/java-secure-coding-reviewer/` | KISA·OWASP·PII·시크릿·CVE |
| 성능 | `skills/java-performance-reviewer/` | N+1·JPA·캐시·트랜잭션·리소스·GC |
| 아키텍처·컨벤션 | `skills/java-architecture-reviewer/` | 4-Tier·Bean 관리·모듈 관계·pasta-rules |
| 복합 | `agents/java-composite-reviewer/` | 4개 스킬 조합 오케스트레이터 |

---

## Phase 0. 사전 확인

1. **현재 브랜치 확인**: `git branch --show-current` — dev/main이면 리뷰 대상 없음, 안내
2. **비교 기준 확인**: 기본 `dev`. 사용자가 다른 브랜치를 지정하면 해당 브랜치 사용
3. **변경 범위 파악**: `git log dev..HEAD --oneline` + `git diff dev...HEAD --stat`
4. **변경 파일 없으면**: 리뷰 대상 없음 안내
5. **admin 모듈 포함 여부**: 변경 파일에 `admin/` 경로가 있는가? → YES면 13~16 규칙 추가 로드

---

## 핵심 규칙

### 리뷰 대상

- `dev` 브랜치 이후 **추가·변경된 코드만** 리뷰
- 변경되지 않은 기존 코드는 리뷰하지 않음
- 삭제된 코드는 "삭제가 적절한지"만 확인

### 리뷰 관점 (우선순위 순, v2.0 공통 스코프)

| 우선순위 | 관점 | 설명 |
|---------|------|------|
| 1 | **하드 가드레일 위반** | AUTO FAIL 대상 (@Profile 문법·Session 오염 재조회 등) |
| 2 | **컨벤션 위반** | 로깅 형식·PII 마스킹·i18n Locale·입력 검증 |
| 3 | **설정 누락** | 환경변수 4곳·SecurityConstants·마이그레이션 |
| 4 | **품질 개선** | catch 부가 주석·임시 로그 부채·가독성 |

> 아키텍처·의존성·Bean·FQCN 위반은 `java-architecture-reviewer` 담당.
> 보안·PII·시크릿·KISA는 `java-secure-coding-reviewer` 담당.
> N+1·트랜잭션·WebClient·싱글톤은 `java-performance-reviewer` 담당.

---

## 실행 프로토콜

### Step 1. 변경 범위 수집

```bash
git log dev..HEAD --oneline
git diff dev...HEAD --stat
git diff dev...HEAD -- {path}
```

### Step 2. 규칙 로드

`.claude/rules/` 하위 규칙 파일을 Read 도구로 참조:

| 규칙 파일 | 검사 대상 |
|-----------|-----------|
| `06-exception-handling-convention.md` | MoneyballException, ExceptionConstants |
| `07-general-project-convention.md` | 네이밍, 로깅, Import, 환경변수, DB 마이그레이션 |
| `08-test-code-convention.md` | TDD, Fake/Spy, 계층별 테스트 |
| `09-guardrails.md` | Testcontainers, 커밋 보호, 마이그레이션 보호 |
| `12-multipart-image-validation.md` | 이미지 업로드 검증 |
| `13-admin-module-overview.md` | admin 모듈 구조 (admin/** 변경 시) |
| `14-admin-thymeleaf-layout-convention.md` | Thymeleaf 레이아웃 정합 (admin/** 변경 시) |
| `15-admin-security-history-convention.md` | @PreAuthorize, AdminHistory (admin/** 변경 시) |
| `16-admin-static-assets-convention.md` | 페이지별 JS, sidebar (admin/** 변경 시) |

> 아키텍처 계열 규칙(01·02·03·04·05·19)은 `java-architecture-reviewer`가 참조. 이 스킬은 직접 대조하지 않음.

### Step 3. 공통 검사 항목

- **환경변수 검사**: `application.yml`에 `${env.KEY}` 추가 시 → `application-jp-dev/stg/prd.yml`에 `${KEY}` 존재 확인
- **시큐리티 경로 검사**: 새 API 엔드포인트 추가 시 → `SecurityConstants.airArray` 등록 확인
- **마이그레이션 검사**: `obesity/` 하위 기존 파일 수정/삭제 여부 확인
- **로깅 형식 검사**: `[ClassName.methodName]` 접두사 사용 여부, 민감정보 마스킹 여부 (상세 PII는 `java-secure-coding-reviewer`)
- **재시도 로직 검증**: 재시도 로직이 있으면 실제 catch/retry가 동작하는지 로직 흐름 검증
- **JPQL 페이지네이션 검사**: `JOIN FETCH` + `Page` 사용 시 `countQuery` 분리 여부
- **페이지네이션 필터 파라미터 검사**: 페이지네이션 링크에 현재 필터 파라미터가 모두 포함되었는지

#### (v1.9) catch 블록 부가 주석 검출

catch 블록의 **부가 설명 주석**은 log 메시지로 흡수하고 주석은 제거 권장.

```java
// ❌ 검출 — 주석 + log가 동일 정보 중복
} catch (Exception e) {
  // ACL 변환 실패 시 빈 리스트로 fallback
  log.error("Failed to get PGHD by recordMapId: {}", pghdRecordMapId, e);
  return Collections.emptyList();
}

// ✅ 권장 — log 메시지에 의도 포함, 주석 제거
} catch (Exception e) {
  log.error("ACL 변환 실패 — recordMapId {} fallback empty list. {}", pghdRecordMapId, e);
  return Collections.emptyList();
}
```

**검출 룰**: catch 블록 안에 `//` 한국어 주석 + `log.*(...)` 호출이 모두 있고 의미 중복이면 → "주석 제거, log로 의도 흡수" 권장.

#### (v1.10) 임시 진단 로그 후속 제거 강제

2026-06-23 (#616) 사례. 임시 진단 로그가 제거 커밋 없이 기술 부채화.

| 패턴 | 검출 | 권장 수정 |
|------|------|----------|
| 임시 진단 로그 | log 문구/주석에 "임시\|진단\|temp\|diagnostic\|for debug" 키워드 | TODO 태그 + JIRA/이슈 링크 필수 (`// TODO(GLOB-XXX): 원인 확인 후 제거`) |
| 커밋 메시지 표기 | 임시 로그 추가 commit은 message에도 "임시\|diagnostic" 포함 | 후속 제거 커밋 추적 가능 |

**이전 이력 확인**: `git log dev..HEAD -S"임시" -- '*.java'` 로 임시 로그가 이전 커밋에서 추가됐는지 확인. 있는데 제거 커밋 없으면 "제거 여부 확인" 알림.

#### (v1.11) Spring `@Profile` 문법 오류 `&&` → `&` — **AUTO FAIL**

2026-07-07 GLOB-566 / GLOB-567 두 곳 동일 실수 재발 (#49c513f596, #0df4473548). Spring `@Profile`은 표현식 문법상 **단일 `&`만 지원** — `&&`는 프로파일 매칭 실패로 Bean 미로드. `||`(or)는 지원.

| 패턴 | 검출 | 등급 |
|------|------|------|
| `@Profile("... && ...")` | `grep -rn '@Profile.*&&' --include='*.java' src/` 매칭 시 | **AUTO FAIL** |

**허용 예**: `@Profile("dev")`, `@Profile("!prod")`, `@Profile("dev & !test")`, `@Profile("dev | stage")`

#### (v1.11) DataIntegrityViolationException 광범위 catch 검출

미션 뱃지 사고(#633) CodeRabbit 피드백. 광범위 catch는 unique 위반 외 NOT NULL/FK 위반 결함도 은폐. SQL 에러코드로 좁혀 판별 필수.

| 패턴 | 검출 | 권장 수정 |
|------|------|----------|
| 광범위 catch + 삼킴 | `catch\s*\(\s*(DataIntegrityViolationException\|ConstraintViolationException\|PersistenceException)` 블록에서 로깅만 하고 반환 | SQL 에러코드로 좁혀 판별 |

**통과 예**:
```java
} catch (DataIntegrityViolationException e) {
  if (e.getCause() instanceof SQLException sql && sql.getErrorCode() == 1062) {
    return existing;  // ER_DUP_ENTRY만 흡수
  }
  throw e;  // 나머지는 재발
}
```

**False positive 회피**: catch 블록에서 `getErrorCode()`/`getSQLState()`/`instanceof SQLException` 형태로 좁혀 판별하면 skip.

#### (v1.11) Hibernate Session 오염 재조회 검출 — **AUTO FAIL 후보**

미션 뱃지 사고(#633). unique constraint violation catch 이후 **같은 Session/EntityManager로 재조회**하면 `AssertionFailure` + 상위 트랜잭션 롤백 유발. 한국(moneyball) 재발 패턴.

| 패턴 | 검출 | 등급 |
|------|------|------|
| unique violation catch 안 재조회 | catch 블록 안에 `entityManager\.\|session\.\|.*Repository\.\(find\|get\|exists\)` 조회 호출 | **AUTO FAIL** |

**권장 수정**: 예외 처리는 최상단(트랜잭션 경계 밖)에서만. catch 블록 내 재조회 필요 시 **`@Transactional(propagation = REQUIRES_NEW)` 별도 트랜잭션 명시** (java-spring-coder v1.11-A 하드 가드레일 정본 참조).

**False positive 회피**: catch 안에서 `throw`/`return`/로깅만 하면 skip. 재조회 메서드에 REQUIRES_NEW 명시되어 있으면 skip.

#### (v1.11) 입력 형식 검증 누락 검출

병원/그룹 관리자 등록 사고(#623). 사번 형식 검증 어노테이션 누락 → 잘못된 데이터 통과.

| 패턴 | 검출 | 권장 수정 |
|------|------|----------|
| 형식 제약 필드 검증 누락 | `@RequestParam`/`@RequestBody` DTO의 `employeeId`/`phoneNumber`/`email`/`businessNumber` 등 필드에 `@Pattern`/`@Email`/`@Size` 없음 | 프로젝트 표준 formatting 상수 참조 |
| 검증 실패 메시지 4로케일 미정의 | `@Pattern(message="{key}")` message 키가 `message-shared*.properties` 4파일(default/ko/en/ja)에 모두 정의? | 누락 로케일 파일 추가 (tolgee 스킬 연계) |

**False positive 회피**: 내부용 DTO·배치 파라미터는 skip. 컨트롤러 진입점 DTO만 대상.

#### (v1.8) i18n / Locale 함정 검사

| 패턴 | 정규식 | 권장 수정 | 등급 |
|------|--------|----------|------|
| `toLowerCase()` 단독 | `\.toLowerCase\s*\(\s*\)` | `.toLowerCase(Locale.ROOT)` 명시 | 필수 |
| `toUpperCase()` 단독 | `\.toUpperCase\s*\(\s*\)` | `.toUpperCase(Locale.ROOT)` 명시 | 필수 |
| `String.format` 로케일 누락 (내부 키·로그·API용) | `String\.format\s*\(\s*"` (첫 인자가 Locale 아님) | `String.format(Locale.ROOT, ...)` | 권장 |
| i18n 4파일 동기화 | `message-shared*.properties` 변경 시 4파일(default/ko/en/ja) 동일 키 존재 | 누락 로케일 파일 추가 |

**False positive 회피**: 사용자 화면 출력용 `String.format`은 Locale 명시 필요 없음. 내부 키·로그·API 응답 본문이면 `Locale.ROOT` 강제.

#### admin 모듈 검사 (admin/** 변경 시에만)

- **컨트롤러**: `@Controller` + Thymeleaf 뷰 반환 (NOT `@RestController`)
- **템플릿**: `layout:decorate` 사용, URL-View-File 정합 (14 규칙)
- **보안**: `@PreAuthorize` 어노테이션, `AdminHistoryService` 감사 로그 호출 (15 규칙)
- **정적 자산**: 페이지별 JS 파일, sidebar 메뉴 정합 (16 규칙)
- **sidebar 링크 정합**: 컨트롤러 `@GetMapping`과 sidebar 링크 1:1 대응
- **권한 마이그레이션**: `@PreAuthorize` 추가 시 SUPER_ADMIN permission 마이그레이션 존재 확인

### Step 4. 리뷰 결과 보고

```markdown
## 자체 코드 리뷰 결과

**브랜치**: {현재 브랜치}
**비교 기준**: dev
**커밋 수**: {N}개 / **변경 파일**: {N}개
**관점 스코프**: 공통 룰만 (보안/성능/아키텍처 관점은 각 관점 스킬 또는 composite 에이전트 사용)

### 필수 수정 (규칙 위반)

| # | 파일:위치 | 위반 규칙 | 내용 | 수정 방향 |
|---|----------|-----------|------|-----------|

### 권장 개선

| # | 파일:위치 | 내용 | 개선 방향 |
|---|----------|------|-----------|

### 관점 리뷰 필요 안내 (변경 성격 기반)

- 보안 관점 검토 권장: {yes/no} — `java-secure-coding-reviewer`
- 성능 관점 검토 권장: {yes/no} — `java-performance-reviewer`
- 아키텍처 관점 검토 권장: {yes/no} — `java-architecture-reviewer`
- 전체 통합 리뷰 원하면: `java-composite-reviewer` 에이전트
```

---

## 가드레일

### 하드 가드레일 (절대 위반 불가)

- **코드 변경 금지** — 이 스킬은 **읽기 전용**. 코드를 수정하지 않는다
- **커밋/push 금지** — 리뷰 결과 보고만
- **git stash 금지** — 데이터 유실 방지
- **스코프 침범 금지** — 보안·성능·아키텍처 관점 룰은 이 스킬에서 검사하지 않음. 각 관점 스킬 위임 안내

### 소프트 가드레일

- 변경되지 않은 기존 코드에 대한 리뷰 최소화 (변경 코드에 집중)
- 사소한 스타일 이슈는 "권장 개선"으로 분류
- 관점 리뷰 필요성 판단 시 근거(파일 종류·변경 성격) 명시

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
8. [ ] **admin 모듈**: admin 변경이 있으면 13~16 규칙을 Read하고 대조했는가?
9. [ ] **확인 vs 가정 분리**: "수정 방향"이 규칙 본문 명시 / 리뷰어 추론 중 어느 것인지 분리 표기했는가?
10. [ ] **변경 의도 파악 근거**: PR 제목·커밋 메시지·연결된 PRD/TDD 중 무엇을 근거로 썼는지 보고서 헤더에 명시했는가?
11. [ ] **(v1.9) catch 부가 주석**: 변경된 catch 블록에 주석+log 의미 중복 검사했는가?
12. [ ] **(v1.10) 임시 진단 로그**: 변경된 로그·주석에 "임시/진단/temp/diagnostic" 키워드 있으면 TODO+이슈 링크 강제? 이전 커밋의 임시 로그 잔존도 `git log -S`로 확인?
13. [ ] **(v1.11) `@Profile` && 문법**: `grep -rn '@Profile.*&&'` 매칭 검사 — 매칭 시 AUTO FAIL?
14. [ ] **(v1.11) DataIntegrityViolationException 광범위 catch**: SQL 에러코드로 좁혀 판별하는지 확인?
15. [ ] **(v1.11) Hibernate Session 오염**: unique/제약 위반 catch 안에 조회 호출 있으면 AUTO FAIL 보고? REQUIRES_NEW 격리 요구?
16. [ ] **(v1.11) 입력 형식 검증 누락**: 컨트롤러 DTO 도메인 특화 식별자 필드에 `@Pattern`/`@Email`/`@Size`? 4로케일 메시지 정의?
17. [ ] **(v1.8) i18n / Locale.ROOT**: `.toLowerCase()`/`.toUpperCase()` 단독, 내부용 `String.format` Locale 누락?
18. [ ] **(v1.8) i18n 4파일 동기화**: `message-shared*.properties` 변경 시 4파일(default/ko/en/ja) 동일 키 모두 존재?
19. [ ] **(v2.0) 관점 스코프 준수**: 보안·성능·아키텍처 관점 룰을 이 스킬에서 검사하지 않았는가? 필요 시 관점 스킬 안내했는가?
20. [ ] **(v2.0) 관점 리뷰 필요성 안내**: 변경 성격 기반으로 어느 관점 스킬 검토가 필요한지 보고서에 명시했는가?

---

## 참조 인덱스

### 관점 스킬 (v2.0 위임 대상)

| 컴포넌트 | 위치 | 스코프 |
|---------|------|--------|
| java-secure-coding-reviewer | `skills/java-secure-coding-reviewer/SKILL.md` | KISA·OWASP·PII·시크릿·CVE |
| java-performance-reviewer | `skills/java-performance-reviewer/SKILL.md` | N+1·JPA·캐시·트랜잭션·리소스·GC |
| java-architecture-reviewer | `skills/java-architecture-reviewer/SKILL.md` | 4-Tier·Bean 관리·모듈 관계·pasta-rules |
| java-composite-reviewer | `agents/java-composite-reviewer/java-composite-reviewer.md` | 4개 스킬 조합 오케스트레이터 |

### 이 스킬 내부

| 파일 | 내용 |
|------|------|
| `references/review-checklist.md` | 규칙별 상세 검사 항목 체크리스트 |
| `references/evaluation-rubric.md` | 평가 루브릭 (100점, AUTO FAIL 조건) |
