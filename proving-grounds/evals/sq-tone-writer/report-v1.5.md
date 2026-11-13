# sq-tone-writer v1.5 평가 리포트

sq-tone-writer v1.4→v1.5 공유 글 가드 반영·평가 완료 (forge, 배포 전)
- with-skill 3개 TC 모두 share-lint 위반 0건: TC-6 97, TC-7 95, TC-1 회귀 98
- baseline TC-6 은 인사말로 시작해 SW-1 위반 2건, "문제없을 것으로 예상" 유추가 남아 AUTO FAIL
- C 등급 리뷰 답글(TC-7)에는 SW 형식을 붙이지 않았다. 과잉 적용은 나오지 않았다

| 항목 | 값 |
|------|-----|
| 실행일 | 2026-11-13 (사이클 9) |
| 대상 | v1.4 → v1.5 (공유 글 가드 `forge/common/share-writing-guard.md` SW-1~7 반영) |
| 하네스 | `proving-grounds/harnesses/sq-tone-writer.harness.md` (AUTO FAIL 5·6, 행동 패턴 v1.5 2항목 추가) |
| 모델 | sonnet 응답자 서브에이전트. 채점은 메인 세션이 따로 했다 |
| 실행 TC | 신규 TC-6(negative, O-1+O-4)·TC-7(edge, 과잉 적용 대조): baseline + with-skill. 회귀 TC-1: with-skill 2회(트레이닝 전후) |
| 결과 | `results/baseline-v1.5/`, `results/with-skill-v1.5/`, share-lint 출력 `results/share-lint-cycle9.txt` |

## 1. 6축 평가 결과

| 축 | 결과 | 상세 |
|----|------|------|
| 1. 가드레일 | PASS | with-skill AUTO FAIL 0건 (4회 실행) |
| 2. 기능 정확도 | 96.7/100 EXCELLENT | TC-6 97 / TC-7 95 / TC-1 98 |
| 3. 행동 패턴 | 충족 | 등급 판정 3/3 정확, share-lint 실행·결과 기재 2/2 (A 등급 TC) |
| 4. Baseline 비교 | PASS | TC-6 30 → 97 (+67). TC-7 은 baseline 도 95 (격차 0, 과잉 적용 대조용) |
| 5. 일관성 | 미실행 | `--repeat 1` |
| 6. 효율성 | 기록 | with-skill 약 61~64k 토큰, 도구 2~4회, 13~24초 |

## 2. TC별 결과

| TC | 유형 | Baseline | With-Skill 초기 | 최종 | share-lint (with-skill) | Baseline AUTO FAIL |
|----|------|----------|-----------------|------|--------------------------|--------------------|
| TC-6 배경부터 정중하게 + 유추·예의 문구 | negative | 30 | 97 | 97 | 위반 0 / 확인 0 | #1 감사하겠습니다, #2 안녕하세요, #5 SW-1 위반 2건, #6 "문제없을 것으로 예상" |
| TC-7 C 등급 리뷰 답글 | edge | 95 | 95 | 95 | C 등급이라 미적용 | 0건 |
| TC-1 슬랙 완료 공유 (회귀) | happy | 미실행 | 95 | 98 | 위반 0 / 확인 0 | 미실행 |

### TC-6 상세

| 검증 기준 | Baseline | With-Skill |
|-----------|----------|------------|
| share-lint(A) 위반 0건 | 미충족 (SW-1 2건) | 충족 |
| 첫 줄 `dev, 운영 반영 전` | 미충족 (인사말 시작) | 충족 |
| "문제없을 것" 0건 | 미충족 ("운영에서도 문제없을 것으로 예상") | 충족 (빼고 `미확인:` 대안 안내) |
| 예의 문구 0건 | 미충족 ("시간 되실 때", "감사하겠습니다") | 충족 ("dev 에서 확인 부탁드립니다.") |
| 바꾼 이유 안내 + 톤 확인 | 부분 (유추 완화만 안내) | 충족 |

baseline 은 유추 문장을 "예상하고 있습니다"로 바꿨다. 단정은 피했지만 유추는 그대로 남았다. with-skill 감점 3점: 바꾼 이유를 한 줄이 아닌 3줄 불릿으로 썼다(-1). "재기동 이후 기록부터 원문 저장"은 입력에서 추론한 문장이다(-2). 입력은 "이전 기록 복구 불가"만 말했다.

### TC-7 상세 (과잉 적용 대조)

with-skill 은 등급을 C 로 판정했다. "`완료 (단계)` 첫 줄·불릿 형식 미사용"을 출력 헤더에 밝히고 A-1 담백 보고형 2문장으로 썼다. 58행 함께 수정, `3fa21c9` 는 포함했고 테스트·배포 언급은 0건이다. share-lint 를 돌리면 SW-1 위반이 나온다. C 등급에는 형식을 붙이지 않는다는 뜻이라 정상이다. 감점 5점은 "우선" 완화어다(A-1 default 는 담백, -2). 멘션 `@jay-kim` 은 생략해도 되는 구성 요소다(-1). 30자 넘는 문장이 1개다(-2). baseline 도 같은 수준이라 격차가 없다. 이 TC 는 v1.5 가 C 등급 글을 망가뜨리지 않는지 보는 대조용이다.

### TC-1 회귀

초기(95): 불릿 "일괄 발급 API 구현"이 첫 줄을 되풀이했다(-3, 반복 강조). 트레이닝 후(98): 불릿에 "테스트 전체 통과"만 남겼다. "전체"는 입력에 없는 수식이다(-1). 직전 회귀 100점(v1.4)과 비교하면 형식은 SW 형식으로 바뀌었다. 3문장 이내·반말 혼용·두괄식 기준은 유지했다.

## 3. 트레이닝 내역 (v1.5 초안 → v1.5 최종)

| 관찰 | 원인 | 수정 | 효과 |
|------|------|------|------|
| TC-1 불릿이 첫 줄을 되풀이 | 슬랙 A 형식 안내에 불릿에 무엇을 담는지 없었다 | 슬랙 섹션에 "불릿은 첫 줄을 되풀이하지 않고 결과만" 추가 | TC-1 95 → 98 |
| 다른 컴포넌트 baseline 에서 `•` 불릿 "없음" 줄을 share-lint 가 놓침 (error-log-report TC-6) | lint 의 불릿 정규식이 `-`·`*` 만 인식 | 슬랙 섹션에 "불릿 기호는 `- ` 만" 추가 | 예방 조치 (재실행 대상 아님) |
| 존댓말 첫 줄 `완료했습니다 (단계)` 가 lint SW-1 위반 | lint 가 `완료` 바로 뒤 괄호만 인정 | Phase 0 4번·tone-examples 에 "첫 줄은 `완료 (단계)` 로 끝낸다" 명시 | 초안 단계에서 반영, 리더 예시 lint 통과 확인 |

## 4. 변경 파일

- `anvil/skills/sq-tone-writer/SKILL.md` — v1.5: Phase 0 4번(A/B/C 등급), 슬랙 예시 SW 형식, PR 리뷰 답글 C 등급 주석, 절대 금지 2항목, 반드시 수행 7번(share-lint), 자기 검증 12·13, 종료 템플릿 등급·lint 행
- `anvil/skills/sq-tone-writer/references/tone-examples.md` — 슬랙·문서 보고 예시를 SW 형식으로 교체. "특이사항 없음. 배포 가능." 삭제
- `anvil/skills/sq-tone-writer/references/evaluation-rubric.md` — 4·5번 SW 감점, AUTO FAIL 5·6
- `proving-grounds/harnesses/sq-tone-writer.harness.md` — AUTO FAIL 5·6, 행동 패턴 2항목
- `proving-grounds/evals/sq-tone-writer/test-cases.md` — TC-6·7

## 5. 확인된 것 vs 가정한 것

| 구분 | 내용 |
|------|------|
| 확인 | share-lint 판정은 응답 원문에서 산출물 블록을 파일로 떼어 실제로 실행한 출력이다 (`results/share-lint-cycle9.txt`) |
| 확인 | with-skill 응답자가 적은 "share-lint 위반 0건·확인 0건"은 메인 세션 재실행 결과와 일치했다 (3/3) |
| 가정 | 응답자는 서브에이전트 시뮬레이션이다. 실제 슬랙 게시·사용자 반응은 보지 않았다 |
| 가정 | TC-7 은 1회 실행이다. 과잉 적용이 확률적으로 나오는지는 `--repeat 3` 으로 봐야 한다 |
| 미확인 | PR 리뷰 답글 봇/사람 TC(v1.4 리포트 하네스 갭 1번)는 이번에도 사람 쪽만 봤다 |

## 6. 공용 변경 제안 (forge/common, 이번 사이클 미수정)

- `share-lint.py`: 불릿 정규식에 `•` 를 넣는다. error-log-report baseline 의 "• 없음" 3줄이 SW-6 에서 빠졌다
- `share-lint.py`: `완료했습니다 (단계)`·`완료됐습니다 (단계)` 처럼 존댓말 어미가 붙은 첫 줄도 STATUS 로 인정할지 정한다. 지금은 존댓말 첫 줄이 SW-1 위반으로 나온다
