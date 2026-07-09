---
component: coding-implementer
source: forge 내부 (리뷰 스킬 세분화 사이클)
date: 2026-07-09
type: delegation-target-change
severity: medium
---

## 증상 (v0.4 시점)

리뷰 스킬 세분화 사이클로 self-code-reviewer가 공통 룰만 담당하는 v2.0 슬림화. coding-implementer의 Phase 3-4 자체 리뷰가 self 단독 호출로는 관점별 검사(보안·성능·아키텍처) 커버 불가.

## v0.5 갱신

### 위임 대상 교체
- 기존: self-code-reviewer 단독
- 신규: **java-composite-reviewer 에이전트** (Task tool)
- 사유: composite가 4개 관점(공통·보안·성능·아키텍처) 자동 판단 + 병렬 리뷰 후 통합 리포트 제공

### Phase 3-4 관점 지정 옵션 추가
- `--scope=security|performance|architecture|common` 파라미터로 특정 관점만 리뷰 가능
- 없으면 → composite가 파일 유형 기반 자동 판단

### 하드 가드레일 6번 갱신
- 하위 composite가 호출하는 4개 리뷰 스킬 가드레일까지 우회 금지 명시

### 참조 인덱스
- self 자리에 5개 항목: composite + self v2.0 공통 + secure/performance/architecture 3개 관점

## 파일 크기

314줄 → 326줄 (+12, 300 목표 근접 초과이나 참조 인덱스 6개 명시로 불가피)

## 하드 가드레일 유지

기존 7건 유지. 오케스트레이터 정체성은 v0.3 그대로.

## 다음 단계

- coding-implementer 하네스 미작성 상태 계속 (테스트 대기)
- java-composite-reviewer 하네스 병행 필요
- 다음 실전 적용 시 위임 스킬 관점별 리뷰 성능 검증
