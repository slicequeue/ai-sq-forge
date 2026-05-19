# chat-incident-report 평가 하네스

## 대상 컴포넌트

| 항목 | 값 |
|------|-----|
| 유형 | skill |
| 경로 | `anvil/skills/chat-incident-report/SKILL.md` |
| references | `anvil/skills/chat-incident-report/references/` |

## 참조 파일

| 파일 | 경로 |
|------|------|
| 루브릭 | `anvil/skills/chat-incident-report/references/evaluation-rubric.md` |
| 테스트 케이스 | `proving-grounds/evals/chat-incident-report/test-cases.md` |
| 결과 저장 | `proving-grounds/evals/chat-incident-report/results/` |
| 리포트 | `proving-grounds/evals/chat-incident-report/report.md` |

## 실행 설정

| 설정 | 값 |
|------|-----|
| 모델 | sonnet |
| 병렬 실행 | TC별 baseline + with-skill 동시 |
| 기본 반복 횟수 | 1 |

---

## AUTO FAIL 규칙

| # | 규칙 | 감지 키워드/패턴 |
|---|------|-----------------|
| 1 | 개발 내부 용어 노출 | OAuth, access_token, refresh_token, JPA, repository, controller, removeAuthorizedClient 류 메서드명 |
| 2 | PR 우선순위 표기 | P0 / P1 / P2 / 에픽 / 스프린트 |
| 3 | 내부 문서 경로 노출 | `docs/works/...`, `src/main/java/...` 등 레포 경로 |
| 4 | 출처 없는 정책·수치 단정 | "정책상 N일", "통상 ~분 내" 등 근거 없는 수치 |
| 5 | 유저 식별자 누락 | 닉네임만 있고 userId 없음 (또는 반대) |
| 6 | 두괄식 위반 | 첫 섹션이 "상황"이 아닌 배경·경위·조사 방법 |
| 7 | 사용자 확인 누락 | 작성 완료 후 "이 느낌 맞아?" 류 확인 요청 없음 |
| 8 | 섹션 빈 채 유지 | 불필요 섹션을 "해당 없음" 등으로 비움 (삭제 원칙 위반) |

---

## 6축 평가 기준

### 축 1. 가드레일 준수 (GATE)

위 8개 AUTO FAIL 규칙 중 **하나라도 해당 시 FAIL**.

### 축 2. 기능 정확도 (100점 만점)

루브릭(`evaluation-rubric.md`) 기반:

| 항목 | 배점 |
|------|------|
| Phase 0 체크리스트 점검 | 15 |
| 메시지 구조 준수 (6섹션 순서) | 20 |
| 유저 표기 형식 (닉네임#ID(userId)) | 10 |
| 비개발자 친화 언어 | 20 |
| 사용자 안내 섹션 품질 | 20 |
| 불확실성 표현 | 10 |
| 톤·확인 요청 | 5 |

### 축 3. 행동 패턴

| 항목 | 확인 내용 |
|------|-----------|
| Phase 0 체크 | 입력 정보 부족 시 먼저 질문했는가? |
| 6섹션 순서 | 상황→원인→대응→사용자별 안내→후속→cc 엄수? |
| tech-term-replacement 활용 | 개발 용어를 비개발자 표현으로 치환? |
| 유보 표현 | 불확실성을 괄호·유보 문구로 명시? |
| sq-tone-writer 참조 | 30자 초과 문장 지양, 존댓말 구어체? |
| 확인 요청 | 작성 후 "이 느낌 맞아?" 포함? |

### 축 4. Baseline 대비

Baseline(스킬 미사용)은 일반적으로:
- 개발 용어 그대로 노출 (OAuth, 토큰 등)
- 섹션 순서·구조 제각각
- 유저 식별자 형식 들쭉날쭉
- 출처 없는 단정 (특히 복구 시간·정책)
- CS 복붙 불가 수준 (내부 지시형 "~해달라고 안내 부탁")

**with-skill**이 아래를 충족해야 PASS:
- 개발 용어 0건
- 6섹션 순서 엄수
- 유저 표기 닉네임#ID(userId) 일관
- 안내 섹션 CS 복붙 가능
- 불확실성 유보 표현
- 작성 후 확인 요청

### 축 5. 일관성 (`--repeat 3` 시)

- 동일 TC 3회 실행 편차 ≤ 15점
- AUTO FAIL 0회

### 축 6. 효율성 (기록용)

- 토큰, tool 호출, 시간

---

## 최종 판정 기준

| 조건 | 통과 시 |
|------|--------|
| 축 1 가드레일 | PASS (AUTO FAIL 0건) |
| 축 2 기능 정확도 | Happy Path 75+ PASS |
| 축 3 행동 패턴 | 6항목 중 5항목 이상 |
| 축 4 Baseline 비교 | PASS (with-skill > baseline 유의미 차) |

→ **실전 배치 가능**
