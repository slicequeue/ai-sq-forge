# java-architecture-reviewer v0.2 → v0.3 평가·트레이닝 리포트

java-architecture-reviewer v0.3 조직 컨벤션 검사(ARCH-VC) 반영 평가 완료 (forge, 배포 전)
- 신규 TC-11(적용 프로젝트 Negative) with-skill 100, baseline 83
- 신규 TC-12(비적용 대조) with-skill 92 → 트레이닝 후 100, baseline 92
- 회귀 TC-1 95, 과잉 지적(기존 줄·비적용 프로젝트) 0건, AUTO FAIL 0건

| 항목 | 값 |
|------|-----|
| 실행일 | 2026-11-13 |
| 대상 | v0.3 (virtualcare/coding-conventions PR #7 7cc266d 기준 조직 컨벤션 검사 추가) |
| 이전 평가 | v0.1 (2026-07-29) 95.4, --skip-baseline |
| 하네스 | harness-version 0.3 (AUTO FAIL 7 → 9, TC 10 → 12) |
| 모델 | sonnet (응답자 서브에이전트, TC·조건마다 독립) |
| 실행 방식 | TC-11·12 baseline + with-skill, 회귀 TC-1 with-skill, 트레이닝 후 TC-12 재실행 |
| lint 근거 | TC 의 review-lint 출력은 forge review-lint.py 의 lint() 에 TC diff 를 넣어 얻은 실제 결과 |

## 1. 변경 내용

| 위치 | 변경 |
|------|------|
| Phase 0 항목 6 | `.claude/shared/vc-conventions-guide.md` 존재로 적용 판정, 적용이면 가이드·원문(pkg-structure·entity·dto·lombok·naming) Read |
| 핵심 규칙 4 | DTO 정적 팩토리 문구 조건부 (비적용: 규칙 05 `of`/`from`/`to`, 적용: 핵심 규칙 8) |
| 핵심 규칙 8 신설 | ARCH-VC. 신규·변경 줄만, review-lint VC 원문 인용, 판정·등급 표(4-1 + 3절 예외), 비적용 프로젝트 ARCH-VC 0건 |
| 리포트 형식 | 머리 "조직 컨벤션: 적용/비적용", 유형 ARCH-VC, 범위 밖 제안 절(없으면 뺌), AUTO FAIL 절 제목을 HG-1~4 위반으로 |
| 가드레일·자기 검증 11~13 | 지적 범위, 3절 판정 우선, lint 인용 |

본문 284 → 319줄. 루브릭(AUTO FAIL 7·8, 부분 범위 채점), 하네스(AUTO FAIL 8·9), TC(11·12) 동반 수정.

## 2. TC별 결과

| TC | 유형 | 대상 프로젝트 | Baseline | With-skill 초기 | 최종 | AUTO FAIL |
|----|------|---------------|----------|-----------------|------|-----------|
| TC-11 | negative | pasta-japan-server (적용) | 83 | 100 | 100 | 0 |
| TC-12 | edge (대조) | poc-meal-recommender (비적용) | 92 | 92 | 100 (run2) | 0 |
| TC-1 (회귀) | happy | pasta-japan-server | — | 95 | 95 | 0 |

### TC-11 기준 상세

| 기준 | With-skill | Baseline |
|------|-----------|----------|
| 적용 판정 + 머리 표기 | 충족 | 충족 |
| @Setter High + lint [위반] 원문 인용 | 충족 | 부분 (원문 인용 없음) |
| 신규 DTO from() 기존 관례로 통과 안 함 | 충족 | 충족 |
| presentation → web (중복 1건) | 충족 | 충족 |
| req·dto 지적 | 충족 | 충족 |
| CouponSummaryOutDto 기존 from() 수정 통과 (3절 예외) | 충족 | 충족 |
| 기존 줄 ARCH-VC 0 (범위 밖 제안까지만) | 충족 | 충족 |
| 유형 코드 ARCH-VC | 충족 | 미충족 |
| AUTO FAIL 0 | 충족 | 충족 |
| (가점) 신규 Controller 이름 CouponCommandController | 충족 | 충족 |

### TC-12 기준 상세

| 기준 | run1 | run2 | Baseline |
|------|------|------|----------|
| 비적용 판정 + 머리 표기 | 충족 | 충족 | 충족 |
| ARCH-VC 0, 조직 컨벤션 근거 지적 0 | 충족 | 충족 | 충족 |
| from() 규칙 05 준수로 통과 | 충족 | 충족 | 충족 |
| HG-2 AUTO FAIL 검출 | 부분 (AUTO FAIL 절 비움, 필수 수정 절에 표기) | 충족 | 부분 (AUTO FAIL 개념 없음) |
| 줄임 변수명 조직 컨벤션 근거 지적 안 함 | 충족 | 충족 | 충족 |
| AUTO FAIL 0 | 충족 | 충족 | 충족 |

## 3. 트레이닝

| 관찰 | 원인 | 수정 | 효과 |
|------|------|------|------|
| TC-12 run1 이 HG-2 를 찾고도 AUTO FAIL 절을 비워 둠 | 절 제목 "AUTO FAIL (기동/컴파일 실패 확정)" | 제목을 "하드 가드레일 HG-1~4 위반, HG-2 계층 역행 포함"으로 | run2 92 → 100 |
| run1 범위 밖 제안 절을 빈 칸으로 채움 | 형식 예시가 절을 항상 보여 줌 | "없으면 이 절을 뺀다" | run2 빈 절 없음 |

v0.2 이전부터 있던 절 제목이라 TC-5(HG-2) 재확인 필요.

## 4. Baseline 비교 (유형별)

| 유형 | TC | Baseline | With-skill | 격차 |
|------|----|----------|------------|------|
| negative | TC-11 | 83 | 100 | +17 |
| edge (대조) | TC-12 | 92 | 100 | +8 |

하네스 기준(+20) 미달. TC 입력에 프로젝트 맥락과 lint 출력을 그대로 줬고 baseline 에도 가이드 위치를 알려 줬기 때문이다. 판정 지식은 가이드에 있고, 스킬 차이는 리포트 체계와 lint 인용에서 난다.

## 5. 확인된 것 vs 가정한 것

| 확인된 것 | 가정한 것 (재평가 트리거) |
|-----------|---------------------------|
| TC-11 lint 출력은 실제 lint() 결과 (위반 1, 확인 16, VC 켜짐). TC-12 는 VC 꺼짐 0건, 켜면 확인 4건 | 실제 PR diff 아님. 실전 VC 출력 양 미확인 → 첫 배포 사이클 리뷰 로그 |
| presentation 검사가 신규 파일 줄마다 1건씩 나와 13줄 중복 → 파일당 1건으로 수정함 | 응답자는 1건으로 묶었다 |
| pasta 실물 패키지는 web | TC-1 은 코드 본문이 없어 ARCH-VC 를 "미판정"으로 처리. 코드 있는 회귀 TC(4·5) 미실행 |
| 응답자·채점자 분리 | 채점자가 TC 설계자와 같다. 저확신: TC-1 규칙 문구 인용 정도 |

## 6. 효율성

| 실행 | 토큰 | tool | 시간 |
|------|------|------|------|
| TC-11 baseline | 61,986 | 4 | 64초 |
| TC-11 v0.3 | 87,242 | 7 | 81초 |
| TC-12 baseline | 61,826 | 4 | 44초 |
| TC-12 v0.3 run1 | 79,999 | 5 | 58초 |
| TC-12 v0.3 run2 | 80,071 | 6 | 55초 |
| TC-1 v0.3 | 77,458 | 6 | 65초 |

## 7. 판정

PASS. v0.3 확정, AUTO FAIL 0건. 축 4 격차 미달은 TC 설계 원인으로 기록.

## 8. 남은 약점

- TC-2~10 회귀 미실행. AUTO FAIL 절 제목 변경 영향은 TC-5 로 확인 필요
- 복잡한 변환일 때 from() 을 허용하는 경계 TC 없음
