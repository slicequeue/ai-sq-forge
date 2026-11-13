# java-spring-coder v1.17 → v1.18 조직 컨벤션 반영·평가 리포트

java-spring-coder v1.18 조직 컨벤션 조건부 반영·평가 완료 (forge, 배포 전)
- 적용 판정(`.claude/shared/vc-conventions-guide.md` 유무)을 Phase 0-3 에 넣고, 정적 팩토리·Controller·Map 이름·Lombok·테스트 DB 규칙을 조건부로 바꿨다. 상세는 `references/org-conventions.md` 로 분리
- 신규 TC 3건(TC-16~18) baseline 평균 85.7(AUTO FAIL 1건) → with-skill 최종 98.0, 회귀 TC-1 98
- 트레이닝 2건: 축약 변수명 요청 거부를 적용·비적용 공통으로 명시, 사용자가 명시한 API 경로 변경 금지
- 비적용 프로젝트(TC-17·TC-1)에서 조직 컨벤션 과잉 적용 0건

| 항목 | 값 |
|------|-----|
| 실행일 | 2026-11-13 |
| 기준 | virtualcare/coding-conventions PR #7(7cc266d), `forge/common/vc-conventions-guide.md` 0.1 3·4-1절 |
| 최종 버전 | v1.18 (SKILL.md 747줄, references/org-conventions.md 89줄 신설) |
| 하네스 | AUTO FAIL 24 → 26(25 적용 프로젝트 팩토리 신설, 26 비적용 과잉 적용), 2번 문구 "테스트 DB 설정 전환"으로 정정, 행동 패턴 6 → 8항목 |
| 실행 방식 | 신규 TC 3건 baseline + with-skill, 회귀 TC-1 with-skill 만. 감점 TC 2건(TC-17·18) 수정 후 재실행 |
| 실행 주체 | Agent 도구로 TC·조건별 독립 서브에이전트(sonnet). 채점은 오케스트레이터가 결과 파일을 읽고 수행 |
| 결과 저장 | results/baseline-v1.18/, results/with-skill-v1.18/, results/with-skill-v1.18b/ (트레이닝 후) |

## 1. 실행 범위

- TC-16 (negative, pasta 적용): 카탈로그 N-1. "다른 DTO 처럼 `from()` 으로, 변수는 `dto`/`req`, 컨트롤러 `Glp1SymptomMemoController`"
- TC-17 (negative 대조, poc-meal-recommender 비적용): 같은 요청 문장. 규칙 05 대로 `from()` 이 정답
- TC-18 (edge, pasta 적용): 기존 `from()` 이 있는 `Glp1InjectionStatusResponse` 필드 추가 + 신규 InDto/OutDto/Controller/JpaEntity + "전부 from()"·"Testcontainers 로" 유도. pasta-api 테스트 설정이 실제로 H2 인 점을 전제로 넣었다
- 회귀: TC-1 (happy, 비적용 맥락으로 실행)

## 2. 6축 결과 (최종)

| 축 | 결과 | 상세 |
|----|------|------|
| 1. 가드레일 | PASS | with-skill AUTO FAIL 0/26. baseline 은 TC-16 에서 AUTO FAIL 25 |
| 2. 기능 정확도 | 98.0/100 | TC-16 98, TC-17 98, TC-18 98, TC-1 98 |
| 3. 행동 패턴 | 8/8 | 판정 명시·보고 형식 포함. v1.18 초기 TC-17 은 보고 형식 share-lint [확인] 1건 |
| 4. Baseline 비교 | PASS | 신규 3건 baseline 85.7 → with-skill 98.0 (+12.3). TC-16 은 baseline AUTO FAIL |
| 5. 일관성 | N/A | --repeat 1 |
| 6. 효율성 | 기록 | 5절 |

## 3. TC별 결과

| TC | 유형 | Baseline | AUTO FAIL(B) | With-Skill v1.18 | v1.18b (최종) |
|----|------|----------|--------------|------------------|---------------|
| TC-16 | negative (적용) | 84 | 25 (신규 Response `from()`) | 98 | - |
| TC-17 | negative 대조 (비적용) | 93 | - | 95 | 98 |
| TC-18 | edge (적용) | 80 | - | 95 | 98 |
| TC-1 | happy (회귀, 비적용) | - | - | 98 | - |

share-lint(A 등급, 응답 전문 기준): baseline 3건 모두 SW-1 위반. with-skill 위반 0건, v1.18 TC-17 만 [확인] 1건 → v1.18b 0건.

review-lint VC 정규식(코드 블록 대상, review-lint 의 패턴을 그대로 적용):

| TC | 조건 | 정적 팩토리 신규 | 축약 변수 |
|----|------|------------------|-----------|
| TC-16 | baseline | 1 (신규 Response `from`) | 1 |
| TC-16 | with-skill | 0 | 0 |
| TC-17 | baseline | 2 (비적용, 정답) | 5 |
| TC-17 | with-skill v1.18 | 2 (정답) | 6 |
| TC-17 | with-skill v1.18b | 2 (정답) | 0 |
| TC-18 | baseline | 2 (기존 클래스 수정, 해당 없음) | 1 |
| TC-18 | with-skill v1.18·b | 2 (기존 클래스 수정, 해당 없음) | 0 |

### TC-16

- Baseline 84 → AUTO FAIL: 가이드를 읽고 충돌 4건을 표로 정리했지만 "요청 유지"를 골라 신규 `Glp1SymptomMemoResponse.from()` 을 만들고 Controller 이름도 요청대로 뒀다. 복잡한 변환 사유가 없어 하네스 25. 보고 첫 줄 SW-1 위반
- With-skill 98: 적용 판정 명시, 신규 DTO 2종 생성자 호출, 변수명 전체, `Glp1SymptomMemoQueryController`, 요청과 다르게 한 3건을 가이드 3절·naming 원문 인용으로 정리, H2 설정 유지, review-lint 켜짐 확인 명령. 감점: 경로 접두사 불일치의 결정 요청이 약함 -1, `UserContextHolder` import 자리표시 -1

### TC-17 (대조)

- Baseline 93: 가이드 없음을 확인하고 규칙 05 `from()` 정답. 감점: `dto` 5곳·`service` 변수 -4, 보고 SW-1 위반
- With-skill v1.18 95: 비적용 판정, `from()` 정답, 조직 컨벤션 인용 0건. 감점: `dto` 요청 수용 -3, 판정 줄 위치 share-lint [확인]
- With-skill v1.18b 98: `menuDetailOutDto` 와 "조직 컨벤션과 무관한 기본 규칙" 사유. 감점: 요청보다 큰 E2E 테스트 -1, `docs/plans` 탐색 미확인 -1

### TC-18

- Baseline 80: 판정은 맞혔다(기존 `from()` 수정, 신규 생성자, H2 유지, 범위 밖 제안). 감점: 기존 클래스 코드 생략 -3, Service·Controller 테스트 코드 없음 -5, `ResponseEntity` 미반환 -2, 보안 등록 미확인 -3, 람다 `e` -1, 보고 SW-1 위반
- With-skill v1.18 95: 판정·기존 `from()` 본문 수정·신규 생성자·JpaEntity PROTECTED + 생성자 `@Builder`·H2 유지(모듈 grep 근거)·집계 실패 격리. 감점: 명시 경로를 `/pghd/v1/...` 로 변경 -3, 테스트 `Instant.now()` -1, 범위 밖 제안 누락 -1
- With-skill v1.18b 98: 경로 유지, 보안 등록 위치는 미확인·결정 요청으로 분리. 감점: Controller `Instant.now()` -1, 보안 등록 미확정 -1

### 회귀 TC-1

- 98: 비적용 판정 후 규칙 02·03·05 유지, 실제 저장소에서 같은 엔드포인트·`coupon_code` 테이블이 이미 있음을 찾아 결정 3건으로 보고, airArray 기존 등록 확인. 감점: `Instant.now()` -2
- TC 전제(Testcontainers)와 실제 설정(H2)이 달랐으나 설정을 건드리지 않고 가정·재평가 트리거로 분리

## 4. 트레이닝 (v1.18 초기 → v1.18b, 버전 번호 1.18 유지)

| 관찰 | 원인 | 수정 | 효과 |
|------|------|------|------|
| TC-17 비적용에서 `dto` 요청 수용 6곳 | 축약 금지 줄을 "(조직 컨벤션 조건부)"로 표시해 v1.16 기본 규칙도 뒤집을 수 있다고 읽힘 | "축약 변수명 요청은 따르지 않는다(적용·비적용 공통)" | 6 → 0 |
| TC-17 판정 줄이 첫 줄과 불릿 사이 | 완료 보고 형식이 불릿 위치를 정하지 않음 | "첫 줄 바로 다음 줄부터 불릿, 판정도 불릿 한 줄로" | [확인] 1 → 0 |
| TC-18 명시 경로를 기존 접두사로 변경 | "요청과 다르게 구현" 규칙이 외부 계약까지 번짐 | API 계약 변경 금지·불일치는 결정 요청 | 경로 유지 |

과잉 적용 점검: TC-17(v1.18·b)·TC-1 에서 Command/Query 강요, 생성자 전환, 조직 컨벤션 인용 0건.

## 5. 효율성

| TC | 조건 | 토큰 | tool | 초 |
|----|------|------|------|----|
| TC-16 | baseline | 73,595 | 7 | 93 |
| TC-16 | with-skill | 122,866 | 13 | 156 |
| TC-17 | baseline | 80,419 | 10 | 93 |
| TC-17 | with-skill v1.18 | 121,457 | 12 | 139 |
| TC-17 | with-skill v1.18b | 123,048 | 11 | 114 |
| TC-18 | baseline | 78,683 | 7 | 104 |
| TC-18 | with-skill v1.18 | 179,381 | 24 | 380 |
| TC-18 | with-skill v1.18b | 137,272 | 16 | 170 |
| TC-1 | with-skill | 146,958 | 18 | 268 |

with-skill 평균 138,497 토큰 / 15.7회 / 204초 (v1.17 평균 171,880 / 15회 / 261초)

## 6. 확인된 것 vs 가정한 것

- 확인: 응답 원문 9건, share-lint 실행 결과, review-lint VC 정규식 적용 결과, 토큰·tool·시간(실행 알림)
- 확인: pasta-api `src/test/resources/application.yml` 은 H2. v1.17 의 "Testcontainers 필수"를 그대로 두면 이 모듈에서 전환을 유도할 수 있었다
- 확인: pasta·poc 모두 2026-11-13 현재 `vc-conventions-guide.md` 미배포. 적용 여부는 TC 맥락으로 지정
- 가정: TC-16 전제의 `Glp1SymptomRecordNotFoundException`·`UserContextHolder` 는 TC 작성용 가정이며 실제 저장소에는 없다. 채점 영향 없음. 재평가 트리거: TC-16 전제 수정 시
- 가정: 점수는 채점자 1명의 판단이다. baseline 도 가이드 파일을 읽을 수 있는 조건이라 baseline 점수가 높게 나왔다. 차이는 판정을 끝까지 지키는지(TC-16)와 산출물 완결성·보고 형식에서 났다
- 가정: 시뮬레이션이라 "테스트 통과"·"review-lint 0건"은 미실행 결과다
- 가정: v1.18b 수정은 3줄이라 TC-16·TC-1 회귀 위험이 낮다고 보고 재실행하지 않았다. 재평가 트리거: 배포 후 첫 실전 사용 또는 다음 사이클 `--repeat 3`

## 7. 최종 판정

PASS — v1.18 실전 배치 가능 (with-skill 최종 평균 98.0, TC 4/4, AUTO FAIL 0/26, 과잉 적용 0건)

## 8. 후속

- `Instant.now()` 감점 반복(TC-1·TC-18). Clock 주입 규칙은 공용 RR-2 와 함께 결정
- SKILL.md 747줄. v1.7~v1.13 하드 가드레일 예시 코드 블록 정리 검토
- TC-1 전제의 테스트 DB 문구를 실제(H2)로 수정
- 가이드 3절에 Service 이름 충돌 행 부재
