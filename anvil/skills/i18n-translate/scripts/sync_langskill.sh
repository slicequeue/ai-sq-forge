#!/usr/bin/env bash
# references/langskill.md 를 번역팀 정본으로 갱신한다.
#
# 정본은 번역팀 사내 GitLab 저장소에 있고 Figma 플러그인은 매번 거기서 fetch 한다.
# 사내 주소·경로는 저장소에 남기지 않고 환경변수로 받는다.
# 토큰(read_repository)이 있으면 GitLab 에서, 없으면 로컬 사본에서 가져온다.
#
# 사용:
#   LANGSKILL_LOCAL=<로컬 langSKILL.md 경로> scripts/sync_langskill.sh
#   GITLAB_HOST=<https://사내 GitLab> LANGSKILL_PROJECT=<URL 인코딩된 프로젝트 경로> \
#     GITLAB_TOKEN=xxx scripts/sync_langskill.sh
set -euo pipefail

DEST="$(cd "$(dirname "$0")/.." && pwd)/references/langskill.md"
LOCAL="${LANGSKILL_LOCAL:-}"
GITLAB_HOST="${GITLAB_HOST:-}"
PROJECT="${LANGSKILL_PROJECT:-}"
BRANCH="${GITLAB_BRANCH:-main}"

TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

if [ -n "${GITLAB_TOKEN:-}" ]; then
  [ -n "$GITLAB_HOST" ] && [ -n "$PROJECT" ] || { echo "GITLAB_HOST·LANGSKILL_PROJECT 를 지정해야 한다" >&2; exit 1; }
  URL="$GITLAB_HOST/api/v4/projects/$PROJECT/repository/files/langSKILL.md/raw?ref=$BRANCH"
  if curl -fsS -H "PRIVATE-TOKEN: $GITLAB_TOKEN" "$URL" -o "$TMP"; then
    ORIGIN="GitLab $BRANCH"
  else
    echo "GitLab 조회 실패 — 로컬 사본으로 대체한다" >&2
    [ -f "$LOCAL" ] || { echo "로컬 사본도 없다: LANGSKILL_LOCAL 을 지정할 것" >&2; exit 1; }
    cp "$LOCAL" "$TMP"; ORIGIN="로컬 사본(GitLab 실패)"
  fi
else
  [ -f "$LOCAL" ] || { echo "로컬 사본이 없다: LANGSKILL_LOCAL 을 지정할 것 (현재: ${LOCAL:-미지정})" >&2; exit 1; }
  cp "$LOCAL" "$TMP"; ORIGIN="로컬 사본"
fi

{
  cat <<HDR
<!--
  이 파일은 번역팀이 관리하는 langSKILL.md 의 사본이다. 직접 고치지 말 것.
  정본(upstream): 번역팀 사내 GitLab 저장소의 langSKILL.md
  경유 사본:      LANGSKILL_LOCAL
  이번 갱신:      $ORIGIN, $(date '+%Y-%m-%d %H:%M')
  갱신:           scripts/sync_langskill.sh
  규칙이 생긴 근거·실측 이력은 같은 저장소의 langskillHistory.md 에 있다.
-->

HDR
  cat "$TMP"
} > "$DEST"

echo "갱신 완료: $DEST ($ORIGIN, $(wc -l < "$DEST" | tr -d ' ')줄)"
echo "SKILL.md 의 규칙 요약과 어긋나는 변경이 있는지 diff 로 확인할 것."
