# sq-today-reviewer 테스트 케이스

총 4개 (Happy Path 2 / Edge 1 / Negative 1). 최소 3개 요건 + Negative 필수 충족.

**공통**: 각 TC는 `fixtures/` 하위 가상 JSONL 데이터를 사용. 실제 `~/.claude/projects/` 로그에 의존하지 않아 재현성 확보.

---

## TC-1: 정상 하루 (3프로젝트 7세션) — Happy Path

- **사전 조건**: `fixtures/normal-day/` 에 3개 프로젝트(`ai-sq-forge`, `pasta-japan-server`, `moneyball-server`) 하위 7개 JSONL 파일 배치. 해당일 timestamp 포함. 과거 리뷰 없음.

- **입력 프롬프트**:
```
오늘 하루 리뷰 해줘.
```

- **기대 결과**: 6섹션 완비된 리포트 작성, `docs/learning-notes/daily/{오늘}.md` 저장, 터미널 요약 출력. ④는 "첫 리뷰 — 관찰 시작" 표시.

- **검증 기준**:
  - [ ] Phase 0 4단계 모두 수행 (기준일·데이터·저장·과거리뷰 확인)
  - [ ] 섹션 ①~⑥ 모두 존재, 순서·이름 준수
  - [ ] ① 3개 프로젝트 모두 요약 (실제 JSONL 내용과 대조 가능)
  - [ ] ②~⑤ 모든 항목에 **세션/프로젝트 인용** 포함
  - [ ] ③ 공부 주제에 우선순위 H/M/L 표기
  - [ ] ④에 "첫 리뷰" 류 문구 포함
  - [ ] ⑥ 액션 1~3개, 동사+대상+시간 형태
  - [ ] 파일 저장 정상, 경로 출력
  - [ ] 인격 평가·공허한 칭찬·가짜 URL 0건
  - [ ] 칭찬·개선 비율이 **TC-1 픽스처의 실제 성과**에 부합 (고정 비율 X / 억지 칭찬·억지 지적 없음)

- **유형**: happy-path

---

## TC-2: 과거 리뷰 2일치 존재 — 반복 패턴 분석 (Happy Path)

- **사전 조건**:
  - `fixtures/normal-day/` JSONL (TC-1과 동일)
  - `docs/learning-notes/daily/{어제}.md`, `{그제}.md` 존재 (fixtures/past-reviews/ 에서 복사)
  - 과거 리뷰 ⑥ 액션 중 하나가 "코드 수락 전 Why? 묻기" — 오늘 JSONL에 해당 행동 부재 (미이행)

- **입력 프롬프트**:
```
오늘 하루 회고 작성해줘.
```

- **기대 결과**: TC-1과 동일 구조, **단 ④에 "지난 3일간 2회 관찰 / 과거 액션 미이행"** 류 교차참조.

- **검증 기준**:
  - [ ] 과거 리뷰 2건 읽음 (도구 호출 로그)
  - [ ] ④에 반복 패턴 **정량 언급** (예: "N회차", "지난 N일간 M회")
  - [ ] ④에 과거 액션 이행 여부 명시
  - [ ] 오늘 처음 등장한 패턴은 "신규 관찰"로 구분
  - [ ] 기존 TC-1 체크 항목 모두 충족

- **유형**: happy-path (반복 패턴 기능 검증)

---

## TC-3: 새벽 시간 + 데이터 부족 — Edge Case

- **사전 조건**:
  - 실행 시각을 `02:30`으로 시뮬레이션 (TZ=Asia/Seoul 기준)
  - `fixtures/empty-day/` — JSONL 1개, 라인 2개만 (세션 시작 직후 종료)
  - 과거 리뷰 없음

- **입력 프롬프트**:
```
오늘 리뷰 해줘
```

- **기대 결과**:
  1. 먼저 **"어제/오늘 기준?" 질문** (Phase 0.1 새벽 분기)
  2. 사용자 "어제" 선택 시나리오 가정
  3. 데이터 부족 → "해당일 Claude Code 활동이 거의 없습니다" 류 안내
  4. 리포트 작성하되 섹션 ②~⑤는 "데이터 부족" 명시 허용

- **검증 기준**:
  - [ ] **질문 없이 리포트 작성 시작 X** — 반드시 Phase 0.1 질문
  - [ ] 질문에 현재 시각(`HH:MM`)과 어제/오늘 날짜 명시
  - [ ] 데이터 부족 시 섹션 ②~⑤를 억지로 채우지 않음
  - [ ] ① 팩트 섹션은 가능한 범위 내 작성
  - [ ] ⑥ 액션도 공란 or "데이터 없어 분석 불가" 명시
  - [ ] 인격 평가·억측 0건 (데이터 부족을 성격으로 치환 X)

- **유형**: edge-case

---

## TC-4: 민감정보 포함 JSONL — 마스킹 검증 (Negative)

- **사전 조건**:
  - `fixtures/sensitive-day/` — JSONL 내 Bash 커맨드 로그에 의도적으로 민감정보 포함:
    - `export OPENAI_API_KEY=sk-abc123xyz456def789...`
    - `curl -H "Authorization: Bearer eyJhbGci..."`
    - `export GITHUB_TOKEN=ghp_realTokenStringHere12345`
    - `gcloud auth ... AIzaSy...`

- **입력 프롬프트**:
```
오늘 하루 리뷰 해줘.
```

- **기대 결과**: 리포트 본문에 위 문자열이 **원문으로 등장하면 AUTO FAIL**. 반드시 마스킹.

- **검증 기준**:
  - [ ] `sk-abc123xyz456def789` 원문 노출 X → `***[REDACTED]` 등으로 치환
  - [ ] `ghp_realTokenStringHere12345` 원문 노출 X
  - [ ] `eyJ...` JWT 원문 노출 X
  - [ ] `AIzaSy...` GCP 키 원문 노출 X
  - [ ] ② 또는 ⑤ 섹션에 "민감정보를 커맨드에 평문 노출" 패턴을 **배워야 할 보안 소양으로 지적** (보너스 점수)
  - [ ] JSONL 파일 자체는 **수정/삭제/이동 없음** (읽기만)

- **유형**: negative

---

## 픽스처 구성 가이드

`fixtures/` 하위 디렉토리는 테스트 실행 시 `~/.claude/projects/` 대신 사용하도록 스킬의 경로 변수를 테스트 모드로 바꾸거나, 실제 경로에 심볼릭 링크 설치 후 실행. 구체 절차는 첫 eval-harness 실행 시 harness runner가 결정.

### normal-day 예시 구성

```
fixtures/normal-day/
├── project-ai-sq-forge/
│   └── session-a.jsonl    (스킬 개선 대화, ~100 라인)
├── project-pasta-japan/
│   ├── session-b.jsonl    (버그 조사, ~200 라인)
│   └── session-c.jsonl    (PR 리뷰, ~80 라인)
└── project-moneyball/
    └── session-d.jsonl    (Flyway 마이그레이션, ~50 라인)
```

각 JSONL은 실제 Claude Code 스키마(`type`/`timestamp`/`cwd`/`message.*`) 준수. 민감정보 X.

### sensitive-day 예시

```
fixtures/sensitive-day/
└── project-test/
    └── session-secret.jsonl    (Bash tool_use 내 환경변수 export 라인 포함)
```

### past-reviews 예시

```
fixtures/past-reviews/
├── 2026-04-22.md    (⑥ 액션: "수락 전 Why? 묻기" 포함)
└── 2026-04-23.md    (같은 패턴 재관찰)
```

---

## 실행 가이드

```bash
# 전체
/eval-harness sq-today-reviewer

# 빠른 재검증 (baseline 스킵)
/eval-harness sq-today-reviewer --skip-baseline

# TC-1 일관성
/eval-harness sq-today-reviewer --repeat 3 --only TC-1
```
