#!/usr/bin/env python3
"""리뷰 재발 방지 기계 검사 (review-recurrence-guard.md RR-L 항목).

바뀐 줄만 검사해서 사람 리뷰에서 반복 지적된 패턴을 푸시 전에 출력한다.
판단이 필요한 항목은 [확인] 으로, 규칙 위반이 거의 확실한 항목은 [위반] 으로 표시한다.

사용:
  review-lint.py                     # merge-base(origin/dev) ~ 작업 트리
  review-lint.py --base origin/dev   # 기준 브랜치 지정
  review-lint.py --head <sha>        # 특정 커밋까지만 (과거 PR 재검사용)
종료 코드: [위반] 이 있으면 1, 없으면 0
"""
import argparse
import re
import subprocess
import sys


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, check=True).stdout


def changed_lines(base, head):
    diff_args = ["diff", "-U0", "--no-color", base] + ([head] if head else []) + ["--", "*.java", "*.sql"]
    result = {}
    path = None
    line_no = 0
    for raw in git(*diff_args).splitlines():
        if raw.startswith("+++ "):
            path = None if raw.endswith("/dev/null") else raw[6:]
            continue
        if raw.startswith("@@"):
            m = re.search(r"\+(\d+)", raw)
            line_no = int(m.group(1)) if m else 0
            continue
        if path and raw.startswith("+") and not raw.startswith("+++"):
            result.setdefault(path, []).append((line_no, raw[1:]))
            line_no += 1
    return result


def added_files(base, head):
    args = ["diff", "--name-only", "--diff-filter=A", base] + ([head] if head else [])
    return set(git(*args).split())


def read_file(path, head):
    try:
        if head:
            return git("show", f"{head}:{path}")
        with open(path, encoding="utf-8") as f:
            return f.read()
    except (subprocess.CalledProcessError, OSError):
        return ""


STATEFUL_TYPE = re.compile(r"@Mock\b[^;]*?\b(\w+(?:Repository|UseCase|QueryService|CommandService))\s+\w+\s*;")
COLLECTION_DECL = re.compile(r"\b(?:List|Set|Collection)<[^=;()]+>\s+(\w+)\s*=")
INSTANT_DECL = re.compile(r"\bInstant\s+(\w+)\s*=")
FQCN = re.compile(r"(?<![\w.\"])(?:java|javax|jakarta|org|com)\.[a-z]\w*(?:\.[a-z]\w*)*\.[A-Z]\w*")
LOG_PII = re.compile(r"\blog\.(?:info|warn|error|debug)\(.*\buserId\b")
DOMAIN_HTTP_IMPORT = re.compile(r"^import .*\.(?:exception\.\w*(?:BadRequest|NotFound|Moneyball|Conflict|Forbidden)\w*Exception|ExceptionConstants|web\.)")
COMMENT_PLAIN = re.compile(r"[가-힣](?<!니)다\.\s*(\*/)?$")
CONTROLLER_METHOD = re.compile(r"^\s*public\s+(?!ResponseEntity\b|class\b|interface\b|record\b)([\w<>, ?]+)\s+\w+\s*\(")
ALL_ANY_STUB = re.compile(r"(?:given|when)\(\s*\w+\.\w+\(\s*(?:any\w*\(\)\s*,\s*)*any\w*\(\)\s*\)\s*\)")


def lint(base, head):
    findings = []

    def add(level, rule, path, line, message):
        findings.append((level, rule, path, line, message))

    lines_by_file = changed_lines(base, head)
    new_files = added_files(base, head)

    for path, lines in lines_by_file.items():
        anchored = "/" + path  # 저장소 루트의 src/test/·domain/ 경로도 판정되게 앞에 / 를 붙인다
        is_test = "/src/test/" in anchored
        is_java = path.endswith(".java")
        content = read_file(path, head) if is_java else ""
        is_spring_test = any(a in content for a in ("@SpringBootTest", "@WebMvcTest", "@DataJpaTest", "AcceptanceSupport"))

        for line, text in lines:
            stripped = text.strip()
            if stripped.startswith(("//", "*", "/*")):
                # 코드 주석은 존댓말 (java-spring-coder v1.16, #791). 평서형 "~다." 로 끝나는 주석만 잡는다
                if is_java and COMMENT_PLAIN.search(stripped):
                    add("확인", "NAMING", path, line, "코드 주석이 평서형(~다.)으로 끝난다. 주석은 존댓말(~합니다.)로 쓴다")
                continue

            if is_java and not stripped.startswith(("import ", "package ")) and FQCN.search(text) and "@Schema" not in text and '"' not in text:
                add("위반", "FQCN", path, line, "패키지 경로를 본문에 쓰지 말고 import 한다")

            if is_java and LOG_PII.search(text):
                add("위반", "PII", path, line, "로그 본문에 userId 를 넣지 않는다 (MDC 에 있음)")

            if is_java:
                m = COLLECTION_DECL.search(text)
                if m and not re.search(r"(List|Set|Collection|Ids|Map)$", m.group(1)):
                    add("확인", "NAMING", path, line, f"컬렉션 변수 '{m.group(1)}' 는 요소 타입+List 로 이름 짓는다 (예: xxxEntityList)")
                m = INSTANT_DECL.search(text)
                if m and not re.search(r"(At|_AT)$", m.group(1)):
                    add("확인", "NAMING", path, line, f"시각 변수 '{m.group(1)}' 는 At 접미사를 붙인다 (예: currentAt)")
                if "Collectors.toMap(" in text:
                    add("확인", "RR-13", path, line, "toMap 은 value null·키 중복에 예외를 던진다. 데이터 한 건이 응답 전체를 깨뜨리지 않는지 확인")

            if is_test:
                m = STATEFUL_TYPE.search(text)
                if m and not is_spring_test:
                    add("위반", "RR-12", path, line, f"단위 테스트에서 상태를 가진 {m.group(1)} 를 @Mock 으로 둔다. 규칙 08: Fake 우선")
                if "lenient()" in text:
                    add("확인", "RR-12", path, line, "lenient 스텁이 검증하려던 분기를 가리지 않는지 확인 (예외 분기 미실행)")
                if ALL_ANY_STUB.search(text):
                    add("확인", "RR-12", path, line, "인자를 전부 any() 로 받는 스텁은 인자가 바뀌어도 통과한다. 핵심 인자는 값·isNull() 로 고정")
                if ".doesNotExist()" in text:
                    add("확인", "RR-12", path, line, "doesNotExist() 는 JSON null 도 통과한다. 키 부재는 doesNotHaveJsonPath()")
                if ".asBoolean()" in text or ".asText()" in text or ".asInt()" in text:
                    add("확인", "RR-12", path, line, "asXxx() 는 null·타입 불일치를 기본값으로 바꾼다. isBoolean()/isTextual() 로 타입부터 확인")
                if re.search(r"jsonPath\([^)]*\)\.isEmpty\(\)", text):
                    add("확인", "RR-12", path, line, "isEmpty() 는 빈 객체·배열·문자열도 통과한다. null 계약이면 value(nullValue())")

            if is_java and "/domain/" in anchored and not is_test and DOMAIN_HTTP_IMPORT.search(stripped):
                add("위반", "LAYER", path, line, "domain 패키지가 HTTP 예외·에러 코드·web 을 참조한다. 예외는 application/exception 으로")

            if is_java and not is_test and re.search(r"Controller(V\d+)?\.java$", path):
                if CONTROLLER_METHOD.search(text) and "@RestController" in content:
                    add("확인", "LAYER", path, line, "이 컨트롤러 메서드는 ResponseEntity 를 반환하지 않는다. 규칙 05 는 ResponseEntity 반환. 같은 파일 기존 관례를 따른 것이면 PR 본문에 사유")

        if path.endswith(".sql") and "/db/migration/" in anchored and path in new_files:
            first = read_file(path, head).lstrip().splitlines()[:1]
            if not first or "Copyright" not in first[0]:
                add("위반", "RR-11", path, 1, "신규 마이그레이션 첫 줄에 Copyright 헤더가 없다 (flyway_preflight 실패)")

    return findings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="origin/dev")
    parser.add_argument("--head", default=None)
    args = parser.parse_args()

    try:
        base = git("merge-base", args.base, args.head or "HEAD").strip()
    except subprocess.CalledProcessError:
        print(f"review-lint: 기준 '{args.base}' 와 공통 조상을 찾지 못했다. git fetch 후 다시 실행한다")
        return 2
    findings = lint(base, args.head)
    if not findings:
        print("review-lint: 지적 0건")
        return 0

    findings.sort(key=lambda f: (f[0] != "위반", f[2], f[3]))
    for level, rule, path, line, message in findings:
        print(f"[{level}][{rule}] {path}:{line} {message}")
    violations = sum(1 for f in findings if f[0] == "위반")
    print(f"\nreview-lint: 위반 {violations}건, 확인 {len(findings) - violations}건")
    print("위반은 고치고, 확인은 해당 없으면 PR 본문이나 답글에 사유를 남긴다. 상세: review-recurrence-guard.md (forge/common, 배포본 .claude/shared)")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
