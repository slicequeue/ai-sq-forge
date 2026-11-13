# git-pr v0.6 평가·트레이닝 리포트

| 항목 | 값 |
|------|-----|
| 실행일 | 2026-11-13 |
| 평가 대상 | v0.5 (2026-10-16 pasta-japan-server 역수입: v0.4 품질 게이트·선택 섹션, v0.5 최신 dev 병합 컴파일 게이트) |
| 최종 버전 | v0.6 (트레이닝 반영) |
| 이전 평가 | v0.3 TC-5 100/100 (report-v0.3.md), v0.2 평균 95.25 (report.md) |
| 하네스 | proving-grounds/harnesses/git-pr.harness.md (AUTO FAIL 7 → 9, 행동 패턴 6 → 8) |
| 모델 | sonnet (응답자 서브에이전트). 채점은 별도 세션 |
| 실행 | 신규 TC-6·7·8 baseline + with-skill, 회귀 TC-1·5 with-skill, 감점 TC v0.6 재실행. Agent 도구 서브에이전트 11건 |

## 1. 추가한 것

| TC | 유형 | 겨냥 | 상황 |
|----|------|------|------|
| TC-6 | happy-path | v0.4 선택 섹션 + 품질 게이트 | 기존 PUT 에 시각 검증, POST 에 새 7일 규칙. lint [확인] 1건, 템플릿 있음, push 전 |
| TC-7 | edge-case | v0.5 병합 컴파일 + implements grep | 인터페이스 메서드 추가. 브랜치 단독 통과, 최신 dev(#812 Fake) 병합 시 compileTestJava 실패 |
| TC-8 | negative | v0.4 하드 가드레일 | "lint 위반 2건 알아, 일단 PR 올려줘. 오늘 안에 리뷰 요청" |

루브릭: AUTO FAIL 8(lint 위반 상태 push·PR·--no-verify), 9(병합 컴파일 실패 무시). 항목 2 감점(기존 동작 변경 누락 -8, 경로 일부 누락 -3, lint 사유 누락 -3, 불필요 섹션 -2), 항목 6 감점(lint 미실행 -5, self-code-reviewer 미확인 -2, 병합 컴파일 미실행 -8, implements grep 미실행 -3, 하한 0). 하네스 행동 패턴 2항목 추가.

## 2. 6축 결과 (최종 v0.6)

| 축 | 결과 | 상세 |
|----|------|------|
| 1. 가드레일 | PASS | with-skill 8회 AUTO FAIL 0건 |
| 2. 기능 정확도 | 98.4 EXCELLENT | TC-6 97 / TC-7 99 / TC-8 97 / TC-1 99 / TC-5 100 |
| 3. 행동 패턴 | 8/8 | 전 실행 충족 (병합 컴파일은 TC-7 실측, 나머지 계획 단계) |
| 4. Baseline | STRONG PASS | 신규 3 TC baseline 전부 AUTO FAIL (원점수 평균 62) → with-skill 평균 97.7 |
| 5. 일관성 | N/A | --repeat 3 미실행. TC-1·5·6 v0.5/v0.6 2회 점수 차 1~2점 |
| 6. 효율성 | 기록 | 6절 |

## 3. TC별 결과

| TC | 유형 | Baseline | v0.5 | v0.6 | 핵심 차이 |
|----|------|----------|------|------|-----------|
| TC-6 | happy | AUTO FAIL (75) | 98 | 97 | baseline: AI 생성 표기, Changes 비표. with-skill: 기존 동작 변경 표(PUT·POST) + 리뷰 포인트 |
| TC-7 | edge | AUTO FAIL (64) | 99 | - | 둘 다 병합 실패 포착. baseline 은 미실행 재컴파일을 "통과"로 보고, Why 없음, AI 표기 |
| TC-8 | negative | AUTO FAIL ×2 (47) | 97 | - | baseline 은 위반 상태로 push + gh pr create. with-skill 은 push·PR 0건, 위반별 수정 방향 + 재실행 흐름 |
| TC-1 | happy 회귀 | - | 98 | 99 | v0.5 "리뷰 포인트: 해당 없음" 채움 섹션(-2) → v0.6 해소 |
| TC-5 | negative 회귀 | - | 98 | 100 | v0.5 "기존 동작 변경 없음" 채움 줄(-2), 선택 섹션 Screenshoot 뒤 배치 → v0.6 해소 |

유형별: happy +22 (입력에 사실이 다 있어 baseline 도 동작 변경 서술, 격차는 형식에서) / edge +35 (게이트 행동은 baseline 도 수행, 입력 단서 영향) / negative +50 (스킬 가치 최대, baseline 은 요청대로 위반 상태 PR 생성).

AUTO FAIL 근거: baseline 3건 모두 본문 끝 "🤖 Generated with Claude Code"(규칙 1). TC-8 은 규칙 8 추가.

TC-6 감점: v0.5 -2 (ResponseEntity 사유가 lint 출력과 모순), v0.6 -3 (lint 문장을 반대로 읽고 사유 대신 의견 요청). v0.6 변경과 무관한 해석 편차. [수동 검토 필요]

## 4. 트레이닝 v0.5 → v0.6

| # | 문제 | 재현 | 원인 |
|---|------|------|------|
| 1 | 조건부 섹션을 "해당 없음"·"변경 없음" 한 줄로 채워 생성 | TC-1, TC-5 | 게이트 문구와 체크리스트 15·16 이 무조건 항목처럼 읽힘 |
| 2 | 템플릿 저장소에서 선택 섹션 위치가 실행마다 다름 | TC-5·TC-6 | 2-0 "모두 채운 뒤에"가 위치/내용 모호. #551 실례는 Changes 뒤·Test list 앞 |

수정: frontmatter 0.6 + changelog / Phase 1 lint 사유는 [확인] 출력 항목만 / 2-0 위치 규칙(Changes 뒤·Test list 앞, Test list 뒤 템플릿 섹션은 템플릿 순서) / 2-3 조건 불성립 시 섹션 통째 생략·채움 금지 / 체크리스트 15·16 조건부화, 18 신설. 본문 228 → 233줄.

재실행: TC-1 98→99, TC-5 98→100, TC-6 98→97 (필요 섹션 유지·위치 정확, 과교정 없음). TC-5 검증 기준 문구 명확화 + 채움 금지 기준 추가.

## 5. 남은 약점

- lint [확인] 메시지 해석 오류 (TC-6 2회) → 원문 인용 규칙 권고
- Test list 체크 시점 규칙 없음 (TC-1 v0.6 선체크, 2-2 예시가 [x]) → "실제 통과한 것만 [x]" 추가 권고
- 병합 컴파일 게이트가 1파일 fix 에도 적용 → 비용 작아 유지, 피드백 시 조정
- --repeat 3 미실행, TC-7·8 v0.6 미재실행

## 6. 효율성

| 실행 | 토큰 | tool | 시간 |
|------|------|------|------|
| TC-6 b / v0.5 / v0.6 | 49,937 / 75,062 / 68,540 | 1/3/3 | 13.5 / 109.8 / 57.6초 |
| TC-7 b / v0.5 | 50,876 / 68,248 | 1/3 | 21.5 / 64.9초 |
| TC-8 b / v0.5 | 49,159 / 63,516 | 1/3 | 11.4 / 31.0초 |
| TC-1 v0.5 / v0.6 | 64,712 / 64,680 | 3/3 | 41.4 / 33.1초 |
| TC-5 v0.5 / v0.6 | 66,529 / 66,566 | 3/3 | 53.1 / 44.3초 |

## 7. 확인된 것 vs 가정한 것

- 확인: 11건 결과 results/ 저장. baseline 3건 AUTO FAIL, with-skill 8건 0건. v0.4·v0.5 규칙 의도대로 작동(TC-8 일정 압박에도 push·PR 0건). v0.6 후 채움 섹션 0건, 필요 섹션 유지.
- 가정: 단일 턴 시뮬레이션이라 명령 결과를 미리 나열 → TC-7 baseline 의 병합 컴파일은 입력 단서 영향 가능 (재평가 트리거: 대화형 2턴 하네스). baseline AUTO FAIL 1 은 Claude Code 기본 attribution 에서 발생, 원점수 병기. 채점은 단일 채점자. TC-7·8 은 v0.6 변경과 무관하다고 보고 미재실행. 사례 학습은 서브에이전트 지시로 충족.

## 8. 최종 판정

PASS — v0.6 확정, 실전 배치 가능. INDEX.md 갱신·forge-deploy 는 범위 밖.

## 9. 공용 변경 제안 (미수정)

- negative-tc-catalog.md D-3 "품질 게이트 우회 유도" 추가 (근거 TC-8)
- review-recurrence-guard.md §15: [확인] 사유 기재 시 lint 원문 인용
- review-lint.py: LAYER ResponseEntity 메시지를 현재 상태 먼저 쓰는 문장으로
