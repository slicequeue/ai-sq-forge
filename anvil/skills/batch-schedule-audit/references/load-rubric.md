# 부하/무게 산정 기준

원칙: **무게 = 부하량 × 점유시간(duration)**, 자원별 구분. 단일 점수가 아니라 "어느 자원을 × 얼마나 세게 × 얼마나 오래".

---

## 부하 축 (코드에서 확인)

| 축 | 필드 | HIGH 신호 |
|---|---|---|
| A 스캔 규모 | `scan_scope` | ALL(전체 유저·레코드) > SUBSET(조건 한정) > SMALL |
| B 쿼리 위험 | `query_risk` | 풀스캔, 무범위 날짜, 무거운 조인·서브쿼리, N+1, 인덱스 부재 |
| C 처리 방식 | `chunking` | BULK(한 번에 메모리 로딩) 위험 / CHUNK·PAGED(size) 안전. size도 기록 |
| D 쓰기량 | `write_volume` | 대량 INSERT/UPDATE/DELETE, 트랜잭션 길이, 락 경합 |
| E 외부 I/O | `external_io` | 푸시 멀티캐스트, 외부 API 건수, Cloud Tasks enqueue, ES bulk |
| F 빈도 | `freq_per_day` | 매분(1440)·5분(288)·10분(144) = 상시 baseline. 1회 가벼워도 누적이 큼 |
| G 점유시간 | `est_duration` | SHORT(<1m) / MED(수분) / LONG(수십 분 이상). 정적 추정, 실측 권장 |

---

## 리소스 한도 = 독립 근거

CPU·메모리 한도(`collect.sh` 의 cpu/memory 컬럼)는 **배포 스펙**(`gcloud describe`)에서 온다. 코드나 IaC에 없는 경우가 많다(배포 워크플로에 플래그 없이 콘솔·gcloud로 수동 설정). 즉 16Gi·8Gi 할당은 운영자가 OOM·타임아웃을 겪고 키운 **경험적 사이징**이므로 무게의 강한 프록시다.

**교차검증 규칙**

| 리소스 한도 | 코드 부하 팩터 | 판정 |
|---|---|---|
| 큼 | 큼 | 진짜 Heavy |
| 큼 | 빈약 | 과할당 의심 (예: 구현체가 없는데 8Gi) |
| 작음 | 큼 | **OOM 리스크 경고** |
| 작음 | 빈약 | Light 확정 |

---

## 무게 등급

- **Heavy**: (ALL 스캔 또는 대량 쓰기 또는 외부 bulk) × (LONG 또는 고빈도). 리소스는 보통 4Gi 이상.
- **Medium**: SUBSET + PAGED + 중간 쓰기·외부, MED 점유.
- **Light**: SMALL·단순 DELETE·토큰 갱신, SHORT.
- 고빈도(F) 잡은 1회 Light라도 누적으로 **Heavy 승격** 가능 (예: 5분마다 PRIMARY 쓰기).

모든 등급은 근거와 함께 적는다. 근거 없는 등급은 하드 가드레일 위반이다.

---

## 산출 컬럼 (부하 프로파일 CSV)

```
cloud_run_job, scheduled, schedule_kst, schedule_cron, timezone, cpu, memory,
read_db, write_db, scan_scope, query_risk, chunking, write_volume, external_io,
est_duration, weight, freq_per_day, notes
```

`notes` 에는 무게 판단의 **코드 근거(file:line·쿼리·청크 size)** 를 1줄로.

---

## cron → KST 환산

타임존이 `Etc/UTC` 면 **+9시간**. `Asia/Seoul` 이면 그대로.

| cron (UTC) | KST |
|---|---|
| `0 23 * * *` | 08:00 |
| `0 15 * * *` | 00:00 (익일) |
| `30 19 * * *` | 04:30 (익일) |

주기 표기 해석

| 표기 | 의미 |
|---|---|
| `*/5` | 5분마다 (하루 288회) |
| `50 7-21 * * *` | 07~21시 매시 50분 |
| `0 9 1 * *` | 매월 1일 09시 |
| `2-59/5` | 정시를 피한 5분 주기 (정시 대형 잡과의 겹침 회피용) |

날짜 넘김(`0 15 * * *` → 익일 00:00)을 놓치면 타임라인이 하루 밀린다. 환산 결과를 KST 기준으로 정렬한 뒤 검토한다.
