# 참고 사례 — PR #551 (Dexcom WebClient 연결 풀 안정화)

> 양식 표준의 출처. 새 PR 본문 작성 전 한 번 읽고 분량/표현/구조 감각을 잡는다. pasta-japan-server 실전 사례 — 다른 프로젝트에서는 양식과 표현 원칙만 참고.

**제목**: `fix: Dexcom WebClient 연결 풀 안정화 및 재시도 횟수 상향`

**URL**: https://github.com/virtualcare/pasta-japan-server/pull/551

**본문 구성** (139줄, 표 3개):

````markdown
## Why need this PR❓

prd 환경에서 Dexcom 호출이 간헐적으로 실패하면서 사용자 혈당 데이터가 가끔 저장 안 되던 문제 (하루 평균 50~90건의 `Connection reset by peer` 발생).

**원인**: WebClient의 connection 풀 설정이 명시되지 않아, 죽은 connection이 풀에 그대로 남아있다가 재사용 시 reset 발생. 재시도도 1회뿐이라 burst 시 살릴 기회 부족.

## Changes ✌️

**파일 2개, 32 lines 추가 / 2 lines 삭제** (lilly 프로파일 무관)

| 파일 | 변경 |
|---|---|
| `cgm/.../DexcomWebClientConfiguration.java` | WebClient에 `ConnectionProvider` 명시 — idle 20초 후 정리, 백그라운드 60초 주기 점검 |
| `cgm/.../DexcomClient.java` | 재시도 1회 → 3회 (최대 backoff 2초). 로그 포맷도 통일 |

설정값 근거: Dexcom JP idle TCP timeout이 공개되지 않아, 일반 LB(60초~수분)보다 짧게(20초) 잡아 client가 먼저 끊는 방식 채택. 자세한 비교/대안은 작업 문서 참고.

## 측정 결과 (4/27 시점, 100% 적용 약 2일 후)

| 지표 | 변경 전 | 변경 후 | 효과 |
|---|---|---|---|
| Connection reset (하루 평균) | 50~90건 | **약 23건** | ✅ 60~75% 감소 |
| 사용자 영향까지 도달한 실패 | 일부 발생 | **0건** | ✅ 완전 차단 |
| 1분 burst (한꺼번에 ~10건) | 종종 발생 | 시간당 4건 이하 | ✅ 사라짐 |
| 새로운 부작용 (풀 고갈 등) | — | **0건** | ✅ 안전 |

> ⚠️ 단, 일부 404 응답은 다른 경로(OAuth 토큰 갱신 실패 등)로 잔존. 후속 작업으로 처리 예정.

## 배포

- **4/24 22:06 KST**: 신규 버전을 절반 트래픽에 먼저 적용 (canary)
- **4/25 00:24 KST**: 약 2시간 모니터링 후 100% 전환
- **4/28 (예정)**: 평일 1일치 추가 측정 후 결론 마감

## 후속 작업 (별도 PR)

본 PR로 풀리지 않은 잔존 이슈:

1. **OAuth 토큰 갱신 경로의 connection 설정** (현재 PR은 일반 API 호출만 적용)
2. **재시도 조건 보강** — 일부 예외 케이스에서 재시도 미동작 / NPE 의심
3. **운영 메트릭 노출** (`ConnectionProvider.builder().metrics(true)` + Prometheus)

---

📘 **상세 분석/측정 결과/근거 문서는 Notion으로 별도 공유 예정**

## Test list 📝

- [x] `./gradlew :cgm:test` 통과 (회귀 없음)
- [x] Canary 50:50 → 100% 무중단 승격
- [ ] 4/28 평일 측정 후 결론 마감
````

## 이 사례에서 학습할 포인트

| 포인트 | 어떻게 |
|---|---|
| **Why** 짧음 (3줄) | 현상 1줄 + 원인 1줄. 자세한 분석은 본문에 안 넣음 |
| **Changes** 표 | 파일별 1줄. 코드 스니펫 없음 |
| **측정 결과** 표 | 4지표만. baseline/method 등 자세한 건 한계/잔존 ⚠️ 1줄로 위임 |
| **배포** 3줄 | 시점 + 무엇만. 명령어 없음 |
| **후속 작업** 3개 | 항목명 + 1줄. 자세한 진행 방향은 별도 PR로 |
| **링크** | docs/ 링크 0개. "Notion 공유 예정" 한 줄만 |
