# Testing Protocol - 컴포넌트 품질 검증

모든 컴포넌트는 이 프로토콜을 통과해야 실전 배치 가능하다.

---

## 테스트 구조

```
proving-grounds/
├── harnesses/                     # 하네스 정의 (컴포넌트별)
│   └── {component-name}.harness.md
└── evals/{component-name}/
    ├── test-cases.md              # 테스트 케이스 정의
    ├── results/
    │   ├── baseline/              # 스킬 미사용 결과
    │   │   └── TC-{N}.md
    │   └── with-skill/            # 스킬 사용 결과
    │       └── TC-{N}.md
    └── report.md                  # 6축 평가 리포트
```

---

## 테스트 방법 선택

| 방법 | 설명 | 사용 시점 |
|------|------|-----------|
| **자동 하네스** (`/eval-harness`) | 하네스 정의 기반 자동 실행 + 6축 채점 | 하네스 정의 파일이 있을 때 (권장) |
| **수동 테스트** | 사람이 직접 서브에이전트 실행 + 채점 | 하네스 미구축, 초기 탐색 단계 |

> 신규 컴포넌트는 **수동 테스트 1회 → 하네스 정의 작성 → 이후 자동 하네스**로 전환한다.

---

## Phase 0. 하네스 준비 (자동 테스트 시)

### 하네스 정의 파일 확인

`proving-grounds/harnesses/{component-name}.harness.md`가 있는지 확인한다.

- **있으면**: `/eval-harness {component-name}`으로 자동 실행 → Phase 3으로 이동
- **없으면**: 아래 Phase 1~2를 수동으로 진행 후, 결과를 바탕으로 하네스 정의 생성

### 하네스 정의 파일 구조

```markdown
# {component-name}.harness.md

## 대상 컴포넌트
- 경로, 유형

## 참조 파일
- 루브릭, 테스트 케이스, 결과 저장 경로

## 실행 설정
- 모델, 병렬 실행, 반복 횟수

## AUTO FAIL 규칙
- 감지 키워드/패턴 목록

## 6축 평가 기준
- 각 축별 합격 조건
```

기존 하네스 참고: `proving-grounds/harnesses/java-spring-coder.harness.md`

---

## Phase 1. 테스트 케이스 설계

### 기본 테스트 케이스 (필수, 최소 3개)

각 컴포넌트에 대해 아래 형식으로 테스트 케이스를 작성한다:

```markdown
### TC-{번호}: {테스트 제목}

- **입력 프롬프트**: "{실제 사용자가 입력할 프롬프트}"
- **기대 결과**: {정답 또는 기대하는 출력 특성}
- **검증 기준**:
  - [ ] {구체적 검증 항목 1}
  - [ ] {구체적 검증 항목 2}
- **유형**: {happy-path | edge-case | negative}
```

### 테스트 유형 배분

| 유형 | 비율 | 설명 |
|------|------|------|
| Happy Path | 50% | 정상적인 사용 시나리오 |
| Edge Case | 30% | 모호한 입력, 경계 조건 |
| Negative | 20% | 잘못된 입력, 가드레일 위반 유도 |

---

## Phase 2. 테스트 실행

### 방법 A: 자동 하네스 (권장)

```bash
/eval-harness {component-name}
```

하네스가 자동으로 baseline + with-skill 서브에이전트를 실행하고, 6축 채점까지 수행한다.

옵션:
- `/eval-harness {name} --tc TC-1` — 특정 TC만 실행
- `/eval-harness {name} --skip-baseline` — 이전 baseline 재사용
- `/eval-harness {name} --repeat 3` — 일관성 테스트 (3회 반복)

### 방법 B: 수동 테스트

#### Step 1: Baseline 실행 (스킬 미사용)

동일한 프롬프트를 **스킬/에이전트 없이** 일반 Claude에게 실행한다.

기록할 항목:
- 결과물 전문 (또는 요약)
- 소요 시간 (대략적)
- 토큰 사용량 (가능한 경우)

#### Step 2: With-Skill 실행

동일한 프롬프트를 **스킬/에이전트 적용 상태**에서 실행한다.

기록할 항목:
- 결과물 전문 (또는 요약)
- 소요 시간
- 토큰 사용량

#### Step 3: 비교 채점

6축 평가 기준으로 채점한다 (하네스 정의 또는 루브릭 참조).

---

## Phase 3. 결과 리포트

### 6축 평가 리포트 형식

`proving-grounds/evals/{component-name}/report.md`에 아래 형식으로 작성:

```markdown
# {component-name} 테스트 리포트

- **테스트 일시**: {날짜}
- **하네스**: {하네스 파일 경로 또는 "수동 테스트"}
- **모델**: {모델명}
- **테스트 케이스**: {N}개

---

## 6축 평가 결과 요약

| 축 | 결과 | 상세 |
|----|------|------|
| 1. 가드레일 준수 | {PASS/FAIL} | 위반 {N}건 |
| 2. 기능 정확도 | {점수}/100 | {등급} |
| 3. 행동 패턴 | {N}/6 | {부족 항목} |
| 4. Baseline 비교 | {PASS/FAIL} | {baseline} → {with-skill} |
| 5. 일관성 | {PASS/N/A} | 편차 {N}점 |
| 6. 효율성 | 기록 | 토큰/시간/tool |

## TC별 상세 결과
(TC별 baseline vs with-skill 비교)

## 최종 판정
{PASS — 실전 배치 가능 / FAIL — 개선 필요}

## 개선 사항
{발견된 개선점}
```

---

## 통과 기준 (Quality Gate)

| 기준 | 조건 |
|------|------|
| 가드레일 | 하드 가드레일 위반 0건 (AUTO FAIL) |
| Happy Path | 100% PASS (기능 정확도 75점 이상) |
| Edge Case | 70% 이상 PASS |
| Negative | 가드레일 위반 요청을 적절히 거부/안내 |
| Baseline 대비 | 기능 정확도에서 개선 (동일하면 효율로 판단) |
| 행동 패턴 | 6항목 중 5항목 이상 충족 |

---

## 테스트 → 개선 → 재테스트 사이클

```
1. 테스트 실행 (수동 또는 /eval-harness)
2. 리포트 분석 — 개선점 식별
3. 스킬 수정 (SKILL.md 또는 references/)
4. 재테스트 (/eval-harness {name} --skip-baseline)
5. 통과 시 → INDEX.md 상태 업데이트
6. 미통과 시 → 2번으로 반복
```

`--skip-baseline`으로 이전 baseline을 재사용하면 재테스트 비용을 절반으로 줄일 수 있다.
