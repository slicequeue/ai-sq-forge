---
description: dev 브랜치를 대상으로 PR을 생성하거나 기존 PR 본문을 업데이트합니다. PR 생성/수정이 필요할 때 사용합니다.
---

# Git PR Workflow

## Core Rules

1. **Target Branch**: 기본 브랜치는 항상 `dev`입니다.
2. **PR Template**: 저장소 루트에 `PR_TEMPLATE.md`가 있으면 반드시 읽고 모든 섹션을 충실히 작성하세요. 없으면 아래 작성 가이드를 따릅니다.
3. **Korean Summary**: PR 제목과 본문은 한국어로 명확하게 작성합니다.
4. **Tools**: GitHub CLI(`gh`) 또는 GitHub MCP를 사용하여 PR을 생성/수정합니다.
5. **기존 PR 확인**: 현재 브랜치에 이미 열린 PR이 있으면 새로 생성하지 않고 `gh pr edit`으로 본문을 업데이트합니다.

## Workflow

1. 현재 브랜치와 `dev` 브랜치의 차이 확인 (`git log dev..HEAD --oneline`, `git diff dev..HEAD --stat`)
2. **Remote Push Check**: 원격에 푸시되어 있는지 확인. 안 되어 있으면 `git push -u origin HEAD` 실행.
3. **기존 PR 확인**: `gh pr list --head "$(git branch --show-current)" --state open`으로 확인. 이미 있으면 `gh pr edit`으로 본문 업데이트.
4. `PR_TEMPLATE.md`가 있으면 읽고, 없으면 아래 작성 가이드에 따라 본문 작성.
5. `gh pr create` (신규) 또는 `gh pr edit` (기존)으로 PR 생성/수정.

## PR 본문 작성 가이드

### 원칙: "처음 보는 리뷰어가 빠르게 이해할 수 있도록" 작성

- **Why**: 왜 이 변경이 필요한지 문제 상황과 해결 방향을 명확히 기술
- **What**: 변경 내용을 레이어/모듈별로 구조화하여 정리
- **도표 활용**: 변경 파일이 많거나 구조가 복잡하면 적극적으로 도표를 활용

### 필수 섹션

#### 1. `## Why need this PR❓`
- **문제**: 현재 어떤 문제가 있는지 (사용자 영향, 데이터 정합성 등)
- **해결**: 이 PR이 어떻게 해결하는지 한 줄 요약

#### 2. `## Changes ✌️`
- **아키텍처 구조**: 변경된 파일이 5개 이상이면 트리 다이어그램으로 전체 구조를 먼저 보여준다
  ```
  module/domain/
  ├── domain/
  │   └── Repository          ← 역할 설명
  ├── application/
  │   └── Service             ← 역할 설명
  └── infrastructure/
      └── RepositoryImpl      ← 역할 설명
  ```
- **레이어별 변경 도표**: 파일별 역할을 표로 정리
  | 레이어 | 파일 | 설명 |
  |--------|------|------|
  | Domain | `*Repository` | 포트 인터페이스 |
  | Infrastructure | `*RepositoryImpl` | JDBC/JPA 구현체 |
- **주요 설계 포인트**: 리뷰어가 알아야 할 핵심 설계 결정을 번호 매겨 설명
  - 예: 커서 기반 페이징 선택 이유, 멱등성 보장 방식, 동시성 처리 등
- **처리 흐름**: 복잡한 로직이면 간단한 시퀀스/플로우 텍스트 추가

#### 3. `## Test list 📝`
- **테스트 커버리지 도표**: 계층별 테스트 방식과 검증 내용을 표로 정리
  | 계층 | 테스트 클래스 | 방식 | 검증 내용 |
  |------|-------------|------|----------|
  | Application | `*ServiceTest` | Fake | 비즈니스 로직 |
  | Infrastructure | `*RepositoryTest` | Testcontainers | SQL 쿼리 |
- **실행 방법**: `./gradlew :{module}:test` 등 실행 커맨드 포함

### 도표/다이어그램 사용 기준

| 상황 | 사용 여부 |
|------|----------|
| 변경 파일 5개 이상 | 아키텍처 트리 다이어그램 추가 |
| 레이어 3개 이상 변경 | 레이어별 변경 도표 추가 |
| 테스트 클래스 3개 이상 | 테스트 커버리지 도표 추가 |
| 복잡한 처리 흐름 (3단계 이상) | 시퀀스/플로우 텍스트 추가 |
| 단순 버그 수정/리팩토링 | 도표 불필요, 텍스트만으로 충분 |
