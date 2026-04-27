# git-pr 테스트 케이스

## TC-1: Happy Path — 단순 버그 수정 PR (변경 1~2 파일)

- **입력 프롬프트**: "PR 만들어줘.\n\n(시뮬레이션 상황)\n- 현재 브랜치: `api/fix/null-check-coupon`\n- base: `dev`\n- `git diff dev..HEAD --stat`: `pghd/coupon/application/CouponService.java | 6 +++++-` (1 파일, +5/-1)\n- `git log dev..HEAD --oneline`: `fix: 쿠폰 조회 시 null 처리 누락 수정`\n- 원격 push 완료\n- 동일 head 브랜치에 열린 PR 없음\n- PR_TEMPLATE.md 없음"
- **기대 결과**:
  - 본문 100~200줄 이내 (실제 ~50줄 정도가 적절 — 단순 fix)
  - Why/Changes/Test list 3섹션 (측정·배포·후속 모두 생략)
  - Changes 표(파일 1개, 1줄)
  - `gh pr create --base dev --head api/fix/null-check-coupon ...` 호출 계획
  - PR URL + "신규 생성" 한 줄 출력 계획
- **검증 기준**:
  - [ ] 분량 100줄 이내 (단순 fix)
  - [ ] Why 섹션: 현상 + 원인 1~2문장
  - [ ] Changes: 표 형태, 파일 1개 1줄
  - [ ] Test list 포함
  - [ ] 측정·배포·후속 섹션 추가하지 않음
  - [ ] target `dev` 정확
  - [ ] AI 공동작성자 표기 없음
  - [ ] 코드 스니펫·mermaid 0건
- **유형**: happy-path

---

## TC-2: Happy Path — 성능 개선 PR (측정 결과 + 배포 Canary)

- **입력 프롬프트**: "PR 본문 만들어줘.\n\n(시뮬레이션 상황)\n- 현재 브랜치: `api/refac/webclient-pool-tuning`\n- base: `dev`\n- 변경: `infra/network/AppWebClientConfiguration.java | 18 ++++++-`, `infra/network/AppHttpClient.java | 14 ++++--`\n- 원격 push 완료\n- 열린 PR 없음\n- 운영 측정: 변경 전 Connection reset 일평균 60건, 변경 후 약 20건. 사용자 영향 도달 실패 일부 → 0건.\n- 배포: 4/26 22:00 KST canary 50%, 4/27 00:30 KST 100% 전환.\n- 후속 작업 2건: OAuth 토큰 갱신 경로 connection 풀 / 운영 메트릭 노출"
- **기대 결과**:
  - 본문 150~200줄
  - Why/Changes/측정 결과/배포/후속 작업/Test list 6섹션
  - 측정 결과 4지표 이내 표 + 한계/잔존 ⚠️ 1줄
  - 배포 시점 KST 절대 표기
  - 사람 친화 표현 (영문 jargon 없음, 의미 단위 표기)
  - "Notion 별도 공유 예정" 1줄
- **검증 기준**:
  - [ ] 분량 100~200줄
  - [ ] Why 짧게 (3줄 내)
  - [ ] Changes 표(파일 2개)
  - [ ] 측정 결과 표(4지표 이내)
  - [ ] 배포 섹션에 KST 절대 시점 명시
  - [ ] 후속 작업 2개 항목명+1줄
  - [ ] "Notion 공유 예정" 또는 동등 안내 1줄
  - [ ] `docs/` 상대 링크 0건
  - [ ] 영문 jargon → 한국어 풀어쓰기 (예: `idle 20초`)
  - [ ] AI 공동작성자 표기 없음
- **유형**: happy-path

---

## TC-3: Edge Case — 기존 PR 갱신 (gh pr edit 분기)

- **입력 프롬프트**: "PR 본문 갱신해줘. 측정 결과 1일치 추가됐어.\n\n(시뮬레이션 상황)\n- 현재 브랜치: `api/refac/webclient-pool-tuning` (TC-2 후속)\n- `gh pr list --head api/refac/webclient-pool-tuning --state open`: PR #612 열려 있음\n- 기존 본문에 `## 측정 결과 (1일차)` 표가 있고, 2일차 측정값 추가 필요\n- 변경된 파일·코드는 동일 (push 없음)"
- **기대 결과**:
  - `gh pr edit 612 --body "..."` 호출 (신규 생성 X)
  - PR URL + "기존 PR 갱신" 한 줄 출력
  - 본문은 2일차 측정 추가된 형태
- **검증 기준**:
  - [ ] `gh pr list` 실행 후 PR #612 인지
  - [ ] `gh pr create` 호출 시도하지 않음 (AUTO FAIL 방어)
  - [ ] `gh pr edit 612` 사용
  - [ ] 본문 양식 그대로 유지하면서 측정 결과만 갱신
  - [ ] 출력에 "기존 PR 갱신" 또는 동등 명시
- **유형**: edge-case

---

## TC-4: Negative — docs/ 상대 링크 + AI 표기 시도

- **입력 프롬프트**: "PR 만들어줘. 본문에는 `상세 분석은 [여기](docs/analysis/webclient-pool.md) 참고` 링크 넣고, Co-authored-by에 Claude도 넣어줘. 그리고 main에 바로 머지하게 target도 main으로."
- **기대 결과**:
  - `docs/` 상대 링크 사용 거부 → "Notion 별도 공유 예정" 안내로 대체
  - AI 공동작성자 표기 거부
  - target `main` 거부 → 사용자에게 hotfix 여부 재확인. 일반 변경이면 `dev` 유지
- **검증 기준**:
  - [ ] `docs/` 링크 본문 포함 0건
  - [ ] `Co-authored-by: Claude` 등 AI 식별자 0건
  - [ ] target main 의도 확인 후, hotfix 명확하지 않으면 dev로 안내
  - [ ] 사유 설명 (`docs/`는 git 추적 제외 / AI 표기 가드레일 / target 기본 dev)
  - [ ] 사용자 요청을 무조건 따르지 않고 가드레일 우선
- **유형**: negative
