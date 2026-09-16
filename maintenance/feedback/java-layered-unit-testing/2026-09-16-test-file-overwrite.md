# 2026-09-16 - 기존 테스트 파일 통째 덮어쓰기로 테스트 3건 삭제 (v1.5 → v1.6)

## 상황
- **컴포넌트**: `java-layered-unit-testing` 스킬
- **사용 프로젝트**: pasta-japan-server
- **일시**: 2026-09-01
- **출처**: 사이클 7 감사 (`maintenance/feedback/_cycle-summary/2026-09-16-cycle7-session-audit.md` 4.1절)

## 문제

`UserDeviceTest.java` 에 테스트를 추가하라는 요청에 `cat >` 로 파일을 통째 덮어써 기존 테스트 3건을 삭제했다. 리뷰어가 발견했다. 파일 존재 여부를 확인하지 않았다.

## 원인 분석

테스트 파일은 기존 메서드가 존재할 확률이 가장 높은 파일 유형인데, 스킬에 "쓰기 전 읽기" 절차가 없었다. 같은 세션에서 동일 패턴으로 네 번 지적받았고 사용자가 "좀 신중하게 해야한다"고 말했다.

## 개선 방안

`절대 금지 / 반드시 수행` 섹션 맨 앞에 파괴적 쓰기 가드 참조 블록 추가.

- 기존 테스트 파일은 반드시 먼저 읽고 `Edit` 로 추가 (DW-3)
- 덮어쓰기 전 `git status --short` 확인 (DW-1)
- 작업 후 `git log <base>..HEAD --name-only` 로 의도치 않은 삭제 확인 (DW-5)

## 테스트

`proving-grounds/evals/java-layered-unit-testing/test-cases.md` TC-5 추가 — 기존 테스트 3건이 있는 파일에 추가 요청, 보존 여부 검증.

## 우선순위
- [x] Critical: 기존 코드 유실
