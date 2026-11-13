# java-layered-unit-testing v1.9 → v1.10 평가·트레이닝 리포트

java-layered-unit-testing v1.10 평가·트레이닝 완료 (forge, 배포 전)
- 조직 테스트 컨벤션 반영: 적용 판정, Fake* 이름, Thread.sleep·E2E 외 @SpringBootTest 금지, 테스트 DB 모듈 기존 설정 유지
- 신규 TC-9·10·11 baseline 평균 74점(AUTO FAIL 2건) → with-skill 최종 95.3점, AUTO FAIL 0건
- 회귀 TC-8 92·92점, 트레이닝 후 94점 (v1.9 기준 94점)
- 완료 보고 형식 감점 3건 트레이닝 후 해소, share-lint 위반 0건

| 항목 | 값 |
|------|-----|
| 실행일 | 2026-11-13 |
| 평가 대상 | v1.10 초안(조직 컨벤션 반영) → v1.10 최종(완료 보고 형식 트레이닝) |
| 모델 | sonnet (응답자 서브에이전트). 채점은 메인 세션에서 따로 함 |
| 실행 | 신규 TC-9·10·11 baseline + with-skill, 회귀 TC-8 with-skill 2회, 트레이닝 후 TC-8·9·11 재실행 |
| 기계 검사 | 코드 블록에 review-lint VC 정규식(`Thread.sleep`, `@SpringBootTest`, `Stub*` 클래스, JUnit Assertions, 모호한 `@DisplayName`, `var`, 축약 변수명, FQCN) 적용. 완료 보고에 `share-lint.py`(A 등급) 적용 |

## 1. 반영 내용 (SKILL.md 339 → 365줄)

| 위치 | 변경 |
|------|------|
| Phase 0-5·0-6 | 조직 컨벤션 적용 판정(`.claude/shared/vc-conventions-guide.md` 유무), 테스트 DB 실제 설정 확인 순서 |
| `references/vc-testcode.md` 신설 | 적용 프로젝트 전용. 대상별 테스트 더블 표, `@SpringBootTest` 예외 기준, 테스트 DB 판정, 작성 규칙(Fake*·DisplayName·GWT·상태 공유·sleep·@Nested·AssertJ·논리 검증 하나) |
| Web | 적용 시 `@MockitoBean`, Spring Boot 3.4 미만이면 `@MockBean` 유지 |
| Infra·통합·절대 금지·체크 #3 | 비적용: Testcontainers 필수·H2 금지 유지. 적용: 모듈 기존 설정 유지·전환 금지(규칙 09) |
| 통합 테스트(5)·실패 격리 | 적용 시 `@SpringBootTest` 는 E2E 만, rollback-only 처럼 슬라이스로 재현 안 되는 검증만 예외(테스트 주석 + PR 본문) |
| 체크 #7 | 비적용: 메서드별 `@Nested`. 적용: 1개짜리 `@Nested` 금지 |
| 체크 #24·#25, 작업 종료 출력 | 판정 보고, 적용 프로젝트 테스트 컨벤션, share-writing-guard A 형식 |
| 루브릭·하네스 | AUTO FAIL 1 조건부, 루브릭 AUTO FAIL 7·8 / 하네스 12·13 신설, 행동 패턴 6 → 8 |

## 2. 신규 TC

| TC | 유형 | 대상 프로젝트 맥락 | 유혹 |
|----|------|--------------------|------|
| TC-9 | Negative (N-3) | moneyball, 적용 | Stub + `@SpringBootTest` + `Thread.sleep(500)` + DisplayName '성공' |
| TC-10 | Edge | moneyball `analysis`, 적용, H2 클래스(실측) | "이참에 `@ActiveProfiles(\"test\")` 로 Testcontainers 전환" |
| TC-11 | 대조 | poc-meal-recommender, 비적용 | Stub 이름, 테스트 DB 알아서, "조직 컨벤션 맞춰야 하나?" |

## 3. 6축 결과

| 축 | 결과 | 상세 |
|----|------|------|
| 1. 가드레일 | PASS | with-skill 9회 AUTO FAIL 0건. baseline 3건 중 2건 AUTO FAIL |
| 2. 기능 정확도 | 95.0점 | 최종 TC-8·9·10·11 (94·96·95·95) |
| 3. 행동 패턴 | 8/8 | |
| 4. Baseline 비교 | PASS | 신규 3건 74.0 → 초기 93.7 → 최종 95.3 |
| 5. 일관성 | 참고값 | TC-8 같은 버전 2회 92·92 |
| 6. 효율성 | 기록 | with-skill 78k~128k 토큰, baseline 62k~72k |

## 4. TC별 결과

| TC / 실행 | 방식 25 | 통과 25 | 커버리지 20 | 컨벤션 15 | 일관성 15 | 합계 |
|-----------|---------|---------|-------------|-----------|-----------|------|
| TC-9 baseline | 25 | 21 | 16 | 5 | 12 | 79 |
| TC-9 초안 | 25 | 21 | 20 | 13 | 14 | 93 |
| TC-9 트레이닝 후 | 25 | 21 | 20 | 15 | 15 | 96 |
| TC-10 baseline (AUTO FAIL 1) | 10 | 18 | 18 | 8 | 12 | 66 |
| TC-10 초안 | 25 | 21 | 20 | 15 | 14 | 95 |
| TC-11 baseline (AUTO FAIL 5) | 25 | 15 | 19 | 5 | 13 | 77 |
| TC-11 초안 | 25 | 21 | 20 | 13 | 14 | 93 |
| TC-11 트레이닝 후 | 25 | 21 | 20 | 15 | 14 | 95 |
| TC-8 r1 | 25 | 20 | 18 | 15 | 14 | 92 |
| TC-8 r2 | 25 | 20 | 20 | 13 | 14 | 92 |
| TC-8 트레이닝 후 | 25 | 20 | 20 | 15 | 14 | 94 |

감점 사유:
- TC-9 baseline: 가이드가 있다는 맥락을 받고도 적용 판정 없음 -3, GWT 주석 없음 -2, `sut`·`saved` 이름 -2, 한 테스트에 성격이 다른 검증 여럿 -2, review-lint 없음 -3, 첫 줄 결론 없음 -2, "성공 -" 접두 -1. `Thread.sleep`·`@SpringBootTest` 는 baseline 이 스스로 거부했다
- TC-10 baseline: 요청대로 `@ActiveProfiles("test")` 추가(전환)
- TC-11 baseline: 비적용 판정은 맞음. 본문 FQCN 2건, `service`·`result` 이름 -2
- TC-9 초안: 요약 하위 불릿 12줄 -2 / TC-11 초안: "없음" 줄 -2
- TC-8 r1: Fake 가 `currentAt` 조건을 재현하지 않음 -2 / TC-8 r2: 완료 보고가 응답 첫 줄이 아님 -2

해석: baseline 이 v1.9 평가 때(평균 60.7)보다 강했다. 격차는 사용자가 위반을 명시적으로 요청한 TC(TC-10 프로필 전환), 이름 규칙, 형식에서 났다.

## 5. 과잉 적용 점검 (TC-11, 두 번 실행)

비적용 판정과 근거, `Stub*` 유지(규칙 08 §2-1), Testcontainers(규칙 09), 비적용 기본값인 메서드별 `@Nested` 를 두 번 모두 지켰다. 조직 컨벤션을 근거로 바꾼 것은 0건이다.

## 6. 트레이닝

| # | 관찰 | 수정 | 효과 |
|---|------|------|------|
| 1 | 요약 하위 불릿 12줄 (TC-9) | 요청 변경은 한 줄에 `A→B(근거)` 로 묶음 | 93 → 96 |
| 2 | "요청과 다르게 한 것: 없음" (TC-11) | 요청을 그대로 따랐으면 줄을 쓰지 않음 | 93 → 95 |
| 3 | 완료 보고가 4절에 있음 (TC-8 r2) | 응답의 맨 첫 줄이 요약 | 92 → 94 |

## 7. 확인된 것 vs 가정한 것

| 구분 | 내용 |
|------|------|
| 확인 | moneyball `analysis`: `application.yml` H2(MODE=MySQL), `application-test.yml` Testcontainers. Repository 테스트 7개 중 4개 `@ActiveProfiles("test")`, 3개 프로필 없음 |
| 확인 | pasta·moneyball Spring Boot 3.2.2, `@MockitoBean` 사용 0건, `@MockBean` 사용 140·270개 파일 |
| 확인 | pasta 테스트 resources 대부분이 H2. 기존 "H2 절대 금지" 문구는 실제 상태와 맞지 않았다 |
| 확인 | with-skill 9회 코드 블록 스캔: `Thread.sleep`·JUnit Assertions·`var`·FQCN·`@BeforeAll` 0건, `@SpringBootTest` 는 TC-8 의 사유 주석 달린 통합 테스트에만 있었다 |
| 확인 | 트레이닝 후 3회 share-lint 위반 0건 |
| 가정 | "테스트 통과" 점수는 코드 검토로만 매겼다 |
| 가정 | poc 의 규칙 08·09 는 pasta 와 같다 |
| 가정 | 트레이닝이 TC-10 에 회귀를 만들지 않는다 |
| 가정 | baseline 응답자가 전역 CLAUDE.md 를 읽었을 수 있다 |

재평가 트리거: 3.4 미만 모듈에 `@MockitoBean` 을 넣는 사례가 나오거나, H2 모듈에서 MySQL 전용 쿼리 테스트 요청이 오면 vc-testcode.md 1·3절을 다시 본다.

## 8. 최종 판정

PASS. v1.10 을 확정하고 배포 가능으로 본다. 배포할 때 `references/vc-testcode.md` 도 함께 옮겨야 한다.

## 9. 남은 약점

- `--repeat 3` 미실행. TC-1~7 v1.10 미재실행. TC-3 에 "대상 프로젝트 맥락"을 추가해야 한다
- H2 모듈에서 MySQL 전용 쿼리를 테스트하는 경로를 다루는 TC 가 없다
- Awaitility 로 실제 스레드풀을 기다리는 코드는 아직 검증하지 못했다

## 10. 공용 변경 제안

share-lint `- 키: 없음` 변형 검출·로컬 단계 표기 인정, vc-conventions-guide 4-2 `@MockitoBean` 버전 단서, 카탈로그 N-3 동기 실행기 허용, 규칙 08 §3 H2 문구와 규칙 09 충돌(pasta 소유). 앞의 셋은 사이클 9 에 반영했다.
