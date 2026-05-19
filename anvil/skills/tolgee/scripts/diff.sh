#!/usr/bin/env bash
# tolgee diff helper — properties ↔ 콘솔 키 정합성 검증
# 사용:
#   ./diff.sh --prefix <key.prefix>
#   ./diff.sh --prefix <key.prefix> --values  # 카피 본문까지 비교
#
# 출력: 키별 ko-KR / en-US / ja-JP 존재 여부 + 상태 표
set -euo pipefail

PREFIX=""
COMPARE_VALUES=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --prefix) PREFIX="$2"; shift 2 ;;
    --values) COMPARE_VALUES=1; shift ;;
    -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done
[[ -z "$PREFIX" ]] && { echo "[tolgee/diff] --prefix 필수" >&2; exit 1; }

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
[[ -z "$ROOT" ]] && { echo "[tolgee/diff] git 저장소가 아닙니다." >&2; exit 1; }
cd "$ROOT"

[[ -f .env ]] || { echo "[tolgee/diff] .env 없음." >&2; exit 1; }
# shellcheck disable=SC1091
set -a; . ./.env; set +a
: "${TOLGEE_API_URL:?}"; : "${TOLGEE_PROJECT_ID:?}"; : "${TOLGEE_API_KEY:?}"

TS=$(date +%Y%m%d-%H%M%S)
OUT="/tmp/tolgee-diff-${TS}"
mkdir -p "$OUT"

# 1) 콘솔 export
npx -y @tolgee/cli@latest pull \
  --api-url "$TOLGEE_API_URL" \
  --api-key "$TOLGEE_API_KEY" \
  --project-id "$TOLGEE_PROJECT_ID" \
  --format PROPERTIES_ICU \
  --languages "ko-KR,en-US,ja-JP" \
  --path "$OUT" >/dev/null 2>&1 || {
    echo "[tolgee/diff] pull 실패. 토큰/프로젝트 확인." >&2
    exit 1
  }

SRC_DIR="shared/src/main/resources/messages"
PAT="^${PREFIX//./\\.}\."

# 키 집합 수집
collect_keys() {
  grep -hE "$PAT" "$@" 2>/dev/null | sed -E 's/=.*//' | sort -u
}
LOCAL_KEYS=$(collect_keys \
  "${SRC_DIR}/message-shared_ko_KR.properties" \
  "${SRC_DIR}/message-shared_en_US.properties" \
  "${SRC_DIR}/message-shared_ja_JP.properties")
REMOTE_KEYS=$(collect_keys "${OUT}/ko-KR.properties" "${OUT}/en-US.properties" "${OUT}/ja-JP.properties")
ALL_KEYS=$(printf "%s\n%s\n" "$LOCAL_KEYS" "$REMOTE_KEYS" | sort -u)

has_key_locale() {
  local key="$1" file="$2"
  grep -qE "^${key//./\\.}=" "$file" 2>/dev/null
}

get_value() {
  local key="$1" file="$2"
  grep -E "^${key//./\\.}=" "$file" 2>/dev/null | head -1 | sed -E 's/^[^=]+=//'
}

declare -A LOCAL_FILE=(
  [ko-KR]="${SRC_DIR}/message-shared_ko_KR.properties"
  [en-US]="${SRC_DIR}/message-shared_en_US.properties"
  [ja-JP]="${SRC_DIR}/message-shared_ja_JP.properties"
)
declare -A REMOTE_FILE=(
  [ko-KR]="${OUT}/ko-KR.properties"
  [en-US]="${OUT}/en-US.properties"
  [ja-JP]="${OUT}/ja-JP.properties"
)

printf "\n%-50s | %-9s | %-9s | %-9s | %s\n" "KEY" "ko-KR" "en-US" "ja-JP" "STATUS"
printf -- "%s\n" "$(printf '%.0s-' {1..110})"

while IFS= read -r key; do
  [[ -z "$key" ]] && continue
  status_arr=()
  cell=()
  for loc in ko-KR en-US ja-JP; do
    L=$(has_key_locale "$key" "${LOCAL_FILE[$loc]}" && echo 1 || echo 0)
    R=$(has_key_locale "$key" "${REMOTE_FILE[$loc]}" && echo 1 || echo 0)
    if [[ "$L" == 1 && "$R" == 1 ]]; then
      if [[ "$COMPARE_VALUES" == 1 ]]; then
        lv=$(get_value "$key" "${LOCAL_FILE[$loc]}")
        rv=$(get_value "$key" "${REMOTE_FILE[$loc]}")
        if [[ "$lv" == "$rv" ]]; then cell+=("OK"); else cell+=("DIFF"); status_arr+=("${loc} value diff"); fi
      else
        cell+=("OK")
      fi
    elif [[ "$L" == 1 ]]; then cell+=("local"); status_arr+=("${loc} console missing")
    elif [[ "$R" == 1 ]]; then cell+=("console"); status_arr+=("${loc} local missing")
    else cell+=("-")
    fi
  done
  status="${status_arr[*]:-OK}"
  [[ -z "${status_arr[*]:-}" ]] && status="OK"
  printf "%-50s | %-9s | %-9s | %-9s | %s\n" "$key" "${cell[0]}" "${cell[1]}" "${cell[2]}" "$status"
done <<< "$ALL_KEYS"

echo
echo "[tolgee/diff] 비교 산출물: $OUT"
