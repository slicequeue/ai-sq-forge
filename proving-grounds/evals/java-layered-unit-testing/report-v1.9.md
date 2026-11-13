# java-layered-unit-testing v1.8 → v1.9 평가·트레이닝 리포트

| 항목 | 값 |
|------|-----|
| 실행일 | 2026-11-13 |
| 평가 대상 | v1.8 (2026-10-16 실전 역수입: Application 계층 Fake 우선 전환 등) → v1.9 (이번 트레이닝) |
| 모델 | sonnet (응답자 서브에이전트). 채점은 메인 세션으로 분리 |
| 실행 TC | 신규 TC-6·7·8 baseline + with-skill, 회귀 TC-1·4 with-skill, v1.9 재실행 TC-4·6 |
| 결과 | `results/baseline/`, `results/with-skill/` (11개 파일) |

## 1. 정합성 점검

평가 자원이 Mockito 를 정답으로 채점하고 있었다. 그대로 돌렸으면 Fake 우선(v1.8)을 지킨 응답이 감점됐다.

| 대상 | 수정 | 사유 |
|------|------|------|
| 루브릭 1번 항목(25점) | "App=Mockito" → Fake 우선(외부 통신 Spy, Web @WebMvcTest). AUTO FAIL 6(RR-F14 상태 저장소 Mock 정답 주입) 추가. v1.8 감점 기준 신설(기본값과 같은 값만 검증, 진입 경로 일부만, 느슨한 JSON 단언, 저장 미호출 확인 누락, 실패 격리 누락, 이름 규칙, lint 누락) | v1.8 본문과 충돌 |
| TC-1 | 검증 기준의 `@ExtendWith(MockitoExtension.class)`·`@Mock` Repository·`@InjectMocks` 를 Fake 기준으로 교체. 이전 점수(91·92)는 Mockito 기준이라 비교 대상에서 제외 | 동일 |
| TC-4 | `willThrow` 전제를 테스트 더블 중립 표현으로, Fake 항목 추가. FQCN 검증 의도 유지 | 동일 |
| 하네스 | AUTO FAIL 11(RR-F14) 추가 — 금지 설명 문장 오탐 방지 위해 코드 블록만 매칭(v1.7 후속 과제). 행동 패턴 4 → 6(Fake 탐색, review-lint 실행) | 동일 |

## 2. 신규 TC

| TC | 유형 | 겨냥한 규칙 | 유혹 |
|----|------|-------------|------|
| TC-6 | Negative | Fake 우선, RR-F14 | "기존 테스트처럼 `@Mock` Repository·UseCase로, Fake는 오버" |
| TC-7 | Edge | 기본값 true 필드, POST/PUT 공용 검증, null 계약 | "검증은 등록만, true로만 확인, `doesNotExist()`로" |
| TC-8 | Happy | 실패 격리(RR-13), rollback-only | 없음 (평범한 조립 서비스 테스트 요청) |

## 3. 6축 결과

| 축 | 결과 | 상세 |
|----|------|------|
| 1. 가드레일 | PASS | with-skill 7회 AUTO FAIL 0건, baseline 3건 모두 AUTO FAIL 11 |
| 2. 기능 정확도 | 93.4점 | EXCELLENT (최종 버전 기준 평균) |
| 3. 행동 패턴 | 6/6 | 전 TC |
| 4. Baseline 비교 | STRONG PASS | 신규 3건 평균 60.7점 → v1.8 91.7점 |
| 5. 일관성 | N/A | `--repeat 1` |
| 6. 효율성 | 기록 | with-skill 토큰이 baseline 의 약 1.9배 |

with-skill 7회는 코드 블록 자동 스캔에서 FQCN·상태 저장소 Mock·`var` 모두 0건.

## 4. TC별·유형별 결과

| TC | Baseline | With-skill v1.8 | v1.9 재실행 |
|----|----------|-----------------|-------------|
| TC-6 (Negative) | 54, AUTO FAIL | 90 | **95** |
| TC-7 (Edge) | 63, AUTO FAIL | **91** | 재실행 안 함 |
| TC-8 (Happy) | 65, AUTO FAIL | **94** | 재실행 안 함 |
| TC-1 (회귀) | 실행 안 함 | **92** | 재실행 안 함 |
| TC-4 (회귀) | 실행 안 함 | 85 | **95** |

| TC / 실행 | 방식 25 | 통과 25 | 커버리지 20 | 컨벤션 15 | 일관성 15 | 합계 |
|-----------|---------|---------|-------------|-----------|-----------|------|
| TC-6 baseline | 5 | 15 | 12 | 9 | 13 | 54 |
| TC-6 v1.8 | 25 | 21 | 17 | 14 | 13 | 90 |
| TC-6 v1.9 | 25 | 21 | 20 | 15 | 14 | 95 |
| TC-7 baseline | 13 | 18 | 11 | 9 | 12 | 63 |
| TC-7 v1.8 | 25 | 20 | 19 | 14 | 13 | 91 |
| TC-8 baseline | 8 | 20 | 17 | 9 | 11 | 65 |
| TC-8 v1.8 | 25 | 21 | 20 | 15 | 13 | 94 |
| TC-1 v1.8 | 25 | 21 | 18 | 15 | 13 | 92 |
| TC-4 v1.8 | 25 | 19 | 15 | 13 | 13 | 85 |
| TC-4 v1.9 | 25 | 21 | 20 | 15 | 14 | 95 |

감점 사유:
- TC-6 v1.8: NotFound 분기를 제안만 함 -3, 규칙 원본 미인용 -1
- TC-7 baseline: POST 만 검증 -5, `doesNotExist` 유지 -3
- TC-4 v1.8: 서비스 이중 호출로 fallback 이 아닌 선조회 경로를 검증하는 결함을 찾고도 설명만 붙여 제출 -5, 규칙 07 미인용 -2

유형별 해석: baseline 3건 모두 Application 테스트를 기본으로 Mockito(`@Mock` Repository·UseCase + 반환값 주입)로 작성해 AUTO FAIL 11. 그래서 Happy(TC-8)에서도 격차가 +29점이다. "happy-path 는 격차가 작다"는 기존 관찰과 다르며, 이 스킬에서는 테스트 더블 선택 자체가 기본값 격차를 만든다.

## 5. 트레이닝 (v1.8 → v1.9)

| # | 변경 | 근거 | 전 → 후 |
|---|------|------|---------|
| 1 | 자기 검증 #2 의 "App=Mockito" 잔재 정정 | TC-1 응답자가 본문과 충돌 지적 | — |
| 2 | v1.4 예시 정정: `var` 4곳 명시 타입, 동작하지 않는 Mockito `spy` + `getPublishCallCount()` 조합을 손으로 쓴 Spy 로 교체, verify·Spy 선택표를 규칙 08 §2-2 기준으로 재작성 | 예시 오류 | — |
| 3 | 요청 범위가 예외 분기보다 좁아도 빠진 분기를 작성하고 `// 요청 외 추가` 표시 (체크리스트 #22) | TC-6 | 90 → 95 |
| 4 | 스스로 찾은 결함은 제출 코드에서 고친 뒤 보고 (체크리스트 #23) | TC-4 | 85 → 95 |
| 5 | 규칙 때문에 사용자 요청을 바꿨다면 규칙 원본(07·08·RR-n) 인용 | TC-4·6 | — |
| 6 | 오탈자("위로 안 되는") 정정 | — | — |

SKILL.md 339줄, frontmatter 1.9 + changelog 기록.

## 6. 확인된 것 vs 가정한 것

| 구분 | 내용 |
|------|------|
| 확인 | 루브릭·하네스·TC-1·TC-4 가 Mockito 를 정답으로 채점하고 있었다 |
| 확인 | with-skill 7회 코드 블록 스캔 결과 FQCN·상태 저장소 Mock·`var` 0건 |
| 확인 | v1.9 재실행에서 TC-4·6 감점 원인 해소 |
| 가정 | "테스트 통과"(25점)는 시뮬레이션이라 컴파일 가능성·단언 논리로만 판단 |
| 가정 | v1.9 가 TC-1·7·8 에 회귀를 만들지 않는다 |
| 가정 | 일관성 미측정 |
| 가정 | baseline 응답자가 CLAUDE.md 를 자동 로드했을 가능성 (tool 사용 0회) |

재평가 트리거: TC-1·7·8 이 v1.8 대비 5점 넘게 떨어지면 수정 3(요청 외 분기 추가)의 과잉 적용을 의심한다.

## 7. 최종 판정

PASS — v1.9 확정, 실전 배치 가능.

## 8. 남은 약점

- `--repeat 3` 미실행 (TC-6 반복 권장)
- TC-1·7·8 v1.9 미재실행, TC-2·3·5 이번 미실행
- "테스트 통과" 항목 근거 없음 → 실전 `./gradlew test`·review-lint 결과로 확인 필요
- 외부 Client 인터페이스가 infrastructure 에 있을 때 Spy 를 둘 패키지 기준 없음

## 9. 공용 변경 제안

1. `forge/common/negative-tc-catalog.md`: M-7 "상태 저장소 Mock 유도", M-8 "부분 검증 유도"(진입 경로 하나만, 기본값과 같은 값만, `doesNotExist()` 지정)
2. 규칙 08 §3 "Integration/Acceptance Test … H2 DB 사용" 이 스킬의 H2 절대 금지와 충돌 → pasta 원본 쪽 정정 필요
3. `forge/common/review-recurrence-guard.md` RR-12 표가 중간 빈 줄 때문에 둘로 끊겨 렌더링됨
4. `anvil/INDEX.md` v1.9 / 93.4점 갱신
5. `forge/common/review-lint.py` 가 git 미추적 → 커밋에 포함해야 배포본에서 동작
