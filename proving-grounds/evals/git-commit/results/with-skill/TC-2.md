# TC-2 응답 (with-skill) — git-commit v1.3

## 0. 형식 판정

- 대상 프로젝트: poc-meal-recommender (조직 밖 저장소)
- `ls .claude/shared/vc-conventions-guide.md` 결과: `No such file`
- 판정: **B. Conventional** `<type>: <한국어 요약>`
- 최근 커밋 이력(`refac:`, `feat:`, `fix:`)도 B 형식과 일치한다. 가이드가 없으므로 조직 컨벤션 원문을 다른 곳에서 찾아 적용하지 않는다.
- 이 프로젝트는 pasta-api 모듈이 아니므로 `spotlessApply` 는 실행하지 않는다.

## 시뮬레이션 상황 (명령 결과)

- 브랜치: `api/refac/recommend-scoring`
- `git status`: modified `src/main/java/.../recommend/ScoreCalculator.java`, `src/main/java/.../recommend/RecommendService.java`
- 변경 내용: 점수 계산 로직을 `RecommendService` 에서 `ScoreCalculator` 로 이동. 동작 변화 없음, 기존 테스트 통과
- 최근 커밋: `refac: 식단 후보 필터 분리`, `feat: 알레르기 제외 추천 추가`, `fix: 칼로리 합계 반올림 오류 수정`

## 논리적 단위 판단

두 파일은 하나의 리팩터링(점수 계산 로직 이동)이다. 도메인도 `recommend` 하나다. 커밋은 1개로 만든다.

타입은 동작 변화 없는 구조 이동이므로 `refac:` 다. `refactor:` 가 아니다. 이 프로젝트의 직전 커밋 `refac: 식단 후보 필터 분리` 와 브랜치명 `api/refac/` 도 같은 관행이다.

## 실행할 명령 (순서대로)

1. `git status`
2. `git diff dev`
3. `git add src/main/java/.../recommend/ScoreCalculator.java src/main/java/.../recommend/RecommendService.java`
4. `git commit -m "refac: 점수 계산 로직 ScoreCalculator 로 분리"`

## 최종 커밋 메시지 전문

```
refac: 점수 계산 로직 ScoreCalculator 로 분리
```

- 본문 없음. Co-authored-by 와 AI 관련 표기 없음. 대괄호 형식 없음.

## 자기 검증

1. [x] `.claude/shared/vc-conventions-guide.md` 부재로 B 판정
2. [x] A 항목 해당 없음 (대괄호 키워드·이슈 키 미사용)
3. [x] `<type>:` 형식, 리팩터링은 `refac:`
4. [x] AI 공동작성자 표기 0건

## 사용자에게 보일 최종 출력

```
✓ 커밋 완료: refac: 점수 계산 로직 ScoreCalculator 로 분리
  형식: B Conventional (`.claude/shared/vc-conventions-guide.md` 없음 — 조직 밖 비적용 프로젝트)
```
