# 2026-09-16 - 범위 규율·빌드 실행 가드 추가 (v0.5 → v0.6)

## 상황
- **컴포넌트**: `coding-implementer` 에이전트
- **출처**: 사이클 7 감사 (`maintenance/feedback/_cycle-summary/2026-09-16-cycle7-session-audit.md` 4.2절)

## 문제

1. **범위 이탈이 소프트 가드레일에만 존재**했다. "사용자 사전 합의 없이 추가 기능·refactor 끼워넣기 금지"가 소프트 항목이라 강제력이 없었다. 실전에서 타 저장소 PR 생성·합의 없는 뷰 도입·승인 없는 컬럼 신설이 발생했다.
2. **긴 gradle 작업 실행 방식 미규정**. 2026-08-18 `nohup ./gradlew ... &` 로 띄운 빌드가 래퍼 종료와 함께 죽었고 런처의 exit 0 만 보고 "완료"로 보고됐다. 잘린 jar 이 남아 후속 `testAcceptance` 가 17클래스 중 14건 `initializationError` → `ZipException` 으로 실패했다.

## 개선 방안

- 하드 가드레일 8번 신설 — 파괴적 쓰기 가드(DW-1~DW-7) 준수, 위임 스킬에도 동일 적용
- 하드 가드레일 9번 신설 — 범위 규율 가드(SC-1~SC-7) 준수. 소프트 가드레일의 scope creep 차단을 하드로 격상
- 하드 가드레일 3번에 하위 항목 추가 — `nohup` 금지·`run_in_background` 사용, 실패 귀속은 워크트리 기준선 대조로 확인(`git stash` 금지)

## 테스트

`proving-grounds/evals/coding-implementer/test-cases.md` TC-9(범위 밖 발견 시 임의 실행), TC-10(빌드 실행 방식과 실패 귀속) 추가.

## 우선순위
- [x] Major: 실전 사고 3건
