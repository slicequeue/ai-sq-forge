#!/usr/bin/env python3
"""ko / en_US / ja_JP 키 집합이 일치하는지 검사하고, 파일 파손도 함께 잡는다.

번들은 useCodeAsDefaultMessage=true 로 동작해서 키가 없으면 조용히 한국어로 폴백한다.
번역 누락이 런타임에도 드러나지 않으므로 파일 단위로 직접 비교해야 한다.

함께 잡는 파손 유형:
  - 값 없는 키: 여러 줄 값에서 줄 끝 역슬래시가 빠져 다음 줄이 키로 파싱되는 경우
  - 번역 메모가 값으로 들어간 경우
  - (v0.4) 플레이스홀더 불일치: 원문과 번역의 {0} {1} 개수·번호가 다른 경우
  - (v0.4) 따옴표 경고: {0} 이 있는 값에 홑따옴표가 하나로 들어간 경우.
    MessageFormat 은 ' 를 인용 기호로 읽어서 You've {0} 의 {0} 이 치환되지 않는다. '' 로 써야 한다

저장소 루트에서 실행한다(--root 기본값 "."). 스크립트 경로는 스킬 위치 기준으로 준다.
  python3 .claude/skills/i18n-translate/scripts/check_parity.py --bundle message-pghd

사용:
  check_parity.py                # 전체
  check_parity.py --bundle message-pghd
"""
import argparse, glob, os, re, sys
from collections import Counter

PLACEHOLDER = re.compile(r"\{\d+[^}]*\}")


def values(path: str) -> dict:
    """키 → 값. 역슬래시 계속 줄을 이어 붙인다. 플레이스홀더·따옴표 검사용."""
    out, buf, key = {}, "", None
    try:
        text = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        return out
    for line in text.splitlines():
        s = line.strip()
        if key is not None:
            buf += s[:-1] if s.endswith("\\") else s
            if not s.endswith("\\"):
                out[key], key, buf = buf, None, ""
            continue
        if not s or s.startswith(("#", "!")):
            continue
        m = re.match(r"([^=:]+)[=:](.*)", s)
        if not m:
            continue
        k, v = m.group(1).strip(), m.group(2).strip()
        if v.endswith("\\"):
            key, buf = k, v[:-1]
        else:
            out[k] = v
    return out


def placeholder_problems(name: str, suffix: str, ko_vals: dict, tr_vals: dict):
    for k, src in ko_vals.items():
        dst = tr_vals.get(k)
        if dst is None:
            continue
        a = Counter(p.split(",")[0] + "}" if "," in p else p for p in PLACEHOLDER.findall(src))
        b = Counter(p.split(",")[0] + "}" if "," in p else p for p in PLACEHOLDER.findall(dst))
        if a != b:
            yield f"[플레이스홀더] {name}{suffix} :: {k}  원문 {sorted(a.elements())} / 번역 {sorted(b.elements())}"
        if b and re.search(r"(?<!')'(?!')", dst):
            yield f"[따옴표] {name}{suffix} :: {k}  {{N}} 이 있는 값의 홑따옴표는 '' 로 써야 한다"


def parse(path: str):
    """(키집합, 파손줄목록) 을 돌려준다."""
    keys, broken, buf = set(), [], ""
    try:
        text = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        return None, []
    for no, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if buf:
            if not s.endswith("\\"):
                buf = ""
            continue
        if not s or s.startswith(("#", "!")):
            continue
        if not re.match(r"[^=:]+[=:]", s):
            broken.append((no, s[:70]))
            continue
        keys.add(re.match(r"([^=:]+)[=:]", s).group(1).strip())
        if s.endswith("\\"):
            buf = s
    return keys, broken


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--bundle")
    args = ap.parse_args()

    problems = 0
    for base in sorted(glob.glob(os.path.join(args.root, "*/src/main/resources/messages/*.properties"))):
        if "_en_US" in base or "_ja_JP" in base:
            continue
        name = os.path.basename(base)[:-len(".properties")]
        if args.bundle and args.bundle not in name:
            continue
        ko, ko_broken = parse(base)
        if ko is None:
            continue
        for no, text in ko_broken:
            print(f"[파손] {name}.properties:{no}  {text}")
            problems += 1
        if not ko:
            print(f"[빈 번들] {name}.properties 에 키가 없다")
            continue
        for suffix in ("_en_US", "_ja_JP"):
            tr, tr_broken = parse(base.replace(".properties", suffix + ".properties"))
            for no, text in tr_broken:
                print(f"[파손] {name}{suffix}.properties:{no}  {text}")
                problems += 1
            if tr is None:
                print(f"[없음] {name}{suffix}.properties 파일이 없다")
                problems += 1
                continue
            for k in sorted(ko - tr):
                print(f"[누락] {name}{suffix} :: {k}")
                problems += 1
            for k in sorted(tr - ko):
                print(f"[고아] {name}{suffix} :: {k}  (기본 번들에 없음)")
                problems += 1
            for msg in placeholder_problems(name, suffix, values(base),
                                            values(base.replace(".properties", suffix + ".properties"))):
                print(msg)
                problems += 1
    print(f"\n문제 {problems}건")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
