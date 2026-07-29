# gcloud 조회·집계·딥링크 스니펫

`<PROJECT>` `<REGION>` `<SERVICE>` `<START>` `<END>` 는 Phase 0에서 확정한 값으로 치환한다. 하드코딩된 예시 값을 그대로 실행하지 않는다.

---

## §1. 수집 (TSV 파일로 저장)

스택트레이스는 제외하고 핵심 4필드만 뽑는다. 컨텍스트에 원본 로그를 통째로 올리지 않는다.

```bash
OUT=<scratchpad>/errlog.tsv
gcloud logging read 'resource.type="cloud_run_revision"
  AND resource.labels.service_name="<SERVICE>"
  AND resource.labels.location="<REGION>"
  AND jsonPayload.level="ERROR"
  AND timestamp>="<START>" AND timestamp<="<END>"' \
  --project=<PROJECT> \
  --format="value(timestamp,jsonPayload.logger_name,jsonPayload.exception.exception_class,jsonPayload.message)" \
  --limit=5000 2>/dev/null > "$OUT"

grep -c '^20' "$OUT"   # 총 ERROR 로그 건수
```

- 인프라 레벨 집계로 확장할 때는 `jsonPayload.level="ERROR"` → `severity>="ERROR"`. **두 기준은 결과가 다르므로 어느 쪽인지 보고서에 명시한다.**
- 앱 로그 스키마가 다르면(`jsonPayload.level`이 없는 프로젝트) 먼저 단건을 `--format=json`으로 떠서 필드명을 확인한 뒤 치환한다.
- 반환 건수가 `--limit` 과 같으면 **절단 의심** → limit을 올리거나 구간을 쪼개고, 절단 사실을 보고서에 적는다.

---

## §2. 유형 분류 (집계)

```bash
# (logger || exception_class) 별 건수
awk -F'\t' '{print $2" || "$3}' "$OUT" | sort | uniq -c | sort -rn

# message 시그니처(앞 90자)별 건수
awk -F'\t' '{print substr($4,1,90)}' "$OUT" | sort | uniq -c | sort -rn

# 시간 분포(UTC 시:분)
awk -F'\t' '{print substr($1,12,5)}' "$OUT" | sort | uniq -c
```

### 중복 로깅 판별

같은 실패가 여러 로거에 기록되는지 확인한다. 동일 시각(초 단위) + 동일 메시지 조각이 여러 `logger_name`으로 나오면 중복이다.

```bash
# 초 단위 시각별 로거 조합 — 같은 초에 2~3개 로거가 반복 등장하면 중복 로깅
awk -F'\t' '{print substr($1,1,19)"\t"$2}' "$OUT" | sort | uniq | awk -F'\t' '{c[$1]=c[$1]" "$2} END{for(k in c) print k, c[k]}' | sort | head -30
```

판별 결과로 **"로그 건수 ÷ 배수 = 실패 이벤트 수"** 를 산정하고, 어느 로거들이 같은 이벤트를 찍는지 보고서에 적는다. 흔한 조합: 예외 핸들러 + AOP Aspect + `AsyncUncaughtExceptionHandler`.

---

## §3. 주목 유형 상세 조회

```bash
# 특정 예외의 메시지 전문 (저장된 파일에서)
awk -F'\t' '$3 ~ /NullPointerException/ {print $1"  ::  "$4}' "$OUT"

# 스택 포함 단건 재조회 (insertId·timestamp는 위 결과에서 확보)
gcloud logging read 'insertId="<ID>" AND timestamp="<TS>"' --project=<PROJECT> --freshness=3d \
  --format="value(severity,resource.labels.revision_name,jsonPayload.exception.stacktrace)" --limit=1
```

- `revision_name`을 함께 떠서 **수정 코드가 배포된 리비전인지** 확인한다. 수정 커밋이 있어도 관측 리비전이 이전이면 "미배포"로 판정한다.
- 재시도 래퍼 예외면 스택에서 `Caused by:` 를 찾아 **원인 예외**를 유형명으로 쓴다.

---

## §4. Cloud Logging 딥링크 생성

URL 인코딩은 python으로 처리한다. `START`/`END`/`insertId`를 실제 값으로 치환한다.

```bash
python3 - <<'PY'
import urllib.parse
PROJ  = "<PROJECT>"
START = "<START>"   # 예: 2026-07-13T15:00:00.000Z
END   = "<END>"
base = ['resource.type = "cloud_run_revision"',
        'resource.labels.service_name = "<SERVICE>"',
        'resource.labels.location = "<REGION>"',
        'jsonPayload.level = "ERROR"']

def link(extra=None, cursor=None):
    q = "\n".join(base + (extra or []))
    enc = urllib.parse.quote(q, safe="")
    u = f"https://console.cloud.google.com/logs/query;query={enc};startTime={START};endTime={END}"
    if cursor:
        u += f";cursorTimestamp={cursor}"
    return u + f"?project={PROJ}"

print("ALL:    ", link())
print("BY_EXC: ", link(['jsonPayload.exception.exception_class = "org.springframework.retry.ExhaustedRetryException"']))
print("BY_MSG: ", link(['jsonPayload.message : "getAsleepData"']))
print("SINGLE: ", link(['insertId = "<ID>"'], cursor="<TS>"))
PY
```

링크 텍스트는 자기설명형으로 쓴다.

| 좋음 | 나쁨 |
|------|------|
| `[구간 내 유형 3 전체(NullPointerException 기준, 12건)](URL)` | `[여기](URL)` |
| `[대표 단건 스택(insertId 1a2b3c, 07-14 02:13 KST)](URL)` | `[로그 링크](URL)` |

---

## §5. 완료 전 검수 (formal-doc-ko)

```bash
REPORT=<보고서 경로>

# 장식 기호 — 0이어야 함
grep -nP "[\x{1F000}-\x{1FAFF}\x{2600}-\x{27BF}\x{2B00}-\x{2BFF}★☆✅❌❓⭐]" "$REPORT"

# 비유·구어 표현 — 없어야 함
grep -nE "좌표|폭주|멈칫|배율|DB 멈춤|멈추기 직전|터졌|난리|엄청" "$REPORT"

# 시각 병기 누락 점검 — KST만 또는 UTC만 쓴 줄 확인
grep -nE "KST" "$REPORT" | grep -v "UTC" | head
```

세 스캔이 모두 통과한 뒤 사용자에게 제출한다.
