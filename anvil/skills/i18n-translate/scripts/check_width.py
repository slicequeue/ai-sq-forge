#!/usr/bin/env python3
"""한국어 원문과 번역의 표시 폭을 비교한다.

UI 는 한국어 문구 길이에 맞춰 잡혀 있어서, 번역이 길어지면 줄바꿈이나 말줄임이 생긴다.
한글·일본어는 전각이라 글자 수로 비교하면 실제 화면 폭을 못 잡는다. 그래서 전각 2, 반각 1 로 센다.

사용:
  check_width.py                      # 저장소 전체 번들 검사
  check_width.py --bundle message-pghd
  check_width.py --min-ratio 2.0      # 2배 초과만
  check_width.py --key food.request.type.user-custom-creation
"""
import argparse, glob, os, sys, unicodedata

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
    ap.add_argument("--min-ratio", type=float, default=1.5)
    ap.add_argument("--min-width", type=int, default=6, help="한글 표시 폭이 이 값 미만이면 비율이 왜곡되어 제외")
    args = ap.parse_args()

    pattern = os.path.join(args.root, "*/src/main/resources/messages/*.properties")
    rows = []
    for base in sorted(glob.glob(pattern)):
        if "_en_US" in base or "_ja_JP" in base:
            continue
        name = os.path.basename(base)[:-len(".properties")]
        if args.bundle and args.bundle not in name:
            continue
        ko = load(base)
        for suffix, lang in (("_en_US", "en"), ("_ja_JP", "ja")):
            tr = load(base.replace(".properties", suffix + ".properties"))
            for key, src in ko.items():
                if args.key and args.key not in key:
                    continue
                dst = tr.get(key, "")
                if not src.strip() or not dst.strip():
                    continue
                wk = width(src)
                if wk < args.min_width:
                    continue
                rows.append((width(dst) / wk, wk, width(dst), lang, name, key, src, dst))

    rows.sort(reverse=True)
    over = [r for r in rows if r[0] >= args.min_ratio]
    print(f"비교 대상 {len(rows)}쌍 (한글 표시 폭 {args.min_width} 이상)")
    print(f"{args.min_ratio}배 이상 긴 번역 {len(over)}건\n")
    for r in over:
        print(f"x{r[0]:.2f} [{r[3]}] {r[4]} :: {r[5]}")
        print(f"      ko({r[1]:>3}) {r[6]}")
        print(f"      {r[3]}({r[2]:>3}) {r[7]}")
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main())
