# java-spring-coder v1.16 → v1.17 검증·트레이닝 리포트

| 항목 | 값 |
|------|-----|
| 실행일 | 2026-11-13 |
| 검증 대상 | v1.16 (pasta-japan-server 역수입, 2026-10-16 GLP-1 PR 19건 리뷰 45건 반영분) |
| 최종 버전 | v1.17 (723줄) |
| 이전 회귀 | v1.15 (2026-09-16) 100/100, TC 5/5 |
| 하네스 | proving-grounds/harnesses/java-spring-coder.harness.md (AUTO FAIL 19 → 24) |
| 실행 방식 | 신규 TC 3건 baseline + with-skill, 회귀 TC 2건 with-skill 만(--skip-baseline), 실패 TC 1건 v1.17 재실행 |
| 실행 주체 | Agent 도구로 TC·조건별 독립 서브에이전트(sonnet). 채점은 오케스트레이터가 결과 파일을 읽고 수행(응답자·채점자 분리) |
| 결과 저장 | results/baseline-v1.16/, results/with-skill-v1.16/, results/with-skill-v1.17/ |

## 1. 실행 범위

- 신규 TC-13(edge): 여러 소스 조립 응답 + "서비스 전체 try → 빈 카드"·"Repository @Mock" 유도. RR-13·RR-14(최신=현재 이하)·RR-12·이름·ResponseEntity
- 신규 TC-14(negative): 기존 PUT 에 공용 검증 + "validate 먼저"·"동작 변경 없음이라고만"·"PUT 테스트만" 유도. RR-14
- 신규 TC-15(negative): 외부 호출 루프 "rollbackFor 로 전부 롤백" + shared 이벤트 `isOn` YAGNI 유도. RR-13·YAGNI·RR-9
- 회귀: TC-1(happy), TC-7(negative)
- 하네스 AUTO FAIL 20~24(RR-F11~F15), 루브릭 v1.16 감점 위치 표 추가

## 2. 6축 결과 (최종 v1.17)

| 축 | 결과 | 상세 |
|----|------|------|
| 1. 가드레일 | PASS | with-skill AUTO FAIL 0건(24개). baseline 은 신규 3건 모두 AUTO FAIL |
| 2. 기능 정확도 | 97.6/100 | 5건 전원 EXCELLENT (TC-15 는 v1.17 점수) |
| 3. 행동 패턴 | 6/6 | v1.16 TC-15 만 자기 검증 미충족(5/6) → v1.17 6/6 |
| 4. Baseline 비교 | STRONG PASS | 신규 3건 baseline 평균 66.7 → with-skill 97.7 |
| 5. 일관성 | N/A | --repeat 1 |
| 6. 효율성 | 기록 | 5절 |

## 3. TC별 결과

| TC | 유형 | Baseline | AUTO FAIL(B) | With-Skill v1.16 | v1.17 |
|----|------|----------|--------------|------------------|-------|
| TC-13 | edge | 70 | RR-F14, RR-F15 | 97 | - |
| TC-14 | negative | 66 | RR-F13, RR-F14 | 98 | - |
| TC-15 | negative | 64 | 규칙1 Domain @Entity, RR-F15 | 95 | 99 |
| TC-1 | happy(회귀) | 재사용 | - | 98 | - |
| TC-7 | negative(회귀) | 재사용 | - | 97 | - |

### 유형별 Baseline 비교

| 유형 | Baseline | With-Skill | 차이 |
|------|----------|------------|------|
| Happy | 신규 없음 | TC-1 98 | - |
| Edge (TC-13) | 70 | 97 | +27 |
| Negative (TC-14·15) | 65 | 98.5 | +33.5 |

### TC-13

- Baseline: 넓은 try 거부·일정 조회만 좁게 catch·rollback-only 지적·planStatus 구분까지 스킬 없이 해냈다. 실패: 서비스 테스트 Repository @Mock(RR-F14), WARN 로그 본문 userId(RR-F15), 최신 조회에 현재 이하 조건 없음, interval_days 0·음수 미방어, ResponseEntity 미사용, 변수명 latest/recent/now/service/result, SecurityConstants 미언급
- With-skill 97: 일정 조회 별도 빈 REQUIRES_NEW+readOnly(기존 QueryService 에 직접 붙이지 않은 이유를 RR-14 로 설명), toMap 앞 null 필터 + lint 확인 사유, interval_days<=0 건만 null+WARN, LessThanEqual(currentAt)+IdDesc, Fake 3종 + 실제 프록시 테스트 + 변이 표. 감점: catch(RuntimeException) 범위 -2, 변수명 e -1

### TC-14

- Baseline: 동작 변경을 PR 본문에 기재, 자기 자신 제외 탐색은 맞혔다. 검증 순서는 지시대로 validate 먼저 구현하고 질문으로만 남김(RR-F13). validator 테스트 Repository @Mock(RR-F14), var 사용, POST 직전 기록이 미래 기록 포함
- With-skill 98: 사용자 지시 5개 중 4개를 사유와 함께 정정. 소유 확인→검증, IdNot 별도 메서드(id<>null 함정 설명), 상한 POST=현재·PUT=새 injectedAt, POST·PUT·Infra 테스트와 순서 역전 탐지 테스트, 시각 미변경 PUT 은 검증 생략. 감점: 테스트 Instant.now() -2

### TC-15

- Baseline: 전체 롤백 거부·건 단위·cancel 보상·isOn 거부 모두 해냈다(RR-F12 미해당). 실패: domain 클래스에 @Entity(규칙 1), 로그 본문 userId(RR-F15), 대상 전체 로드, 테스트 더블 미명시
- With-skill v1.16 95: keyset 500 페이징 + IN 선조회, 건별 REQUIRES_NEW 저장 빈, 4종 집계, 저장 타임아웃 시 보상의 한계까지 기록. 감점: 코드 주석 평서형 3건(v1.16 규칙) -3 + 자기 검증에서 준수로 오보고(행동 패턴 미충족), Clock 미주입 -1, 스케줄러 위치 -1
- With-skill v1.17 99: 주석 평서형 0건, 주석 줄 열거 확인 절 포함, 나머지 동작 유지. 감점: Clock -1

### 회귀

- TC-1 98: 4 Phase 전수, Fake/MockMvc/Testcontainers, SecurityConstants, review-lint 단계, 미확인 체크박스 보류, 커밋 안 함. v1.16 이름 규칙·ResponseEntity 자연 적용. 감점 Instant.now() -2
- TC-7 97: 1062 판별, REQUIRES_NEW 격리 + 새 트랜잭션 재조회, FK·NOT NULL 전파 테스트, 질문 4번으로 동작 변경을 스스로 찾아 PR 본문 기재. 감점: CodeRabbit 인용 누락 -2, Instant.now() -1
- 과잉 적용: 질문 5개가 happy 에서도 나왔으나 구현을 막지 않았고 승인 항목은 실제 위험에 한정

## 4. 트레이닝 (v1.16 → v1.17)

| 관찰 | 원인 |
|------|------|
| 본문 평서형 응답에서 주석 3건 평서형 | 주석 존댓말 규칙이 `### 변수 네이밍` 목록 한 줄에 묻혀 있었고, 본문 문체가 주석으로 번지는 경로를 언급하지 않았다 |
| 자기 검증 오보고 | 체크리스트 43번이 이름 규칙과 주석 문체를 한 항목으로 묶었고 확인 방법이 없었다 |
| (부수) 번호 41 중복 | v1.16 이 42~44 를 v1.11 의 41번 앞에 끼워 넣었다 |

나머지 4건은 본문을 존댓말로 써서 우연히 지켜졌다.

수정: `### 코드 주석 문체` 절 분리(본문 문체와 섞지 않기, 주석 줄만 훑는 확인 방법), 체크리스트 42(v1.11)·43·44(이름)·45(주석 문체 신설)·46(lint) 재정렬, version 1.17·changelog.

효과: TC-15 95(5/6) → 99(6/6), 주석 평서형 3 → 0.

## 5. 효율성

| TC | 조건 | 토큰 | tool | 초 |
|----|------|------|------|----|
| TC-13 | baseline | 59,649 | 1 | 80 |
| TC-13 | with-skill | 216,968 | 22 | 430 |
| TC-14 | baseline | 55,542 | 1 | 55 |
| TC-14 | with-skill | 185,518 | 17 | 321 |
| TC-15 | baseline | 53,146 | 1 | 39 |
| TC-15 | with-skill v1.16 | 166,064 | 14 | 241 |
| TC-15 | with-skill v1.17 | 152,418 | 14 | 180 |
| TC-1 | with-skill | 162,892 | 13 | 239 |
| TC-7 | with-skill | 147,417 | 10 | 153 |

with-skill 평균 171,880 토큰 / 15회 / 261초 (v1.15 91,360 / 6.8회 대비 약 1.9배)

## 6. 확인된 것 vs 가정한 것

- 확인: 서브에이전트 응답 원문 8+1건, 코드 블록 주석 문체(정규식), 토큰·tool·시간(실행 알림), v1.17 TC-15 주석 평서형 0건
- 확인: baseline 은 RR-13·YAGNI 의 핵심 판단을 맞혔고, 차이는 프로젝트 규칙(Fake·PII·계층·검증 순서·이름)에서 났다
- 가정: 점수는 채점자 1명의 판단. 감점 폭(-1~-3)에 판단이 들어감. [수동 검토 필요] TC-13 catch(RuntimeException) 감점 폭
- 가정: v1.17 변경은 주석 절·번호 정리뿐이라 다른 TC 회귀 위험이 낮다고 보고 TC-15 만 재실행. 재평가 트리거: 다음 사이클에 TC-13 또는 TC-1 을 v1.17 로 실행
- 가정: 시뮬레이션이라 "테스트 통과"·"review-lint 0건"은 응답자의 가정 결과

## 7. 최종 판정

PASS — v1.17 실전 배치 가능 (평균 97.6, TC 5/5, AUTO FAIL 0/24, 회귀 없음)

## 8. 후속

- Clock 주입 규칙 부재(5건 중 4건이 now() 직접 호출) — 공용 RR-2 와 함께 결정
- 본문 723줄(400줄 원칙 초과), 체크리스트 머리말 "12항목" 불일치, test-cases.md 제목 coding-implementer 복붙
- TC-15 v1.17 `--repeat 3` 일관성 테스트 권장
