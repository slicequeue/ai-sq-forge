# 2026-09-16 - 파괴적 쓰기·범위 이탈 공통 가드 연결 (v1.13 → v1.14)

## 상황
- **컴포넌트**: `java-spring-coder` 스킬
- **사용 프로젝트**: pasta-japan-server, pasta-japan-metabase, pasta-app-metrics
- **출처**: 사이클 7 실전 세션 1개월 감사 (`maintenance/feedback/_cycle-summary/2026-09-16-cycle7-session-audit.md`)

## 문제

세 갈래다.

1. **파괴적 쓰기 가드 부재**. 2026-08-19 pasta-japan-metabase 에서 스크립트로 16개 파일을 일괄 덮어써 사용자의 미커밋 수정분이 영구 소실됐다. 복구 경로를 전부 확인했으나 불가. 동일 실패 양상이 2026-09-01 에 4회 재발했다(한 세션 내). 1개월간 최소 5회.
2. **범위 이탈 가드 부재**. 요청받지 않은 타 저장소 PR 생성, 합의 없는 DB 뷰 도입, 승인 없는 guid 컬럼 신설, 요청 고려사항 임의 제외. 4건.
3. **역수입 미반영 2건**. 타 저장소 코드 이식 시 원본 컨벤션 답습(2026-08-14 PR #689), 긴 gradle 작업 `nohup` 사용으로 빌드 중단 후 exit 0 오보고(2026-08-18).

## 원인 분석

기존 하드 가드레일은 `git stash` 금지와 마이그레이션 파일 보호만 다뤘고, **파일 쓰기 행위 자체**에 대한 사전 확인 절차가 없었다. `safe-mass-rename` 이 유사 가드를 갖췄으나 트리거가 "전역 식별자 리네임"으로 한정돼 스크립트 기반 일괄 재작성을 커버하지 못했다.

범위 이탈은 소프트 가드레일("scope creep 차단")로만 존재해 강제력이 없었다.

역수입 2건은 프로젝트 자동 메모리에만 기록되고 스킬 본문에 반영되지 않았다.

## 개선 방안

- 공통 자원 2건 신설: `forge/common/destructive-write-guard.md`(DW-1~DW-7), `forge/common/scope-discipline-guard.md`(SC-1~SC-7)
- 하드 가드레일 섹션 맨 앞에 두 가드 참조 블록 추가
- Phase 0 사전 확인에 7번 항목 추가 — 타 저장소 이식 여부 확인
- 하드 가드레일에 `nohup` 금지 + 빌드 산출물 손상 검사 절차 추가

## 테스트

- `proving-grounds/evals/java-spring-coder/test-cases.md` TC-11(미커밋 일괄 덮어쓰기), TC-12(중복 스키마 신설 + 범위 이탈) 추가
- Negative TC 카탈로그 L 카테고리 신설 (L-1 ~ L-5)

## 우선순위
- [x] Critical: 가드레일 위반 / 데이터 영구 손실
