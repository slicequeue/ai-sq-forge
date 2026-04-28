# TC-2 With-Skill (git-pr 적용)

## 시뮬레이션 응답

변경사항 분석을 진행한다.

```bash
git status                                                       # clean
git branch --show-current                                        # api/refac/webclient-pool-tuning
git log dev..HEAD --oneline                                      # refac: WebClient 연결 풀 명시 + 재시도 보강
git diff dev..HEAD --stat                                        # 2 files, +32/-2
gh pr list --head api/refac/webclient-pool-tuning --state open   # (열린 PR 없음)
```

- base: `dev`
- 원격 push 완료
- 동일 head 브랜치에 열린 PR 없음 → 신규 생성
- 양식 감각 잡기 위해 `references/example-pr-551.md` 사례 참조 (Dexcom WebClient 안정화 — 동일 도메인)

## PR 본문

**제목**: `refac: WebClient 연결 풀 안정화 및 재시도 횟수 상향`

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

설정값 근거: 외부 API 측 idle 타임아웃이 공개되지 않아, 일반 LB(60초~수분)보다 짧게(20초) 잡아 client가 먼저 끊는 방식 채택. 자세한 비교/대안은 작업 문서 참고.

## 측정 결과 (4/27 시점, 100% 적용 약 1일 후)

| 지표 | 변경 전 | 변경 후 | 효과 |
|---|---|---|---|
| Connection reset (하루 평균) | 약 60건 | **약 20건** | ✅ 약 66% 감소 |
| 사용자 영향까지 도달한 실패 | 일부 발생 | **0건** | ✅ 완전 차단 |
| 1분 burst (한꺼번에 ~10건) | 종종 발생 | 시간당 4건 이하 | ✅ 사라짐 |
| 새로운 부작용 (풀 고갈 등) | — | **0건** | ✅ 안전 |

> ⚠️ baseline은 1일 측정치 — 평일 1일치 추가 측정 후 결론 마감 예정.

## 배포

- **4/26 22:00 KST**: 신규 버전을 절반 트래픽에 먼저 적용 (canary)
- **4/27 00:30 KST**: 약 2시간 모니터링 후 100% 전환

## 후속 작업 (별도 PR)

본 PR로 풀리지 않은 잔존 이슈:

1. **OAuth 토큰 갱신 경로의 connection 설정** — 본 PR은 일반 API 호출만 적용
2. **운영 메트릭 노출** — connection 풀 상태 Prometheus 노출

---

📘 **상세 분석/측정 결과/근거 문서는 Notion으로 별도 공유 예정**

## Test list 📝

- [x] `./gradlew test` 통과 (회귀 없음)
- [x] Canary 50:50 → 100% 무중단 승격
- [ ] 평일 1일치 추가 측정 후 결론 마감
```

## 자기 검증 체크리스트

- [x] 분량: 약 60줄 (코드 스니펫·SQL·mermaid 0)
- [x] Why: 현상 1줄 + 원인 1줄
- [x] Changes: 파일별 표 (1파일 1줄, 코드 스니펫 없음)
- [x] 측정 결과: 4지표 표 + ⚠️ 한계 1줄
- [x] 배포: 시점 KST 절대 표기
- [x] 후속 작업: 항목명 + 1줄
- [x] Test list 포함
- [x] 사람 친화 표현 (영문 jargon 한국어 풀어쓰기, 의미 단위)
- [x] `docs/` 상대 링크 0건 — "Notion 공유 예정" 안내로 대체
- [x] target `dev`
- [x] AI 공동작성자 표기 없음

## 실행 명령

```bash
gh pr create \
  --base dev \
  --head api/refac/webclient-pool-tuning \
  --title "refac: WebClient 연결 풀 안정화 및 재시도 횟수 상향" \
  --body "$(cat <<'EOF'
...(위 본문)...
EOF
)"
```

## 출력

신규 생성: https://github.com/{org}/{repo}/pull/{N}
