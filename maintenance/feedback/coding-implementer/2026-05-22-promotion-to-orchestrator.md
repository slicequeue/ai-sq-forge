---
component: coding-implementer
source: forge 내부 (통합 검토 결정)
date: 2026-05-22
type: improvement
severity: high
---

## 증상 (이전 상태)

v0.2 시점에 `coding-implementer` 에이전트가 `java-spring-coder` 스킬과 본질적으로 같은 영역(Spring Boot 4-Tier 구현)을 다루고 있었음. 차별 가치는 "agent 형태의 컨텍스트 격리"뿐 — 본질이 약함. 통합 검토 시 폐기 후보로 거론.

## 사용자 결정 (2026-05-22)

> "본질 차별화로 해보자! 뭔가 한단계 더 위에서 여러 개발 스킬들을 조합해서 멋지개 개발 해내는 쪽 그리고 통합으로 문제 있는지 까지 자체 점검 스킬들 다 있으니 그거까지 해내는 것으로! 커멘드도 잘 써서 작업 단계별로 커밋도 잘하고! 브렌치 안되어 있으면 잘 나누고 등등 종합 적으로 해내는 친구로 격상"

결정: **'개발 사이클 오케스트레이터'로 격상**. 단일 청크 구현은 java-spring-coder 스킬, 본 에이전트는 사이클 전체.

## 격상 내용 (v0.3)

### 정체성 재정의

기존: "pasta-japan-server 코딩·단위 테스트 구현 전문가"
신규: "한 기능을 처음부터 끝까지 자율 진행하는 개발 사이클 오케스트레이터"

### 본문 재구성 (244줄 → ~280줄)

- 기존 v0.2의 코딩 규칙 본문(1.1~1.10)은 java-spring-coder v1.9 위임으로 일원화 — 중복 정의 제거
- Phase 0~6 워크플로 신설:
  - Phase 0: 현황 점검 6항목 (브랜치/uncommitted/TDD/PRD/JDK/dev 동기화)
  - Phase 1: 브랜치 준비 (`/git-branch` 트리거)
  - Phase 2: 계획 확인 (TDD/PRD 부재 분기)
  - Phase 3: Phase별 구현 사이클 (3-1 구현 / 3-2 테스트 / 3-3 빌드·테스트 / 3-4 자체 리뷰 / 3-5 사용자 확인 / 3-6 커밋)
  - Phase 4: 인수 테스트 (`acceptance-tester` agent 위임)
  - Phase 5: PR 준비 (`git-pr` 스킬 위임)
  - Phase 6: 최종 보고

### 오케스트레이션 대상

9개 컴포넌트 조합:
- `/git-branch`, `/git-commit` (커맨드)
- `prd-designer`, `tdd-designer`, `admin-prd-plan-designer` (계획)
- `java-spring-coder`, `java-layered-unit-testing` (구현·테스트)
- `self-code-reviewer` (자체 리뷰)
- `acceptance-tester` (인수 테스트 — agent → agent Task tool 호출)
- `git-pr` (PR 본문)
- `pr-feedback-resolver` (선택)

### 하드 가드레일 7건

1. 사용자 명시 승인 없이 push/PR 생성 금지
2. dev/main 직접 커밋 금지
3. 5회 연속 빌드 실패 시 즉시 중단
4. self-review 위반 수정 3회 초과 → 사용자 위임
5. TDD/PRD 부재 시 임의 진행 금지
6. 위임 스킬 가드레일 우회 금지
7. git stash / reset --hard / push --force 금지

### 자기 검증 12항목

기존 항목 + v0.3 신규 3건 (위임 컨텍스트 압축 / Phase 보고 패턴 / 5회·3회 가드 발동 시 즉시 보고)

## 개선 효과 예상

| 사용자 요청 | 이전 (v0.2) | 격상 후 (v0.3) |
|------------|-------------|---------------|
| "TDD 기반으로 사이클 전체" | java-spring-coder 호출 후 사용자가 매 단계 수동 | 한 호출로 Phase 1~N + 인수 테스트 + PR 준비까지 자율 |
| 작업 브랜치 없을 때 | 사용자가 별도로 `/git-branch` 호출 | 본 에이전트가 Phase 1에서 자동 트리거 |
| Phase별 커밋 | 사용자가 각 Phase 후 수동 `/git-commit` | Phase 3-6에서 자동 트리거 (사용자 승인 후) |
| 자체 리뷰 | 별도 호출 | Phase 3-4 자동 + 위반 시 자동 수정 루프 |

## 잠재 리스크

1. **컨텍스트 폭주**: 위임 호출이 많아 토큰 비용·시간 큼. 단순 1청크 작업에 본 에이전트 쓰면 비효율 → 자기 검증 #10(컨텍스트 압축) + 사용 시점 표로 회피
2. **자율 실행의 통제력**: 사용자 확인 포인트(Phase 3-5, Phase 4, Phase 5)에서 멈추지 않으면 의도하지 않은 변경 누적 위험 → 하드 가드레일 1, 6번으로 차단
3. **위임 스킬 변경 시 본 에이전트 영향**: java-spring-coder가 v2.0으로 메이저 변경되면 본 에이전트 워크플로 재점검 필요 → 본 파일의 참조 인덱스에 정본 위치 명시로 추적

## 다음 단계

- 평가 루브릭 + 하네스 작성 → `/eval-harness coding-implementer` (현재 '테스트 대기')
- 첫 실전 적용 후 maintenance/feedback 추가 누적
- 통합 검토 사이클: prd-plan-designer agent도 같은 톤으로 격상 검토 (PRD ↔ TDD 일관성 매핑 자동 산출 본질)

## 누적 검토

본 컴포넌트 격상은 단일 사례지만 정체성 재정의 + 본문 80% 재작성이라 v0.3 마이너 bump가 아니라 **메이저 변경**에 가까움. 다음 회귀 평가에서 본질 차별화 효과 측정 필요.
