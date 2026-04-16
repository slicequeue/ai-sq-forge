---
name: self-code-reviewer
description: "dev 브랜치 기준으로 변경 코드를 프로젝트 규칙(.claude/rules/)과 대조하여 위반/개선점을 보고하는 자체 코드 리뷰 스킬. 코드 리뷰, 품질 검사, self review, 규칙 준수 검사 요청 시 사용. Use proactively when the user asks for code review, quality check, or rule compliance review."
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
| 1 | **가드레일 위반** | 하드 가드레일 위반 여부 (즉시 수정 필요) |
| 2 | **아키텍처 위반** | 의존성 방향, Domain 순수성, Repository 패턴 |
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

#### admin 모듈 검사 (admin/** 변경 시에만)

변경 파일이 admin 모듈이면 01~09 규칙 대신 13~16 규칙을 우선 적용:

- **아키텍처**: 레이어 혼합형 구조가 정상 (4-Tier 위반으로 잘못 판단하지 않을 것)
- **컨트롤러**: `@Controller` + Thymeleaf 뷰 반환 (NOT `@RestController`)
- **템플릿**: `layout:decorate` 사용, URL-View-File 정합 (14 규칙)
- **보안**: `@PreAuthorize` 어노테이션, `AdminHistoryService` 감사 로그 호출 (15 규칙)
- **정적 자산**: 페이지별 JS 파일, sidebar 메뉴 정합 (16 규칙)

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

---

## 참조 인덱스

| 파일 | 내용 |
|------|------|
| `references/review-checklist.md` | 규칙별 상세 검사 항목 체크리스트 |
| `references/evaluation-rubric.md` | 평가 루브릭 (100점, AUTO FAIL 조건) |
