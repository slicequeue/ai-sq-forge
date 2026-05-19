# Claude Code Hooks 설정 가이드

프로젝트에 적용할 수 있는 Claude Code Hooks 설정. `.claude/settings.json`에 추가하여 AI 도구의 위험 행동을 사전 차단한다.

---

## 1. 보호 브랜치 커밋 차단 Hook

dev, stg, main 브랜치에서 `git commit`을 실행하면 자동 차단한다.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -q 'git commit'; then branch=$(git branch --show-current 2>/dev/null); if [ \"$branch\" = 'dev' ] || [ \"$branch\" = 'stg' ] || [ \"$branch\" = 'main' ]; then echo \"BLOCKED: 보호 브랜치($branch)에서 커밋 금지. 작업 브랜치를 생성하세요.\"; exit 2; fi; fi"
          }
        ]
      }
    ]
  }
}
```

### 동작 방식
- Claude Code가 Bash 도구로 `git commit`을 실행하려 할 때 hook이 먼저 실행
- 현재 브랜치가 `dev`, `stg`, `main`이면 `exit 2`로 도구 실행을 차단
- 차단 메시지가 Claude Code에 전달되어 작업 브랜치 생성을 안내

### 적용 위치
- 프로젝트별: `{프로젝트 루트}/.claude/settings.json`
- 전역: `~/.claude/settings.json`

---

## 2. 보호 브랜치 push 차단 Hook

보호 브랜치에서 `git push`도 차단한다. Hook 1과 함께 사용 권장.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'git (commit|push)'; then branch=$(git branch --show-current 2>/dev/null); if [ \"$branch\" = 'dev' ] || [ \"$branch\" = 'stg' ] || [ \"$branch\" = 'main' ]; then echo \"BLOCKED: 보호 브랜치($branch)에서 commit/push 금지.\"; exit 2; fi; fi"
          }
        ]
      }
    ]
  }
}
```

---

## 3. 통합 설정 (권장)

위 hooks를 통합한 `.claude/settings.json` 예시:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'git (commit|push)'; then branch=$(git branch --show-current 2>/dev/null); if [ \"$branch\" = 'dev' ] || [ \"$branch\" = 'stg' ] || [ \"$branch\" = 'main' ]; then echo \"BLOCKED: 보호 브랜치($branch)에서 commit/push 금지. 작업 브랜치를 생성하세요.\"; exit 2; fi; fi"
          }
        ]
      }
    ]
  }
}
```

---

## 배포 방법

### forge-deploy로 배포하는 경우

이 hooks 설정은 forge-deploy의 이식 대상이 아니다 (프로젝트별 설정이므로). 수동으로 대상 프로젝트에 적용한다:

```bash
# 대상 프로젝트의 .claude/settings.json에 hooks 섹션 추가
# 기존 settings.json이 있으면 hooks 키만 병합
```

### 주의사항

- hooks는 Claude Code 세션 시작 시 로드된다. 설정 변경 후 세션을 재시작해야 적용
- `exit 2`는 도구 실행을 차단하고 메시지를 Claude에게 전달
- `exit 1`은 도구 실행은 허용하되 경고 메시지를 표시
- hooks 환경 변수: `$CLAUDE_TOOL_INPUT` (도구 입력 JSON)
