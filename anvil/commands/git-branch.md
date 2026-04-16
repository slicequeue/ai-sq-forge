---
name: git-branch
description: "프로젝트 브랜치 전략(api/{type}/name)에 따라 새로운 작업 브랜치를 생성합니다."
trigger: "/git-branch"
args: "{작업 설명 또는 브랜치명}"
version: "1.0"
last-modified: "2026-04-10"
changelog: "초기 배포"
---

# /branch

## 용도

프로젝트 브랜치 네이밍 규칙(`api/{type}/task-name`)에 맞는 작업 브랜치를 `dev` 기반으로 생성한다.

## 인자

| 인자 | 필수 | 설명 | 기본값 |
|------|------|------|--------|
| 작업 설명 | O | 수행할 작업 내용 (한국어/영어). 브랜치명 자동 생성에 사용 | - |

## 실행 로직

1. 작업 내용을 분석하여 `feat`, `refac`, `fix` 중 적절한 타입을 결정
2. `git checkout dev && git pull origin dev`로 최신 상태 동기화
3. 작업 내용을 바탕으로 간결한 영문 kebab-case `task-name` 생성
4. `git checkout -b api/{type}/{task-name}` 실행
5. 생성된 브랜치명 확인 출력

## 출력 형식

```
✓ 브랜치 생성 완료: api/{type}/{task-name}
  base: dev (최신 동기화 완료)
```

## 가드레일

- 브랜치명은 반드시 `api/{type}/{task-name}` 형식. type은 `feat`, `refac`, `fix` 중 하나
- `refactor`가 아닌 **`refac`** 사용
- `task-name`은 영문 소문자 + 하이픈(`-`)만 사용 (kebab-case)
- base branch는 항상 `dev` (특별한 요청이 없는 한)
