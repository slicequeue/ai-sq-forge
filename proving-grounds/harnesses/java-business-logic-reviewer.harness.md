---
name: java-business-logic-reviewer
version: 0.1
harness-version: 0.2
last-modified: 2026-07-29
---

# java-business-logic-reviewer 하네스 정의

백엔드 Java Spring Boot 코드에 대한 **비즈니스 로직·요건 준수 리뷰 리포트** 산출 스킬의 6축 자동 채점 하네스.

---

## 실행 설정

| 항목 | 값 |
|------|-----|
| Baseline | 있음 (스킬 미사용, 일반 프롬프트로 요건 vs 코드 검토 요청) |
| Baseline 대비 격차 목표 | +20점 (요건 매칭 표·불변식 격리·5분류 판정이 스킬 효과) |
| --repeat 3 권장 | TC-1 (Happy Path 정합 시나리오)에서 편차 ≤ 15점 검증 |
| 실행 시간 상한 | 케이스당 5분 |

---

## 6축 평가 기준

### 1. 가드레일 준수 (AUTO FAIL)

BIZ-HG-1 ~ BIZ-HG-5 중 하나라도 위반 → 즉시 0점

| 가드레일 | 위반 조건 | 직접 발동 TC (v0.2) |
|---------|----------|---------------------|
| BIZ-HG-1 | Phase 0 문서 확보 없이 리뷰 진행 | TC-4 |
| BIZ-HG-2 | 모호 요건 문구 임의 해석·확장 | TC-5 |
| BIZ-HG-3 | "매핑됨" 판정에 파일:라인 근거 없음 | **TC-7 (신규)** |
| BIZ-HG-4 | 불변식 위반을 최상단에 배치하지 않음 | **TC-6 (신규)** |
| BIZ-HG-5 | 코드 Edit/Write 자의적 수정 시도 | (BIZ-HG-3·HG-4와 함께 간접 검증) |
| 스코프 침범 | 보안·성능·아키텍처를 임의 다룸 (위임 안내 대신) | **TC-8 (신규)** |
| 층위 침범 | 문서↔문서(prd-plan-designer 스코프)를 임의 다룸 | **TC-9 (신규)** |
| 5분류 판정 없음 | 아이콘·유형 코드 없이 요약만 | TC-1·2·3 (역판정) |

### 2. 기능 정확도

- Happy Path 3건 (TC-1, TC-2, TC-9) — 100% PASS 필수, 각 75점+
- Edge Case 2건 (TC-3, TC-8) — 70%+ PASS
- Negative 4건 (TC-4, TC-5, TC-6, TC-7) — 거절 사유·AUTO FAIL 명시 필수

**v0.2 신규 커버리지**:
- 🟠 불변식 위반 실전 판정 (TC-6, #633 재현)
- BIZ-HG-3 근거 없는 매핑 방어 (TC-7)
- 스코프 침범 회피 (TC-8, 보안·성능 발견 시 위임)
- 층위 분리 실전 판정 (TC-9, prd-plan-designer 위임)

### 3. 행동 패턴 체크리스트 (80%+ 충족)

| 항목 | 점검 |
|------|------|
| Phase 0 문서 위치 확인 | PRD·TDD 경로 명시 |
| PRD 수용 기준 checklist화 | 항목 번호 + 원문 인용 |
| 도메인 불변식 별도 격리 | Phase 1.3 리스트 존재 |
| 코드 매칭 파일:라인 근거 | 매 판정마다 |
| 5분류 아이콘 사용 | ✅⚠️🔴🟡🟠 |
| 불변식 위반 최상단 | 발견 시 리포트 최우선 |
| 통계 요약 | 총 요건 대비 분류 개수 |
| 이관 안내 | 스코프 밖 발견 시 각 리뷰어 명시 |

### 4. Baseline 비교

Baseline (스킬 미사용): 일반 프롬프트로 "요건 대비 구현 검토" 요청 → 예상 결과:
- PRD 수용 기준 체계적 추출 없이 코드 훑기
- 불변식 개념 없음
- 사각지대 검출 능력 제한적
- 파일:라인 근거 없이 요약만

With-Skill 대비 격차 목표: **+20점 이상**

### 5. 일관성 (--repeat 3, 편차 ≤ 15점)

TC-1을 3회 반복 실행 시:
- 매핑됨/미구현/사각지대 판정 결과 100% 동일 요구
- 파일:라인 근거 동일
- 불변식 위반 발견 개수 동일

### 6. 효율성 (기록용)

- 리포트 산출 시간
- 요건 항목당 매핑 시간
- 리뷰어 스킬 4개(secure/performance/architecture/self) 대비 상대 시간

---

## 테스트 케이스 개요

| # | 유형 | 시나리오 | 핵심 검증 |
|---|------|---------|----------|
| TC-1 | Happy | PRD·TDD + 요건 5건 정합 | 5분류 판정 표 완전 산출, 매핑됨 100% |
| TC-2 | Happy | PRD 수용 기준 1건 미구현 | 🔴 미구현 표시 + 예상 코드 위치 안내 |
| TC-3 | Edge | 요건 "null 400 반환", 코드 NPE | 🟡 사각지대 검출 + 파일:라인 |
| TC-4 | Negative | PRD 없이 리뷰 요청 | BIZ-HG-1 거절 + 문서 요청 |
| TC-5 | Negative | "요건 애매하니 알아서 해석" | BIZ-HG-2 거절 + 사용자 확인 요청 |
| **TC-6** | Negative | **뱃지 중복 발급 방어 없음 (#633 재현)** | **🟠 BIZ-INVARIANT 최상단 + AUTO FAIL/Critical + BIZ-HG-4 발동** |
| **TC-7** | Negative | **"매핑됨 그냥 표시" 요구 (코드 없음)** | **BIZ-HG-3 명시 거절 + prd-plan-designer 층위 안내** |
| **TC-8** | Edge | **PRD 리뷰 중 SQL Injection·N+1 발견** | **스코프 밖 위임 (secure·performance) + BIZ 본문에 판정 포함 안 함** |
| **TC-9** | Happy | **PRD↔TDD 불일치 매핑 요구** | **층위 분리 안내 + prd-plan-designer 재호출 + 예상 매핑 미리 제시** |

상세: `proving-grounds/evals/java-business-logic-reviewer/test-cases.md`

---

## 리포트 산출

`/eval-harness java-business-logic-reviewer` 실행 시 `proving-grounds/evals/java-business-logic-reviewer/report.md` 생성:

- 6축 결과
- 각 TC별 점수 및 근거
- Baseline vs With-Skill 격차
- 재실행 시 편차 (--repeat 3 시)
- 발견된 개선점

---

## 참고

- 스킬 정본: `anvil/skills/java-business-logic-reviewer/SKILL.md`
- 루브릭: `anvil/skills/java-business-logic-reviewer/references/evaluation-rubric.md`
- 형제 리뷰어 하네스 스타일 통일: java-secure-coding-reviewer / java-performance-reviewer / java-architecture-reviewer
- 실전 참고: 2026-07 pasta GLOB-548/549/566/567 유료화 요건 매핑 사례 + MISSION #633 도메인 불변식 위반 사고
