---
description: 한국어 Conventional Commits 형식으로 커밋을 생성하고 관리합니다. 사용자가 커밋을 요청하거나 커밋 메시지 작성이 필요할 때 사용합니다.
---

# Git Commit Workflow

## Core Rules

1. **Korean Conventional Commits**: 반드시 한국어로 메시지를 작성하며 아래 타입을 따릅니다.
   - `feat:` 새로운 기능 추가
   - `fix:` 버그 수정
   - `refac:` 리팩토링 (기능 변경 없이 코드 구조 개선) - **`refactor:`가 아닌 `refac:` 사용**
   - `test:` 테스트 추가 또는 수정
   - `docs:` 문서 수정
   - `chore:` 빌드, 설정, 의존성 관리 등
   - `style:` 코드 포맷팅 (기능 변경 없음)
   - `perf:` 성능 개선

2. **No Brackets**: `[API]`, `[SHARED]`와 같은 대괄호 형식을 절대 사용하지 마세요. 반드시 `<type>:` 형식을 유지합니다.

3. **Human Only**: 커밋 메타데이터나 Co-authored-by에 "claude" 또는 AI 관련 정보를 포함하지 마세요.

## Workflow

1. `git status` 및 `git diff dev`를 실행하여 변경 사항 분석
2. 변경 사항을 논리적 단위로 그룹화
3. `<type>: <한국어 요약>` 형식으로 커밋 생성
