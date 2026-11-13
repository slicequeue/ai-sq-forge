# git-commit v1.3 평가·트레이닝 리포트

git-commit v1.3 조직 컨벤션 분기 반영·평가 완료 (forge, 배포 전)
- 적용 프로젝트는 `[핵심키워드] 명사형 요약`, 비적용(forge·poc)은 기존 Conventional. 하네스·TC 5건·루브릭 신설
- with-skill 최종 평균 98.6, AUTO FAIL 0건. baseline 은 TC-4(N-2) AUTO FAIL, TC-5 FAIL
- 트레이닝 1건: 경로 최다가 `[공통]` 같은 범용 키워드일 때 기능 키워드 우선 (TC-3 95 → 99)

| 항목 | 값 |
|------|-----|
| 실행일 | 2026-11-13 |
| 평가 대상 | v1.3 (사이클 9, 조직 코딩 컨벤션 반영) |
| 이전 평가 | 첫 평가 (커맨드 첫 하네스) |
| 하네스 | proving-grounds/harnesses/git-commit.harness.md (AUTO FAIL 4건) |
| 루브릭 | proving-grounds/evals/git-commit/evaluation-rubric.md (커맨드는 플랫 파일이라 references/ 대신 evals 폴더) |
| 모델 | sonnet 응답자 서브에이전트 12건. 채점은 오케스트레이션 세션 |

## 1. 바꾼 것

| 위치 | 내용 |
|------|------|
| 0절 형식 판정 | `.claude/shared/vc-conventions-guide.md` 존재 → A, 없으면 B. forge 저장소 자체는 B. 사용자가 반대 형식을 요청해도 판정을 따르고 근거 한 줄 |
| A절 | 원문을 가리키고 실행 규칙만: 키워드 실측(`git log -- <경로>`), 범용 키워드면 기능 키워드 우선, 이슈 키 요약 앞, 명사형 종결, 복수 도메인은 분리 우선·불가 시 이력의 복수 표기 |
| B절 | 기존 `refac:` 실측 근거 이동 (조직 컨벤션 도입 전 실측이라는 단서) |
| 가드레일·자기 검증 | A 접두어·`~한다` 금지, B 대괄호 금지, 기존 커밋 재작성 금지. 체크리스트 8항목 |

## 2. 6축 결과

| 축 | 결과 | 상세 |
|----|------|------|
| 1. 가드레일 | PASS | with-skill 7회 AUTO FAIL 0건 |
| 2. 기능 정확도 | 98.6 EXCELLENT | TC-1 98 / TC-2 98 / TC-3 99 / TC-4 100 / TC-5 98 |
| 3. 행동 패턴 | 5/5 | 판정·실측·분리·spotless 판단 전 실행 충족 |
| 4. Baseline | PASS | baseline 평균 81.4(AUTO FAIL 1, FAIL 1) → 98.6 |
| 5. 일관성 | 참고 | TC-1 2회 98 / 98. --repeat 3 미실행 |
| 6. 효율성 | 기록 | with-skill 57~62k 토큰·3 tool·24~50초 / baseline 50~54k·2 tool |

## 3. TC별 결과

| TC | 유형 | 맥락 | Baseline | 초기 | 최종 | 핵심 차이 |
|----|------|------|----------|------|------|-----------|
| TC-1 | happy | pasta 적용 | 92 | 98 | 98 | 입력 실측값 덕에 baseline 도 `[PGHD]`. 판정 근거가 이력 추정뿐 |
| TC-2 | happy | poc 비적용 | 93 | 98 | 98 | 둘 다 `refac:`. 형식 줄 출력 차이 |
| TC-3 | edge | moneyball 적용 | 86 | 95 | 99 | baseline 은 이슈 키를 본문 `Refs:` 로(제목에 없음), 요청 없는 push. 초기 with-skill 은 기능 커밋에 `[공통]` |
| TC-4 | negative N-2 | pasta 적용 | AUTO FAIL (65) | 100 | 100 | baseline `[USER] feat: 회원 탈퇴 API 구현한다`. with-skill `[USER] 회원 탈퇴 API 추가` + 근거 |
| TC-5 | negative 대조 | forge 비적용 | 71 FAIL | 98 | 98 | baseline 은 사용자 지시로 `[chore]`(변경 유형을 키워드로, 실측 없음). 비적용 판정은 해서 AUTO FAIL 3 아님 |

유형별 격차: happy +5.5 / edge +13 / negative +31 이상.

## 4. 트레이닝

| 관찰 | 원인 | 수정 | 효과 |
|------|------|------|------|
| TC-3 에서 위임청구 기능 커밋에 경로 최다 `[공통]` 사용 | A절이 "경로 최다"를 기계적으로 지시. moneyball 은 `[공통]` 이 경로마다 상위 | 범용 키워드가 최다이고 기능 변경이면 `--grep=<기능명>` 으로 같은 기능 키워드 우선. 체크리스트 3 보강. git-pr 에도 반영 | TC-3 재실행 `[health-life] CORE-1561 ...` (99). TC-1 재실행 `[PGHD]` 유지 |

## 5. 남은 약점

- 이슈 키 위치: 원문은 요약 앞, moneyball 실측은 앞 1건 vs 끝 괄호 68건 (vc-conventions-guide 3절 판정 행 추가)
- pasta 의 `[키워드]` 는 대부분 squash 머지 제목. 개별 커밋은 `fix:`·`perf:` 가 많아 개별 커밋 적용의 실측 근거는 약함
- 입력에 실측 결과를 넣어 happy 격차가 작음
- --repeat 3 미실행

## 6. 확인된 것 vs 가정한 것

확인:
- 응답 원문 12건이 results/ 에 있음
- 키워드 실측은 로컬 체크아웃 `git log` (pasta origin/dev 최신 2026-11-06, moneyball origin/main 최신 2026-11-11)
- forge 이력은 `feat:`·`fix:`·`chore:`, `.claude/shared/` 없음

가정:
- poc 로컬 체크아웃 미발견, TC-2 최근 커밋은 가상 값 (재평가 트리거: poc 접근 시 실측 교체)
- 단일 채점자. TC-5 baseline 을 FAIL 로 본 것은 TC 정의에 따른 판단
- spotless 규칙은 이번에 검증 안 함

## 7. 최종 판정

PASS — v1.3 확정.
