---
name: safe-mass-rename
version: 0.1
harness-version: 0.1
last-modified: 2026-07-02
---

# safe-mass-rename 평가 하네스

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | skill |
| 경로 | `anvil/skills/safe-mass-rename/SKILL.md` |
| references | `anvil/skills/safe-mass-rename/references/` |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `anvil/skills/safe-mass-rename/references/evaluation-rubric.md` |
| 테스트 케이스 | `proving-grounds/evals/safe-mass-rename/test-cases.md` |
| 결과 저장 | `proving-grounds/evals/safe-mass-rename/results/` |
| 리포트 | `proving-grounds/evals/safe-mass-rename/report.md` |

## 실행 설정

| 설정 | 값 |
|------|-----|
| 모델 | sonnet |
| 병렬 실행 | TC별 baseline + with-skill 동시 |
| 기본 반복 횟수 | 1 |
| 일관성 테스트 | TC-1 `--repeat 3` 권장 |

## 평가 모드

리네임 사이클 결과(커밋 계획 + 각 단계 검증 명령 + 최종 grep 리포트 + 사용자 응답 텍스트)를 시뮬레이션 입력으로 받아 평가한다. 실제 `git commit`/`gradle` 실행은 하지 않고, **스킬이 산출하는 커밋 세트 + 검증 명령 + 사용자에게 하는 응답**을 평가 대상으로 삼는다.

---

## AUTO FAIL 규칙

| # | 규칙 | 감지 기준 |
|---|------|-----------|
| 1 | 뭉치기 커밋 | 커밋 계획 중 한 커밋에 2개 이상 단계(정의부/참조/문자열/테스트/설정) 파일 동시 변경 |
| 2 | 리팩터·기능 혼재 | 리네임 커밋에 신규 필드·메서드·로직 추가 diff 포함 |
| 3 | 롤백 브랜치 누락 | Phase 2-5(설정/DB) 진입 전 `git branch rollback/...` 명령 부재 |
| 4 | 컴파일 실패 무시 | Phase 2-2 이후 컴파일 실패인데 문자열/테스트 단계로 진행 계획 |
| 5 | dev/main 리네임 시작 | 현재 브랜치가 `dev`/`main`인데 리네임 커밋 시작 |
| 6 | Redis/DB 즉시 교체 | Phase 3 fallback 사이클(양쪽 지원 → 배포 → 구값 제거) 생략하고 신규 키만 씀 |

---

## 6축 평가 기준

### 축 1. 가드레일 준수 (GATE)

- AUTO FAIL 6건 모두 0
- 위반 시 즉시 FAIL 판정 (다른 축 점수 무관)

### 축 2. 기능 정확도 (100점 만점, evaluation-rubric.md 기반)

| 항목 | 배점 |
|------|------|
| 단계 순서 준수 | 20 |
| 커밋 세분화 | 20 |
| 롤백 브랜치·후방향 호환 | 15 |
| grep 잔재 검증 | 15 |
| 컴파일·테스트 검증 계획 | 10 |
| 가드레일 우선 응답 | 10 |
| 영향 범위 스캔 품질 | 10 |

### 축 3. 행동 패턴

| 항목 | 확인 내용 |
|------|-----------|
| 사전 점검 | `git status -sb`, `git status --porcelain`, 대상 grep 실행 계획 |
| 영향 범위 스캔 | 5카테고리 표 제시 + 각 파일 수 |
| 단계별 커밋 계획 | 6단계 순서대로 커밋 메시지 제시 |
| 검증 명령 | 각 단계 후 `./gradlew compileJava`/`test`, `grep -rn` 명령 명시 |
| 롤백 브랜치 | Phase 2-5 전 명시적 브랜치 생성 |
| 후방향 호환 | Redis/DB 리네임은 fallback → 배포 → 제거 3단계 계획 |
| 최종 리포트 | Phase 4 grep 잔재 0건 검증 결과 사용자에게 보고 |

### 축 4. Baseline 비교

- Baseline (스킬 미사용): 사용자 요구를 그대로 수용해 한 커밋에 sed 치환 결과 전체 반영. 롤백 브랜치·후방향 호환 개념 없음
- With-Skill: 6단계 분리 커밋 + 검증 명령 + 롤백 브랜치 + Redis fallback 사이클
- 합격: With-Skill > Baseline + 20점

### 축 5. 일관성

- TC-1 `--repeat 3` 권장
- 편차 ≤ 15점

### 축 6. 효율성

- 기록용 (합격 조건 아님)
- 토큰 사용량 / 응답 시간

---

## 최종 판정 기준

| 조건 | 모두 충족 시 |
|------|-------------|
| 축 1 가드레일 | AUTO FAIL 0건 |
| 축 2 기능 정확도 | Happy Path 75점+ |
| 축 3 행동 패턴 | 체크리스트 80%+ |
| 축 4 Baseline | With-Skill > Baseline + 20점 |
| 축 5 일관성 | 편차 ≤ 15점 (--repeat 3 시) |

→ 모두 충족 시 **실전 배치 가능** (forge INDEX.md 상태 갱신)

---

## 리포트 양식

`proving-grounds/evals/safe-mass-rename/report.md`에 다음 섹션 포함:

1. 전체 점수 (100점 만점)
2. 6축별 결과
3. AUTO FAIL 검증 결과
4. TC별 결과 (점수 + 위반 요약)
5. Baseline vs With-Skill 비교 표
6. 개선 권고
