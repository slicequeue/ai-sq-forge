#!/bin/bash
# PreToolUse(Bash) 훅: git push 직전에 review-lint.py 를 돌려 위반이 있으면 막는다.
# 막힌 뒤 위반을 고치지 않고 의도적으로 푸시하려면 명령 끝에 "# review-lint: ack" 를 붙인다(사유는 PR 본문에).
INPUT=$(cat)
COMMAND=$(printf '%s' "$INPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))' 2>/dev/null)
CWD=$(printf '%s' "$INPUT" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("cwd",""))' 2>/dev/null)

printf '%s' "$COMMAND" | grep -qE '(^|[;&| ])git( -C [^ ]+)? push( |$)' || exit 0
printf '%s' "$COMMAND" | grep -q 'review-lint: ack' && exit 0

TARGET_DIR="$CWD"
C_DIR=$(printf '%s' "$COMMAND" | sed -nE 's/.*git -C ([^ ]+) push.*/\1/p')
[ -n "$C_DIR" ] && TARGET_DIR="$C_DIR"
cd "$TARGET_DIR" 2>/dev/null || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

OUTPUT=$(python3 "$(dirname "$0")/review-lint.py" 2>&1)
STATUS=$?
if [ "$STATUS" -eq 1 ]; then
  {
    echo "review-lint 위반이 있어 git push 를 막았습니다. 고친 뒤 다시 푸시하세요."
    echo "의도적으로 남기려면 PR 본문 '리뷰 포인트'에 사유를 적고 명령 끝에 '# review-lint: ack' 를 붙입니다."
    echo
    echo "$OUTPUT" | grep -E '^\[위반\]|review-lint:'
  } >&2
  exit 2
fi
exit 0
