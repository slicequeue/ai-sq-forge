#!/usr/bin/env python3
"""번역팀 langSKILL 기준으로 번역 길이를 검사한다.

번역팀은 Figma 에서 실제 렌더링 폭을 알 수 없어 **글자 수 비율**을 근사 필터로 쓴다.
  en  원문 대비 1.2배 이하
  ja  원문 대비 0.9배 이하

이 저장소는 properties 를 직접 읽으므로 표시 폭(전각 2, 반각 1)도 같이 계산해서 보여준다.
둘이 어긋나면(예: 글자 수는 통과인데 표시 폭이 2배) 사람이 화면에서 확인해야 한다.

사용:
  check_ratio.py                           # 저장소 전체
  check_ratio.py --bundle message-pghd
  check_ratio.py --key alarm.member_deregister
  check_ratio.py --lang ja
  check_ratio.py --all                     # 위반뿐 아니라 전건 출력
"""
import argparse
import glob
import os
import sys
import unicodedata

# langSKILL.md `## 공통 규칙` > 길이 검수
LIMIT = {"en": 1.2, "ja": 0.9}
WIDE = ("W", "F")


def width(s: str) -> int:
    return sum(2 if unicodedata.east_asian_width(c) in WIDE else 1 for c in s)


def load(path: str) -> dict:
    """properties 를 읽는다. 역슬래시 계속 줄과 주석을 처리한다."""
    out, buf = {}, ""
    try:
        text = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        return out
    for line in text.splitlines():
        s = line.strip()
        if buf:
            buf += s.rstrip("\\")
            if not s.endswith("\\"):
                k, _, v = buf.partition("=")
                out[k.strip()] = v.strip()
                buf = ""
            continue
        if not s or s.startswith(("#", "!")) or "=" not in s:
            continue
        if s.endswith("\\"):
            buf = s.rstrip("\\")
            continue
        k, _, v = s.partition("=")
        out[k.strip()] = v.strip()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--bundle", help="번들 이름 일부로 필터")
    ap.add_argument("--key", help="키 이름 일부로 필터")
    ap.add_argument("--lang", choices=("en", "ja"), help="한 언어만")
    ap.add_argument("--min-chars", type=int, default=4,
                    help="원문이 이 글자 수 미만이면 비율이 쉽게 튀므로 제외")
    ap.add_argument("--all", action="store_true", help="위반이 아닌 건도 출력")
    args = ap.parse_args()

    pattern = os.path.join(args.root, "*/src/main/resources/messages/*.properties")
    rows = []
    for base in sorted(glob.glob(pattern)):
        if "_en_US" in base or "_ja_JP" in base:
            continue
        name = os.path.basename(base)[: -len(".properties")]
        if args.bundle and args.bundle not in name:
            continue
        ko = load(base)
        for suffix, lang in (("_en_US", "en"), ("_ja_JP", "ja")):
            if args.lang and lang != args.lang:
                continue
            tr = load(base.replace(".properties", suffix + ".properties"))
            for key, src in ko.items():
                if args.key and args.key not in key:
                    continue
                dst = tr.get(key, "")
                if not src.strip() or not dst.strip():
                    continue
                if len(src) < args.min_chars:
                    continue
                rows.append({
                    "ratio": len(dst) / len(src),
                    "wratio": width(dst) / width(src) if width(src) else 0.0,
                    "lang": lang, "bundle": name, "key": key,
                    "src": src, "dst": dst,
                })

    rows.sort(key=lambda r: r["ratio"], reverse=True)
    over = [r for r in rows if r["ratio"] > LIMIT[r["lang"]]]
    shown = rows if args.all else over

    print(f"비교 대상 {len(rows)}쌍 (원문 {args.min_chars}자 이상)")
    print(f"기준 초과 {len(over)}건  —  en ≤ {LIMIT['en']}배, ja ≤ {LIMIT['ja']}배 (글자 수)\n")
    for r in shown:
        flag = "!" if r["ratio"] > LIMIT[r["lang"]] else " "
        print(f"{flag}x{r['ratio']:.2f} (폭 x{r['wratio']:.2f}) [{r['lang']}] {r['bundle']} :: {r['key']}")
        print(f"      ko({len(r['src']):>3}자) {r['src']}")
        print(f"      {r['lang']}({len(r['dst']):>3}자) {r['dst']}")
    if over:
        print("\n초과분은 더 짧은 대안을 함께 제시하고, 이 저장소에는 태그 기능이 없으므로 PR 본문에 키와 수치를 적는다.")
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main())
