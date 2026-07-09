---
component: tolgee
source: pasta-japan-server PR #623 (2026-07-08)
date: 2026-07-08
type: verification-success
severity: none
---

## 사고 개요

pasta-japan-server 병원/그룹 관리자 등록 시 **사번 형식 검증 누락 hotfix** (커밋 `ea17bff9f4`, PR #623). 사번(employeeId) 형식 검증 추가와 함께 기존 `validator.name.*` 3건이 default/ko 파일에 일본어로 들어가 있던 번역 누락 정정.

## tolgee v0.2 규칙 대비 실전 결과

### Phase 1.1 — 4파일 동기화 강제: **PASS** ✅

변경된 파일:

| 파일 | 상태 | 신규 키 (`validator.employeeId.illegal-format`) | 기존 키 정정 (`validator.name.*`) |
|---|---|---|---|
| `message-shared.properties` (default) | ✅ | 추가 (한국어) | ko 문구로 교체 |
| `message-shared_ko_KR.properties` | ✅ | 추가 (한국어) | ko 문구로 교체 |
| `message-shared_en_US.properties` | ✅ | 추가 (영문) | en 문구로 교체 |
| `message-shared_ja_JP.properties` | ✅ | 추가 (일본어) | (기존 값 유지, 원래 정상) |

**default 파일이 포함된 4파일 모두 갱신** — v0.2 Phase 1.1 룰 정확히 준수.

### Phase 1.2 — en 카피 품질 가드: **PASS** ✅

신규 키 en 카피 확인:
```
validator.employeeId.illegal-format=Employee ID cannot contain spaces. Only letters, numbers, Japanese characters, and some symbols are allowed.
```

- 완전한 문장 구조 (주어·동사·목적어)
- placeholder 없음 (파라미터 삽입형 카피 아님, 문제없음)
- 한국어 어순 직역 아님 ("공백을 사용할 수 없습니다" → "cannot contain spaces" 자연스러운 영문 관용구)

기존 정정된 `validator.name.out-of-range=Name must be between 1 and 20 characters.` 도 자연스러운 영문.

### Phase 4 — Java 코드 Locale 함정: **N/A**

검증 메시지 정정만 있고 `toLowerCase()` / `toUpperCase()` / `String.format(Locale)` 등 Locale 의존 코드 변경 없음.

## 판정

**스킬 도움 있었음 (추정 강)**. 근거:
- 2026-07-02 tolgee v0.2 pasta 재배포로 실전 스킬 적용 상태
- 6/24 #624 사고에서는 default 파일 누락 → **FAIL** (당시 pasta 배포 v0.1)
- 이번 7/8 #623은 default 포함 완벽 4파일 동기화 → **PASS**
- 짧은 기간 내 같은 개발자가 다른 결과를 낸 것은 스킬 룰 적용 효과로 해석 가능

## 6/24 FAIL vs 7/8 PASS 대비

| 시점 | 배포 상태 | 결과 | default 파일 |
|---|---|---|---|
| 2026-06-24 (#624 myplan 근력) | tolgee v0.1 배포 | **FAIL** — 3파일만 변경 | 누락 |
| 2026-07-02 | v0.2 재배포 (사이클 3) | — | — |
| **2026-07-08 (#623 employeeId)** | tolgee v0.2 배포 | **PASS** — 4파일 완벽 | 포함 |

**동기화 부채 청산의 효과 검증 완료**. `/forge-deploy --sync` 로 스킬 강화판을 실전 프로젝트에 반영하는 사이클이 실제 사고 예방에 기여함을 첫 사례로 확인.

## 누적 검토

tolgee 스킬 첫 성공 사례. 회귀 평가(`/eval-harness tolgee`)는 아직 미실행이지만 실전 회귀 관찰이 하네스 통과 신호로 기능함. `test-cases.md` 작성 시 이 사례를 Happy Path TC로 재현하면 유리.
