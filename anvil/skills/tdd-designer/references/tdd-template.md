# TDD 문서 구조 & 구현 워크플로 & 작성 원칙

- [문서 구조](#문서-구조)
- [구현 워크플로](#구현-워크플로)
- [작성 원칙](#작성-원칙)
- [경량 TDD 구조](#경량-tdd-구조)
- [참조 규칙 인덱스](#참조-규칙-인덱스)

---

## 문서 구조

```markdown
# [기능명] TDD (Technical Design Document)

## 1. 개요
- 연관 PRD: `docs/prd/{기능명}-prd.md` (있는 경우 링크)
- 구현 목표 요약 (기술 관점)
- 변경 범위 (모듈, 레이어)

## 2. 시스템 아키텍처
- 전체 서버 구조 내에서 이 기능의 위치
- 모듈 간 관계 및 레이어 흐름
- Mermaid 다이어그램 + 한글 Note 주석

## 3. 데이터베이스 설계
- ERD (Mermaid erDiagram 또는 텍스트 표)
- 신규/변경 테이블 명세 (컬럼, 타입, 제약조건, 인덱스)
- 마이그레이션 파일명: `V<YYYYMMDDHHmm>__description.sql`

## 4. API 명세 (해당 시)
- 엔드포인트, HTTP 메서드, 요청/응답, 상태 코드

## 5. 알고리즘 및 비즈니스 로직 (해당 시)
- 복잡한 처리 흐름, 분기 조건, 계산식

## 6. 인터페이스 정의 (해당 시)
- 외부 시스템·다른 도메인과의 연동 방식

## 7. 아키텍처 적합성 분석
- 프로젝트 규칙 준수 여부
- 우려 지점 및 대안

## 8. 구현 단계 (Phases)

### 구현 워크플로
(아래 참조)

### Phase N: [단계명]
- **목표**: ...
- **TODO**:
  - [ ] 작업 1 (패키지 경로 / 클래스명 명시)
  - [ ] 작업 2
- **테스트**: 이 Phase에서 작성할 테스트
- **커밋 계획**:
  - `type: 한국어 설명`
- **커밋 대상 파일 목록**:
  - `path/to/File.java`

## 9. 테스트 전략
- 계층별 테스트 계획
- Testcontainers(MySQL) 사용 여부
- 주요 테스트 시나리오 목록
```

---

## 구현 워크플로

TDD 문서의 **구현 단계(Phases)** 섹션 상단에 아래를 명시한다.

```markdown
### 사전 준비
1. 작업 브랜치 생성 (`api/{type}/what-to-do`)

### Phase 실행 (에이전트 1회 호출로 전체 구현)
1. Phase 1~N 코드를 **한번에 구현**
2. 전체 구현 완료 후 **테스트 실행** (`./gradlew :{module}:test`)
3. 테스트 실패 시 자체 수정·재실행 (5회 미만). **5회 이상 실패 시 중단, 보고**
4. 테스트 통과 후 반환

### 커밋·체크 (메인 컨텍스트)
1. Phase별 관련 파일을 나눠 **개별 커밋**
2. 각 커밋 후 TDD의 `- [ ]`를 `- [x]`로 업데이트
3. 전체 완료 후 PR 생성 여부 확인
```

> **핵심**: 코드를 한번에 구현하고 테스트는 마지막 1회만. 커밋은 Phase 단위로 분리.

---

## 작성 원칙

### 기술적 정확성

- **TODO**: 패키지 경로·클래스명 포함한 구체적 작업 항목
- **테스트 계층별 규칙**:
  - Domain: 순수 JUnit 5 + Fake 객체
  - Application: Mockito (`@ExtendWith`, `@Mock`, `@InjectMocks`)
  - Infrastructure: `@DataJpaTest` + Testcontainers (MySQL 필수)
  - Web: `@WebMvcTest` + MockMvc
- **커밋 계획**: 한국어, `feat:` / `fix:` / `refac:` / `test:` 등
- **커밋 대상 파일 목록**: Phase별 변경/생성 파일 경로 명시

### 가독성

- 기술 용어 첫 등장 시 괄호 설명
- 다이어그램에 한글 Note 주석
- 우려 지점은 쉬운 설명 먼저 → 기술 상세

---

## 경량 TDD 구조

단순 CRUD, 필드 추가 등은 아래 4섹션으로 충분하다:

```markdown
# [기능명] TDD (경량)

## 1. 개요
## 2. API 명세
## 3. 구현 단계 (Phases)
## 4. 테스트 전략
```

---

## 참조 규칙 인덱스

규칙 위치: 프로젝트의 `.claude/rules/` (Read 도구로 참조)

| 파일 | 핵심 내용 |
|------|-----------|
| `01-architecture-convention.md` | 레이어 구조, 의존성 방향, Client 패턴 |
| `02-domain-entity-convention.md` | 도메인 엔티티, Lombok, primitive/wrapper |
| `03-jpa-entity-convention.md` | JPA 엔티티, Builder, 변환 메서드 |
| `04-repository-pattern-convention.md` | 3단계 Repository 패턴 (DIP) |
| `05-dto-web-layer-convention.md` | DTO record, Controller |
| `06-exception-handling-convention.md` | 예외 처리, i18n |
| `07-general-project-convention.md` | 네이밍, 로깅, DB 마이그레이션 |
| `08-test-code-convention.md` | 계층별 테스트, Fake/Mock |
| `09-guardrails.md` | Testcontainers 필수, 커밋 보호 |
| `11-git-workflow-convention.md` | 브랜치 네이밍, 커밋, PR |
