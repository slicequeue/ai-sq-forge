---
name: java-performance-reviewer
version: 0.2
harness-version: 0.2
last-modified: 2026-07-29
---

# java-performance-reviewer 평가 하네스

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | skill |
| 경로 | `anvil/skills/java-performance-reviewer/SKILL.md` |
| references | `anvil/skills/java-performance-reviewer/references/` |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `anvil/skills/java-performance-reviewer/references/evaluation-rubric.md` |
| 테스트 케이스 | `proving-grounds/evals/java-performance-reviewer/test-cases.md` |
| 결과 저장 | `proving-grounds/evals/java-performance-reviewer/results/` |
| 리포트 | `proving-grounds/evals/java-performance-reviewer/report.md` |

## 실행 설정

| 설정 | 값 |
|------|-----|
| 모델 | sonnet |
| 병렬 실행 | TC별 baseline + with-skill 동시 |
| 기본 반복 횟수 | 1 |
| TC 개수 | 8 (Happy 4 / Edge 2 / Negative 2) |
| 일관성 테스트 | TC-1 `--repeat 3` 권장 |

## 평가 모드

성능 관점 리뷰 결과(AUTO FAIL/필수 수정/권장 개선 3분류 리포트 + 자기 검증 응답 + 사용자 반문 대응)를 시뮬레이션 입력으로 받아 평가한다. 실제 코드 실행이나 EXPLAIN·프로파일링은 하지 않고, **스킬이 산출하는 리뷰 리포트 + 라우팅 안내 + 사용자에게 하는 응답**을 평가 대상으로 삼는다.

---

## AUTO FAIL 규칙

| # | 규칙 | 감지 기준 |
|---|------|-----------|
| 1 | G-1 놓침 | 변경 파일에 `@OneToMany`/`@ManyToMany` EAGER 있는데 AUTO FAIL 리포트 없음 |
| 2 | G-2 놓침 | for/stream 안 `Repository.findBy...`/`getBy...` 있는데 AUTO FAIL 리포트 없음 |
| 3 | G-3 놓침 | `WebClient.builder().*build()`에 timeout 관련 코드 없는데 AUTO FAIL 리포트 없음 |
| 4 | G-4 놓침 | Retry 필터에 4xx 한정자 없는데 AUTO FAIL 리포트 없음 |
| 5 | G-5 놓침 | `@Service`/`@Component` 싱글톤 클래스에 mutable instance field 있는데 AUTO FAIL 리포트 없음 |
| 6 | 관점 침범 | 아키텍처·보안·컨벤션 지적을 이 스킬 리포트에 넣음 (라우팅 안내로 그쳐야 함) |
| 7 | 코드 변경 실행 | 스킬이 파일 수정·커밋·push를 실제로 실행 (읽기 전용 위반) |
| 8 | AUTO FAIL 완화 수용 | 사용자가 "N+1 두자"·"timeout 나중에" 등 요구를 근거 없이 수용 |

**PERF-OPS 검증 요구 (v0.2 신규, 하드 가드레일 아님이지만 High 등급 검출 필수)**:
- HikariCP `maximum-pool-size`·`connection-timeout`·`max-lifetime` 미설정 → 검출 필요
- `server.shutdown: graceful` 미설정 → 검출 필요
- `spring.lifecycle.timeout-per-shutdown-phase` 미설정 → 검출 필요
- Kubernetes startup probe 짧음 (콜드스타트 앱) → 검출 필요
- `resources.limits` 미설정 → 검출 필요
- 인스턴스 수 × pool size × 앱 수 vs DB `max_connections` 정합성 검증 → 판정 유보 or 검증 권장

**검출 실패 시** AUTO FAIL은 아니지만 High 등급 놓침 → 축 2 기능 정확도 감점.

---

## 6축 평가 기준

### 축 1. 가드레일 준수 (GATE)

- AUTO FAIL 8건 모두 0
- 위반 시 즉시 FAIL 판정 (다른 축 점수 무관)

### 축 2. 기능 정확도 (100점 만점, evaluation-rubric.md 기반)

| 항목 | 배점 |
|------|------|
| 하드 가드레일 탐지 정확도 | 25 |
| N+1·JPA 검사 품질 | 15 |
| 캐시 계층 검사 품질 | 15 |
| 트랜잭션·비동기 검사 | 10 |
| 리소스·로깅 스팸 검사 | 10 |
| 관점 침범 회피 | 10 |
| 리포트 형식 준수 | 10 |
| 가드레일 우선 응답 | 5 |

### 축 3. 행동 패턴

| 항목 | 확인 내용 |
|------|-----------|
| 사전 점검 | Phase 0 5항목 (브랜치·변경 범위·성능 영향 파일 필터·현재 상태·baseline) |
| 하드 가드레일 우선 검사 | G-1~G-5 5개를 다른 검사보다 먼저 스캔 |
| 리포트 3분류 | AUTO FAIL·필수·권장 3분류 표 산출 |
| 관점 라우팅 | 성능 외 지적은 스킬 이름 명시하여 라우팅 안내 |
| 자기 검증 실행 | 리포트 하단에 자기 검증 10항목 체크 결과 |
| 사용자 반문 대응 | AUTO FAIL 완화 요구 거절 + 가드레일 번호 근거 명시 |

### 축 4. Baseline 비교

- Baseline (스킬 미사용): 성능 관점 지적 산발적, 하드 가드레일 개념 없음, 관점 분리 없이 뭉뚱그림
- With-Skill: G-1~G-5 하드 가드레일 정확 검출 + 3분류 리포트 + 관점 라우팅
- 합격: With-Skill > Baseline + 20점

### 축 5. 일관성

- TC-1 `--repeat 3` 권장
- 편차 ≤ 15점

### 축 6. 효율성

- 기록용 (합격 조건 아님)
- 토큰 사용량 / 응답 시간

---

## 최종 판정 기준

| 조건 | 모두 충족 시 |
|------|-------------|
| 축 1 가드레일 | AUTO FAIL 0건 |
| 축 2 기능 정확도 | Happy Path 75점+ |
| 축 3 행동 패턴 | 체크리스트 80%+ |
| 축 4 Baseline | With-Skill > Baseline + 20점 |
| 축 5 일관성 | 편차 ≤ 15점 (--repeat 3 시) |

→ 모두 충족 시 **실전 배치 가능** (forge INDEX.md 상태 갱신)

---

## 리포트 양식

`proving-grounds/evals/java-performance-reviewer/report.md`에 다음 섹션 포함:

1. 전체 점수 (100점 만점)
2. 6축별 결과
3. AUTO FAIL 검증 결과
4. TC별 결과 (점수 + 위반 요약)
5. Baseline vs With-Skill 비교 표
6. 개선 권고
