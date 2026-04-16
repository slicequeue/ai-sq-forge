---
description: Git 커밋 메시지 규칙 및 PR 작성 가이드
globs:
alwaysApply: false
---
# Git Workflow Rules

## 1. Branch Naming Convention
- **Format**: `api/{feat|refac|fix}/what-to-do`
- **Types**:
  - `feat`: New feature
  - `refac`: Refactoring
  - `fix`: Bug fix
- **Examples**:
  - `api/feat/add-user-login`
  - `api/fix/resolve-payment-error`

### ⚠️ 브랜치 생성 기준 (필수)
- **작업 브랜치는 반드시 `dev` 브랜치에서 생성합니다.**
- **`main` 브랜치에서 작업 브랜치를 생성하는 것은 절대 금지합니다.**
- `main`과 `dev` 사이에 차이가 존재하므로, `main`에서 브랜치를 따면 `dev`에 없는 파일들이 diff에 포함되어 PR이 오염됩니다.
- 올바른 예시:
  ```bash
  git fetch origin dev
  git checkout -b api/feat/my-feature origin/dev
  ```
- ❌ 금지:
  ```bash
  git checkout -b api/feat/my-feature origin/main  # 절대 금지
  ```

## 2. Commit Message Convention
- **Format**: `[Domain] Description` (dev branch) OR `type: description` (feature branch)
- **Language**: **Korean (한국어)** - All commit messages must be written in Korean.
- **AI 공동작성자 표기 금지**: 커밋 메시지에 `Co-authored-by`, AI 도구 공동작성자 표기를 포함하지 않습니다.
- **Types**:
  - `feat`: New feature
  - `fix`: Bug fix
  - `refactor`: Code restructuring
  - `test`: Test code
  - `docs`: Documentation
  - `chore`: Build/Config

### Examples
- `[건강] 체중 기록 API 추가`
- `fix: 로그인 실패 시 에러 메시지 수정`
- `refactor: 서비스 계층 구조 개선`

### Co-Authored-By 금지
- **AI 도구(Cursor, Claude Code, GitHub Copilot 등)는 공동 저자로 자신을 추가하지 않습니다.**
- author는 실제 개발자만 표시합니다.

**보완:**
- `git commit` 실행 시 `--trailer` 옵션을 사용하지 않고, `git commit -m "메시지"` 형식만 사용합니다. (IDE가 trailer를 자동 주입하는 경우에도 동일 원칙)
- Claude Code: `attribution.commit` 또는 `includeCoAuthoredBy` 설정을 비활성화합니다.

## 3. Pre-commit / Pre-push 체크리스트 (필수)
커밋/푸시 전에 아래를 반드시 수행합니다. (변경 모듈 기준)

- **JDK**: JDK 21로 실행합니다.
- **포맷(spotless)**:
  - **pasta-api 모듈**: 커밋/푸시 전 **항상** 자동 적용 (`./gradlew :pasta-api:spotlessApply`). 변경 사항은 반드시 커밋에 포함.
  - **그 외 모듈 (pghd, api 등)**: AI/자동화 도구가 `spotlessApply`를 실행하지 않습니다. 개발자가 필요 시 **직접 수동으로만** 실행합니다.
- **테스트**: 수정한 모듈의 테스트를 실행합니다. (예: `./gradlew :pasta-api:test`)
- **빌드**: 필요 시 모듈 빌드를 확인합니다. (예: `./gradlew :pasta-api:build`)

## 4. Pull Request (PR)
- **Language**: **Korean (한국어)** - Titles and descriptions must be written in Korean.
- **Title**: Same as commit message convention.
- **Template**:
  ```markdown
  ## Why need this PR❓
  - Purpose and context

  ## Changes ✌️
  - Detailed list of changes

  ## Test list 📝
  - How to verify the changes
  ```
- **Diagrams**: Use Mermaid.js for complex logic changes.
