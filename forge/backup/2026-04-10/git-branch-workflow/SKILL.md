---
description: 프로젝트 브랜치 전략(api/{type}/name)에 따라 새로운 작업 브랜치를 생성합니다. 새로운 기능을 개발하거나 버그 수정을 시작할 때 사용합니다.
---

# Git Branch Workflow

## Core Rules

1. **Branch Naming Convention**: 반드시 `api/{type}/what-to-do` 형식을 따릅니다.
   - `api/feat/`: 새로운 기능 추가 (feature)
   - `api/refac/`: 리팩토링 (기능 변경 없이 코드 구조 개선) - **`refactor`가 아닌 `refac` 사용**
   - `api/fix/`: 버그 수정 (bug fix)
   - 예시: `api/feat/add-dashboard-cards`, `api/fix/resolve-schema-deprecation`

2. **Base Branch**: 모든 작업 브랜치는 항상 `dev` 브랜치로부터 생성하는 것을 원칙으로 합니다. (특별한 요청이 없는 한)

3. **Naming Style**: `what-to-do` 부분은 영문 소문자와 하이픈(`-`)만 사용하는 **kebab-case**를 사용합니다.

## Workflow

1. **Context Analysis**: 작업 내용을 분석하여 `feat`, `refac`, `fix` 중 적절한 타입을 결정합니다.
2. **Sync with Dev**:
   - `git checkout dev`
   - `git pull origin dev` (필요 시)
3. **Generate Branch Name**: 작업 내용을 바탕으로 간결한 영문 `task-name`을 생성합니다. (예: `api/feat/user-profile-v1`)
4. **Create Branch**: `git checkout -b api/{type}/{task-name}` 명령어로 브랜치를 생성합니다.
5. **Verify**: 생성된 브랜치명을 확인하고 작업을 시작합니다.
