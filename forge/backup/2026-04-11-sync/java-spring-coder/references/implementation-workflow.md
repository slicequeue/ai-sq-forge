# 구현 워크플로 상세

- [모드 A: TDD 계획서 기반 전체 구현](#모드-a-tdd-계획서-기반-전체-구현)
- [모드 B: 단순 구현 요청](#모드-b-단순-구현-요청)
- [모드 C: 테스트만 추가](#모드-c-테스트만-추가)
- [테스트 실패 대응 프로토콜](#테스트-실패-대응-프로토콜)
- [커밋 분리 전략](#커밋-분리-전략)
- [사용 가능한 스킬](#사용-가능한-스킬)

---

## 모드 A: TDD 계획서 기반 전체 구현

### 사전 준비

```
1. 작업 브랜치 확인 (이미 생성되어 있어야 함: api/{type}/what-to-do)
2. TDD 문서 위치 확인: docs/plans/{기능명}-*.md 또는 docs/tdd/{기능명}-*.md
3. .claude/rules/ 규칙 참조 (인덱스: 00-rules-index.md)
4. 같은 도메인 기존 코드 패턴 확인 (Entity, Service, Controller 구조)
5. JDK 21 설정: export JAVA_HOME=$(/usr/libexec/java_home -v 21)
```

### Phase 실행 (한번에 전체 구현)

```
1. TDD 문서의 Phase 1~N TODO를 순서대로 한번에 구현
   - 코드 생성 순서: Domain → Infra → App → Web → 설정 → TestDouble → Test
   - 각 Phase의 패키지 경로·클래스명을 정확히 따름
2. 전체 구현 완료 후 테스트 실행
   ./gradlew :{module}:test
3. 테스트 실패 시 자체 수정·재실행 (5회 미만)
   5회 이상 실패 → 즉시 중단, 보고
4. pasta-api 모듈이면 spotless 포맷 적용
   ./gradlew :pasta-api:spotlessApply
5. 테스트 통과 후 TDD 체크박스 업데이트 (- [ ] → - [x])
6. 변경 사항 보고 (커밋하지 않음)
```

> **핵심**: 코드를 한번에 구현하고 테스트는 마지막 1회만. 에이전트를 Phase마다 반복 호출하는 것보다 **훨씬 빠르다** (코드베이스 탐색 중복 제거, 테스트 1회만 실행).

---

## 모드 B: 단순 구현 요청

TDD 문서가 없을 때:

```
1. 사용자 요구사항 확인
   - 어떤 모듈? 어떤 도메인? 어떤 기능?
2. 기존 코드 패턴 파악
   - 같은 도메인의 기존 Entity, Service, Controller 구조 읽기
   - 예외 처리 패턴 (MoneyballException, ExceptionConstants)
   - 응답 포맷 (ApiResponse 래퍼 여부)
3. 코드 생성 순서에 따라 구현
   Domain → Infra → App → Web → 설정 → TestDouble → Test
4. .claude/rules/ 규칙에 맞게 코드 작성
   - 계층 구조, 네이밍, DTO 패턴 등
5. 계층별 테스트 작성
   - Fake(Domain/App), MockMvc(Web), Testcontainers(Infra)
6. JDK 21 설정 후 테스트 실행
   export JAVA_HOME=$(/usr/libexec/java_home -v 21)
   ./gradlew :{module}:test
7. 변경 사항 보고 — 커밋은 사용자 요청 시에만
```

---

## 모드 C: 테스트만 추가

기존 코드에 테스트만 추가하는 경우:

```
1. 테스트 대상 코드 분석
   - 어떤 계층? (Domain/App/Web/Infra)
   - 의존성 파악 (어떤 Repository, Client를 주입받는지)
   - 기존 Fake/Spy가 있는지 확인
2. Test Double 결정
   - 기존 Fake 있으면 재사용
   - 없으면 Fake/Spy 신규 생성
3. 테스트 시나리오 도출
   - Happy Path: 정상 동작
   - Edge Case: 경계 조건 (null, 빈 리스트, 최대값)
   - Error Case: 예외 상황 (not found, 중복, 만료)
4. BDD 스타일로 테스트 작성
   - @DisplayName 한글 구체적
   - Given-When-Then 주석 필수
   - Fixture 패턴 활용
5. 테스트 실행 → 보고
```

---

## 테스트 실패 대응 프로토콜

### 5회 미만 실패

```
실패 → 에러 메시지 정독 → 원인 특정 → 최소 범위 수정 → 재실행
```

### 5회 이상 연속 실패 → 즉시 중단

보고 내용:
1. **실패 테스트 목록**: 클래스명 + 메서드명
2. **에러 메시지**: 각 테스트의 핵심 에러 (스택 트레이스 핵심부)
3. **원인 분석**: 왜 실패하는지 판단
4. **수정 시도 이력**: 지금까지 시도한 수정 내역
5. **제안**: 다음에 시도할 접근 방향

---

## 커밋 분리 전략

에이전트(서브에이전트)로 실행될 때:

- **에이전트는 커밋하지 않는다**
- 메인 컨텍스트가 TDD의 Phase별 커밋 계획을 참고하여 분리 커밋
- 커밋 시 `/git-commit-workflow` 스킬 사용

메인 컨텍스트에서 직접 실행될 때:

- 사용자가 커밋을 요청하면 `/git-commit-workflow` 스킬로 커밋
- Phase별로 관련 파일을 나눠 개별 커밋
- 각 커밋 후 TDD의 `- [ ]`를 `- [x]`로 업데이트

---

## 사용 가능한 스킬

| 스킬 | 용도 | 사용 시점 |
|------|------|-----------|
| `/git-commit-workflow` | 한국어 Conventional Commits 커밋 | 사용자 커밋 요청 시 |
| `/git-branch-workflow` | `api/{type}/name` 브랜치 생성 | 작업 시작 시 |
| `/git-pr-workflow` | dev 대상 PR 생성 | 작업 완료 후 |
