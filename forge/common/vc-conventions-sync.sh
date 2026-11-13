#!/usr/bin/env bash
# virtualcare/coding-conventions 문서를 forge/common/vc-conventions/ 로 받아온다.
#
# 원문은 사내 공개(internal) 저장소 문서라 forge 저장소에 커밋하지 않는다(.gitignore).
# 받는 ref 는 아래 REF 로 고정하고, 바꿀 때 vc-conventions-guide.md 의 "기준 버전" 표도 함께 고친다.
#
# 사용:
#   forge/common/vc-conventions-sync.sh            # 기본 REF
#   VC_CONV_REF=main forge/common/vc-conventions-sync.sh
#
# 필요: gh CLI 로그인 계정이 virtualcare 조직 읽기 권한을 가질 것.
set -euo pipefail

REPO="virtualcare/coding-conventions"
REF="${VC_CONV_REF:-7cc266d}"   # PR #7 (convention/align-review-rules) 최신 커밋, 2026-11-13 기준 미병합
DEST="$(cd "$(dirname "$0")" && pwd)/vc-conventions"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

gh repo clone "$REPO" "$TMP/repo" -- -q
git -C "$TMP/repo" fetch -q origin "pull/7/head:pr7" 2>/dev/null || true
git -C "$TMP/repo" checkout -q "$REF"
SHA="$(git -C "$TMP/repo" rev-parse --short HEAD)"

mkdir -p "$DEST"
find "$DEST" -maxdepth 1 -name '*.md' -type f -exec rm -f {} +
cp "$TMP/repo"/*.md "$DEST/"
printf 'repo: %s\nref: %s\ncommit: %s\nsynced: %s\n' "$REPO" "$REF" "$SHA" "$(date '+%Y-%m-%d %H:%M')" > "$DEST/SOURCE"

echo "동기화 완료: $DEST ($REPO@$SHA, $(ls "$DEST"/*.md | wc -l | tr -d ' ')개 문서)"
