---
name: forge-deploy
description: "Forge에서 개발·검증한 컴포넌트를 실전 프로젝트에 이식합니다. 경로 리매핑, 기존 컴포넌트 백업, 배치 상태 검증을 자동으로 수행합니다."
trigger: "/forge-deploy"
args: "{대상 프로젝트 경로} [--component 컴포넌트명] [--dry-run]"
version: "1.2"
last-modified: "2026-05-19"
changelog: "v1.2: 배포정책 필드(`일반`/`역수입전용`/`forge전용`) 가드 추가 — 정책 위반 컴포넌트 이식 자동 차단. 경로 리매핑 매핑 테이블 내장(`forge/common/pasta-rules/` → `.claude/rules/`)으로 수동 sed 치환 제거 | v1.1: Deploy Registry 연동, --sync, 커맨드 이식 프로세스, 버전 관리 추가"
---

# /forge-deploy

## 용도

Forge(`anvil/`)에서 개발·테스트를 거친 컴포넌트를 **실전 프로젝트의 `.claude/` 디렉토리**에 이식한다. 경로 자동 리매핑, 충돌 분석, 기존 컴포넌트 백업을 포함한 안전한 배포 워크플로.

## 인자

| 인자 | 필수 | 설명 | 기본값 |
|------|------|------|--------|
| `{대상 프로젝트 경로}` | 필수 | 이식 대상 프로젝트 루트 경로 | - |
| `--component {name}` | 선택 | 특정 컴포넌트만 이식 | 전체 |
| `--dry-run` | 선택 | 실제 파일 변경 없이 이식 계획만 출력 | - |
| `--sync` | 선택 | 레지스트리 등록된 전체 프로젝트의 동기화 상태 확인 및 재배포 | - |

---

## 실행 로직

### Phase 0. 사전 검증

```
1. 대상 프로젝트 경로 존재 확인
2. 대상 프로젝트에 .claude/ 디렉토리 존재 확인
   - 없으면: "대상 프로젝트에 .claude/ 디렉토리가 없습니다. 생성할까요?" 질문
3. anvil/INDEX.md 로드 — 컴포넌트 목록 및 상태 파싱
4. 대상 프로젝트의 .claude/ 하위 구조 스캔
   - .claude/skills/, .claude/agents/, .claude/commands/ 등 기존 컴포넌트 목록 수집
```

### Phase 1. 이식 대상 선정

```
1. anvil/INDEX.md에서 전체 컴포넌트 목록 추출 (Skills + Commands + Agents 모두 포함)
2. 각 컴포넌트의 배치 상태 확인:
   - "실전 배치 가능" → 이식 가능
   - 그 외 (테스트 대기, 개선 중 등) → 이식 불가 (경고)
   - 배치 상태 컬럼이 없는 컴포넌트(Commands 등) → "[미검증]" 경고 표시 후 포함 여부 확인
3. **배포정책 가드 (v1.2 신규)** — `anvil/INDEX.md`의 배포정책 컬럼을 읽고 정책별로 처리:
   - `일반` → 이식 가능
   - `역수입전용` → **이식 불가**. "실전 → forge 한 방향 동기화 컴포넌트입니다. forge→실전 배포가 차단되었습니다." 경고 후 자동 제외.
     예: `chat-incident-report` (실전에서 마스킹 처리 후 forge에 보존되는 컴포넌트)
   - `forge전용` → **이식 불가**. forge 내부 전용 컴포넌트.
     예: `forge-deploy`, `eval-harness`
   ※ 정책 컬럼이 누락되었으면 `일반`으로 간주하되 "[정책 미지정] 일반으로 처리" 표시.
4. --component 옵션이 있으면 해당 컴포넌트만 필터링 (단, 정책 가드는 항상 우선)

4. 사용자에게 이식 대상 목록을 제시하고 확인 요청:

   이식 가능한 컴포넌트:
   ✓ [skill] java-spring-coder (100/100) — 실전 배치 가능
   ✓ [skill] self-code-reviewer (95/100) — 실전 배치 가능
   ✓ [command] eval-harness — [미검증] 배치 상태 없음

   이식 불가 (테스트 미통과):
   ✗ [skill] example-skill — 테스트 대기
   → 이 컴포넌트는 테스트를 통과하지 않았습니다. 그래도 포함할까요?

5. 사용자가 선택한 컴포넌트 목록 확정
```

### Phase 2. 충돌 분석

```
1. 각 이식 대상에 대해 대상 프로젝트의 기존 컴포넌트와 비교
2. 충돌 유형 분류:
   - 동일 이름 존재: 직접 대체
   - 유사 기능 존재: 대체 후보로 제안
   - 신규: 충돌 없음
   ※ 커맨드 ↔ 기존 스킬 간 교차 충돌도 검사한다.
     예: commands/git-branch.md ↔ skills/git-branch-workflow/ (동일 기능, 다른 유형)

3. 충돌 리포트를 사용자에게 제시:

   충돌 분석 결과:
   [대체] java-spring-coder → 기존 skills/core-java/ 대체
   [대체] self-code-reviewer → 기존 agents/code-quality-manager.md (부분 대체)
   [교차 대체] commands/git-branch.md → 기존 skills/git-branch-workflow/ 대체 (커맨드↔스킬)
   [신규] eval-harness → 신규 배치 (충돌 없음)

   대체되는 기존 컴포넌트는 백업 후 삭제됩니다.
   진행할까요?

4. 사용자 확인 후 진행
   - 삭제 범위 조정 요청이 오면 개별 선택을 받는다.
```

### Phase 3. 경로 리매핑

**v1.2 내장 매핑 테이블** (자동 적용):

```yaml
path_remapping:
  # 공통 자원
  - from: "forge/common/pasta-rules/"
    to: ".claude/rules/"
  - from: "forge/common/"
    to: ".claude/shared/"
  # 컴포넌트 본체
  - from: "anvil/skills/"
    to: ".claude/skills/"
  - from: "anvil/agents/"
    to: ".claude/agents/"
  - from: "anvil/commands/"
    to: ".claude/commands/"
  - from: "anvil/skill-chains/"
    to: ".claude/skill-chains/"
  # 이식 제외 (남으면 경고)
  exclude_with_warning:
    - "proving-grounds/"
    - "maintenance/"
    - "forge/blueprints/"
    - "forge/protocols/"
```

```
1. 이식 대상 컴포넌트의 모든 파일(SKILL.md + references/*) 스캔
2. 내장 매핑 테이블로 자동 치환 시도. 매칭되지 않는 forge 내부 경로 참조는 잔여 목록에 기록.
3. exclude_with_warning에 매칭되는 참조가 있으면 → 사용자에게 경고:
   "{파일}:{줄} → '{경로}' 참조는 실전 환경에 존재하지 않습니다. 어떻게 처리할까요? (제거 / 주석 처리 / 그대로)"
4. 대상 프로젝트의 디렉토리 존재 검증:
   - `.claude/rules/`, `.claude/skills/`, `.claude/commands/`, `.claude/agents/` 등 매핑 대상 경로 존재 여부 확인
   - 없으면: 생성 여부 질문
5. 리매핑 결과 요약을 사용자에게 제시 (전체 확인 1회 — v1.1과 달리 항목별 질문 생략):

   경로 리매핑 결과 (자동):
   - forge/common/pasta-rules/ → .claude/rules/  ({N}건)
   - anvil/skills/.../references/ → .claude/skills/.../references/  ({M}건)
   - [잔여 — 사용자 결정 필요] proving-grounds/.../ ({K}건)

   진행할까요? (잔여 항목별 처리 방식 변경하려면 알려주세요)

6. 사용자 확인 후 리매핑 규칙 확정
```

**리매핑 자동화의 가치**: v1.1 이전에는 매 배포마다 `sed`로 수동 치환했음 (2026-04-22 `gcp-infra-architect.md` 2건). v1.2부터 내장 매핑으로 0건 수동 작업.

### Phase 4. 백업

```
1. 백업 위치 결정 (사용자에게 확인):
   a. forge 프로젝트 내: forge/backup/{YYYY-MM-DD}/ (forge에서 이력 관리 시 권장)
   b. 대상 프로젝트 내: {대상}/.claude/backup/{YYYY-MM-DD}/ (대상 프로젝트 자체 복원 시 권장)
   ※ 사용자가 별도 지정하면 해당 경로 사용

2. 대체 대상 기존 컴포넌트를 백업 디렉토리로 복사:
   - skills/core-java/ → backup/{date}/core-java/
   - agents/code-quality-manager.md → backup/{date}/code-quality-manager.md
   - skills/git-branch-workflow/ → backup/{date}/git-branch-workflow/
   (교차 대체 대상 스킬도 포함)

3. 백업 완료 확인 메시지:
   백업 완료: {선택된 백업 경로}
   - (백업된 파일 목록)
```

### Phase 5. 이식 실행

```
1. --dry-run이면 여기서 중단 (Phase 6 리포트만 출력)

2. 각 컴포넌트에 대해:
   a. 소스 파일 읽기 (anvil/{type}/{name}/)
   b. 경로 리매핑 적용 (Phase 3 규칙)
   c. 대상 경로에 파일 쓰기:
      - Skills: {대상}/.claude/skills/{name}/SKILL.md + references/
      - Commands: {대상}/.claude/commands/{name}.md
        ※ .claude/commands/ 디렉토리가 없으면 자동 생성
      - Agents: {대상}/.claude/agents/{name}.md (또는 폴더)

3. 대체된 기존 컴포넌트 삭제:
   - Phase 2에서 확인된 대체 대상만 삭제 (교차 대체 포함)
   - 백업이 Phase 4에서 완료되었음을 재확인

4. 파일별 이식 결과 기록
```

### Phase 6. 이식 리포트

```
사용자에게 최종 결과를 보고:

forge-deploy 완료
  대상: /path/to/project
  일시: {날짜시간}

이식된 컴포넌트:
  ✓ [skill] java-spring-coder → .claude/skills/java-spring-coder/
    - SKILL.md + references/ {N}개 파일 ({M}줄)
    - 경로 리매핑 {N}건 적용
  ✓ [command] git-branch → .claude/commands/git-branch.md
    - [미검증] 배치 상태 없음

백업됨:
  {백업 경로}/
  - skills/core-java/ (→ java-spring-coder로 대체)
  - agents/code-quality-manager.md (→ self-code-reviewer + pr-feedback-resolver로 대체)
  - skills/git-branch-workflow/ (→ commands/git-branch.md로 교차 대체)

삭제됨:
  - skills/core-java/ (→ java-spring-coder로 대체)
  - skills/git-branch-workflow/ (→ commands/git-branch.md로 교차 대체)

유지됨 (건드리지 않음):
  - (삭제 범위에서 제외된 기존 컴포넌트 목록)

경로 리매핑:
  (총 {N}건 적용, 또는 "0건 — 리매핑 불필요")
```

---

## 사용자 확인 전략

Phase 1~3은 각각 사용자 확인이 필수지만, 질문 피로도를 줄이기 위해 다음 전략을 따른다:

- **Phase 1 + Phase 2를 가능한 한 통합 제시** — 이식 대상 목록과 충돌 분석을 한 번에 보여주고 한 번의 확인으로 처리. 단, 사용자가 삭제 범위 조정을 요청하면 추가 질문.
- **Phase 3(경로 리매핑)이 0건이면 별도 확인 생략** — "리매핑 불필요" 한 줄 보고 후 바로 Phase 4로 진행.
- **dry-run과 실행 확인은 반드시 분리** — dry-run 결과를 보여준 후 실행 여부를 별도 확인.

## 출력 형식

```
forge-deploy 시작: {대상 프로젝트 경로}

Phase 0. 사전 검증 ... ✓
Phase 1. 이식 대상 선정 ... (사용자 확인 대기)
  ✓ [skill] java-spring-coder (100/100)
  ✓ [command] git-branch — [미검증] 배치 상태 없음
  선택된 컴포넌트: 스킬 {N}개, 커맨드 {M}개

Phase 2. 충돌 분석 ... (사용자 확인 대기)
  [대체] {N}건 / [교차 대체] {M}건 / [신규] {K}건

Phase 3. 경로 리매핑 ...
  리매핑 규칙: {N}건 (0건이면 "불필요 — 생략")

Phase 4. 백업 ... ✓
  백업 위치: {사용자 선택 경로}

Phase 5. 이식 실행 ... ✓
  파일 {N}개 이식, {M}개 삭제 완료

Phase 6. 리포트
  (이식/백업/삭제/유지 항목별 최종 결과 출력)
```

---

## 가드레일

### 하드 가드레일 (절대 위반 불가)

1. **테스트 미통과 컴포넌트 무조건 이식 금지** — "실전 배치 가능"이 아닌 컴포넌트는 사용자에게 경고하고 포함 여부를 반드시 확인. 사용자가 동의해도 리포트에 "[미검증]" 경고 표시.
2. **백업 없이 삭제 금지** — 기존 컴포넌트를 삭제하기 전에 반드시 백업 완료.
3. **사용자 확인 없이 실행 금지** — Phase 1(대상 선정), Phase 2(충돌 분석), Phase 3(경로 리매핑) 각각에서 사용자 확인을 받아야 다음 단계 진행.
4. **대상 프로젝트의 rules/ 파일 수정 금지** — 규칙 파일은 참조만 하고 절대 수정/삭제하지 않음.
5. **proving-grounds/ 이식 금지** — 하네스, 테스트 케이스, 리포트는 forge 전용. 이식 대상에서 제외.
6. **배포정책 위반 금지** — `역수입전용`/`forge전용`은 어떤 옵션·플래그로도 우회 불가. 정책 변경은 INDEX.md에서 명시적 수정이 필요.

### 소프트 가드레일 (권장)

- `--dry-run`으로 먼저 확인 후 실제 이식 권장
- 이식 후 대상 프로젝트에서 기본 동작 확인 권장 (스킬 트리거 테스트)
- 한 번에 너무 많은 컴포넌트를 이식하지 말고 단계적 배포 권장

---

## Deploy Registry 연동

### 배포 레지스트리 (`anvil/INDEX.md` > Deploy Registry)

이식 완료 후 `anvil/INDEX.md`의 Deploy Registry 테이블을 자동 업데이트한다.

```
1. 이식 완료 시 (Phase 6 리포트 후):
   - anvil/INDEX.md의 Deploy Registry 섹션 확인
   - 해당 프로젝트 행이 있으면 → 배포된 컴포넌트 목록 + 최종 배포일 업데이트
   - 없으면 → 새 행 추가

2. 레지스트리 형식:
   | 프로젝트 | 경로 | 배포된 컴포넌트 | 최종 배포일 |
   |---------|------|----------------|-----------|
   | {프로젝트명} | {절대 경로} | {컴포넌트 목록} | {YYYY-MM-DD} |
```

### 스킬 개선 시 연결 프로젝트 확인

컴포넌트가 수정/개선되었을 때 (INDEX.md 상태 변경, 하네스 재검증 등):

```
1. anvil/INDEX.md의 Deploy Registry 스캔
2. 수정된 컴포넌트가 배포된 프로젝트 목록 추출
3. 사용자에게 알림:

   [연결 프로젝트 감지]
   수정된 컴포넌트: java-spring-coder
   배포된 프로젝트:
     - pasta-japan-server (최종 배포: 2026-04-10)

   연결된 프로젝트에 재배포할까요?
   → "예" → /forge-deploy {경로} --component java-spring-coder 자동 실행
   → "아니오" → 레지스트리에 "[미동기]" 표시
```

### --sync 옵션

```
/forge-deploy --sync
```

레지스트리에 등록된 모든 프로젝트에 대해:
1. 각 프로젝트의 배포된 컴포넌트 버전과 forge 최신 버전 비교
2. 차이가 있는 컴포넌트 목록 제시
3. 사용자 확인 후 선택적 재배포
