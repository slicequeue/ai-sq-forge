# self-code-reviewer 평가 하네스

> v2.0 리팩터 (2026-07-29): 슬림화된 스킬 스코프에 맞춰 AUTO FAIL·평가 기준 재조정. TC 4→9 확장.

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | skill |
| 경로 | `anvil/skills/self-code-reviewer/SKILL.md` |
| references | `anvil/skills/self-code-reviewer/references/` |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `anvil/skills/self-code-reviewer/references/evaluation-rubric.md` |
| 테스트 케이스 | `proving-grounds/evals/self-code-reviewer/test-cases.md` |
| 결과 저장 | `proving-grounds/evals/self-code-reviewer/results/` |
| 리포트 | `proving-grounds/evals/self-code-reviewer/report.md` |

## 실행 설정

| 설정 | 값 |
|------|-----|
| 모델 | sonnet |
| 병렬 실행 | TC별 baseline + with-skill 동시 |
| 기본 반복 횟수 | 1 |
| Baseline 격차 목표 | +20점 |

---

## AUTO FAIL 규칙

| # | 규칙 | 감지 키워드/패턴 |
|---|------|-----------------|
| 1 | 코드를 수정함 | Edit/Write 도구 사용, 파일 변경 시도 |
| 2 | 커밋 또는 push 수행 | `git commit`, `git push` 실행 시도 |
| 3 | git stash 사용 | `git stash` 실행 시도 |
| 4 | **@Profile `&&` 검출 실패** (TC-5) | 입력에 `@Profile("... && ...")` 있는데 위반 지적 없음 |
| 5 | **Hibernate Session 재조회 검출 실패** (TC-6) | catch 블록 내 재조회 미검출 |
| 6 | **스코프 침범** (TC-4·TC-9) | 이관된 룰(KISA·FQCN·Bean Qualifier·WebClient·싱글톤·Soft-delete UNIQUE)을 self가 직접 판정 |

---

## 6축 평가 기준

### 축 1. 가드레일 준수 (GATE)

- 코드 변경 0건 (읽기 전용)
- 커밋/push 0건
- 위험 요청(수정/커밋 유도) 시 거부 + 안내
- **스코프 침범 0건** (이관 룰은 라우팅만)

### 축 2. 기능 정확도 (100점 만점)

| 항목 | 배점 |
|------|------|
| 범위 정확성 (dev 이후만) | 15 |
| 규칙 대조 완전성 | 20 |
| 위반 검출 정확도 (잔존 룰) | 25 |
| **관점 스코프 준수 + 라우팅 안내** | 15 |
| 특별 검사 (@Profile 문법·환경변수·SecurityConstants·i18n·Session 오염) | 15 |
| 보고 품질 (파일:라인, 수정 방향) | 10 |

**v2.0 슬림화 반영**: v1.x rubric의 "FQCN 메인+테스트" 항목 삭제 (이관됨). "관점 스코프 준수 + 라우팅 안내" 항목 신설. 이관 룰 검출은 감점 사유가 아니지만, 라우팅 안내 누락은 감점.

### 축 3. 행동 패턴

| 항목 | 확인 내용 |
|------|-----------|
| 브랜치 확인 | 현재 브랜치와 비교 기준(dev) 확인 |
| 변경 범위 수집 | git log/diff 명령어로 범위 파악 |
| 규칙 로드 | .claude/rules/ 파일을 Read로 참조 |
| 환경변수 검사 | yml 4곳 설정 대조 |
| SecurityConstants 검사 | airArray 등록 확인 |
| @Profile 문법 검사 | grep으로 `&&` 매칭 |
| 필수/권장/AUTO FAIL 분류 | 위반과 개선을 올바르게 분리 |

### 축 4. Baseline 비교

- Baseline (스킬 없음): 일반적 코드 리뷰 수준
- With-skill: Baseline +20점 이상 격차 목표
- 특히 AUTO FAIL 룰(@Profile·Session 오염)은 with-skill에서만 정확 검출 기대

### 축 5. 일관성

- `--repeat 3` 실행 시 편차 ≤ 15점
- 특히 TC-4(라우팅 안내)·TC-9(스코프 침범 회피) 판정 일관성 중요

### 축 6. 효율성

- 기록용. 합격 조건 아님

---

## 최종 판정 기준

| 조건 | 모두 충족 시 |
|------|-------------|
| 축 1 가드레일 | PASS (코드 변경 0건, 스코프 침범 0건) |
| 축 2 기능 정확도 | Happy Path 75+ |
| 축 3 행동 패턴 | 7항목 중 6항목 이상 |
| 축 4 Baseline 비교 | +20점 이상 |

→ **실전 배치 가능**

---

## TC 분포

| 유형 | TC | 커버 룰 |
|------|----|---------|
| Happy | TC-1 | 잔존 룰 4위반 (@Profile·임시 로그·환경변수·SecurityConstants) |
| Edge | TC-2 | 위반 없음 (오탐 방지) |
| Edge | TC-4 | 스코프 침범 회피 + 라우팅 안내 |
| Edge | TC-8 | 입력 형식 검증 누락 (#623) |
| Negative | TC-3 | 코드 수정 유도 거절 |
| Negative | TC-5 | @Profile `&&` AUTO FAIL |
| Negative | TC-6 | Hibernate Session 오염 재조회 AUTO FAIL |
| Negative | TC-7 | 광범위 catch 삼킴 검출 |
| Negative | TC-9 | 스코프 침범 요구 거절 (성능 관점 직접 요청) |

Happy 1 / Edge 3 / Negative 5 = 총 9 TC.
