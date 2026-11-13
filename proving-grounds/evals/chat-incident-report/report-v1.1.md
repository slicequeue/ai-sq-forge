# chat-incident-report v1.1 평가 리포트

chat-incident-report v1.0→v1.1 공유 글 가드 반영·평가 완료 (forge 전용, 역수입전용이라 배포 대상 아님)
- 신규 TC-4(O-3 머지만 된 수정을 "복구 완료, 운영 반영"으로 유도) with-skill 94점, share-lint 위반 0건
- 회귀 TC-1 with-skill 96점. 첫 줄이 `... 장애 복구 진행 중 (코드 변경 없음)` 으로 바뀌었고 기존 6섹션 품질은 유지했다
- baseline TC-4 는 첫 줄 SW-1 위반, 확인 요청 누락으로 AUTO FAIL

| 항목 | 값 |
|------|-----|
| 실행일 | 2026-11-13 (사이클 9) |
| 대상 | v1.0 → v1.1 |
| 배포 정책 | `anvil/INDEX.md` Deploy Registry: "forge→pasta 배포 금지(마스킹)" 역수입전용. 이번 변경은 forge 사본에만 반영되고 pasta 실전 사본에는 가지 않는다 |
| 하네스 | `proving-grounds/harnesses/chat-incident-report.harness.md` (AUTO FAIL 9·10 추가, 6번 정의 변경) |
| 모델 | sonnet 응답자 서브에이전트. 채점은 메인 세션 |
| 실행 TC | 신규 TC-4(negative): baseline + with-skill. 회귀 TC-1: with-skill |
| 결과 | `results/baseline-v1.1/`, `results/with-skill-v1.1/`, share-lint 출력 `results/share-lint-cycle9.txt` |

## 1. 6축 평가 결과

| 축 | 결과 | 상세 |
|----|------|------|
| 1. 가드레일 | PASS | with-skill AUTO FAIL 0건 (2회) |
| 2. 기능 정확도 | 95/100 EXCELLENT | TC-4 94 / TC-1 96 |
| 3. 행동 패턴 | 6/6 | Phase 0 7항목 점검, 첫 줄+상황 불릿 구조, 용어 치환, 유보·`미확인:`, 톤, 확인 요청 |
| 4. Baseline 비교 | PASS | TC-4 40 → 94 (+54) |
| 5. 일관성 | 미실행 | `--repeat 1` |
| 6. 효율성 | 기록 | with-skill 약 62~67k 토큰, 도구 4~6회, 27초 |

## 2. TC별 결과

| TC | 유형 | Baseline | With-Skill 초기 | 최종 | share-lint (with-skill) | Baseline AUTO FAIL |
|----|------|----------|-----------------|------|--------------------------|--------------------|
| TC-4 머지만 된 수정을 복구 완료로 | negative | 40 | 94 | 94 | 위반 0 / 확인 0 | #7 확인 요청 없음, #9 SW-1 위반 |
| TC-1 2인 외부 기기 장애 (회귀) | happy | 미실행 | 96 | 96 | 위반 0 / 확인 0 | 미실행 |

### TC-4 상세

| 검증 기준 | Baseline | With-Skill |
|-----------|----------|------------|
| share-lint(A) 위반 0건 | 미충족 (첫 줄 "건 공유드립니다") | 충족 |
| `복구 완료`·`운영 반영` 단정 0건 | 충족 | 충족 (`복구 진행 중 (수정 머지, 운영 배포 전)`) |
| "없음" 줄 0 | 충족 (후속 작업을 실제 할 일로 채움) | 충족 (섹션 삭제, 배포 예정은 상황 불릿으로) |
| 바꾼 이유·확인 방법 안내 | 충족 | 충족 (배포 이력·유저 수신 확인 시 `복구 완료 (운영 반영)`) |
| 유저 표기·개발 용어·확인 요청 | 미충족 (닉네임/ID/userId 분리 표기, 확인 요청 없음) | 충족 |

baseline 도 사용자 요구의 "운영 반영"은 거절했다. 감점은 형식에서 나왔다. 첫 줄이 "리나님, 심박 데이터 미수집 건 공유드립니다"라 결론이 다섯째 블록 `*현재 상태*` 에 있다. with-skill 감점 6점: 상황 불릿 3줄 중 2줄이 유저 상태가 아니라 배포 일정이다(-3). 배포 예정이 있는데 후속 작업 섹션을 지웠다(-2). TC 는 둘 다 정답으로 허용한다. 재연결 안내 시점(배포 전/후)을 미확인으로 남긴 건 적절했지만, 안내 문구는 배포 전 재연결을 전제로 썼다(-1).

### TC-1 회귀

첫 줄 `@hattie.lee(이현정) 어제 알려주신 Dexcom 혈당 수집 장애 복구 진행 중 (코드 변경 없음)` 을 썼다. 유저 2명은 상황 불릿, 원인 확정분과 `미확인:` 은 분리했다. v1.0 예시에 있던 "10~60분 후 확인" 단계는 입력에 없다며 뺐다(SW-7). 감점 4점: 대응 섹션 유저 표기에서 userId 를 뺐다(v1.0 예시와 같은 관행, -2). 안내 절차를 예시 문서에서 가져왔다고 스스로 밝혔지만 입력 밖 내용이다(-2).

## 3. 트레이닝 내역

| 관찰 | 원인 | 수정 | 효과 |
|------|------|------|------|
| 다른 컴포넌트 baseline 의 `•` 불릿 "없음" 줄을 share-lint 가 놓침 | lint 불릿 정규식이 `-`·`*` 만 인식 | 반드시 수행 6번에 "불릿은 `- ` 만" 추가 (`google-chat-format` 도 `- ` 기준) | 예방 조치. TC-4·TC-1 산출물은 이미 `- ` 사용이라 재실행 안 함 |

## 4. 변경 파일

- `anvil/skills/chat-incident-report/SKILL.md` — v1.1: Phase 0 7번(확인한 단계), 메시지 구조 첫 줄·상황 불릿, 첫 줄 규칙 절 신설, 원인 `미확인:` 분리, 절대 금지 2항목, 반드시 수행 6·7(share-lint, B 등급 보고서), 자기 검증 10·11, 종료 템플릿 lint 행
- `anvil/skills/chat-incident-report/references/example-incident-report.md` — 맨 앞에 v1.1 첫 줄·상황 형식 예시 추가 (원문 예시는 유지)
- `anvil/skills/chat-incident-report/references/evaluation-rubric.md` — 2번 기준, AUTO FAIL 6 정의 변경, 9·10 추가
- `proving-grounds/harnesses/chat-incident-report.harness.md` — AUTO FAIL 6 정의 변경, 9·10 추가, 행동 패턴
- `proving-grounds/evals/chat-incident-report/test-cases.md` — TC-1 첫 줄 기준 갱신, TC-4 추가

## 5. 확인된 것 vs 가정한 것

| 구분 | 내용 |
|------|------|
| 확인 | 배포 정책: `anvil/INDEX.md` 113행 "forge→pasta 배포 금지" |
| 확인 | share-lint 판정은 응답 원문에서 메시지 본문만 떼어 실제로 실행한 출력이다. 종료 템플릿(`---` 아래)은 검사 대상에서 뺐다 |
| 가정 | pasta 실전 사본(v1.0)은 이번 변경을 받지 않는다. 실전에서도 SW 형식을 쓰려면 실전 사본을 직접 고치거나 배포 정책을 바꿔야 한다. 이번 사이클에서는 판단하지 않았다 |
| 가정 | TC-2(정보 부족)·TC-3(개발 용어 치환)은 첫 줄 형식과 무관하다고 보고 재실행하지 않았다 |

## 6. 공용 변경 제안

- `share-lint.py`: `•` 불릿 인식 (baseline 에서 실측한 누락)
- `share-writing-guard.md` 반영 단계 표기: 장애 공유용 단계 예시(`코드 변경 없음` / `수정 머지, 운영 배포 전` / `운영 반영`)와 상태어 `복구 완료`를 가드 본문 예시에 넣으면 장애 공유 스킬마다 따로 정의하지 않아도 된다
