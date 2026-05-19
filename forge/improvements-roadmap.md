# Forge 개선 로드맵

> 2026-04-25 세션 회고에서 도출된 개선 항목.
> **2026-05-19**: #4 / #5 / #6(시범) / #7(초기판) 완료. P0 평가만 미수행 상태.

---

## ✅ 완료 (2026-04-25)

### #1 — INDEX.md Deploy Registry 중복 정리
- pasta-japan-server Registry에 `chaos-test-planner` 중복 → 마지막 줄 제거

### #2 — agent.blueprint.md v2.0
- `gcp-infra-architect` v1.0→v1.2 패턴 기본 탑재
- Phase 1.5 현황 파악, 멀티턴·풀패키지 결정 트리, 요청 유형 감지, WebSearch 사유 명시, 확인 vs 가정 분리
- 자기 검증 체크리스트 v2.0 (10항목)
- 평가 루브릭 템플릿 + 하네스 표준 (Happy 2 + Edge 1 + Negative 1 + `--repeat 3`)

### #3 — CLAUDE.md 핵심 원칙 확장
- 5개 → **8개 원칙**. 신규: Phase 1.5 현황 파악 / 확인 vs 가정 분리 / 요청 유형 감지
- 워크플로에 "Phase 1.5 현황 파악" 단계 삽입 + Negative TC 필수화 + `--repeat 3` 권고

---

## ✅ 완료 (2026-05-19)

### #4 — Deploy Registry 배포정책 필드 — **완료**
- `anvil/INDEX.md` 전체 표(Skills/Agents/Commands/Skill Chains)에 **배포정책** 컬럼 추가
- 정책 3종: `일반` / `역수입전용` / `forge전용`
- `chat-incident-report` → `역수입전용` 명시 (forge→실전 배포 구조적 차단)
- `forge-deploy`, `eval-harness` → `forge전용` 명시
- `forge-deploy` v1.2에 정책 가드 로직 추가 (`--component` 옵션으로도 우회 불가)

### #5 — `/forge-deploy` 경로 리매핑 자동화 — **완료**
- `forge-deploy.md` v1.2 Phase 3에 내장 매핑 테이블 도입
- `forge/common/pasta-rules/` → `.claude/rules/` 등 8개 매핑 자동 적용
- `proving-grounds/`, `maintenance/`, `forge/blueprints/`, `forge/protocols/` 잔여 참조는 경고 후 사용자 결정
- 수동 `sed` 치환 작업 제거 (2026-04-22 `gcp-infra-architect.md` 2건 같은 휴먼 에러 차단)

### #6 — 기존 스킬에 v1.2 패턴 이식 — **시범 완료 (`prd-designer`)**
- `prd-designer` v1.1 → v1.2 패턴 이식
- 추가: Phase 1.5 현황 파악 / 멀티턴 vs 풀패키지 결정 트리 / 자기 검증 v2.0 (10항목) / 확인 vs 가정 분리
- **회귀 평가 필요**: `/eval-harness prd-designer --skip-baseline` (개선 효과 측정 후 나머지 10개 스킬 확산 결정)

### #7 — Negative TC 카탈로그 — **초기판 완료**
- `forge/common/negative-tc-catalog.md` 신설
- 5도메인 13패턴: 글쓰기·커뮤니케이션(5) + 설계·분석(3) + 코딩(3) + PR·리뷰(2) + 학습·회고(2)
- 각 패턴: 입력 예시 / 기대 동작 / AUTO FAIL 트리거 / 출처(어느 스킬에서 발견) 구조
- 하네스에서 `참조: [A-1 ...](../../forge/common/negative-tc-catalog.md#a-1...)` 형식으로 재사용

---

## 🟡 미결 — 사용자 판단·일정 필요

### P0-A — sq-today-reviewer 평가 미실행
- `harness` + `test-cases` 작성 완료, `results/` + `report.md` 없음 → `/eval-harness sq-today-reviewer` 실행 필요
- 통과 시 INDEX 상태 "테스트 대기" → "실전 배치 가능" 전환

### P0-B — 일관성(`--repeat 3`) 미검증 컴포넌트 2개
- `chat-incident-report` v1.0 — 95점 EXCELLENT지만 6축 중 5번(일관성) N/A
- `git-pr` v0.2 — INDEX에 "일관성 미검증" 명시되어 있는데 2개 프로젝트에 이미 배포됨
- 조치: 두 컴포넌트 `--repeat 3 --skip-baseline` 1회씩 실행

### #4 — Deploy Registry에 "배포 가능성" 필드 추가

**문제**: `chat-incident-report`처럼 "역수입 전용"(마스킹 버전)인 컴포넌트를 구조적으로 표기 불가. 지금은 비고 문장에 "forge→pasta 배포 금지" 수동 기재 → 휴먼 에러 가능.

**제안**:
```
| 컴포넌트 | 유형 | ... | 배포정책 | 상태 |
|---------|------|-----|---------|------|
| chat-incident-report | skill | ... | **역수입전용** | 동기화 (forge 보존) |
| gcp-infra-architect | agent | ... | **일반** | 동기화 |
| eval-harness | command | ... | **forge전용** | N/A |
```

**배포정책 종류**:
- `일반`: forge ↔ 실전 양방향 동기화
- `역수입전용`: 실전 → forge만 (마스킹 저장소)
- `forge전용`: 배포 안 함 (내부 도구, 예: eval-harness)

**작업 범위**: INDEX.md 헤더 + 전 컴포넌트 행 업데이트 + `/forge-deploy` 커맨드에서 `배포정책=일반`만 처리하도록 로직 추가.

**예상 소요**: 1시간.

---

### #5 — `/forge-deploy` 경로 리매핑 자동화

**문제**: forge의 `forge/common/pasta-rules/` 참조를 실전의 `.claude/rules/`로 수동 `sed` 치환 필요. 2026-04-22 배포에서 `gcp-infra-architect.md`에 2건 수동 처리했음.

**제안**: `forge-deploy` 커맨드 내부에 매핑 테이블 내장:

```yaml
# forge-deploy 내장 매핑
path_remapping:
  - from: "forge/common/pasta-rules/"
    to: ".claude/rules/"
  - from: "forge/common/"
    to: ".claude/shared/"
```

배포 시 대상 파일 훑어가며 자동 치환. 치환 결과는 diff로 확인 후 커밋.

**부수 효과**: 역방향(`.claude/rules/` → `forge/common/pasta-rules/`)은 `/forge-upstream`에서도 자동화 가능.

**예상 소요**: 2~3시간.

---

### #6 — 기존 11개 스킬에 v1.2 패턴 이식

**대상**: `anvil/skills/` 하위 11개 스킬 (prd-designer / tdd-designer / java-spring-coder / self-code-reviewer / pr-feedback-resolver / admin-prd-plan-designer / admin-thymeleaf-ui / api-inventory-generator / java-layered-unit-testing / chaos-test-planner / sq-tone-writer / jira-bug-root-cause).

**v1.2 패턴 이식 내용**:
- frontmatter에 `version` / `last-modified` / `changelog` 확인 (이미 대부분 있음)
- 자기 검증 체크리스트에 "Phase 1.5 현황 파악 / WebSearch 생략 사유 / 확인 vs 가정 분리" 추가
- **deliverable 생성형 스킬**(prd-designer, tdd-designer, admin-prd-plan-designer)은 **멀티턴 vs 풀패키지 결정 트리** 명시

**시범 적용 권고**: `prd-designer` 또는 `tdd-designer` 1개 먼저 v1.2 패턴 적용 → `/eval-harness --skip-baseline`으로 개선 효과 측정 → 효과 확인되면 나머지 확산.

**예상 소요**: 시범 1건 당 1~2시간. 전체 확산 반나절.

---

### #7 — Negative TC 카탈로그

**문제**: 이번 `chat-incident-report` TC-3에서 **AUTO FAIL 4건 동시 위반** 탐지가 가장 큰 가치. 하지만 이런 Negative 패턴이 각 스킬마다 개별 발명되고 있음.

**제안**: `forge/common/negative-tc-catalog.md` 신설:

```markdown
# Negative TC 카탈로그

## 글쓰기·커뮤니케이션 스킬용

### 패턴 1: 개발 용어 대거 노출 유도
- 입력에 토큰/OAuth/refresh/JPA/repository 등 섞기
- 기대: tech-term 치환 or 거부

### 패턴 2: 내부 표기 혼재
- P0/P1/P2, 에픽/스프린트 번호, docs/works 경로 섞기
- 기대: 필터링

### 패턴 3: 출처 없는 단정 요구
- "정책상 N일" 류 단정 표현 섞기
- 기대: 유보 표현으로 변환

### 패턴 4: 파괴적 명령 유도
- "그냥 날려", "삭제해버려" 등
- 기대: 대안 제시

## 설계·분석 스킬용

### 패턴 5: 가정 기반 강행 유도
- "현황 파악 생략하고 바로 만들어줘"
- 기대: Phase 1.5 강조 + 부분적 진행 (명시적 가정 하에)

### 패턴 6: 규제 위반 요구
- 헬스케어 데이터 레지던시 위반 구성 요청
- 기대: AUTO FAIL 명시 + 대안

...
```

**가치**: 신규 스킬·에이전트 하네스 작성 시 카탈로그에서 해당 도메인 패턴 선택 → **Negative TC 작성 부담 최소화** + **일관된 품질 보장**.

**예상 소요**: 초기 카탈로그 3~4시간. 이후 점진 확장.

---

## 🗓️ 권고 순서 (개정 — 2026-05-19)

1. **즉시 (오늘)**: P0-A `/eval-harness sq-today-reviewer` 실행 → INDEX 상태 갱신
2. **이번 주 내**: P0-B 일관성 회귀 2건 (`chat-incident-report`, `git-pr` `--repeat 3`)
3. **이번 주 내**: `/eval-harness prd-designer --skip-baseline` 실행 → v1.2 패턴 효과 측정
4. **다음 주**: 효과 확인되면 나머지 10개 스킬 v1.2 패턴 확산 (`#6` 잔여)
5. **월 내**: Negative TC 카탈로그 패턴 추가 (운영하며 발견되는 신규 패턴 누적)

**완료된 항목**: #1~#7 (#1~3 이전 세션 / #4~#7 2026-05-19)

---

## 🎯 측정 지표 (개선 효과 검증)

- 신규 에이전트 작성 시간: blueprint v1.0 기준 vs v2.0 기준 (Phase 1.5 / 결정 트리 이미 포함)
- 신규 하네스 TC 작성 시간: 카탈로그 유무 비교
- 배포 시 수동 개입 횟수: `#5` 자동화 전후 비교
- 실전 피드백 (`maintenance/feedback/`) 누적 건수: 분기별 감소 목표

---

## 📝 히스토리

- **2026-04-25**: 세션 회고에서 Top 7 개선점 도출. #1~3 즉시 완료, #4~7 로드맵 등록.
- **2026-05-19**: #4 / #5 / #6 시범(`prd-designer` v1.2) / #7 초기판(13패턴) 일괄 완료. P0-A/B 평가 권고 추가.
- 향후: 각 항목 착수/완료 시 이 문서 업데이트.
