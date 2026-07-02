---
component: tolgee
source: pasta-japan-server PR #624 (사고 검증)
date: 2026-06-24
type: verification
severity: medium
---

## 사고 요약

`hotfix: 마이플랜 추천 운동 근력 그룹 메시지 키 변경 및 일본어 문구 수정 (#624)` — commit `e0eaf3fc99`, 2026-06-24. 근력 그룹 i18n 키를 `myplan.guide.workout.group.strength.title` → `create_myplan.result.recommended_workout.muscular`로 변경하고 일본어 문구를 자연스럽게 재작성.

## tolgee v0.2 규칙 대비 실전 결과

### 4파일 동기화 (Phase 1.1) — **FAIL**

배포 리포에는 `message-shared.properties` (default, `ls` 확인됨), `_ko_KR`, `_en_US`, `_ja_JP` 4파일이 존재. 그러나 이 커밋에서 변경된 것은 **3파일뿐**:

| 파일 | 변경 |
|---|---|
| `message-shared.properties` (default) | ❌ **누락** |
| `message-shared_ko_KR.properties` | ✅ 변경 |
| `message-shared_en_US.properties` | ✅ 변경 |
| `message-shared_ja_JP.properties` | ✅ 변경 |

tolgee v0.2 Phase 1.1의 사후 검증 (`grep -l "$key" message-shared*.properties | wc -l`) 결과가 `3`이므로 룰이 적용됐다면 **push 직전에 FAIL로 사전 차단**됐어야 하는 케이스.

### 커밋 원자성 (Java 코드 상수 + i18n) — PASS

Java 소스(`MyPlanRoutineRaceQueryResultMaker.java`) 상수 변경 + 3개 언어 파일이 한 커밋에 묶여 있음. 키 리네임은 코드-i18n을 함께 배포해야 정합성이 유지되므로 원자 커밋이 정답. tolgee v0.2에 명시적 룰은 없지만 위반 없음.

### en 카피 품질 (Phase 1.2) — SKIP

en 카피는 값 변경 없이 **키 이름만 변경**됨 (`Want to build strong muscles with strength training?` 그대로). 이번 사이클에서는 en 카피 품질 가드 검증 대상 아님.

### ja 카피 품질 — 사람 수정 (스킬 밖)

- before: `筋力トレーニングで体の中の固い筋肉を作りたいなら？` ("몸속의 딱딱한 근육"에 가까운 어색한 직역)
- after: `筋力トレーニングで引き締まった体を目指したいなら？` ("잘 다듬어진 몸을 목표로")

**직역 → 자연스러운 어휘로 개선**. tolgee v0.2가 Phase 1.2에서 다루는 en 품질 가드와 동일 성격의 문제가 ja에도 존재함이 확인됨. **개선점 파생**(아래 참고).

## 판정

**스킬 미사용 처리로 판정** (스킬 v0.2는 forge에만 존재, pasta 배포는 여전히 v0.1). 사람이 3개 언어 파일만 수정. default 파일 누락은 아무도 잡지 않고 그대로 머지됨. **재발 위험 있음** — 후속 코드에서 `message-shared.properties`를 참조하는 경로가 있다면 이전 키가 남아 lookup 시 fallback 동작 혼란 가능.

## 다음 개선점

1. **동기화 부채 청산 시급**: tolgee v0.2를 pasta-japan-server에 재배포. Phase 1.1이 적용됐다면 이 사고 사전 차단.
2. **default 파일 fallback 오염 확인 필요**: `message-shared.properties`에 이전 키 `myplan.guide.workout.group.strength.title`이 여전히 남아 있는지 grep 확인. 남아 있다면 소스 오브 트루스 관점에서 정합성 깨진 상태.
3. **Phase 1.2 확장 제안 — ja 품질 가드 추가 검토**: 현재 Phase 1.2는 en 어순·관사·placeholder만 다룸. ja도 직역체("体の中の固い" 같은) 패턴을 사전 차단할 수 있는지 검토. 다만 ja 자연어 판정은 en보다 문화적 판단 폭이 커서 자동 룰화 어려울 수 있음 → 사람 리뷰 프로세스로 유지가 합리적일 수도.
4. **키 리네임 사이클 지원 부재**: 이번 사고처럼 "기존 키 → 신규 키" 리네임 시, tolgee 스킬은 신규 키 추가에는 강하지만 **기존 키 제거 여부**는 다루지 않음. Phase 1.1에 "리네임 시 이전 키 제거 확인" 항목 추가 후보.

## 누적 검토

tolgee v0.2가 존재는 하지만 실전 미배포 상태로 인해 이번 사고를 못 잡음. 스킬 자체 품질보다 **동기화 부채**가 실전 안전망 실패의 주 원인. 배포 사이클(`/forge-deploy --sync`) 우선순위를 규칙 강화보다 앞에 두어야 하는 사례. 또한 키 리네임 시나리오는 tolgee 스킬이 아직 완전히 커버하지 못하는 영역으로, v0.3 후보로 기록.
