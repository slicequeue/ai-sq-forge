---
name: java-architecture-reviewer
version: 0.1
harness-version: 0.1
last-modified: 2026-07-09
---

# java-architecture-reviewer 평가 루브릭

백엔드 Java Spring Boot 코드에 대한 아키텍처·컨벤션 관점 리뷰를 100점 만점으로 채점한다. 스킬이 산출하는 **리뷰 리포트(AUTO FAIL / 필수 수정 / 권장 개선 표 + 로드된 규칙 명시 + 검사 통과 항목)** 를 평가 대상으로 삼는다.

---

## 평가 항목

| # | 항목 | 배점 | 설명 |
|---|------|------|------|
| 1 | **AUTO FAIL 검출 정확도** | 20 | 4건 하드 가드레일(Bean Qualifier cross-module / 4-Tier 위반 / 공용 모듈 @Entity / FQCN 인라인) 위반이 코드에 있으면 반드시 AUTO FAIL로 보고 |
| 2 | **pasta-rules 참조 정확도** | 15 | 변경 파일 유형에 맞는 규칙 파일을 실제 Read하고 인용. 파일 경로만 나열 금지 |
| 3 | **Bean 관리 검사 품질** | 15 | @Bean 상수화 · Qualifier cross-module · @ConditionalOnBean vs @Profile · 인터페이스 구현체 모듈 등록 |
| 4 | **4-Tier + 모듈 관계 검사** | 15 | import 방향 · @Entity 스캔 경계 · admin/api/batch 격리 · 순환 의존 |
| 5 | **패턴 준수 검사** | 10 | DDD Entity/Repository 3단계/DTO record/명명 컨벤션 |
| 6 | **스코프 준수 (out-of-scope 안내)** | 10 | 보안·성능·문법·Session 오염·i18n은 담당 스킬로 안내만, 본인 리뷰 결과에 포함 금지 |
| 7 | **리포트 형식 준수** | 10 | 유형·등급 표기 · AUTO FAIL/Critical/High/Medium/Low/Info 분류 · 검사 통과 항목 명시 |
| 8 | **admin 모듈 예외 인지** | 5 | admin 변경 시 13/14 규칙 우선, 01/04 4-Tier 맹목 적용 금지 |
| | **합계** | **100** | |

---

## AUTO FAIL 조건

다음 중 하나라도 위반하면 즉시 0점 처리:

1. **HG-1 미검출** — 코드에 `@Qualifier(CONST)` 소비자가 있고 특정 모듈이 `@Bean(CONST)` 미명시인데 리뷰에서 AUTO FAIL로 보고 안 함
2. **HG-2 미검출** — Domain이 Infrastructure/Web을 import하는데 발견 못 함
3. **HG-3 미검출** — 공용 모듈에 `@Entity` 있는데 발견 못 함
4. **HG-4 미검출** — 코드 본문에 FQCN 인라인 있는데 발견 못 함
5. **범위 침범** — 보안·성능·문법 오류·Hibernate Session 오염·i18n을 이 스킬 리뷰 결과에 섞어 보고
6. **코드 수정 시도** — 리뷰 결과 보고 대신 파일 편집이나 커밋 시도

---

## 합격 기준

| 등급 | 점수 |
|------|------|
| EXCELLENT | 90~100 |
| PASS | 75~89 |
| FAIL | 0~74 (또는 AUTO FAIL) |

---

## 채점 가이드

### 항목 1. AUTO FAIL 검출 정확도 (20점)

| 상태 | 점수 |
|------|------|
| 4건 하드 가드레일 위반 100% 검출 + AUTO FAIL 정확 표기 | 20 |
| 3건 검출 (1건 놓침) | 12 |
| 2건 이하 검출 | AUTO FAIL |
| 위반 없는데 오탐 (false positive) 1건 이상 | 8 (감점) |

### 항목 2. pasta-rules 참조 정확도 (15점)

| 상태 | 점수 |
|------|------|
| 변경 유형별 필요 규칙 파일 실제 Read + 규칙 문구 인용 + 위반 근거 매핑 | 15 |
| 규칙 파일 경로만 나열, 실제 내용 인용 없음 | 8 |
| 규칙 참조 자체가 없거나 잘못된 규칙 인용 | 3 |

### 항목 3. Bean 관리 검사 품질 (15점)

| 상태 | 점수 |
|------|------|
| Qualifier cross-module grep + 상수화 권장 + 게이팅 방식 + 구현체 모듈 등록 모두 검사 | 15 |
| 4항목 중 3개 검사 | 10 |
| 4항목 중 2개 이하 검사 | 5 |
| HG-1 위반 놓침 | AUTO FAIL |

### 항목 4. 4-Tier + 모듈 관계 (15점)

| 상태 | 점수 |
|------|------|
| import 방향 · @Entity 스캔 · admin/api/batch 격리 · 순환 의존 4항목 모두 검사 | 15 |
| 3항목 검사 | 10 |
| 2항목 이하 | 5 |
| HG-2 또는 HG-3 위반 놓침 | AUTO FAIL |

### 항목 5. 패턴 준수 (10점)

| 상태 | 점수 |
|------|------|
| DDD Entity/Repository 3단계/DTO record/명명 4항목 모두 검사 | 10 |
| 3항목 검사 | 7 |
| 2항목 이하 | 4 |
| 애매한 판정 케이스에 대해 "판정 유보 + 사용자 확인" 명시 | 가점 (최대 +2) |

### 항목 6. 스코프 준수 (10점)

| 상태 | 점수 |
|------|------|
| out-of-scope 위반 발견 시 담당 스킬 참조만 명시하고 본인 리뷰에 안 넣음 | 10 |
| 담당 스킬 참조는 하되 본인 리뷰에도 넣음 (중복) | 5 |
| 다른 관점 위반을 본인 리뷰에 정식으로 넣음 (스코프 침범) | AUTO FAIL |

### 항목 7. 리포트 형식 준수 (10점)

| 상태 | 점수 |
|------|------|
| 유형 5종(ARCH-*) + 등급 6단계 + AUTO FAIL/필수 수정/권장 개선/검사 통과 4섹션 | 10 |
| 유형·등급 표기 일부 누락 | 6 |
| 검사 통과 항목 섹션 누락 | 4 |
| 표 형식이 아닌 자유 서술로 흘림 | 2 |

### 항목 8. admin 모듈 예외 인지 (5점)

| 상태 | 점수 |
|------|------|
| admin 변경 시 13/14 규칙 우선 로드 + 01/04 4-Tier 맹목 적용 안 함 | 5 |
| 13/14 규칙 로드는 하나 여전히 4-Tier 위반 지적 | 3 |
| admin에 4-Tier 맹목 적용 → false positive | 0 |

---

## 참고

- 하드 가드레일 정본: `anvil/skills/java-architecture-reviewer/SKILL.md` "하드 가드레일" 섹션
- 짝 스킬: `java-spring-coder` v1.11 (코드 생성 시점 동일 원칙), `self-code-reviewer` v2.0 (공통 룰)
- 실전 사례: 2026-05 batch·batch-app #593 / 2026-06 admin #588 Bean Qualifier 재발 사고 · 2026-07 access 4-Tier 사후 재편
