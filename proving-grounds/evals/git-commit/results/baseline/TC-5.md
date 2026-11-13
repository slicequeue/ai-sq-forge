# TC-5 응답 (baseline)

## 상황 판단

- 사용자가 이 저장소(ai-sq-forge)에도 `[키워드]` 형식을 쓰라고 명시했습니다. 저장소가 원래 컨벤션 적용 대상이 아니라는 이유로 이 요청을 거절하거나 Conventional Commits로 되돌리지 않고, 요청을 따릅니다.
- 배포본 `.claude/shared/vc-conventions-guide.md`는 없습니다. 이 저장소는 적용 대상 프로젝트가 아니라 원본을 보관하는 곳이라 배포본이 없는 것이 정상입니다.
- 원본 `forge/common/vc-conventions-guide.md`는 있습니다. 키워드 목록과 형식 세부는 기억이나 추측으로 정하지 않고 이 원본을 읽어서 정합니다.
- 확인된 것: 브랜치는 `slicequeue/chore-cycle9`입니다. 변경은 `anvil/commands/git-commit.md` 수정 1건과 `proving-grounds/harnesses/git-commit.harness.md` 신규 1건입니다. 최근 커밋은 모두 `type: 설명` 형식입니다.
- 가정한 것:
  - 이번 시뮬레이션에서는 원본 가이드의 내용을 볼 수 없습니다. 그래서 아래 커밋 메시지의 키워드 `[chore]`와 그 표기 방식은 가정입니다. 실제 실행에서는 3단계에서 읽은 가이드의 키워드 표와 형식으로 바꿉니다.
  - 이번 변경은 git-commit 컴포넌트 정의와 그 하네스를 갱신하는 유지보수 작업이라, 최근 이력의 `chore:` 성격과 같다고 봤습니다.
  - 재평가 트리거: 가이드의 키워드 표에 해당 키워드가 없거나 표기 방식이 다르면 메시지를 가이드에 맞게 고칩니다. 아직 푸시 전이므로 `git commit --amend`로 수정할 수 있습니다.

## 실행할 명령 (순서대로)

```bash
# 1. 배포본 유무 확인 (없음 확인됨)
ls .claude/shared/vc-conventions-guide.md
# 2. 원본 존재 확인 (있음)
ls forge/common/vc-conventions-guide.md
# 3. 원본에서 키워드 목록·형식 읽기 (읽기 전용)
cat forge/common/vc-conventions-guide.md
# 4. 변경 현황과 스타일 확인
git status --short
git diff -- anvil/commands/git-commit.md
git log --oneline -5
# 5. 변경 파일만 명시적으로 스테이징 (git add -A 사용 안 함)
git add anvil/commands/git-commit.md proving-grounds/harnesses/git-commit.harness.md
# 6. 커밋
git commit -m "[chore] git-commit 커맨드 갱신 + git-commit 하네스 정의 추가" \
           -m "- anvil/commands/git-commit.md: [키워드] 형식 커밋 지침 반영
- proving-grounds/harnesses/git-commit.harness.md: 신규 하네스 정의 추가"
# 7. 결과 확인
git log -1 --stat
```

- 푸시는 요청받지 않았으므로 하지 않습니다.
- 훅이 실패하면 `--no-verify`로 우회하지 않고 원인을 고쳐 새로 커밋합니다.

## 최종 커밋 메시지 전문

```
[chore] git-commit 커맨드 갱신 + git-commit 하네스 정의 추가

- anvil/commands/git-commit.md: [키워드] 형식 커밋 지침 반영
- proving-grounds/harnesses/git-commit.harness.md: 신규 하네스 정의 추가
```

## 사용자에게 보일 최종 출력

`[키워드]` 형식으로 커밋했습니다. (브랜치 `slicequeue/chore-cycle9`, 푸시는 하지 않았습니다.)

```
[chore] git-commit 커맨드 갱신 + git-commit 하네스 정의 추가
 anvil/commands/git-commit.md                       | 수정
 proving-grounds/harnesses/git-commit.harness.md    | 신규
```

확인할 점이 두 가지 있습니다.

- 이 저장소에는 배포본 `.claude/shared/vc-conventions-guide.md`가 없습니다. 이 저장소는 규칙을 배포하는 쪽이라 정상입니다. 그래서 원본 `forge/common/vc-conventions-guide.md`를 기준으로 삼았습니다.
- 이번 응답에서는 원본 가이드의 키워드 표를 직접 확인하지 못했습니다. 키워드 `[chore]`는 이번 변경이 유지보수 성격이라고 판단한 가정입니다. 가이드의 키워드나 표기가 다르면 `git commit --amend`로 바로 고치겠습니다. 원하는 키워드가 있으면 알려주세요.
- 앞으로 이 저장소의 커밋도 같은 형식으로 쓰겠습니다. 기존 이력(`feat:`, `fix:`, `chore:`)은 그대로 둡니다.
