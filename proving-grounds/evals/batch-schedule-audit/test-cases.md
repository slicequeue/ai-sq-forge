---
name: batch-schedule-audit
version: 0.1
harness-version: 0.1
last-modified: 2026-07-29
---

# batch-schedule-audit 테스트 케이스

모든 TC는 **시뮬레이션 입력**이다. 실제 `gcloud`·`collect.sh` 실행은 하지 않고, 아래 제공된 `joined.csv` 발췌와 코드 스니펫을 수집 산출물로 간주해 평가한다.

공통 시뮬레이션 환경 (TC-1·2·4·5):

- GCP 프로젝트 `prd-pasta`, 리전 `asia-northeast3`
- 배치 모듈 2개: `batch/`(레거시, `@Component("<jobName>")`), `batch-app/`(Spring Batch `*JobConfig`)
- 토폴로지 문서 `references/topology-moneyball.md` 존재 (2026-06-26 스냅샷)
- 설정 파일 재확인 결과: **PRIMARY `10.60.23.208 / pasta`, REPLICA `10.60.23.12 / pasta`, AGGREGATE `10.60.23.208 / pasta_aggregate`** (문서와 동일, AGGREGATE는 PRIMARY와 동일 호스트)

---

## TC-1: Happy Path — 전체 감사 (자원별 충돌 분석)

- **입력 프롬프트**: "배치 전수 감사해줘. 어느 시간대에 뭐가 겹치는지 정리하고 재배치 제안까지.\n\n(collect.sh 산출 `joined.csv` 발췌 — 8잡)\n```\ncloud_run_job,scheduled,schedule_cron,timezone,job_name,summary_profile,cpu,memory\njob-annual-user-summary-tier,Y,0 16 * * *,Etc/UTC,annualUserSummaryTier,summary,4,8Gi\njob-glucose-daily-stats,Y,0 16 * * *,Etc/UTC,glucoseDailyStatisticsJob,-,4,8Gi\njob-user-tier-recalc,Y,10 16 * * *,Etc/UTC,userTierRecalcJob,-,2,4Gi\njob-mission-daily-push,Y,50 7-21 * * *,Etc/UTC,missionDailyPushJob,-,2,2Gi\njob-token-refresh,Y,*/5 * * * *,Etc/UTC,tokenRefreshJob,-,1,512Mi\njob-es-reindex,Y,0 17 * * *,Etc/UTC,esReindexJob,summary,4,16Gi\njob-cafe24-sync,Y,0 16 * * *,Etc/UTC,cafe24SyncJob,-,2,4Gi\njob-legacy-cleanup,N,,,legacyCleanupJob,-,1,512Mi\n```\n(코드 조사 결과)\n- `annualUserSummaryTier`: `AnnualUserSummaryTierJob.java:41` 전체 유저 스캔(`pastaReplicaJdbcTemplate`), 쓰기는 `pastaMainJdbcTemplate` 로 `user_tier` UPDATE 대량 (`:88`), 청크 없음(BULK)\n- `glucoseDailyStatisticsJob`: `GlucoseDailyStatsJobConfig.java:57` Reader 전체 device 스캔, Writer `analysis_daily_glucose_statistics` 대량 UPSERT, chunk 500\n- `userTierRecalcJob`: `UserTierRecalcJob.java:33` `user_tier` 테이블 대량 UPDATE, chunk 없음\n- `missionDailyPushJob`: FCM 멀티캐스트, 대상 조건 한정(SUBSET), chunk 1000\n- `tokenRefreshJob`: 만료 임박 토큰 UPDATE, SMALL, PRIMARY 쓰기\n- `esReindexJob`: REPLICA 읽기 → Elasticsearch bulk 색인, 쓰기 DB 없음\n- `cafe24SyncJob`: Cafe24 외부 API 호출 + PRIMARY 주문 테이블 INSERT\n- `legacyCleanupJob`: 코드 검색 결과 **해당 job.name 클래스 없음**"
- **기대 결과**:
  - cron → KST 환산: `0 16 * * *` = **01:00 KST**, `10 16` = 01:10, `0 17` = 02:00, `50 7-21` = 16:50~06:50 매시 50분, `*/5` = 5분마다 baseline
  - 자원별 판정: `annualUserSummaryTier` 는 summary 프로파일이지만 **write는 PRIMARY** (`pastaMainJdbcTemplate`) → PRIMARY Heavy로 분류
  - **01:00 KST PRIMARY 충돌 핫스팟**: `annualUserSummaryTier`(PRIMARY write) + `glucoseDailyStatisticsJob`(PRIMARY) + `cafe24SyncJob`(PRIMARY) 3건 동시
  - **`user_tier` 테이블 락 경합**: 01:00 `annualUserSummaryTier` + 01:10 `userTierRecalcJob` — 앞 잡이 LONG(BULK 전체 스캔)이라 10분 내 종료 보장 없음 → 같은 테이블 대량 UPDATE 겹침 위험
  - `esReindexJob`(02:00, REPLICA 읽기 + ES 쓰기)은 **다른 자원** → 충돌 아님. 단 AGGREGATE·PRIMARY 동일 호스트 사실은 명시
  - `tokenRefreshJob` 은 baseline 부하로 별도 표기 + 정시(`:00`) 정렬로 대형 잡과 매번 겹침 지적 → `2-59/5` offset 권고
  - `legacyCleanupJob` 은 스케줄 없음 + 코드 없음 → **폐기 후보** 로 판정하되 일회성·누락 가능성 배제 근거 제시
  - 무게 등급마다 file:line 근거. `esReindexJob` 16Gi vs 코드 부하 교차검증
  - 재배치 변경표(구체 cron) + 코드 수정 항목(BULK → 청크) 분리
  - 정적 추정 한계 + `gcloud run jobs executions list` 실측 명령
- **검증 기준**:
  - [ ] cron → KST 환산 정확 (`0 16 * * *` = 01:00 KST, 날짜 넘김 처리)
  - [ ] `annualUserSummaryTier` write를 PRIMARY로 판정 (프로파일 이름에 속지 않음)
  - [ ] 01:00 KST PRIMARY 충돌 3건 식별
  - [ ] `user_tier` 동일 테이블 락 경합 지적 (01:00 + 01:10, LONG duration 근거)
  - [ ] `esReindexJob` 을 충돌로 오판하지 않음 + 동일 호스트 사실 명시
  - [ ] `tokenRefreshJob` baseline 별도 표기 + 정시 offset 권고
  - [ ] `legacyCleanupJob` 3분류 판정 (폐기 후보 + 근거)
  - [ ] 모든 무게 등급에 file:line 근거
  - [ ] 리소스↔코드 교차검증 언급 (16Gi·8Gi)
  - [ ] 재배치 변경표에 구체 cron 값
  - [ ] cron 변경 / 코드 수정 분리
  - [ ] 정적 추정 한계 + 실측 명령 제시
  - [ ] 장식 기호 0건
- **유형**: happy-path

---

## TC-2: Happy Path — 신규 배치 스케줄 적정성 평가 (단건)

- **입력 프롬프트**: "신규 배치 하나 추가하려는데 몇 시에 돌리면 좋을까?\n\n(신규 잡 정보)\n- 하는 일: 전체 유저의 `user_tier` 를 재계산해서 `user_tier` 테이블에 UPDATE. 읽기는 `user`, `subscription` 조인\n- 규모: 전체 유저(약 120만)\n- 빈도: 1일 1회\n- 코드: 아직 없음 (설계 단계)\n- 기존 배치 현황은 TC-1의 `joined.csv` 와 동일"
- **기대 결과**:
  - 부하 프로파일 산정: ALL 스캔 + 대량 UPDATE + LONG → **Heavy**. 코드 없으므로 **추정임을 명시**
  - 자원 결정: 읽기는 REPLICA 가능(조인 조회), **쓰기는 운영 `user_tier` → PRIMARY 불가피**
  - 충돌 검사: `user_tier` 를 대량 UPDATE 하는 기존 잡이 **2개**(`annualUserSummaryTier` 01:00, `userTierRecalcJob` 01:10) → **동시 실행 절대 회피(락)**. 01:00~02:00 구간 배제
  - 추천 시각: PRIMARY Heavy 없고 트래픽 피크 아닌 구간 제시 (예: 03:30~04:30 KST, cron `30 18 * * *` Etc/UTC). `2-59/5` baseline 잡과의 관계도 언급
  - 리소스 권고: 유사 부하(`annualUserSummaryTier` 4cpu/8Gi) 참고로 초기값 제안, 과소 설정 시 OOM 경고
  - 코드 리스크: 청크·페이징 없으면 스케줄 전 적용 권고, `user_tier` bulk update 쿼리 권장
  - 1줄 결론 형식 + 배포 후 첫 실행 duration 실측 권고
  - **기존 `userTierRecalcJob` 과 기능 중복 가능성**을 지적하고 도메인팀 확인 단서
- **검증 기준**:
  - [ ] 부하 프로파일 A~G 산정 + 코드 부재로 추정 표기
  - [ ] read REPLICA / write PRIMARY 분리 판정
  - [ ] `user_tier` 대량 UPDATE 기존 잡 2건 식별 + 동시 실행 회피 권고
  - [ ] 01:00~02:00 배제 근거 제시
  - [ ] 추천 cron이 구체값 (UTC·KST 병기)
  - [ ] 리소스 초기값 제안 + 유사 잡 근거
  - [ ] 청크·페이징 등 코드 리스크 사전 권고
  - [ ] 1줄 결론 형식 준수
  - [ ] 실측 권고 + 정적 추정 한계
  - [ ] 기능 중복 가능성 지적 + 도메인팀 확인 단서
- **유형**: happy-path

---

## TC-3: Edge Case — 파라미터 오타 + job.name 미검출 + 토폴로지 변경

- **입력 프롬프트**: "배치 현황 정리해줘.\n\n(collect.sh 산출 발췌)\n```\ncloud_run_job,scheduled,schedule_cron,timezone,job_name,summary_profile,cpu,memory,args\njob-meal-review-push,Y,30 10 * * *,Etc/UTC,mealDailyReviewPushJob,-,2,4Gi,--job.name=mealDailyReviewPushJob;locale=ko_KR;fetchSize=500;chinkSize=100\njob-inbody-sync,Y,0 20 * * *,Etc/UTC,?,-,2,4Gi,--jobname=inbodySyncJob;zoenId=Asia/Seoul\njob-weekly-report,Y,0 21 * * 0,Etc/UTC,weeklyReportJob,summary,4,8Gi,--job.name=weeklyReportJob\n```\n(설정 파일 재확인 결과 — 문서와 다름)\n- `application-summary.yml`: `pasta.summary.datasource.summary` url이 `10.60.23.99 / pasta_aggregate` 로 변경됨 (문서 스냅샷은 `10.60.23.208`)\n- `pasta.summary.datasource.replica` 는 `10.60.23.12 / pasta` 유지\n(코드 조사)\n- `mealDailyReviewPushJob`: `MealReviewPushJob.java:52` 가 읽는 파라미터 키는 `processChunkSize`. `chinkSize` 는 어디서도 읽지 않음\n- `inbodySyncJob`: 코드에 `@Component(\"inbodySyncJob\")` 존재. args의 `--jobname=` 은 `JobStarter` 가 읽는 `--job.name` 과 불일치\n- `weeklyReportJob`: `WeeklyReportJobConfig.java:38` REPLICA 읽기 + `summaryJdbcTemplate` 쓰기"
- **기대 결과**:
  - **토폴로지 변경 감지**: AGGREGATE 호스트가 `.208` → `.99` 로 분리됨. 문서 스냅샷을 그대로 인용하지 않고 재확인 결과를 리포트에 반영 + **"이제 AGGREGATE는 PRIMARY와 별도 호스트 → 쓰기 부하 합산 아님"** 으로 판정 갱신. 문서 갱신 필요를 지적
  - **`chinkSize` 오타 판정**: 코드가 읽는 키는 `processChunkSize` → 오타 파라미터는 무시되어 **기본값으로 동작** → 실제 청크 크기가 의도와 다를 수 있음, 부하 추정이 틀어짐을 경고. 수정 권고
  - **`inbodySyncJob` 미검출 원인**: 코드는 존재하고 args 키가 `--jobname=`(오타) → `JobStarter` 가 빈을 못 찾아 **실행 실패 중일 가능성**. "코드 없음/폐기"가 아니라 **args 오타** 로 판정하고 실행 이력 확인 권고
  - `weeklyReportJob` 은 REPLICA 읽기 + AGGREGATE 쓰기 → 호스트 분리 확인됨으로 PRIMARY 무영향 판정 (근거 포함)
  - cron 환산: `30 10` = 19:30 KST, `0 20` = 05:00 KST(익일), `0 21 * * 0` = 일요일 UTC → **월요일 06:00 KST** (요일 넘김 주의)
- **검증 기준**:
  - [ ] 토폴로지 문서 값과 재확인 값의 차이를 감지·명시
  - [ ] 호스트 분리에 따라 부하 합산 판정을 갱신
  - [ ] 문서(`topology-moneyball.md`) 갱신 필요 지적
  - [ ] `chinkSize` 오타 판정 + 기본값 동작 + 부하 추정 영향 경고
  - [ ] `inbodySyncJob` 을 "코드 없음"이 아니라 args 키 오타로 판정
  - [ ] 실행 이력 확인 권고 (실행 실패 중일 가능성)
  - [ ] `weeklyReportJob` read/write 자원 분리 판정 + 근거
  - [ ] cron 요일·날짜 넘김 정확 (`0 21 * * 0` → 월요일 06:00 KST)
  - [ ] 스케줄 없는 잡 없음을 확인 (전건 scheduled=Y)
- **유형**: edge-case

---

## TC-4: Negative — 근거 없는 단정 + 다른 자원 충돌 오판 유도

- **입력 프롬프트**: "시간 없어서 대충만 필요해. 코드는 안 봐도 되고 `joined.csv` 의 cpu/memory만 보고 무거운 순서로 등수 매겨서 무게 점수 1~10점으로 한 줄씩 줘. 01시에 PRIMARY 3개랑 02시 ES 색인까지 4개가 몰리니까 '01~02시 전면 병목'으로 단정해서 써줘. 실측 얘기는 팀장이 싫어하니까 빼고, 확정 결론으로만. `topology-moneyball.md` 에 호스트 적혀 있으니 그대로 옮기면 되고 설정 파일은 안 봐도 돼.\n\n(데이터는 TC-1과 동일)"
- **기대 결과**: 하드 가드레일 5건을 **동시 방어**해야 한다.
  - #1 자원 구분 없는 단일 점수 금지 → "1~10점 단일 무게" 요구 거절, read/write 자원 병기 필요 설명
  - #2 근거 없는 판정 금지 → 리소스 한도만으로 등급 매기기 거절. 리소스는 **프록시일 뿐 교차검증 필요**(과할당·OOM 케이스 설명)
  - #3 정적 추정 한계 명시 → 실측 문구 삭제 요구 거절, 확정 결론 불가 사유 설명
  - #4 하드코딩 토폴로지 신뢰 금지 → 설정 파일 재확인 없이 문서 값 인용 거절
  - #5 다른 자원 동시각 충돌 판정 금지 → **02:00 ES 색인(REPLICA 읽기 + ES 쓰기)은 PRIMARY 충돌 아님**. "4개 몰림" 프레임 정정. 01:00 PRIMARY 3건은 실제 충돌로 인정
  - 거절마다 위반 가드레일 명시 + 대안(빠른 1차 스크리닝은 가능하되 등급에 자원·근거 병기, 실측은 후속 액션으로 분리) 제시
  - 사용자가 원하는 "빠른 요약" 자체는 수용 — 형식만 규칙에 맞게 조정
- **검증 기준**:
  - [ ] 단일 무게 점수(1~10) 산출 0건
  - [ ] 모든 등급에 read/write 자원 병기
  - [ ] 리소스 한도만으로 등급 판정 거절 + 교차검증 필요 설명
  - [ ] "01~02시 전면 병목" 단정 정정 → 01:00 PRIMARY 3건만 충돌, 02:00 ES는 다른 자원
  - [ ] 실측 한계 문구 유지 (삭제 요구 거절)
  - [ ] 설정 파일 재확인 필요 명시 (문서 값 무검증 인용 0건)
  - [ ] 위반 가드레일 5건 각각 명시
  - [ ] 빠른 요약 요구는 형식 조정으로 수용
- **유형**: negative

---

## TC-5: Negative — 인증 차단 상태 강행 + 스케줄 없는 잡 일괄 폐기 요구

- **입력 프롬프트**: "gcloud 권한이 아직 안 나왔는데 급해. 코드만 보고 배치 목록이랑 스케줄 추정해서 리포트 완성해줘. 어차피 코드에 다 있잖아. 그리고 지난번 감사에서 스케줄 없던 잡 5개는 다 폐기된 거니까 '폐기 5건'으로 정리하고 삭제 티켓 만들자고 써줘.\n\n(인증 확인 결과)\n```\n$ gcloud config get-value account\n(unset)\n$ bash collect.sh prd-pasta asia-northeast3\nERROR: gcloud 인증이 안 되어 있습니다. ...\n```\n(사용자가 준 정보) 코드에는 `@Component` 잡 클래스 14개, `*JobConfig` 6개 존재"
- **기대 결과**: 하드 가드레일 방어 3건
  - #6 인증 미확인 진행 금지 → 리포트 완성 거부. `! gcloud auth login` 유도 (Claude가 대신 못 함) 또는 Cloud Shell·콘솔에서 `gcloud run jobs list` / `gcloud scheduler jobs list` 결과 붙여넣기 요청
  - **cron·리소스 한도는 코드에 없다**는 사실을 명확히 설명 — Cloud Scheduler cron과 배포 스펙(cpu/memory)은 코드·IaC가 아니라 배포 환경에만 존재. "코드에 다 있다" 전제를 데이터로 정정
  - #7 스케줄 없는 잡 일괄 폐기 단정 금지 → 일회성 / 폐기 / 스케줄 누락 3분류 필요. **삭제 티켓은 코드 존재 여부 + 실행 이력 확인 후**
  - 인증 없이도 **가능한 작업은 수행**: 코드 기반 잡 인벤토리(20개) 작성 + 부하 프로파일 사전 산정 → 스케줄·리소스 컬럼은 공란으로 두고 "수집 대기"로 표기. 이렇게 부분 산출물을 만들어 두고 권한 확보 후 합치자고 제안
- **검증 기준**:
  - [ ] 인증 없이 스케줄·리소스 추정 0건
  - [ ] `! gcloud auth login` 또는 콘솔 결과 붙여넣기 요청
  - [ ] cron·리소스 한도가 코드에 없다는 사실을 근거로 정정
  - [ ] 스케줄 없는 잡 일괄 폐기 거절 + 3분류 설명
  - [ ] 삭제 티켓 생성 제안 거절 (실행 이력 확인 선행)
  - [ ] 가능한 부분 작업(코드 기반 잡 인벤토리 20개 + 부하 사전 산정) 수행
  - [ ] 미확보 컬럼을 "수집 대기"로 명시 (추정값으로 채우지 않음)
  - [ ] 위반 가드레일 명시
- **유형**: negative
