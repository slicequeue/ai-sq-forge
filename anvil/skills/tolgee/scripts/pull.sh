#!/usr/bin/env bash
# tolgee pull helper — 콘솔 카피를 로컬에 다운로드 + diff 미리보기
# 사용:
#   ./pull.sh --prefix <key.prefix>
#   ./pull.sh --keys "key1,key2"
#
# 동작:
#   1) .env 로드
#   2) /tmp/tolgee-pull-<ts>/ 에 export
#   3) 로컬 properties와 키별 diff 보고
#   4) 실제 파일 적용은 사용자가 수동 (스크립트는 적용 X)
set -euo pipefail

PREFIX=""
KEYS=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --prefix) PREFIX="$2"; shift 2 ;;
    --keys)   KEYS="$2";   shift 2 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
[[ -z "$ROOT" ]] && { echo "[tolgee/pull] git 저장소가 아닙니다." >&2; exit 1; }
cd "$ROOT"

[[ -f .env ]] || { echo "[tolgee/pull] .env 없음." >&2; exit 1; }
# shellcheck disable=SC1091
set -a; . ./.env; set +a
: "${TOLGEE_API_URL:?}"; : "${TOLGEE_PROJECT_ID:?}"; : "${TOLGEE_API_KEY:?}"

TS=$(date +%Y%m%d-%H%M%S)
OUT="/tmp/tolgee-pull-${TS}"
mkdir -p "$OUT"

echo "[tolgee/pull] pulling project=${TOLGEE_PROJECT_ID} from ${TOLGEE_API_URL}"
npx -y @tolgee/cli@latest pull \
  --api-url "$TOLGEE_API_URL" \
  --api-key "$TOLGEE_API_KEY" \
  --project-id "$TOLGEE_PROJECT_ID" \
  --format PROPERTIES_ICU \
  --languages "ko-KR,en-US,ja-JP" \
  --path "$OUT" || {
    echo "[tolgee/pull] pull 실패. CLI --help로 옵션 확인 필요." >&2
    exit 1
  }

SRC_DIR="shared/src/main/resources/messages"
declare -A REMOTE_TO_LOCAL=(
  ["ko-KR.properties"]="${SRC_DIR}/message-shared_ko_KR.properties"
  ["en-US.properties"]="${SRC_DIR}/message-shared_en_US.properties"
  ["ja-JP.properties"]="${SRC_DIR}/message-shared_ja_JP.properties"
)

# 필터 정규식
if [[ -n "$PREFIX" ]]; then
  PATTERN="^${PREFIX//./\\.}\."
elif [[ -n "$KEYS" ]]; then
  # 콤마 → | 변환
  PATTERN="^($(echo "$KEYS" | sed 's/,/|/g; s/\./\\./g'))="
else
  PATTERN="."
fi

echo
echo "[tolgee/pull] diff preview (remote vs local) — filter: ${PATTERN}"
echo
for remote in "${!REMOTE_TO_LOCAL[@]}"; do
  remote_file="${OUT}/${remote}"
  local_file="${REMOTE_TO_LOCAL[$remote]}"
  if [[ ! -f "$remote_file" ]]; then
    echo "  [skip] $remote not in pull output"
    continue
  fi
  echo "  --- ${remote} ---"
  rf="${OUT}/.${remote}.filtered"
  lf="${OUT}/.local.${remote}.filtered"
  grep -E "$PATTERN" "$remote_file" | sort > "$rf" || true
  grep -E "$PATTERN" "$local_file" 2>/dev/null | sort > "$lf" || true
  if diff -u "$lf" "$rf" > "${OUT}/.diff.${remote}" 2>&1; then
    echo "  (no diff)"
  else
    sed 's/^/    /' "${OUT}/.diff.${remote}"
  fi
  echo
done

echo "[tolgee/pull] 원본 파일: $OUT"
echo "[tolgee/pull] 적용은 수동으로 검수 후 진행하세요. (자동 적용 안 함)"
