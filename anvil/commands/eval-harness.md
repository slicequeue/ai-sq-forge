---
name: eval-harness
description: "컴포넌트 자동 평가 하네스를 실행합니다. 하네스 정의 파일 기반으로 baseline vs with-skill 비교 테스트를 자동 실행하고 6축 채점 리포트를 생성합니다."
trigger: "/eval-harness"
args: "{컴포넌트명} [--tc TC-1,TC-2] [--repeat N] [--baseline-only] [--skip-baseline]"
version: "1.0"
last-modified: "2026-04-10"
changelog: "초기 배포"
---

# /eval-harness

## 용도

스킬/에이전트/커맨드의 품질을 **자동으로 측정**한다. 하네스 정의 파일을 읽어 baseline(스킬 미사용) vs with-skill(스킬 적용) 비교 테스트를 실행하고, 6축 평가 리포트를 생성한다.

## 인자

| 인자 | 필수 | 설명 |
|------|------|------|
| `{컴포넌트명}` | 필수 | 평가 대상 컴포넌트명 (예: `java-spring-coder`) |
| `--tc TC-1,TC-2` | 선택 | 특정 TC만 실행 (기본: 전체) |
| `--repeat N` | 선택 | 반복 실행 횟수 (기본: 1, 일관성 테스트: 3) |
| `--baseline-only` | 선택 | baseline만 실행 |
| `--skip-baseline` | 선택 | 이전 baseline 결과 재사용, with-skill만 실행 |

## 사전 조건

실행 전 아래 파일이 반드시 존재해야 한다. 없으면 실행을 거부하고 생성 안내를 출력한다.

1. **하네스 정의**: `proving-grounds/harnesses/{컴포넌트명}.harness.md`
2. **테스트 케이스**: 하네스에 지정된 경로의 `test-cases.md`
3. **평가 루브릭**: 하네스에 지정된 경로의 `evaluation-rubric.md`
4. **대상 스킬**: 하네스에 지정된 경로의 `SKILL.md`

---

## 실행 로직

### Step 1. 하네스 로드

```
1. proving-grounds/harnesses/{컴포넌트명}.harness.md 읽기
2. 참조 파일 경로 파싱 (루브릭, 테스트 케이스, 스킬)
3. 모든 참조 파일 존재 여부 확인
4. AUTO FAIL 규칙 목록 로드
5. 6축 평가 기준 로드
```

### Step 2. 테스트 케이스 로드

```
1. test-cases.md 읽기
2. TC별 입력 프롬프트, 기대 결과, 검증 기준, 유형 파싱
3. --tc 옵션이 있으면 해당 TC만 필터링
4. TC 유형별 분류: happy-path / edge-case / negative
```

### Step 3. 서브에이전트 실행

각 TC에 대해 **baseline + with-skill 서브에이전트를 병렬 실행**한다.

#### Baseline 서브에이전트

```
프롬프트 구성:
  "일반 Claude Code로서 (특별한 스킬 없이) 아래 요청에 응답하세요.
   실제 코드를 파일에 쓰지 마세요. 어떻게 구현할지 시뮬레이션하세요.
   
   [TC의 입력 프롬프트]"

설정:
  - 모델: 하네스의 실행 설정.모델
  - 스킬 컨텍스트: 없음
  - 프로젝트 규칙: 없음
```

#### With-Skill 서브에이전트

```
프롬프트 구성:
  "아래 스킬을 적용하여 요청에 응답하세요.
   실제 코드를 파일에 쓰지 마세요. 어떻게 구현할지 시뮬레이션하세요.
   
   [스킬 SKILL.md + references/ 전체를 읽은 후 응답]
   
   [TC의 입력 프롬프트]"

설정:
  - 모델: 하네스의 실행 설정.모델
  - 스킬 컨텍스트: SKILL.md + references/ 전체
```

#### 병렬 실행 규칙

- `--skip-baseline`: with-skill만 실행, 기존 baseline 결과 재사용
- `--baseline-only`: baseline만 실행
- `--repeat N`: 각 TC를 N회 반복 (일관성 테스트)
- 기본: TC별로 baseline 1개 + with-skill 1개 = TC 수 x 2 에이전트

### Step 4. 결과 수집

```
1. 각 서브에이전트 완료 대기
2. 결과를 proving-grounds/evals/{컴포넌트}/results/ 에 저장
   - results/baseline/TC-{N}.md
   - results/with-skill/TC-{N}.md
3. --repeat N인 경우: TC-{N}-run{M}.md 형식으로 저장
```

### Step 5. 자동 채점 (6축 순서)

#### 축 1. 가드레일 준수 (GATE)

```
1. 하네스의 AUTO FAIL 규칙 목록을 순회
2. with-skill 결과에서 각 규칙의 감지 키워드/패턴 검색
3. 1건이라도 매칭 → 해당 TC AUTO FAIL 판정
4. Negative TC: 위반 요청을 거부했는지 + 대안 제시했는지 확인
5. 결과: PASS / FAIL
```

#### 축 2. 기능 정확도 (100점)

```
1. 루브릭의 채점표 항목 순회
2. 각 항목에 대해 with-skill 결과를 분석
   - 키워드 매칭 가능한 항목: 자동 채점
   - 판단이 필요한 항목: AI 판단 + 확신도 표시
3. baseline도 동일하게 채점 (비교용)
4. 확신도 낮은 항목은 [수동 검토 필요] 마킹
5. 결과: 점수/100 + EXCELLENT/PASS/FAIL
```

#### 축 3. 행동 패턴 (체크리스트)

```
1. 하네스의 행동 패턴 체크리스트 순회
2. with-skill 결과에서 각 항목 수행 여부 확인
   - Phase 0 언급 여부
   - 모드 A/B/C 선택 언급 여부
   - 기존 코드 Read 시도 여부
   - 생성 순서 (Domain → Infra → App → Web)
   - 자기 검증 체크리스트 수행 여부
   - 설정 체크 언급 여부
3. 결과: N/M 항목 충족
```

#### 축 4. Baseline 대비 개선도

```
1. baseline 기능 정확도 점수 vs with-skill 기능 정확도 점수
2. 점수 차이 및 개선율 계산
3. TC 유형별 비교 (happy-path, edge-case, negative)
4. 결과: PASS / STRONG PASS / FAIL
```

#### 축 5. 일관성 (`--repeat 3` 이상일 때만)

```
1. 동일 TC의 N회 실행 결과 점수 수집
2. 최고/최저/평균/편차 계산
3. AUTO FAIL 발생 횟수 확인
4. 결과: PASS (편차 ≤ 15, AUTO FAIL 0회) / FAIL
```

#### 축 6. 효율성 (기록용)

```
1. 각 서브에이전트의 토큰, tool 호출, 시간 수집
2. baseline vs with-skill 비교
3. TC별 및 전체 평균 기록
4. 결과: 표로 기록 (합격 조건 아님)
```

### Step 6. 리포트 생성

`proving-grounds/evals/{컴포넌트}/report.md`에 아래 형식으로 작성:

```markdown
# {컴포넌트명} 테스트 리포트

- **테스트 일시**: {날짜}
- **하네스**: proving-grounds/harnesses/{컴포넌트명}.harness.md
- **모델**: {모델명}
- **테스트 케이스**: {N}개 (Happy Path {n1} / Edge Case {n2} / Negative {n3})
- **반복 횟수**: {repeat}

---

## 6축 평가 결과 요약

| 축 | 결과 | 상세 |
|----|------|------|
| 1. 가드레일 준수 | {PASS/FAIL} | 위반 {N}건 |
| 2. 기능 정확도 | {점수}/100 | {EXCELLENT/PASS/FAIL} |
| 3. 행동 패턴 | {N}/6 | {부족 항목 나열} |
| 4. Baseline 비교 | {PASS/FAIL} | Baseline {점수} → With-Skill {점수} |
| 5. 일관성 | {PASS/FAIL/N/A} | 편차 {N}점 |
| 6. 효율성 | 토큰 {N} / 시간 {N}초 | tool {N}회 |

## TC별 상세 결과

### TC-{N}: {제목} [{유형}]

| 항목 | Baseline | With-Skill |
|------|----------|------------|
| 기능 정확도 | {점수} | {점수} |
| 가드레일 | {PASS/FAIL} | {PASS/FAIL} |
| 행동 패턴 | - | {N}/6 |
| [수동 검토 필요] | {있으면 표시} | {있으면 표시} |

(TC별 반복)

## 최종 판정

{PASS — 실전 배치 가능 / FAIL — 개선 필요 / AUTO FAIL}

## 개선 사항

{발견된 개선점 나열}
```

---

## 출력 형식

```
eval-harness 실행: {컴포넌트명}
  하네스: proving-grounds/harnesses/{컴포넌트명}.harness.md
  테스트 케이스: {N}개
  반복: {repeat}회

  TC-1 [{유형}] baseline ... with-skill ... 채점 완료
  TC-2 [{유형}] baseline ... with-skill ... 채점 완료
  TC-3 [{유형}] baseline ... with-skill ... 채점 완료

채점 결과:
  축 1 가드레일:   PASS (위반 0건)
  축 2 기능 정확도: {점수}/100 {등급}
  축 3 행동 패턴:  {N}/6
  축 4 Baseline:   {baseline 점수} -> {with-skill 점수} ({개선율})
  축 5 일관성:     {PASS/N/A}
  축 6 효율성:     토큰 {N} / 시간 {N}초 / tool {N}회

리포트 저장: proving-grounds/evals/{컴포넌트명}/report.md
판정: {최종 판정}
```

---

## 가드레일

- **하네스 정의 파일 없으면 실행 거부** — 자동 생성하지 않음. 생성 방법 안내만.
- **서브에이전트는 시뮬레이션만** — 실제 파일 변경 금지. 코드를 "어떻게 구현할지" 설명만.
- **기존 report.md 보호** — 덮어쓰기 전 사용자 확인. 이전 리포트는 `report-{날짜}.md`로 백업.
- **채점 불확실성 표시** — AI 판단에 확신이 낮은 항목은 `[수동 검토 필요]`로 마킹.
- **일관성 테스트 비용 고지** — `--repeat 3`은 에이전트 6~18개 실행. 토큰 비용 안내 후 확인.

---

## 하네스 정의 파일 생성 안내

하네스 정의 파일이 없을 때 아래를 안내한다:

```
하네스 정의 파일이 없습니다.
  경로: proving-grounds/harnesses/{컴포넌트명}.harness.md

생성하려면 아래가 필요합니다:
  1. 테스트 케이스: proving-grounds/evals/{컴포넌트명}/test-cases.md
  2. 평가 루브릭: anvil/skills/{컴포넌트명}/references/evaluation-rubric.md

기존 하네스를 참고하세요:
  proving-grounds/harnesses/java-spring-coder.harness.md
```
