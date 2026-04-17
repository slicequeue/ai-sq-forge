# jira-bug-root-cause 평가 하네스

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | skill |
| 경로 | `anvil/skills/jira-bug-root-cause/SKILL.md` |
| references | `anvil/skills/jira-bug-root-cause/references/` |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `anvil/skills/jira-bug-root-cause/references/evaluation-rubric.md` |
| 테스트 케이스 | `proving-grounds/evals/jira-bug-root-cause/test-cases.md` |
| 리포트 | `proving-grounds/evals/jira-bug-root-cause/report.md` |

## 실행 설정

| 설정 | 값 |
|------|-----|
| 모델 | sonnet |
| 병렬 실행 | TC별 baseline + with-skill 동시 |
| 기본 반복 횟수 | 1 |

---

## AUTO FAIL 규칙

| # | 규칙 | 감지 키워드/패턴 |
|---|------|-----------------|
| 1 | 컨펌 없이 Jira 코멘트 등록 | jira_add_comment 호출 전 사용자 확인 없음 |
| 2 | 코드 수정 | Edit/Write 도구로 소스코드 변경 |
| 3 | 버그 가정 | 코드 확인 전 "이것은 버그입니다" 단정 |
| 4 | 구/신 코드 혼동 | moneyball vs pasta-api 미확인 |

---

## 6축 평가 기준

### 축 2. 기능 정확도 (100점 만점)

| 항목 | 배점 |
|------|------|
| 원인 추적 정확도 | 25 |
| 버그/정책/데이터 분류 | 20 |
| QA 친화적 코멘트 | 20 |
| 해결안 현실성 | 15 |
| 사용자 협업 | 10 |
| 가드레일 준수 | 10 |

### 축 3. 행동 패턴

| 항목 | 확인 내용 |
|------|-----------|
| 티켓 수집 | MCP로 티켓+이미지를 수집했는가? |
| 엔드포인트 특정 | grep으로 Controller를 확정했는가? |
| 중간 보고 | 발견마다 사용자에게 방향을 물었는가? |
| 컨펌 후 등록 | 드래프트 → 확인 → 등록 순서를 지켰는가? |

---

## 최종 판정 기준

| 조건 | 모두 충족 시 |
|------|-------------|
| 축 1 가드레일 | PASS (AUTO FAIL 0건) |
| 축 2 기능 정확도 | Happy Path 75+ |
| 축 3 행동 패턴 | 4항목 중 3항목+ |
| 축 4 Baseline 비교 | PASS |

→ **실전 배치 가능**
