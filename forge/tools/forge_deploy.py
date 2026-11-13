#!/usr/bin/env python3
"""forge-deploy v1.3 실행 보조 (2026-11-13 사이클 9 에서 실배포에 사용). 리허설·실배포 공용.

사용:
  forge_deploy.py --forge FORGE --target TARGET [--apply] [--backup DIR]
  --apply 없으면 계획만 출력(dry-run).
대상 컴포넌트: 대상 .claude 에 이미 배포된 것 중 forge 에 있는 것(--sync 의미) + --add 로 지정한 것.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

FORGE_ONLY_COMMANDS = {"forge-deploy", "eval-harness", "forge-upstream"}
UPSTREAM_ONLY = {"chat-incident-report"}
# 프로젝트별 배포 제외 (anvil/INDEX.md Deploy Registry 기록)
EXCLUDE = {
    "pasta-japan-server": {"commands/git-pr.md", "commands/git-worktree-add.md"},
}

REMAP = [
    (re.compile(r"forge/common/pasta-rules/"), ".claude/rules/"),
    (re.compile(r"forge/common/"), ".claude/shared/"),
    (re.compile(r"anvil/agents/([\w-]+)/\1\.md"), r".claude/agents/\1.md"),
    (re.compile(r"anvil/agents/"), ".claude/agents/"),
    (re.compile(r"anvil/skills/"), ".claude/skills/"),
    (re.compile(r"anvil/commands/"), ".claude/commands/"),
]
# 리매핑 후 "X(배포본 X)" 처럼 같은 경로가 두 번 나오는 표기를 하나로 줄인다
DUP = re.compile(r"(`?)(\.claude/[^\s`()]+)\1\s*\((?:배포본|실전 배포:?)\s*`?\2`?\)")
TEXT_EXT = {".md", ".py", ".sh", ".txt", ".yml", ".yaml", ".json"}


def remap(text):
    for pattern, repl in REMAP:
        text = pattern.sub(repl, text)
    return DUP.sub(r"\1\2\1", text)


def org_of(target):
    try:
        url = subprocess.run(["git", "-C", target, "remote", "get-url", "origin"], capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError:
        return None
    return "virtualcare" if "virtualcare/" in url else url.strip()


def guide_ref(forge):
    text = open(os.path.join(forge, "forge/common/vc-conventions-guide.md"), encoding="utf-8").read()
    m = re.search(r"커밋 `([0-9a-f]{7,})`", text)
    return m.group(1) if m else None


def source_commit(forge):
    path = os.path.join(forge, "forge/common/vc-conventions/SOURCE")
    if not os.path.exists(path):
        return None
    m = re.search(r"^commit: (\S+)", open(path, encoding="utf-8").read(), re.M)
    return m.group(1) if m else None


def plan(forge, target, add):
    name = os.path.basename(target.rstrip("/"))
    claude = os.path.join(target, ".claude")
    items = []  # (src, dst, kind)
    excluded = EXCLUDE.get(name, set())

    for kind in ("skills", "agents", "commands"):
        tdir = os.path.join(claude, kind)
        if not os.path.isdir(tdir):
            continue
        for entry in sorted(os.listdir(tdir)):
            base = entry[:-3] if entry.endswith(".md") else entry
            rel = f"{kind}/{entry}"
            if rel in excluded or base in UPSTREAM_ONLY or (kind == "commands" and base in FORGE_ONLY_COMMANDS):
                continue
            if kind == "skills":
                src = os.path.join(forge, "anvil/skills", base)
                if os.path.isdir(src):
                    items.append((src, os.path.join(tdir, base), "skill"))
            elif kind == "agents":
                src = os.path.join(forge, "anvil/agents", base, base + ".md")
                if os.path.isfile(src) and entry.endswith(".md"):
                    items.append((src, os.path.join(tdir, entry), "agent"))
            else:
                src = os.path.join(forge, "anvil/commands", entry)
                if os.path.isfile(src):
                    items.append((src, os.path.join(tdir, entry), "command"))
    for spec in add:
        kind, base = spec.split("/", 1)
        if kind == "skills":
            items.append((os.path.join(forge, "anvil/skills", base), os.path.join(claude, "skills", base), "skill"))
        elif kind == "commands":
            items.append((os.path.join(forge, "anvil/commands", base + ".md"), os.path.join(claude, "commands", base + ".md"), "command"))
        elif kind == "agents":
            items.append((os.path.join(forge, "anvil/agents", base, base + ".md"), os.path.join(claude, "agents", base + ".md"), "agent"))

    common = os.path.join(forge, "forge/common")
    shared = os.path.join(claude, "shared")
    for f in ("destructive-write-guard.md", "scope-discipline-guard.md", "review-recurrence-guard.md",
              "negative-tc-catalog.md", "review-lint.py", "review-lint-push-hook.sh",
              "share-writing-guard.md", "share-lint.py"):
        items.append((os.path.join(common, f), os.path.join(shared, f), "common"))

    org = org_of(target)
    vc_note = "비대상"
    if org == "virtualcare":
        ref, src_commit = guide_ref(forge), source_commit(forge)
        if not src_commit:
            sys.exit("중단: forge/common/vc-conventions/SOURCE 없음. vc-conventions-sync.sh 먼저 실행")
        if not ref or not src_commit.startswith(ref[:7]) and not ref.startswith(src_commit[:7]):
            sys.exit(f"중단: 원문 커밋 {src_commit} 과 가이드 기준 {ref} 불일치")
        items.append((os.path.join(common, "vc-conventions-guide.md"), os.path.join(shared, "vc-conventions-guide.md"), "common"))
        items.append((os.path.join(common, "vc-conventions"), os.path.join(shared, "vc-conventions"), "common-dir-raw"))
        vc_note = f"배포 (원문 {src_commit})"
    elif os.path.exists(os.path.join(shared, "vc-conventions-guide.md")):
        vc_note = "[확인] 조직 밖 저장소에 조직 컨벤션 잔존"
    return items, org, vc_note


def write_tree(src, dst, raw):
    if os.path.isdir(src):
        for root, _, files in os.walk(src):
            for fname in files:
                if fname == ".DS_Store" or "__pycache__" in root:
                    continue
                s = os.path.join(root, fname)
                d = os.path.join(dst, os.path.relpath(s, src))
                write_file(s, d, raw)
    else:
        write_file(src, dst, raw)


def write_file(src, dst, raw):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not raw and os.path.splitext(src)[1] in TEXT_EXT:
        text = open(src, encoding="utf-8").read()
        open(dst, "w", encoding="utf-8").write(remap(text))
        shutil.copymode(src, dst)
    else:
        shutil.copy2(src, dst)


def backup(target, backup_dir, items):
    claude = os.path.join(target, ".claude")
    for _, dst, _ in items:
        if os.path.exists(dst):
            rel = os.path.relpath(dst, claude)
            bdst = os.path.join(backup_dir, rel)
            os.makedirs(os.path.dirname(bdst), exist_ok=True)
            if os.path.isdir(dst):
                shutil.copytree(dst, bdst, dirs_exist_ok=True)
            else:
                shutil.copy2(dst, bdst)


def verify(target, items, org):
    problems = []
    ref_pat = re.compile(r"\.claude/(shared|rules|skills|agents|commands)/[\w./-]+?\.(md|py|sh)\b")
    for _, dst, kind in items:
        paths = []
        if os.path.isdir(dst):
            for root, _, files in os.walk(dst):
                paths += [os.path.join(root, f) for f in files if f.endswith((".md", ".py", ".sh"))]
        elif os.path.exists(dst):
            paths.append(dst)
        for p in paths:
            if "/vc-conventions/" in p:
                continue
            text = open(p, encoding="utf-8", errors="ignore").read()
            for m in re.finditer(r"(?<![\w/])(forge/common/|anvil/(skills|agents|commands)/)", text):
                line = text.count("\n", 0, m.start()) + 1
                problems.append(f"forge 경로 잔존 {os.path.relpath(p, target)}:{line}")
            for m in ref_pat.finditer(text):
                ref = m.group(0)
                if "{" in ref or "*" in ref:
                    continue
                if org != "virtualcare" and "/vc-conventions" in ref:
                    continue  # 조직 밖 저장소: 가이드 부재가 곧 '비적용' 판정이다(설계 의도)
                if not os.path.exists(os.path.join(target, ref)):
                    line = text.count("\n", 0, m.start()) + 1
                    problems.append(f"참조 대상 없음 {os.path.relpath(p, target)}:{line} → {ref}")
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--forge", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--backup")
    ap.add_argument("--add", action="append", default=[])
    args = ap.parse_args()

    items, org, vc_note = plan(args.forge, args.target, args.add)
    print(f"대상: {args.target}\n조직: {org}\n조직 컨벤션: {vc_note}\n항목 {len(items)}개")
    for src, dst, kind in items:
        print(f"  [{kind}] {os.path.relpath(src, args.forge)} → {os.path.relpath(dst, args.target)}")
    if not args.apply:
        return 0
    if not args.backup:
        sys.exit("중단: --apply 에는 --backup 필수")
    backup(args.target, args.backup, items)
    for src, dst, kind in items:
        write_tree(src, dst, raw=(kind == "common-dir-raw"))
    problems = verify(args.target, items, org)
    print(f"\n검증: 문제 {len(problems)}건")
    for p in problems:
        print("  " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
