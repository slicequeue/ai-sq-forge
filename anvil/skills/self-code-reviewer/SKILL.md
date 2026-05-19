---
name: self-code-reviewer
description: "dev 브랜치 기준으로 변경 코드를 프로젝트 규칙(.claude/rules/)과 대조하여 위반/개선점을 보고하는 자체 코드 리뷰 스킬. 코드 리뷰, 품질 검사, self review, 규칙 준수 검사 요청 시 사용. Use proactively when the user asks for code review, quality check, or rule compliance review."
version: "1.6"
last-modified: "2026-05-19"
changelog: "v1.6: blueprint v2.0 패턴 이식 — 자기 검증 v2.0 확장(확인 vs 가정 분리, 변경 범위 추론 근거 명시). 본질이 분석형이라 Phase 1.5 현황 파악은 기존 Step 1(git log/diff)로 충족. | v1.5 — FQCN 직접 사용 검출 항목 추가 (메인+테스트 모두). PR #527 자체 리뷰 누락 사례 반영. v1.4 — Insights 피드백 반영: Architecture Boundary 검사 강화"
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
  - **검사 룰 (개념)**: 정규식 `\b[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+\.[A-Z][A-Za-z0-9_]*\b` 매칭이 import 문이 아닌 코드 본문에 등장하는지
  - **검사 제외**: 어노테이션 인자 문자열, SpEL 표현식, JPQL/SQL 쿼리 문자열, 로그 메시지 본문은 false positive — 무시
  - **검출 시 등급**: 필수 수정 (07-general-project-convention "Explicit Imports" 명시 위반). 테스트 파일도 동일 적용 — "테스트라 한 번만 쓰니까"는 면죄부 아님

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

---

## 참조 인덱스

| 파일 | 내용 |
|------|------|
| `references/review-checklist.md` | 규칙별 상세 검사 항목 체크리스트 |
| `references/evaluation-rubric.md` | 평가 루브릭 (100점, AUTO FAIL 조건) |
