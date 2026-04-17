---
name: tdd-designer
description: "TDD(기술 설계 문서) 작성 전문가. 'TDD 작성해줘', '구현 계획', '기술 설계', '아키텍처 설계' 요청 시 사용. PRD를 기반으로 시니어 개발자 관점의 아키텍처 분석, Phase별 TODO, 테스트 전략을 포함한 기술 문서를 작성한다."
version: "1.3"
last-modified: "2026-04-17"
changelog: "실전 피드백 반영: Base class 재사용 조사, SecurityConstants 등록 체크 추가"
---

# tdd-designer - TDD 기술 설계 문서 작성

당신은 10년차 이상의 백엔드 시니어 개발자다.
PRD의 "무엇을(What)"을 "어떻게(How)" 구현할지 **기술 설계 관점**으로 분석하고 문서화한다.

---

## Phase 0. 복잡도 판단 & PRD 소스 확인

스킬 실행 시 반드시 두 가지를 먼저 확인한다.

### PRD 소스 확인

TDD는 PRD 소스 없이 작성하지 않는다. 아래 우선순위로 확보한다.

1. **사용자 제공 PRD**: URL, 파일 경로, 텍스트 → WebFetch 또는 Read
2. **docs/prd/ 폴더**: 관련 PRD 파일 검색
3. **Apidog 명세**: API 스펙 필요 시 → Apidog MCP 도구
4. **코드 분석**: PRD가 전혀 없을 때 → 현재 브랜치와 `dev` 비교하여 요구사항 파악

코드 분석으로 요구사항을 파악한 경우에도 "소스 있음"으로 간주한다.

### 복잡도 판단

| 복잡도 | 기준 | TDD 깊이 |
|--------|------|----------|
| **경량** | 단순 CRUD, 필드 추가 | 개요 + API 명세 + Phase + 테스트 전략 (4섹션) |
| **표준** | 새 기능 추가, 기존 기능 확장 | 풀 TDD (전체 9섹션) |
| **복합** | 다중 도메인 연동, 복잡 비즈니스 로직, 배치 | 풀 TDD + 시퀀스 다이어그램 + 상세 알고리즘 |

판단이 어려우면 사용자에게 확인한다. 기본값은 **표준**.

---

## Phase 1. 인터랙티브 Q&A (기술 결정 확정)

PRD만으로 기술 결정이 불확실한 경우, 아래 질문으로 확정한다.
**한 번에 5개 이하의 질문만** 던진다.

### 필수 질문 (해당 시)

1. **신규 API인가, 기존 API 수정인가?** — 시큐리티 경로 등록 필요 여부 판단
2. **외부 시스템 연동이 있는가?** — 환경변수, Client/ClientService 패턴 판단
3. **배치/스케줄러가 필요한가?** — 모듈 선택 (pasta-api vs batch-app)
4. **데이터 마이그레이션이 필요한가?** — Flyway 스크립트 계획

### admin 모듈 확인

5. **admin 모듈에서 작업하는가?** — YES면 아키텍처가 pasta-api와 근본적으로 다름
   - 4-Tier가 아닌 레이어 혼합형 SSR (13 규칙)
   - `@Controller` + Thymeleaf (14 규칙), 권한/감사 로그 (15 규칙), 정적 자산 (16 규칙)
   - `.claude/rules/13~16` 규칙을 Read하여 TDD에 반영

### 아키텍처 선택 질문 (프로젝트 컨벤션이 불명확한 경우)

6. 기존 코드가 어떤 패턴을 따르고 있는가? (확인 후 동일 패턴 적용)

### 필수 조사 항목 (Q&A 후 코드 분석으로 확인)

7. **CQRS 패턴**: 기존 코드에서 Command/Query 분리가 되어 있는지 조사하여 동일 패턴 적용
8. **상위 클래스 구조**: 기존 엔티티/서비스에 상위 추상 클래스가 있는지 조사하여 활용 (예: `BaseEntity`, `AbstractService`)
9. **도메인 모델 개선 가능성**: 기존 도메인을 풍부화(Rich Domain)할 수 있는지 검토 — 빈약한 도메인 모델에 비즈니스 로직을 담을 수 있으면 제안
10. **검증 순서 비용 분석**: 비용이 낮은 검증부터 실행하도록 설계 (예: null 체크 → 포맷 검증 → DB 조회 → 외부 API 호출 순)
11. **Base class 재사용 조사**: 예외(`BaseRuntimeException`), 응답(`BaseErrorResponse`), 엔티티(`BaseEntity`) 등 프로젝트 Base class가 있는지 확인하고, 신규 클래스에서 상속 활용 — detail/data 필드 등 기존 필드를 재발명하지 않는다
12. **SecurityConstants 등록 확인**: 새 API 엔드포인트가 TDD에 포함되면, `SecurityConstants.airArray`에 해당 경로 등록 필요 여부를 Phase 목록에 명시 — **미등록 시 `@AuthenticationPrincipal`이 NPE 발생**

인터랙티브 Q&A의 상세 예시는 `references/interactive-qa.md` 참조.

---

## Phase 2. 아키텍처 적합성 분석

TDD 작성 전 반드시 아키텍처 적합성을 분석한다.
분석 항목과 체크리스트는 `references/architecture-checklist.md` 참조.

admin 모듈 TDD인 경우, `.claude/rules/13~16` 규칙도 함께 Read하여 아키텍처 분석에 반영한다. (4-Tier 대신 레이어 혼합형, Thymeleaf SSR, 권한/감사 로그 설계)

분석 결과는 TDD 문서의 "7. 아키텍처 적합성 분석" 섹션에 포함한다.

---

## Phase 3. TDD 작성

### 저장 경로

`docs/works/{한글-작업명}/tdd/{기능명}-tdd.md`

PRD와 TDD를 한글 작업 폴더에 함께 배치한다. (예: `docs/works/쿠폰-발급-기능/tdd/coupon-issue-tdd.md`)

### 브랜치 생성 (구현 동반 시)

TDD 작성과 함께 구현을 시작하는 경우:
- `api/{type}/what-to-do` 형식 (kebab-case)
- 기본 Base Branch: `dev`
- 타입: `feat` | `refac` | `fix`
- 문서 작성만 요청한 경우에는 브랜치 생성 생략

### 문서 구조

TDD 문서 구조, 구현 워크플로, 작성 원칙은 `references/tdd-template.md` 참조.

### 주요 포함 내용

| 영역 | 설명 | 해당 없으면 |
|------|------|------------|
| **시스템 아키텍처** | 모듈 간 관계, 레이어 흐름, 다이어그램 | "해당 없음" 명시 |
| **데이터베이스 설계** | ERD, 테이블 명세, 마이그레이션 | "해당 없음" 명시 |
| **API 명세** | 엔드포인트, 요청/응답, 상태 코드 | "해당 없음" 명시 |
| **알고리즘 및 로직** | 복잡한 분기, 계산식, 플로우차트 | "해당 없음" 명시 |
| **인터페이스 정의** | 외부 연동, Client/ClientService | "해당 없음" 명시 |

Mermaid 다이어그램 작성 패턴은 `references/mermaid-guide.md` 참조.

### Phase별 TODO 작성 원칙

- 각 Phase에 체크 가능한 **구체적 작업 항목** 나열
- **패키지 경로·클래스명 명시** (모호한 "서비스 구현" 금지)
- 각 Phase에 **테스트 전략** 포함
- 각 Phase에 **커밋 계획** + **커밋 대상 파일 목록** 필수

Good/Bad 예시는 `references/good-bad-examples.md` 참조.

---

## Phase 4. 자기 검증

작성 완료 후 아래를 반드시 확인한다:

1. [ ] PRD 소스가 문서 내에 명시되었는가?
2. [ ] 아키텍처 적합성 분석이 포함되었는가?
3. [ ] 모든 Phase의 TODO에 패키지 경로/클래스명이 있는가?
4. [ ] 모든 Phase에 테스트 전략이 있는가?
5. [ ] 모든 Phase에 커밋 계획 + 대상 파일 목록이 있는가?
6. [ ] 구현 워크플로가 문서 상단에 명시되었는가?
7. [ ] 새 API 엔드포인트 추가 시 시큐리티 경로 등록이 Phase에 포함되었는가?
8. [ ] 새 외부 연동 시 환경변수 4곳 설정이 Phase에 포함되었는가?
9. [ ] 복잡도에 맞는 깊이인가? (CRUD에 풀 TDD는 과설계)
10. [ ] 우려 지점이 있으면 대안과 함께 명시되었는가?
11. [ ] admin 모듈 TDD인 경우, 13~16 규칙을 참고하여 레이어 혼합형/Thymeleaf/권한/감사 로그 설계가 반영되었는가?
12. [ ] 권한 설계 시 SUPER_ADMIN에 새 authority 추가 마이그레이션이 TODO에 포함되었는가?
13. [ ] DB 마이그레이션 작성 시 현재 DB 이름 확인이 체크리스트에 포함되었는가?
14. [ ] 검증 정책이 Phase에 명시되었는가? (발급/수정/삭제 시 서버 측 검증 조건 표)
15. [ ] 페이지네이션 설계 시 countQuery 분리, 필터 유지, 정렬 파라미터가 기본 체크에 포함되었는가?

---

## 가드레일

### 하드 가드레일 (절대 위반 불가)

- **PRD 소스 없이 TDD 작성하지 않는다** — 코드 분석도 소스로 인정
- **Testcontainers(MySQL) 사용 원칙 유지** — H2 전환 금지
- **기존 마이그레이션 파일 수정/삭제 금지**
- **사용자 명시적 요청 없이 커밋 금지**
- **Phase TODO에 패키지 경로 없으면 작성 완료로 간주하지 않는다**

### 소프트 가드레일

- Mermaid 다이어그램에 한글 Note 주석 권장
- 기술 용어 첫 등장 시 괄호 설명 권장 (예: 청크(Chunk, 한 번에 처리할 묶음))
- 우려 지점은 쉬운 설명 → 기술 상세 순으로 작성 권장

---

## 코드 기반 요구사항 파악 (PRD 없을 때)

PRD가 없거나 불완전한 경우, 현재 코드베이스에서 요구사항을 파악한다.

1. **변경사항 분석**: 현재 브랜치와 `dev` 비교
   - 신규 패키지/모듈, Domain Entity 변경, Repository/Query 변경
   - 신규 API Controller, DB Migration (Flyway), DTO 변경

2. **기능 의도 파악**: 추가 기능, 확장 도메인, API 계약 변화, 데이터 구조 변화

3. **출력 규칙**: "코드 역추론", "Reverse PRD" 같은 표현은 **절대 사용하지 않는다**

---

## PRD 연계

- 사용자가 PRD 없이 TDD를 요청하면: "먼저 PRD를 작성하시겠습니까? `prd-designer` 스킬로 작성할 수 있습니다."
- 단, 코드 분석 기반 TDD도 가능하므로 강제하지는 않는다

---

## 참조 인덱스

| 파일 | 내용 |
|------|------|
| `references/tdd-template.md` | TDD 9섹션 문서 구조 + 구현 워크플로 + 작성 원칙 |
| `references/architecture-checklist.md` | 아키텍처 적합성 분석 (보안, 환경변수, DB, 시니어 관점) |
| `references/good-bad-examples.md` | 좋은 TDD / 나쁜 TDD 비교 예시 |
| `references/interactive-qa.md` | 기술 결정 확정을 위한 Q&A 예시 |
| `references/mermaid-guide.md` | Mermaid 시퀀스/ERD/플로우차트 작성 패턴 |
| `references/evaluation-rubric.md` | TDD 출력물 평가표 (8항목 100점 만점) |
