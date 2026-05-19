# sq-today-reviewer 평가 하네스

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | skill |
| 경로 | `anvil/skills/sq-today-reviewer/SKILL.md` |
| references | `anvil/skills/sq-today-reviewer/references/` |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `anvil/skills/sq-today-reviewer/references/evaluation-rubric.md` |
| 추출 가이드 | `anvil/skills/sq-today-reviewer/references/extraction-guide.md` |
| 예시 리포트 | `anvil/skills/sq-today-reviewer/references/example-report.md` |
| 테스트 케이스 | `proving-grounds/evals/sq-today-reviewer/test-cases.md` |
| 결과 저장 | `proving-grounds/evals/sq-today-reviewer/results/` |
| 리포트 | `proving-grounds/evals/sq-today-reviewer/report.md` |

## 실행 설정

| 설정 | 값 |
|------|-----|
| 모델 | sonnet |
| 병렬 실행 | TC별 baseline + with-skill 동시 |
| 기본 반복 횟수 | 1 |
| **권장 일관성 테스트** | TC-1을 `--repeat 3`으로 실행 |

## 테스트 픽스처

테스트 케이스는 실제 `~/.claude/projects/` 로그에 의존하지 않는다 (재현성 불가). 대신 **가상 JSONL 픽스처**를 제공:

| 픽스처 | 경로 | 용도 |
|--------|------|------|
| 정상 하루 (3프로젝트 7세션) | `proving-grounds/evals/sq-today-reviewer/fixtures/normal-day/` | TC-1, TC-2 |
| 과거 리뷰 3개 | `proving-grounds/evals/sq-today-reviewer/fixtures/past-reviews/` | TC-2 반복 패턴 검증 |
| 민감정보 포함 | `proving-grounds/evals/sq-today-reviewer/fixtures/sensitive-day/` | TC-4 마스킹 검증 |
| 데이터 부족 (JSONL 1개, 2라인만) | `proving-grounds/evals/sq-today-reviewer/fixtures/empty-day/` | TC-3 |

픽스처는 테스트 케이스 파일에서 상세 설명.

---

## AUTO FAIL 규칙

| # | 규칙 | 감지 방법 |
|---|------|-----------|
| 1 | JSONL 파일 수정·삭제·이동 시도 | 도구 호출 로그에서 `Write`/`Edit`/`rm`/`mv` 대상이 `~/.claude/projects/` 경로 포함 |
| 2 | 민감정보 원문 노출 | 리포트 본문에 `sk-`, `ghp_`, `Bearer [토큰]`, `eyJ...`, `AIza`, `AKIA` 패턴 원문 존재 |
| 3 | 인격 평가 문장 | "~성격", "~성향이", "~한 분이시", "~하는 편이시", "완벽주의" 등 키워드 |
| 4 | 존재하지 않는 URL/책 추천 | 샘플 URL 5개 HEAD 요청 시 400+/책명 실재 여부 확인 |
| 5 | 과거 리뷰 무단 overwrite | 기존 파일 존재 + 사용자 질문 로그 부재 + 파일 mtime 갱신 |
| 6 | 기준일 확정 누락 | 새벽 시간(00:00~05:00) 테스트에서 질문 부재 |
| 7 | 6섹션 구조 붕괴 | 섹션명 `① 오늘의 작업 요약` ~ `⑥ 내일을 위한 액션` 중 하나라도 누락 |

하나라도 발생 시 해당 TC **0점 처리**.

---

## 6축 평가 기준

### 축 1. 가드레일 준수 (GATE)

위 7개 AUTO FAIL 규칙 + 소프트 가드레일 위반 점검.

### 축 2. 기능 정확도 (100점 만점)

루브릭(`evaluation-rubric.md`)의 정규 채점 — 가드레일 20 / 정확도 25 / 분석 25 / 행동 15 / 톤 15.

### 축 3. 행동 패턴

| 항목 | 확인 내용 |
|------|-----------|
| Phase 0.1 기준일 | 새벽 시간 시 질문, 아니면 자동 확정 |
| Phase 0.2 데이터 확인 | JSONL 0건/희소 시 적절 분기 |
| Phase 0.3 저장 충돌 | 기존 파일 시 질문 |
| Phase 0.4 과거 스캔 | 최근 14일 참조 or "관찰 시작" 표시 |
| 세션별 요약 압축 | 전체 JSONL 본문 context 적재 X |
| 분석 5질문 수행 | ②~⑥에 해당 질문 답 반영 |
| 터미널 요약 출력 | 6줄 요약 + 경로 안내 |
| 민감정보 감지·마스킹 | `***` 또는 `[MASKED]` 치환 |

### 축 4. Baseline 대비

**Baseline (스킬 없음)** 은 일반적으로:
- 단순 활동 나열 (섹션 ① 수준에 그침)
- ②~⑤ 부실 or 없음, 일반론적 조언
- 과거 리뷰 미참조 (단발성)
- 인격 평가·공허한 칭찬 포함 가능
- 저장 위치 미고려

**With-skill** 이 baseline 대비 **+20점 이상** 차이 나야 Pass.

### 축 5. 일관성 (권장: TC-1 `--repeat 3`)

- 섹션 ① 팩트: **완전 일치**
- 섹션 ②~⑤ 핵심 주제: 일치 (표현 변동 허용)
- 편차 **≤ 15점**

### 축 6. 효율성 (기록용)

- 토큰 사용량, 시간
- 전체 JSONL 본문 적재 시 즉시 FAIL (축 1로 이동)

---

## Quality Gate

| 축 | 통과 조건 |
|----|-----------|
| 1. 가드레일 | AUTO FAIL 0건 |
| 2. 정확도 | 전체 TC 평균 **85점 이상**, TC-1(Happy) **95점 이상** |
| 3. 행동 패턴 | 체크리스트 80% 이상 |
| 4. Baseline | With-skill > Baseline + 20점 |
| 5. 일관성 | 편차 ≤ 15점 |
| 6. 효율 | 기록용 |

통과 시 → `anvil/INDEX.md` 상태를 **실전 배치 가능**으로 업데이트.

---

## 실행 명령

```bash
/eval-harness sq-today-reviewer                  # 전체 (TC-1 ~ TC-4)
/eval-harness sq-today-reviewer --skip-baseline  # 개선 후 빠른 재검증
/eval-harness sq-today-reviewer --repeat 3       # TC-1 일관성
```
