# Agent Blueprint

에이전트는 역할 + 지침 + 가드레일을 가진 전문가 페르소나로, Claude Code의 커스텀 에이전트 `.md` 파일로 동작한다.

## 디렉토리 구조

```
anvil/agents/{agent-name}/
├── {agent-name}.md       # 메인 에이전트 정의
└── references/           # 상세 지침/예시 (선택)
    └── {topic}.md
```

## Agent MD 템플릿

```markdown
---
name: {agent-name}
description: "{한 줄 설명. 어떤 요청에 proactively 사용할지 명시.}"
model: {sonnet|opus|haiku}
color: {purple|blue|green|...}
---

# {Agent 이름} - {역할 한 줄 요약}

당신은 {역할 정의}. {핵심 책임 서술}.

---

## 판단 기준

| 요청 유형 | 행동 |
|-----------|------|
| ... | ... |

---

## 실행 지침

### 1단계: {단계명}
{지침}

### 2단계: {단계명}
{지침}

---

## 가드레일

- {절대 하지 말아야 할 것}
- {반드시 해야 할 것}

---

## 사용 가능한 도구/스킬

| 도구/스킬 | 용도 |
|-----------|------|
| ... | ... |
```

## Skill과의 차이점

| 구분 | Skill | Agent |
|------|-------|-------|
| 트리거 | 자동 매칭 or 슬래시 커맨드 | 명시적 호출 or proactive |
| 상태 | Stateless (1회 실행) | Stateful (대화 내 지속) |
| 모델 | 부모 상속 | 독자 지정 가능 |
| 복잡도 | 단일 작업 | 다단계 판단 + 작업 |
