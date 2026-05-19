#!/usr/bin/env bash
# tolgee push helper — 키 명시 + KEEP 모드 안전 푸시
# 사용:
#   ./push.sh --prefix <key.prefix> [--dry-run]
#   ./push.sh --keys "key1,key2,key3"  [--dry-run]
#
# 동작:
#   1) .env 로드
#   2) properties 4파일에서 매칭 키만 추출 → /tmp/tolgee-push-<ts>/ staging
#   3) staging 내용 출력 → dry-run이면 종료
#   4) npx @tolgee/cli push (force-mode KEEP)
set -euo pipefail

# ---- args ----
PREFIX=""
KEYS=""
DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --prefix) PREFIX="$2"; shift 2 ;;
    --keys)   KEYS="$2";   shift 2 ;;
    --dry-run) DRY_RUN=1;  shift ;;
    -h|--help)
      sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done
if [[ -z "$PREFIX" && -z "$KEYS" ]]; then
  echo "[tolgee/push] --prefix 또는 --keys 중 하나는 필수" >&2
  exit 1
fi

# ---- repo root ----
ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [[ -z "$ROOT" ]]; then
  echo "[tolgee/push] git 저장소가 아닙니다." >&2
  exit 1
fi
cd "$ROOT"

# ---- env ----
if [[ ! -f .env ]]; then
  echo "[tolgee/push] .env 파일이 없습니다. TOLGEE_API_URL/PROJECT_ID/API_KEY 필요." >&2
  exit 1
fi
# shellcheck disable=SC1091
set -a; . ./.env; set +a
: "${TOLGEE_API_URL:?TOLGEE_API_URL 미설정}"
: "${TOLGEE_PROJECT_ID:?TOLGEE_PROJECT_ID 미설정}"
: "${TOLGEE_API_KEY:?TOLGEE_API_KEY 미설정}"

# ---- locale 매핑 ----
SRC_DIR="shared/src/main/resources/messages"
declare -A FILE_TO_LOCALE=(
  ["${SRC_DIR}/message-shared_ko_KR.properties"]="ko-KR"
  ["${SRC_DIR}/message-shared_en_US.properties"]="en-US"
  ["${SRC_DIR}/message-shared_ja_JP.properties"]="ja-JP"
)
# default(message-shared.properties)는 콘솔 base 로케일이 ko-KR과 동일하면 별도 푸시 불필요.
# 차이가 있을 때만 별도 처리 — 현재는 ko-KR과 동일 정책이라 스킵.

# ---- staging ----
TS=$(date +%Y%m%d-%H%M%S)
STAGE="/tmp/tolgee-push-${TS}"
mkdir -p "$STAGE"

filter_lines() {
  local src="$1" dest="$2"
  if [[ -n "$PREFIX" ]]; then
    # ^prefix.  로 시작하는 줄만
    grep -E "^${PREFIX//./\\.}\." "$src" > "$dest" 2>/dev/null || true
  else
    # KEYS: 콤마로 분리 후 각 키로 grep
    : > "$dest"
    IFS=',' read -ra KS <<< "$KEYS"
    for k in "${KS[@]}"; do
      k_trim="$(echo "$k" | xargs)"
      grep -E "^${k_trim//./\\.}=" "$src" >> "$dest" 2>/dev/null || true
    done
  fi
}

echo "[tolgee/push] staging at $STAGE"
echo
TOTAL=0
for src in "${!FILE_TO_LOCALE[@]}"; do
  loc="${FILE_TO_LOCALE[$src]}"
  base="$(basename "$src")"
  out="${STAGE}/${base}"
  filter_lines "$src" "$out"
  cnt=$(wc -l < "$out" | tr -d ' ')
  TOTAL=$((TOTAL + cnt))
  echo "  [$loc] $base — keys=$cnt"
  if [[ "$cnt" -gt 0 ]]; then
    sed 's/^/    | /' "$out"
  fi
  echo
done

if [[ "$TOTAL" -eq 0 ]]; then
  echo "[tolgee/push] 매칭되는 키가 없습니다. prefix/keys를 확인하세요." >&2
  exit 1
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "[tolgee/push] dry-run 모드 — 업로드 생략."
  echo "[tolgee/push] staging 디렉토리: $STAGE"
  exit 0
fi

# ---- 사용자 확인 ----
echo "[tolgee/push] 위 ${TOTAL}건을 Tolgee 콘솔(${TOLGEE_API_URL})로 push 합니다."
echo "[tolgee/push] force-mode=KEEP (콘솔에 이미 있는 카피는 보존)"
echo -n "[tolgee/push] 진행하시겠습니까? [y/N] "
read -r ans
if [[ "${ans,,}" != "y" ]]; then
  echo "[tolgee/push] 취소됨."
  exit 0
fi

# ---- push 실행 ----
# Tolgee CLI 옵션은 버전에 따라 다를 수 있어, 실행 전 --help로 확인 권장.
# 아래는 v2 CLI 기준 일반적 호출 형태.
for src in "${!FILE_TO_LOCALE[@]}"; do
  loc="${FILE_TO_LOCALE[$src]}"
  base="$(basename "$src")"
  staged="${STAGE}/${base}"
  if [[ ! -s "$staged" ]]; then continue; fi

  echo "[tolgee/push] push $base → $loc"
  npx -y @tolgee/cli@latest push \
    --api-url "$TOLGEE_API_URL" \
    --api-key "$TOLGEE_API_KEY" \
    --project-id "$TOLGEE_PROJECT_ID" \
    --force-mode KEEP \
    --languages "$loc" \
    --format PROPERTIES_ICU \
    "$staged" || {
      echo "[tolgee/push] $base push 실패. CLI --help 옵션 확인 필요." >&2
      exit 1
    }
done

echo
echo "[tolgee/push] 완료. 콘솔에서 확인: ${TOLGEE_API_URL}/projects/${TOLGEE_PROJECT_ID}/translations"
