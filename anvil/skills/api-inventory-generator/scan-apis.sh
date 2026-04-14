#!/usr/bin/env bash
# API Inventory Scanner (macOS/BSD 호환)
# 프로젝트의 @RestController를 스캔하여 단일 API 목록 문서를 생성한다.
#
# 사용법: bash .claude/skills/api-inventory-generator/scan-apis.sh [출력 디렉토리]
# 기본 출력: docs/api-inventory/{오늘 날짜}/api-inventory.md

set -uo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
TODAY=$(date +%Y-%m-%d)
OUTPUT_DIR="${1:-$PROJECT_ROOT/docs/api-inventory/$TODAY}"
OUTPUT_FILE="$OUTPUT_DIR/api-inventory.md"

mkdir -p "$OUTPUT_DIR"

# 1. 모든 @RestController 파일 찾기
find_controllers() {
  grep -rl '@RestController' "$PROJECT_ROOT" --include="*.java" 2>/dev/null | sort
}

# 2. 컨트롤러에서 API 정보 추출
#    출력: 모듈|컨트롤러|Tag|Method|Path|Summary|Auth
extract_api_info() {
  local file="$1"
  local module
  module=$(echo "$file" | sed "s|$PROJECT_ROOT/||" | cut -d'/' -f1)

  local class_name
  class_name=$(grep 'public class ' "$file" | sed 's/.*class \([A-Za-z0-9_]*\).*/\1/' | head -1)

  local base_path
  base_path=$(grep '@RequestMapping' "$file" | sed 's/.*"\(\/[^"]*\)".*/\1/' | head -1)
  base_path="${base_path:-/}"

  local tag
  tag=$(grep '@Tag' "$file" | sed 's/.*name *= *"\([^"]*\)".*/\1/' 2>/dev/null | head -1)
  tag="${tag:-N/A}"

  # 인증 여부: 컨트롤러 또는 메서드에 @AuthenticationPrincipal이 있으면 인증 필요
  local has_auth_in_file
  if grep -q '@AuthenticationPrincipal' "$file" 2>/dev/null; then
    has_auth_in_file="Y"
  else
    has_auth_in_file=""
  fi

  grep -nE '@(Get|Post|Put|Patch|Delete)Mapping' "$file" | while IFS=: read -r line_num line_content; do
    local method
    method=$(echo "$line_content" | sed -E 's/.*@(Get|Post|Put|Patch|Delete)Mapping.*/\1/' | tr '[:lower:]' '[:upper:]')

    local endpoint_path
    endpoint_path=$(echo "$line_content" | sed -n 's/.*Mapping.*"\(\/[^"]*\)".*/\1/p')

    local full_path
    if [ -n "$endpoint_path" ]; then
      if [ "$base_path" = "/" ]; then
        full_path="$endpoint_path"
      else
        full_path="${base_path}${endpoint_path}"
      fi
    else
      full_path="${base_path}"
    fi

    local summary
    summary=$(sed -n "$((line_num > 5 ? line_num - 5 : 1)),$((line_num + 5))p" "$file" | sed -n 's/.*summary *= *"\([^"]*\)".*/\1/p' | head -1)
    summary="${summary:-}"

    # 메서드별 인증 확인: 해당 메서드 시그니처 근처에 @AuthenticationPrincipal이 있는지
    local auth
    if [ -n "$has_auth_in_file" ]; then
      local method_auth
      method_auth=$(sed -n "$((line_num)),$((line_num + 5))p" "$file" | grep -c '@AuthenticationPrincipal' 2>/dev/null || true)
      if [ "$method_auth" -gt 0 ] 2>/dev/null; then
        auth="Bearer"
      else
        auth="-"
      fi
    else
      auth="-"
    fi

    echo "$module|$class_name|$tag|$method|$full_path|$summary|$auth"
  done
}

# 3. 전체 데이터 수집
echo "API Inventory 스캔 시작..."
echo "출력: $OUTPUT_FILE"
echo ""

TMPFILE=$(mktemp)
find_controllers | while read -r file; do
  extract_api_info "$file"
done | sort -t'|' -k1,1 -k3,3 -k5,5 > "$TMPFILE"

TOTAL=$(wc -l < "$TMPFILE" | tr -d ' ')
CONTROLLER_COUNT=$(find_controllers | wc -l | tr -d ' ')

# 4. 단일 문서 생성
{
  # 헤더
  echo "# pasta-japan-server API 전체 목록"
  echo ""
  echo "> 조사일: $TODAY | 총 ${TOTAL}개 엔드포인트 | ${CONTROLLER_COUNT}개 컨트롤러"
  echo ""

  # 요약 통계
  echo "## 요약"
  echo ""
  echo "### 모듈별"
  echo ""
  echo "| 모듈 | API 수 |"
  echo "|------|--------|"
  cut -d'|' -f1 "$TMPFILE" | sort | uniq -c | sort -rn | while read -r count module; do
    echo "| $module | $count |"
  done
  echo ""

  echo "### Method별"
  echo ""
  echo "| Method | 수 |"
  echo "|--------|----|"
  cut -d'|' -f4 "$TMPFILE" | sort | uniq -c | sort -rn | while read -r count method; do
    echo "| $method | $count |"
  done
  echo ""
  echo "---"
  echo ""

  # 모듈별 분류 목록
  current_module=""
  while IFS='|' read -r module class tag method path summary; do
    if [ "$module" != "$current_module" ]; then
      current_module="$module"
      echo ""
      echo "## $module"
      echo ""
      echo "| Tag | HTTP | 엔드포인트 | 설명 |"
      echo "|-----|------|-----------|------|"
    fi
    echo "| $tag | $method | $path | $summary |"
  done < "$TMPFILE"

} > "$OUTPUT_FILE"

rm -f "$TMPFILE"

echo "완료! $OUTPUT_FILE (총 ${TOTAL}개 API)"
