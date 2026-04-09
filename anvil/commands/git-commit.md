---
name: git-commit
description: "한국어 Conventional Commits 형식으로 커밋을 생성합니다."
trigger: "/git-commit"
args: ""
---

# /commit

## 용도

변경 사항을 분석하여 한국어 Conventional Commits 형식으로 커밋을 생성한다.

## 인자

없음. 현재 변경 사항을 자동 분석한다.

## 실행 로직

1. `git status` 및 `git diff dev`로 변경 사항 분석
2. 변경 사항을 논리적 단위로 그룹화
3. 적절한 커밋 타입 결정 후 `<type>: <한국어 요약>` 형식으로 커밋 생성

## 출력 형식

```
✓ 커밋 완료: {type}: {한국어 요약}
```

## 가드레일

- 커밋 타입: `feat:`, `fix:`, `refac:`, `test:`, `docs:`, `chore:`, `style:`, `perf:`
- `refactor:`가 아닌 **`refac:`** 사용
- 대괄호 형식(`[API]`, `[SHARED]`) 절대 금지. 반드시 `<type>:` 형식 유지
- 커밋 메타데이터나 Co-authored-by에 "claude" 또는 AI 관련 정보 포함 금지
