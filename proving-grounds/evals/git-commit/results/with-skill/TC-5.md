# TC-5 응답 (with-skill, 시뮬레이션)

## 0. 형식 판정

- 확인된 것
  - `ls .claude/shared/vc-conventions-guide.md` 결과는 "No such file" 이다. 배포본 가이드가 없다.
  - `forge/common/vc-conventions-guide.md` 는 forge 원본이며 있다. 원본은 배포 대상 프로젝트에 이식됐을 때 적용 판정에 쓰는 파일이 아니고, 판정 기준은 배포본 경로의 존재 여부다.
  - 최근 커밋 3건은 모두 `feat:`, `fix:`, `chore:` 형식이다.
- 판정: **B. Conventional** `<type>: <한국어 요약>`
- 사용자 요청(`[키워드]` 형식)에 대한 처리: 이 요청은 "조직 컨벤션이 생겼다"는 이유로 forge 저장소의 형식을 바꾸자는 것이다. 판정 규칙은 가이드 원본이 있다는 사실만으로 형식을 바꾸지 않는다(B 프로젝트에서 대괄호 형식 금지). 그래서 이번 커밋은 B 형식으로 진행하고, 아래 출력에 판정 근거를 적는다.
- 가정한 것: 두 변경 파일은 같은 컴포넌트(git-commit)의 개정과 그 하네스라서 한 커밋으로 묶는다. 재평가 트리거는 "사용자가 forge 도 조직 컨벤션 적용 대상으로 바꾸겠다고 명시하고 `forge/common/vc-conventions-guide.md` 를 `.claude/shared/` 에 두는 경우"다.

## 실행할 명령 (순서대로)

1. `ls .claude/shared/vc-conventions-guide.md` : No such file (판정 입력)
2. `git status` : modified `anvil/commands/git-commit.md`, new `proving-grounds/harnesses/git-commit.harness.md`
3. `git diff dev -- anvil/commands/git-commit.md` : 조직 컨벤션 분기(A/B 판정) 신설 내용 확인
4. spotless 생략 : pasta-api 모듈 파일이 아니라 마크다운 변경뿐이다
5. `git add anvil/commands/git-commit.md proving-grounds/harnesses/git-commit.harness.md` : 두 파일만 명시 stage(`git add -A` 사용 안 함)
6. `git commit -m "feat: git-commit 조직 컨벤션 형식 판정 분기 신설 및 하네스 추가"` : 메시지에 AI 공동작성자 표기 없음

## 최종 커밋 메시지 전문

```
feat: git-commit 조직 컨벤션 형식 판정 분기 신설 및 하네스 추가
```

## 사용자에게 보일 최종 출력

```
✓ 커밋 완료: feat: git-commit 조직 컨벤션 형식 판정 분기 신설 및 하네스 추가
  형식: B Conventional (배포본 `.claude/shared/vc-conventions-guide.md` 없음. forge 원본 가이드는 있으나 forge 저장소 자체 커밋은 B)
```

안내: `[키워드]` 형식은 이 저장소에 적용하지 않았다. 판정 기준은 배포본 가이드 존재 여부이고, forge 저장소에는 배포본이 없으며 이력도 `feat:`, `fix:`, `chore:` 다. 조직 컨벤션은 virtualcare 처럼 가이드가 배포된 프로젝트에만 적용된다. forge 저장소 커밋도 바꾸려면 그 방침을 따로 정하고 알려주면 된다. 그때까지는 기존 커밋 메시지를 고쳐 쓰지 않고, 신규 커밋에만 적용한다.
