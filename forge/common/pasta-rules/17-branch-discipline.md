---
description: 브랜치 확인 및 보호 브랜치 커밋 방지 규칙. git commit, push, 브랜치 전환 시 참고.
globs:
alwaysApply: true
---
# Branch Discipline (브랜치 규율)

11-git-workflow-convention과 함께 적용한다. 11은 브랜치 네이밍·생성 규칙, 이 문서는 **런타임 브랜치 안전 규칙**을 다룬다.

## 1. 커밋 전 브랜치 확인 (필수)

코드를 변경하기 **전에** 반드시 현재 브랜치를 확인한다.

```bash
git branch --show-current
```

- 작업 브랜치(`api/feat/*`, `api/fix/*`, `api/refac/*`)가 아니면 **즉시 중단**하고 올바른 브랜치로 전환한다.
- AI 도구(Claude Code, Cursor 등)도 동일하게 적용: 코드 수정·커밋 전 반드시 현재 브랜치를 확인한다.

## 2. 보호 브랜치 직접 커밋 금지

| 브랜치 | 직접 커밋 | 허용 방법 |
|--------|----------|-----------|
| `main` | **금지** | PR merge만 |
| `stg` | **금지** | PR merge만 |
| `dev` | **금지** | PR merge만 |

보호 브랜치에서 작업 중임을 발견하면:
1. 변경사항을 stash하지 **않는다** (데이터 유실 위험)
2. 새 작업 브랜치를 생성하고 변경사항을 옮긴다

## 3. PR 머지 후 브랜치 전환

PR이 머지된 후 새 작업을 시작할 때:

```bash
# 1. dev 최신화
git checkout dev
git pull origin dev

# 2. 새 작업 브랜치 생성
git checkout -b api/{type}/{task-name} dev
```

**머지된 브랜치에서 계속 작업하지 않는다** — 새 커밋이 다음 PR에 포함되어 혼란을 초래한다.

## 4. 브랜치 전환 시 상태 확인

세션 중 브랜치를 전환한 경우:
1. `git status`로 uncommitted 변경사항 확인
2. `git branch --show-current`로 현재 브랜치 재확인
3. 변경사항이 있으면 전환 전에 커밋 또는 명시적으로 처리

## 5. 삭제 전 사용처 확인 (필수)

파일이나 클래스를 삭제하기 전에 반드시 사용처를 확인한다:

```bash
# 삭제 대상 클래스/파일의 사용처 검색
grep -r "ClassName" --include="*.java" .
```

다른 모듈이나 도메인에서 참조 중인 파일을 삭제하면 컴파일 에러가 발생한다.
