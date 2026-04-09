---
name: git-worktree-add
description: "병렬 작업을 위해 git worktree를 생성합니다. 새 브랜치 생성 또는 기존 브랜치 체크아웃을 지원합니다."
trigger: "/git-worktree-add"
args: "{작업 설명 또는 기존 브랜치명}"
---

# /git-worktree-add

## 용도

현재 저장소에서 독립된 작업 디렉토리(worktree)를 생성하여 병렬 작업을 가능하게 한다. stash/commit 없이 다른 브랜치에서 동시에 작업할 수 있다.

## 인자

| 인자 | 필수 | 설명 | 기본값 |
|------|------|------|--------|
| 작업 설명 또는 브랜치명 | O | 새 브랜치 생성 시 작업 설명, 기존 브랜치 체크아웃 시 브랜치명 | - |

## 실행 로직

### 1. 모드 판별

- 인자가 **기존 브랜치명**과 일치하면 → 기존 브랜치 체크아웃 모드
- 그 외 → 새 브랜치 생성 모드 (`api/{type}/{task-name}` 형식 적용)

### 2. 경로 결정

sibling directory 패턴을 사용한다:

```
{레포-루트-경로}--{브랜치명-슬래시를-하이픈으로}/
```

예시:
```
ai-sq-forge/                              # 메인 저장소
ai-sq-forge--api-feat-login/              # worktree: api/feat/login
ai-sq-forge--api-fix-auth-bug/            # worktree: api/fix/auth-bug
```

### 3. 실행

**새 브랜치 생성 모드:**

```bash
git worktree add -b api/{type}/{task-name} {경로} dev
```

**기존 브랜치 체크아웃 모드:**

```bash
git worktree add {경로} {브랜치명}
```

### 4. 확인

- `git worktree list`로 생성 결과 확인
- 생성된 경로 출력

## 출력 형식

```
✓ 워크트리 생성 완료
  경로: {절대 경로}
  브랜치: {브랜치명}
  base: {base 브랜치} (새 브랜치 생성 시)

현재 워크트리 목록:
  {git worktree list 결과}
```

## 가드레일

- 새 브랜치 생성 시 `api/{type}/{task-name}` 형식 준수 (type: `feat`, `refac`, `fix`)
- `refactor`가 아닌 **`refac`** 사용
- `task-name`은 영문 소문자 + 하이픈(`-`)만 사용 (kebab-case)
- 새 브랜치의 base는 `dev` (특별한 요청이 없는 한)
- 이미 다른 워크트리에서 체크아웃된 브랜치는 생성 불가 (git 안전장치)
- `--force` 옵션으로 중복 체크아웃을 우회하지 않는다
- `10-worktree-safety-convention` 규칙 준수: 워크트리 전용 빌드 파일 수정은 커밋 금지
