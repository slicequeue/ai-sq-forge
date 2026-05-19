# Extraction Guide — JSONL 파싱 & 세션 요약 실전 명령

Claude Code 세션 로그(`~/.claude/projects/**/*.jsonl`)를 안전하게 읽어 해당일 활동을 세션·프로젝트 단위로 요약하는 절차.

## 목차
1. JSONL 스키마 (Claude Code 2.1 기준)
2. 해당일 필터링 (find + jq, UTC→KST)
3. 세션별 3줄 요약 패턴
4. 프로젝트별 집계
5. 민감정보 감지·마스킹
6. 전체 파이프라인 예시
7. 성능·안전 주의

---

## 1. JSONL 스키마 (Claude Code 2.1 기준)

한 파일 = 한 세션. 한 라인 = 한 이벤트. 주요 라인 타입:

| type | 의미 | 핵심 필드 |
|------|------|----------|
| `user` | 사용자 입력 또는 시스템 재삽입 | `timestamp`, `cwd`, `gitBranch`, `message.content` (string or `[{type,text}]`) |
| `assistant` | Claude 응답 | `timestamp`, `cwd`, `message.content` (배열: `text`/`thinking`/`tool_use`) |
| `attachment` | 첨부 컨텍스트 | `timestamp`, `cwd` |
| `file-history-snapshot` | 파일 스냅샷 | 무시 가능 |
| `permission-mode` | 퍼미션 변경 | 무시 가능 |
| `last-prompt` | 세션 마지막 프롬프트 메타 | 무시 가능 |

**content 배열 내부**:
```json
[
  {"type": "text", "text": "..."},
  {"type": "thinking", "thinking": "..."},
  {"type": "tool_use", "name": "Bash", "input": {"command": "..."}},
  {"type": "tool_result", "content": "..."}
]
```

**timestamp**는 ISO UTC (`2026-04-25T01:21:00.000Z`). KST는 +9h.

---

## 2. 해당일 필터링

### 2-1. 1차 필터 — 파일 mtime 기반

```bash
DATE="2026-04-25"           # KST 기준
NEXT_DATE="2026-04-26"

# macOS: 한국 시간으로 파일 찾기 (mtime이 KST 기준이면 아래 그대로)
find ~/.claude/projects/ -name "*.jsonl" \
  -newermt "$DATE 00:00" ! -newermt "$NEXT_DATE 00:00" 2>/dev/null
```

파일 mtime은 마지막 수정 시각 — 오늘 한 번이라도 활성화된 세션 파일만 통과.

### 2-2. 2차 필터 — 라인별 timestamp (KST 변환)

```bash
DATE="2026-04-25"
# KST 오늘 00:00~24:00 = UTC 어제 15:00~오늘 15:00
KST_START_UTC="2026-04-24T15:00:00.000Z"
KST_END_UTC="2026-04-25T15:00:00.000Z"

jq -c --arg start "$KST_START_UTC" --arg end "$KST_END_UTC" '
  select(.timestamp
    and .timestamp >= $start
    and .timestamp <  $end)
' "$file"
```

UTC 문자열은 ISO 정렬 가능 → 문자열 비교만으로 충분.

---

## 3. 세션별 3줄 요약 패턴

전체 라인을 LLM 컨텍스트에 적재 금지. 세션당 3줄로 압축:

```bash
# 세션(파일) 1개당:
# - 첫 번째 user 메시지 (세션 시작 의도)
# - 마지막 assistant 메시지의 최종 text 블록 (결론)
# - tool_use 이름별 호출 횟수 집계 (어떤 도구를 주로 썼나)

SESSION_FILE="..."

# a) 첫 user 메시지 (text만)
FIRST_USER=$(jq -c 'select(.type=="user" and .message.role=="user") | .message.content' "$SESSION_FILE" \
  | head -1 \
  | jq -r 'if type=="string" then . else (map(select(.type=="text").text) | join(" ")) end' 2>/dev/null \
  | head -c 500)

# b) 마지막 assistant text 블록
LAST_ASSISTANT=$(jq -c 'select(.type=="assistant") | .message.content' "$SESSION_FILE" \
  | tail -1 \
  | jq -r '[.[] | select(.type=="text").text] | join(" ")' 2>/dev/null \
  | head -c 500)

# c) 도구 호출 집계
TOOL_STATS=$(jq -r 'select(.type=="assistant") | .message.content[]? | select(.type=="tool_use").name' "$SESSION_FILE" \
  | sort | uniq -c | sort -rn | head -5)
```

**주의**:
- `head -c 500`으로 길이 제한 — 장문 프롬프트 방어
- thinking 블록은 제외 (사용자 관점 요약이므로 불필요)
- tool_result는 비포함 (중복 정보, 용량 폭발)

---

## 4. 프로젝트별 집계

```bash
# 각 JSONL의 대표 cwd 추출 (세션 내내 동일)
PROJECT=$(jq -r 'select(.cwd) | .cwd' "$SESSION_FILE" | head -1)

# 프로젝트 이름만 (경로 끝)
PROJECT_NAME=$(basename "$PROJECT")
```

최종 구조 (메모리 내 집계):
```
{
  "프로젝트A": [
    {session_id, first_user, last_assistant, tool_stats, duration},
    ...
  ],
  "프로젝트B": [...]
}
```

리포트 섹션 ①은 프로젝트별로 세션들을 한 줄로 합쳐 요약.

---

## 5. 민감정보 감지·마스킹

리포트 본문에 넣기 전 반드시 통과:

```bash
# 정규식 (bash 호환):
# - sk-XXXXX... (OpenAI)
# - ghp_XXXX... (GitHub personal token)
# - Bearer XXX / Authorization: 
# - eyJ... (JWT, 가능성 있음)
# - @kakao.com 외 사내·개인 이메일 전체 도메인
# - AIza... (GCP), AKIA... (AWS)

mask_secrets() {
  local text="$1"
  echo "$text" \
    | sed -E 's/(sk-[A-Za-z0-9_-]{10,})/***[REDACTED]/g' \
    | sed -E 's/(ghp_[A-Za-z0-9]{20,})/***[REDACTED]/g' \
    | sed -E 's/(Bearer [A-Za-z0-9_.-]{10,})/Bearer ***[REDACTED]/g' \
    | sed -E 's/(eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,})/***[JWT-REDACTED]/g' \
    | sed -E 's/(AIza[A-Za-z0-9_-]{20,})/***[GCP-REDACTED]/g' \
    | sed -E 's/(AKIA[A-Z0-9]{16})/***[AWS-REDACTED]/g'
}
```

**정책**: 의심스러우면 마스킹 우선. 오탐이 누락보다 낫다.

---

## 6. 전체 파이프라인 예시

```bash
#!/bin/bash
set -euo pipefail

DATE="${1:-$(date +%Y-%m-%d)}"
PROJECTS_DIR="$HOME/.claude/projects"

# KST → UTC 범위
KST_START_UTC=$(date -ju -v-9H -f "%Y-%m-%d %H:%M:%S" "$DATE 00:00:00" +"%Y-%m-%dT%H:%M:%S.000Z")
NEXT_DATE=$(date -j -v+1d -f "%Y-%m-%d" "$DATE" +"%Y-%m-%d")
KST_END_UTC=$(date -ju -v-9H -f "%Y-%m-%d %H:%M:%S" "$NEXT_DATE 00:00:00" +"%Y-%m-%dT%H:%M:%S.000Z")

# 1차 필터
FILES=$(find "$PROJECTS_DIR" -name "*.jsonl" \
  -newermt "$DATE 00:00" ! -newermt "$NEXT_DATE 00:00" 2>/dev/null)

if [[ -z "$FILES" ]]; then
  echo "NO_DATA"
  exit 0
fi

# 각 파일 요약
for f in $FILES; do
  # 2차 필터: 해당일 timestamp 라인만
  LINES=$(jq -c --arg s "$KST_START_UTC" --arg e "$KST_END_UTC" \
    'select(.timestamp and .timestamp >= $s and .timestamp < $e)' "$f" 2>/dev/null)

  [[ -z "$LINES" ]] && continue

  CWD=$(echo "$LINES" | jq -r 'select(.cwd) | .cwd' | head -1)
  SESSION_ID=$(basename "$f" .jsonl)

  echo "---"
  echo "SESSION: $SESSION_ID"
  echo "PROJECT: $(basename "$CWD")"

  # 첫 user + 마지막 assistant + tool stats
  echo "FIRST_USER: $(echo "$LINES" | jq -c 'select(.type=="user" and .message.role=="user") | .message.content' | head -1 | jq -r 'if type=="string" then . else (map(select(.type=="text").text) | join(" ")) end' | head -c 300)"
  echo "LAST_ASSISTANT: $(echo "$LINES" | jq -c 'select(.type=="assistant") | .message.content' | tail -1 | jq -r '[.[] | select(.type=="text").text] | join(" ")' | head -c 300)"
  echo "TOOLS:"
  echo "$LINES" | jq -r 'select(.type=="assistant") | .message.content[]? | select(.type=="tool_use").name' | sort | uniq -c | sort -rn | head -5
done
```

**출력 예시**:
```
---
SESSION: 827996da-cd97-480a-a11d-350cd2be443d
PROJECT: ai-sq-forge
FIRST_USER: 오늘 하루 리뷰 스킬 만들어줘...
LAST_ASSISTANT: sq-today-reviewer 초안 작성 완료...
TOOLS:
  12 Write
   8 Bash
   5 Read
   3 Edit
```

LLM은 이 요약을 받아 분석 5질문 수행 → 리포트 조립.

---

## 7. 성능·안전 주의

| 이슈 | 대응 |
|------|------|
| 하루 JSONL 합산 10MB 이상 | 파일당 처리 (stream), 전체 cat 금지 |
| jq 없는 환경 | `brew install jq` 선제 설치 (macOS 기본 미포함) |
| UTF-8 한국어 포함 | jq는 기본 UTF-8 지원 — 추가 설정 불필요 |
| 대규모 세션 (수만 라인) | `head -n 1000` 선제 컷 or `--stream` 사용 |
| 파일 락(쓰기 중) | 현재 활성 세션의 jsonl은 쓰기 중일 수 있음 → 읽기는 안전하지만 마지막 라인 파싱 실패 가능, 에러 무시 |

**절대 금지**:
- `jq -i` (in-place), `sed -i`, `> $jsonl_file` — JSONL 수정 시도
- `rm`, `mv`, `cp`로 JSONL 덮어쓰기
- JSONL을 다른 경로로 백업 복사 (Claude Code가 관리)
