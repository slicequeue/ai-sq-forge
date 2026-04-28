# TC-3 With-Skill (git-pr 적용)

## 시뮬레이션 응답

변경사항 분석을 진행한다.

```bash
git status                                                       # clean
git branch --show-current                                        # api/refac/webclient-pool-tuning
gh pr list --head api/refac/webclient-pool-tuning --state open   # PR #612 열림 ✓
```

- 동일 head 브랜치에 **PR #612가 이미 열려 있음** → 신규 생성 금지, `gh pr edit`으로 갱신
- 코드 변경 없음 → push 불필요
- 본문은 기존 양식 유지하면서 측정 결과 표만 2일차 추가 갱신

기존 PR #612 본문을 읽어 양식을 유지하며 측정 결과 표만 갱신한다.

```bash
gh pr view 612 --json body --jq .body  # 기존 본문 읽기
```

## 갱신된 PR 본문

**제목**: `refac: WebClient 연결 풀 안정화 및 재시도 횟수 상향` (제목 변경 없음)

```markdown
## Why need this PR❓

prd 환경에서 외부 API 호출이 간헐적으로 실패하면서 사용자 데이터가 가끔 처리 안 되던 문제 (하루 평균 약 60건의 `Connection reset by peer` 발생).

**원인**: WebClient의 connection 풀 설정이 명시되지 않아, 죽은 connection이 풀에 그대로 남아있다가 재사용 시 reset 발생. 재시도도 1회뿐이라 짧은 burst 시 살릴 기회 부족.

## Changes ✌️

**파일 2개, +32 / -2 lines**

| 파일 | 변경 |
|---|---|
| `infra/network/AppWebClientConfiguration.java` | WebClient에 연결 풀 명시 — idle 20초 후 정리, 백그라운드 60초 주기 점검 |
| `infra/network/AppHttpClient.java` | 재시도 1회 → 3회 (최대 backoff 2초). 로그 포맷도 통일 |

## 측정 결과 (4/28 시점, 100% 적용 약 2일 후)

| 지표 | 변경 전 | 변경 후 | 효과 |
|---|---|---|---|
| Connection reset (하루 평균) | 약 60건 | **약 22건** | ✅ 약 63% 감소 |
| 사용자 영향까지 도달한 실패 | 일부 발생 | **0건** | ✅ 완전 차단 (2일 연속) |
| 1분 burst (한꺼번에 ~10건) | 종종 발생 | 시간당 3~4건 | ✅ 사라짐 |
| 새로운 부작용 (풀 고갈 등) | — | **0건** | ✅ 안전 |

> ⚠️ 2일 측정치 — 일부 OAuth 토큰 갱신 경로 잔존 실패는 후속 PR로 처리 예정.

## 배포

- **4/26 22:00 KST**: 신규 버전을 절반 트래픽에 먼저 적용 (canary)
- **4/27 00:30 KST**: 약 2시간 모니터링 후 100% 전환

## 후속 작업 (별도 PR)

1. **OAuth 토큰 갱신 경로의 connection 설정** — 본 PR은 일반 API 호출만 적용
2. **운영 메트릭 노출** — connection 풀 상태 Prometheus 노출

---

📘 **상세 분석/측정 결과/근거 문서는 Notion으로 별도 공유 예정**

## Test list 📝

- [x] `./gradlew test` 통과 (회귀 없음)
- [x] Canary 50:50 → 100% 무중단 승격
- [x] 평일 2일치 측정 완료
```

## 자기 검증 체크리스트

- [x] 기존 PR #612 인지 → `gh pr edit` 사용 (신규 생성 금지)
- [x] 양식 유지하면서 측정 결과만 갱신 (4/27 → 4/28, 1일차 → 2일차)
- [x] 분량 약 55줄
- [x] 가드레일 모두 충족 (한국어, docs/ 0, AI 표기 0, target dev)

## 실행 명령

```bash
gh pr edit 612 \
  --body "$(cat <<'EOF'
...(위 갱신 본문)...
EOF
)"
```

## 출력

기존 PR 갱신: https://github.com/{org}/{repo}/pull/612
