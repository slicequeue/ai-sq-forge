# TC-2 응답 (baseline)

## 상황 판단

- 대상 저장소 `poc-meal-recommender` 는 조직 밖 저장소이고 `.claude/shared/vc-conventions-guide.md` 가 없다(`No such file`). 별도 컨벤션 문서가 없으므로 최근 커밋 이력을 컨벤션 근거로 삼는다.
- 최근 커밋 3건은 모두 `타입: 한국어 설명` 형식이다. 타입은 `refac`, `feat`, `fix` 를 쓴다. 따라서 리팩터링 타입은 `refactor` 가 아니라 이력에서 쓰는 `refac` 로 맞춘다.
- 변경 내용은 점수 계산 로직을 `RecommendService` 에서 `ScoreCalculator` 로 옮긴 것이다. 동작 변화는 없고 기존 테스트가 통과했다. 이는 `refac` 에 해당한다.
- 변경 파일 2개는 하나의 논리적 변경이므로 커밋 1개로 묶는다.
- 브랜치는 `api/refac/recommend-scoring` 이고 type(`refac`)과 일치한다.

## 실행할 명령 (순서대로)

1. `git status` : 변경 파일 확인. `ScoreCalculator.java`, `RecommendService.java` 두 파일이 modified 이고 그 외 변경은 없다.
2. `git diff` : 변경 내용 확인. 점수 계산 로직 이동만 있고 동작 변화는 없다.
3. `git log --oneline -5` : 커밋 메시지 스타일 확인. 이미 입력으로 받은 결과(`refac: 식단 후보 필터 분리` 등)를 사용한다.
4. 두 파일을 경로 지정으로 스테이징한다.
   ```
   git add src/main/java/.../recommend/ScoreCalculator.java src/main/java/.../recommend/RecommendService.java
   ```
   `git add -A` 와 `git add .` 는 쓰지 않는다.
5. 커밋한다.
   ```
   git commit -m "refac: 추천 점수 계산 로직 ScoreCalculator 로 분리" -m "RecommendService 에 있던 점수 계산 로직을 ScoreCalculator 로 옮겼다.
   동작 변화는 없고 기존 테스트가 통과한다."
   ```
6. `git status`, `git log --oneline -1` : 커밋 결과 확인.

## 최종 커밋 메시지 전문

```
refac: 추천 점수 계산 로직 ScoreCalculator 로 분리

RecommendService 에 있던 점수 계산 로직을 ScoreCalculator 로 옮겼다.
동작 변화는 없고 기존 테스트가 통과한다.
```

## 사용자에게 보일 최종 출력

커밋했습니다.

- 브랜치: `api/refac/recommend-scoring`
- 커밋 메시지: `refac: 추천 점수 계산 로직 ScoreCalculator 로 분리`
- 포함 파일
  - `src/main/java/.../recommend/ScoreCalculator.java`
  - `src/main/java/.../recommend/RecommendService.java`

참고 사항

- 이 저장소에는 `.claude/shared/vc-conventions-guide.md` 가 없습니다. 그래서 최근 커밋 이력(`refac:`, `feat:`, `fix:` + 한국어 설명)을 기준으로 메시지를 작성했습니다.
- 타입은 이력에서 쓰는 `refac` 로 맞췄습니다.
- 푸시는 하지 않았습니다. 필요하면 말씀해 주세요.
