#!/usr/bin/env python3
"""
API Inventory Scanner
프로젝트의 @RestController를 스캔하여 API 목록 문서를 생성한다.

사용법: python3 .claude/skills/api-inventory-generator/scan-apis.py [출력 디렉토리]
기본 출력: docs/api-inventory/{오늘 날짜}/api-inventory.md
"""

import os
import re
import sys
from datetime import date
from fnmatch import fnmatch
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
TODAY = date.today().isoformat()


# --- 1. SecurityConstants 파싱 ---

def parse_security_constants():
    """SecurityConstants.java에서 airArray, dashboardArray, swaggerArray 패턴을 파싱한다."""
    sc_path = PROJECT_ROOT / "api/src/main/java/com/kakaohealthcare/moneyball/api/common/config/SecurityConstants.java"
    if not sc_path.exists():
        return {}, {}, {}

    content = sc_path.read_text()

    def extract_array(name):
        pattern = rf'{name}\s*=\s*new\s+String\[\]\s*\{{([^}}]+)\}}'
        match = re.search(pattern, content, re.DOTALL)
        if not match:
            return []
        raw = match.group(1)
        return [s.strip().strip('"') for s in re.findall(r'"([^"]+)"', raw)]

    return {
        "app": extract_array("airArray"),
        "dashboard": extract_array("dashboardArray"),
        "swagger": extract_array("swaggerArray"),
        "permitAll": extract_array("permitAllArray"),
    }


def classify_auth(path, security_patterns):
    """API path를 SecurityConstants 패턴에 매칭하여 인증 유형을 반환한다."""
    # AntPathMatcher /** 패턴을 fnmatch로 변환
    def ant_to_glob(pattern):
        return pattern.replace("/**", "/*")  # fnmatch는 *가 /도 매칭

    def matches(path, patterns):
        for p in patterns:
            glob_p = ant_to_glob(p)
            if fnmatch(path, glob_p):
                return True
            # prefix 매칭 (/** 제거 후 startswith)
            prefix = p.replace("/**", "")
            if path.startswith(prefix):
                return True
        return False

    if matches(path, security_patterns.get("swagger", [])):
        return "-"
    if matches(path, security_patterns.get("permitAll", [])):
        return "-"
    if path.startswith("/callback") or path.startswith("/webhook"):
        return "-"
    if matches(path, security_patterns.get("app", [])):
        return "Bearer"
    if matches(path, security_patterns.get("dashboard", [])):
        return "Dashboard"
    return "?"


# --- 2. 컨트롤러 스캔 ---

def find_controllers():
    """프로젝트에서 @RestController가 있는 Java 파일을 찾는다."""
    controllers = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # 빌드 디렉토리 제외
        dirs[:] = [d for d in dirs if d not in ("build", "out", "bin", ".gradle", ".git", "node_modules")]
        for f in files:
            if f.endswith(".java"):
                filepath = Path(root) / f
                try:
                    content = filepath.read_text(errors="ignore")
                    if "@RestController" in content:
                        controllers.append(filepath)
                except Exception:
                    pass
    return sorted(controllers)


def extract_api_info(filepath, security_patterns):
    """컨트롤러 파일에서 API 정보를 추출한다."""
    content = filepath.read_text(errors="ignore")
    lines = content.split("\n")

    # 모듈
    rel = filepath.relative_to(PROJECT_ROOT)
    module = str(rel).split("/")[0]

    # 클래스명
    class_match = re.search(r'public class (\w+)', content)
    class_name = class_match.group(1) if class_match else "Unknown"

    # base path 추출 — 지원 패턴:
    #   @RequestMapping("/path")
    #   @RequestMapping(path = "/path")
    #   @RequestMapping(value = "/path")
    #   @RequestMapping(path = {"/path1", "/path2"})  → 첫 번째 경로 사용
    base_path = ""
    rm_block = re.search(r'@RequestMapping\s*\([^)]*\)', content)
    if rm_block:
        paths = re.findall(r'"(/[^"]*)"', rm_block.group(0))
        if paths:
            base_path = paths[0]

    # Tag
    tag_match = re.search(r'@Tag\s*\(\s*name\s*=\s*"([^"]+)"', content)
    tag = tag_match.group(1) if tag_match else "N/A"

    # 엔드포인트 추출
    apis = []
    # @GetMapping("/path"), @GetMapping(value="/path"), @GetMapping(path="/path"), @GetMapping(path={"/a","/b"}) 지원
    mapping_re = re.compile(r'@(Get|Post|Put|Patch|Delete)Mapping(?:\s*\(\s*(?:(?:value|path)\s*=\s*(?:\{[^}]*\})?)?"(/[^"]*)")?')

    for i, line in enumerate(lines):
        m = mapping_re.search(line)
        if not m:
            continue

        method = m.group(1).upper()
        endpoint = m.group(2) or ""

        if endpoint:
            full_path = base_path + endpoint
        else:
            full_path = base_path if base_path else "/"

        # summary: 근처 줄에서 @Operation summary 추출
        context = "\n".join(lines[max(0, i - 5):i + 5])
        summary_match = re.search(r'summary\s*=\s*"([^"]+)"', context)
        summary = summary_match.group(1) if summary_match else ""

        # 인증 분류
        auth = classify_auth(full_path, security_patterns)

        apis.append({
            "module": module,
            "class": class_name,
            "tag": tag,
            "method": method,
            "path": full_path,
            "summary": summary,
            "auth": auth,
        })

    return apis


# --- 3. 문서 생성 ---

def generate_document(apis, output_path, controller_count):
    """단일 마크다운 문서를 생성한다."""

    # 모듈별 카운트
    module_counts = {}
    method_counts = {}
    auth_counts = {}
    for api in apis:
        module_counts[api["module"]] = module_counts.get(api["module"], 0) + 1
        method_counts[api["method"]] = method_counts.get(api["method"], 0) + 1
        auth_counts[api["auth"]] = auth_counts.get(api["auth"], 0) + 1

    lines = []
    lines.append(f"# pasta-japan-server API 전체 목록")
    lines.append("")
    lines.append(f"> 조사일: {TODAY} | 총 {len(apis)}개 엔드포인트 | {controller_count}개 컨트롤러")
    lines.append("")

    # 요약
    lines.append("## 요약")
    lines.append("")
    lines.append("### 모듈별")
    lines.append("")
    lines.append("| 모듈 | API 수 |")
    lines.append("|------|--------|")
    for module, count in sorted(module_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {module} | {count} |")
    lines.append("")

    lines.append("### Method별")
    lines.append("")
    lines.append("| Method | 수 |")
    lines.append("|--------|----|")
    for method, count in sorted(method_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {method} | {count} |")
    lines.append("")

    lines.append("### 인증별")
    lines.append("")
    lines.append("| 인증 | 수 | 설명 |")
    lines.append("|------|----|------|")
    auth_desc = {"Bearer": "앱 JWT 인증", "Dashboard": "커넥트 대시보드 인증", "-": "인증 없음", "?": "미분류"}
    for auth, count in sorted(auth_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {auth} | {count} | {auth_desc.get(auth, '')} |")
    lines.append("")
    lines.append("---")

    # 모듈별 분류 목록
    sorted_apis = sorted(apis, key=lambda x: (x["module"], x["tag"], x["path"]))
    current_module = None
    for api in sorted_apis:
        if api["module"] != current_module:
            current_module = api["module"]
            lines.append("")
            lines.append(f"## {current_module}")
            lines.append("")
            lines.append("| Tag | HTTP | 엔드포인트 | 설명 | 인증 |")
            lines.append("|-----|------|-----------|------|------|")
        lines.append(f"| {api['tag']} | {api['method']} | {api['path']} | {api['summary']} | {api['auth']} |")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# --- 실행 ---

def main():
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else PROJECT_ROOT / "docs" / "api-inventory" / TODAY
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "api-inventory.md"

    print(f"API Inventory 스캔 시작...")
    print(f"출력: {output_file}")
    print()

    # SecurityConstants 패턴 로드
    security_patterns = parse_security_constants()
    print(f"  SecurityConstants 패턴 로드: app={len(security_patterns.get('app', []))}개, "
          f"dashboard={len(security_patterns.get('dashboard', []))}개")

    # 컨트롤러 스캔
    controllers = find_controllers()
    print(f"  컨트롤러 {len(controllers)}개 발견")

    # API 정보 추출
    all_apis = []
    for ctrl in controllers:
        apis = extract_api_info(ctrl, security_patterns)
        all_apis.extend(apis)
    print(f"  API {len(all_apis)}개 추출")

    # 문서 생성
    generate_document(all_apis, output_file, len(controllers))

    print()
    print(f"완료! {output_file} (총 {len(all_apis)}개 API)")


if __name__ == "__main__":
    main()