#!/usr/bin/env python3
"""공유 글 작성 가드(share-writing-guard.md) 기계 검사.

사용:
  python3 share-lint.py 파일.md            # A 등급(공유 글) 기준
  python3 share-lint.py --grade B 보고서.md  # B 등급(남는 문서): 맨 앞 결론 블록만 형식 검사
  echo "..." | python3 share-lint.py -     # 표준 입력

[위반] 이 있으면 exit 1, 없으면 exit 0. [확인] 은 사람이 판단한다.
"""
import argparse
import re
import sys

STATUS = re.compile(r"(완료|진행 중|막힘)(?:했습니다|됐습니다|되었습니다|입니다)?\s*\(([^)]+)\)")
STAGE_WORDS = re.compile(r"dev|머지|배포|운영|stg|pre|sandbox|로컬|변경 없음|조회만|반영 전|반영|리뷰 전|머지 전|커밋 전|실행 전|작성", re.I)
GREETING = re.compile(r"^(안녕하세요|공유드립니다|공유 드립니다|다름이 아니라)")
EMPTY_FILL = re.compile(r"^\s*(?:[-*•]\s*)?(?:\*\*)?[^:：|]{1,30}?(?:\*\*)?\s*[:：]\s*(없음|해당 없음|해당없음|-|N/?A|n/?a|무)\s*\.?\s*$")
BARE_EMPTY = re.compile(r"^\s*(?:[-*•]\s*)?(없음|해당 없음|해당없음)\s*\.?\s*$")
POLITE = re.compile(r"부탁드려도 될까요|혹시 (시간|괜찮)|시간 되시면|번거로우시겠지만|확인해 주시면 감사|감사합니다")
GUESS = re.compile(r"아마|것 같습니다|것 같아요|문제없을 것|문제 없을 것|추정됩니다|예상됩니다|일 것입니다|일 겁니다")
BULLET = re.compile(r"^\s*[-*•]\s+\S")
NARRATIVE_EMPTY = re.compile(r"(특이사항|이슈|요청|리스크|후속|문제)[^:：]{0,10}[:：].*(없음|없습니다)")
QUOTED = re.compile(r"\"[^\"]*\"|“[^”]*”|'[^']*'|‘[^’]*’|`[^`]*`")


def strip_frontmatter(lines):
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return lines[i + 1:], i + 1
    return lines, 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--grade", choices=["A", "B"], default="A")
    args = parser.parse_args()

    text = sys.stdin.read() if args.path == "-" else open(args.path, encoding="utf-8").read()
    raw_lines = text.splitlines()
    lines, offset = strip_frontmatter(raw_lines)
    findings = []

    def add(level, rule, lineno, message):
        findings.append((level, rule, lineno, message))

    # 첫 줄 결정: 빈 줄과(B 등급은) 마크다운 제목을 건너뛴다
    first_idx = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if args.grade == "B" and stripped.startswith("#"):
            continue
        first_idx = i
        break

    if first_idx is None:
        add("위반", "SW-1", 1, "본문이 비어 있다")
    else:
        first = lines[first_idx].strip().lstrip("#").strip().strip("*").strip()
        lineno = first_idx + 1 + offset
        if GREETING.search(first):
            add("위반", "SW-1", lineno, "첫 줄이 인사말이다. 첫 줄에 결론과 반영 단계를 쓴다")
        match = STATUS.search(first)
        if not match:
            add("위반", "SW-1", lineno, "첫 줄에 '{무엇을} 완료|진행 중|막힘 ({반영 단계})' 형식이 없다")
        else:
            stage = match.group(2)
            if not STAGE_WORDS.search(stage):
                add("확인", "SW-1", lineno, f"괄호 안 '{stage}' 가 반영 단계(dev / 머지, 배포 확인 전 / 운영 반영)로 읽히지 않는다")
            if "운영" in stage and "전" not in stage:
                add("확인", "SW-5", lineno, "운영 반영이라고 썼다. 배포를 직접 확인한 근거가 본문에 있는지 본다")

        if args.grade == "A":
            bullets = 0
            for line in lines[first_idx + 1:]:
                if not line.strip():
                    if bullets:
                        break
                    continue
                if BULLET.match(line):
                    bullets += 1
                else:
                    break
            if bullets == 0:
                add("확인", "SW-2", lineno + 1, "첫 줄 아래에 한 일 불릿이 없다")
            elif bullets > 4:
                add("확인", "SW-2", lineno + 1, f"한 일 불릿이 {bullets}줄이다. 2~4줄로 줄인다")

    in_fence = False
    for i, line in enumerate(lines):
        lineno = i + 1 + offset
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.lstrip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if any(c in ("없음", "해당 없음", "해당없음") for c in cells):
                add("확인", "SW-6", lineno, "표 칸을 '없음'으로 채웠다. 행이나 열을 빼는 편이 나은지 본다")
            continue
        if EMPTY_FILL.match(line) or BARE_EMPTY.match(line):
            add("위반", "SW-6", lineno, "없는 내용을 '없음/해당 없음/-' 으로 채웠다. 줄을 뺀다")
        unquoted = QUOTED.sub("", line)  # 인용한 문구(사용자 요청 인용, 코드)는 유추·예의 판정에서 뺀다
        if not (EMPTY_FILL.match(line) or BARE_EMPTY.match(line)) and NARRATIVE_EMPTY.search(unquoted):
            add("확인", "SW-6", lineno, "서술형으로 빈 칸을 채웠다('특이사항: ... 없음'). 내용이 없으면 줄을 뺀다")
        if POLITE.search(unquoted):
            add("확인", "SW-4", lineno, "예의 문구가 있다. 부탁은 원하는 것만 한 줄로")
        if GUESS.search(unquoted):
            add("확인", "SW-7", lineno, "유추 표현이 있다. 확인한 것만 쓰거나 '미확인:' 으로 분리한다")

    for level, rule, lineno, message in findings:
        print(f"[{level}] {rule} {lineno}행: {message}")
    violations = sum(1 for f in findings if f[0] == "위반")
    confirms = len(findings) - violations
    print(f"share-lint: 위반 {violations}건 / 확인 {confirms}건 (상세: share-writing-guard.md, forge/common · 배포본 .claude/shared)")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
