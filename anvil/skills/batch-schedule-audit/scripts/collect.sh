#!/usr/bin/env bash
# Cloud Run Jobs + Cloud Scheduler 현황 수집기 (배치 감사용)
# 사용법:
#   bash collect.sh <PROJECT> <REGION> [OUTDIR]
# 예:
#   bash collect.sh my-gcp-project asia-northeast3 ./batch-audit-out
#
# 출력:
#   <OUTDIR>/jobs.json       : Cloud Run Jobs 원본(json, 1회 호출)
#   <OUTDIR>/schedulers.csv  : trigger, target_job, schedule_cron, timezone, state, uri
#   <OUTDIR>/joined.csv      : cloud_run_job, scheduled, schedule_cron, timezone, job_name, summary_profile, cpu, memory, args
set -uo pipefail

# ── 인자 필수 (프로젝트 하드코딩 금지) ──────────────────────────────────
if [ $# -lt 2 ]; then
  cat >&2 <<'EOF'
ERROR: PROJECT와 REGION은 필수 인자입니다.
    bash collect.sh <PROJECT> <REGION> [OUTDIR]
현재 설정값 확인:
    gcloud config get-value project
EOF
  exit 1
fi

PROJECT="$1"
REGION="$2"
OUTDIR="${3:-./batch-audit-out}"
# 자원 전환 프로파일 이름 (프로젝트마다 다름. 없으면 판별 결과가 전부 '-')
PROFILE_MARKER="${PROFILE_MARKER:-summary}"
mkdir -p "$OUTDIR"

# ── 0. gcloud 설치·인증 확인 ────────────────────────────────────────────
if ! command -v gcloud >/dev/null 2>&1; then
  echo "ERROR: gcloud CLI 미설치. https://cloud.google.com/sdk/docs/install" >&2; exit 2
fi
ACCOUNT="$(gcloud config get-value account 2>/dev/null)"
if [ -z "$ACCOUNT" ] || [ "$ACCOUNT" = "(unset)" ]; then
  cat >&2 <<'EOF'
ERROR: gcloud 인증이 안 되어 있습니다. 다음을 직접 실행해 로그인하세요:
    gcloud auth login                          # 브라우저 인증
    gcloud auth application-default login      # (ADC 필요 시)
로그인 후 다시 실행하세요.
EOF
  exit 3
fi
if ! gcloud projects describe "$PROJECT" >/dev/null 2>&1; then
  echo "ERROR: '$ACCOUNT' 계정으로 '$PROJECT' 접근 불가. 권한 확인 또는 gcloud config set project $PROJECT" >&2; exit 4
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 필요(json 파싱)." >&2; exit 5
fi
echo "OK: account=$ACCOUNT project=$PROJECT region=$REGION profile_marker=$PROFILE_MARKER"

# ── 1. Cloud Run Jobs (단일 json 호출) ─────────────────────────────────
echo "[1/3] Cloud Run Jobs 수집..."
gcloud run jobs list --project="$PROJECT" --format=json 2>/dev/null > "$OUTDIR/jobs.json"
JOB_COUNT=$(python3 -c "import json;print(len(json.load(open('$OUTDIR/jobs.json'))))" 2>/dev/null || echo 0)
echo "  jobs: $JOB_COUNT"

# ── 2. Cloud Scheduler 트리거 ──────────────────────────────────────────
echo "[2/3] Cloud Scheduler 수집..."
echo "trigger,target_job,schedule_cron,timezone,state,uri" > "$OUTDIR/schedulers.csv"
gcloud scheduler jobs list --project="$PROJECT" --location="$REGION" \
  --format="csv[no-heading](name.basename(),schedule,timeZone,state,httpTarget.uri)" 2>/dev/null \
  | while IFS=, read -r name sched tz state uri; do
      target=$(printf '%s' "$uri" | grep -oE 'jobs/[^:]+:run' | sed -E 's#jobs/##; s#:run##')
      [ -z "$target" ] && target="(non-job)"
      echo "$name,$target,$sched,$tz,$state,$uri" >> "$OUTDIR/schedulers.csv"
    done
SCH_COUNT=$(($(wc -l < "$OUTDIR/schedulers.csv" | tr -d ' ') - 1))
echo "  schedulers: $SCH_COUNT"

# ── 3. 파싱 + 조인 (python) ────────────────────────────────────────────
echo "[3/3] 파싱/조인..."
python3 - "$OUTDIR" "$PROFILE_MARKER" <<'PY'
import json, csv, sys, re
out = sys.argv[1]
marker = sys.argv[2]
jobs = json.load(open(f"{out}/jobs.json"))

# scheduler: target_job -> (cron, tz)
sched = {}
with open(f"{out}/schedulers.csv") as f:
    for r in csv.DictReader(f):
        sched[r["target_job"]] = (r["schedule_cron"], r["timezone"])

rows = []
for j in jobs:
    name = j["metadata"]["name"]
    c = j["spec"]["template"]["spec"]["template"]["spec"]["containers"][0]
    args = " ".join(c.get("args", []))
    m = re.search(r"--job\.name=([^ ;]+)", args)
    jobname = m.group(1) if m else "?"
    env = c.get("env", [])
    prof = marker if any(marker in str(e.get("value", "")) for e in env) else "-"
    lim = (c.get("resources") or {}).get("limits", {})
    cpu = lim.get("cpu", "?"); mem = lim.get("memory", "?")
    if name in sched:
        cron, tz = sched[name]; scheduled = "Y"
    else:
        cron, tz, scheduled = "", "", "N"
    rows.append([name, scheduled, cron, tz, jobname, prof, cpu, mem, args])

rows.sort(key=lambda x: x[0])
with open(f"{out}/joined.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["cloud_run_job","scheduled","schedule_cron","timezone","job_name","summary_profile","cpu","memory","args"])
    w.writerows(rows)

unsched = [r[0] for r in rows if r[1] == "N"]
summ = [r[0] for r in rows if r[5] == marker]
nomap = [r[0] for r in rows if r[4] == "?"]
print(f"  joined rows: {len(rows)}")
print(f"  스케줄 없는 잡({len(unsched)}) — 일회성/폐기/누락 구분 필요: " + ", ".join(unsched))
print(f"  '{marker}' 프로파일({len(summ)}): " + ", ".join(summ))
print(f"  --job.name 미검출({len(nomap)}) — args 규약 확인 필요: " + ", ".join(nomap))
PY

echo
echo "완료. 결과: $OUTDIR/joined.csv (메인), jobs.json, schedulers.csv"
echo "[요약] Jobs=$JOB_COUNT  Schedulers=$SCH_COUNT"
echo "다음: references/code-mapping.md 로 job_name → 코드 매핑, load-rubric.md 로 부하 산정"
