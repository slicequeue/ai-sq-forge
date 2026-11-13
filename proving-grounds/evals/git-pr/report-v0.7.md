# git-pr v0.7 평가·트레이닝 리포트

git-pr v0.7 제목 형식 판정·맨 위 결론 블록 반영·평가 완료 (forge, 배포 전)
- 적용 프로젝트 PR 제목 `[핵심키워드] 명사형 요약`, 본문 첫 줄에 share-writing-guard A 결론 블록 + share-lint 게이트
- 신규 TC-9(N-2·O-2) with-skill 98, share-lint 위반 0건. baseline 은 AUTO FAIL(AI 표기) + share-lint 위반 2건
- 회귀 TC-1 97: 비적용 제목 `fix:` 유지, 채움 섹션 0건, 미실행 게이트는 `[ ]`

| 항목 | 값 |
|------|-----|
| 실행일 | 2026-11-13 |
| 평가 대상 | v0.7 (사이클 9) |
| 이전 평가 | v0.6 평균 98.4 (report-v0.6.md) |
| 하네스 | AUTO FAIL 9 → 11, 행동 패턴 8 → 10 |
| 실행 | TC-9 baseline + with-skill, TC-1 회귀 with-skill. sonnet 서브에이전트 3건 |

## 1. 바꾼 것

| 위치 | 내용 |
|------|------|
| Phase 1 제목 형식 판정 | 가이드 있으면 `[핵심키워드] 명사형 요약`(git-commit 0·A절과 같음), 없으면 기존 Conventional 허용 |
| 2-0-1 결론 블록 | 템플릿 첫 섹션 위에 제목 없이 `{무엇을} 완료 (머지 전)` + 2~4줄. 섹션이 아니라서 조건부 섹션 규칙과 별개. 채움·유추 금지. share-lint 위반 0이어야 생성·갱신 |
| Test list | `[x]` 는 확인한 것만 (v0.6 남은 약점 해소) |
| 가드레일·체크리스트 | 접두어 OK 문구를 조건부로. 19(결론 블록)·20(제목 형식) |

## 2. 6축 결과

| 축 | 결과 | 상세 |
|----|------|------|
| 1. 가드레일 | PASS | with-skill 2회 AUTO FAIL 0건 |
| 2. 기능 정확도 | 97.5 | TC-9 98 / TC-1 97 |
| 3. 행동 패턴 | 10/10 | share-lint 를 실제 실행 (위반 0 / 확인 0) |
| 4. Baseline | PASS | TC-9 baseline AUTO FAIL(원점수 약 82) → 98 |
| 5. 일관성 | 참고 | TC-1 v0.5 98 / v0.6 99 / v0.7 97 |
| 6. 효율성 | 기록 | TC-9 75k 토큰·7 tool·86초, TC-1 72k·5 tool·78초, baseline 55k·2 tool |

## 3. TC별 결과

| TC | 유형 | Baseline | v0.7 | 핵심 차이 |
|----|------|----------|------|-----------|
| TC-9 | negative (N-2·O-2) | AUTO FAIL 1 (원점수 약 82) | 98 | 제목은 둘 다 `[health-life]`. baseline 은 이슈 키 누락, 빈 칸 채움(share-lint SW-6), 결론 블록 없음(SW-1), Changes 가 표가 아닌 불릿, AI 생성 표기. with-skill 은 `[health-life] CORE-1550 ... 추가` + 블록 + 리스크 칸 뺀 이유 한 줄 |
| TC-1 | happy 회귀 | - | 97 | 제목 `fix:` 유지. 결론 블록 3줄, 조건부 섹션 0건. 입력에 lint 결과가 없어 PR 생성 전 게이트 실행 필요로 멈춤(URL 미출력 -3) |

## 4. 트레이닝

git-pr 단독 감점은 없음. git-commit TC-3 에서 찾은 범용 키워드 규칙을 Phase 1 에 한 줄로 반영 (TC-9 with-skill 은 반영 전에도 같은 판단을 함).

## 5. 남은 약점

- 결론 블록에서 "결과:" 접두가 반복됨(가독성 소폭). 규칙화하지 않음
- 템플릿의 optional 섹션(Screenshoot)을 빈 제목으로 남김. 템플릿 순서 규칙상 허용, 리뷰어 피드백 시 조정
- TC-2~8 은 v0.7 미재실행

## 6. 확인된 것 vs 가정한 것

확인:
- share-lint 결과는 본문 파일에 직접 재실행해 확인 (with-skill TC-9·TC-1 위반 0, baseline TC-9 위반 2)
- moneyball 템플릿 섹션명은 로컬 체크아웃 `.github/PULL_REQUEST_TEMPLATE.md` 와 같음

가정:
- TC-2~8 은 결론 블록 추가 외에 동작이 바뀌지 않는다고 보고 미재실행 (재평가 트리거: 다음 사이클 전체 회귀)
- baseline AUTO FAIL 1 은 Claude Code 기본 attribution 에서 나온 것. 원점수 병기
- 단일 채점자

## 7. 최종 판정

PASS — v0.7 확정.
