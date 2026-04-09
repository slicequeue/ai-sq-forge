---
description: Worktree 환경에서 임시 변경이 커밋/푸시되지 않도록 보호
globs:
alwaysApply: true
---
# Worktree Safety Convention

이 저장소는 일부 개발자가 Git worktree 환경에서 작업할 수 있습니다.
worktree는 팀 전체가 사용하지 않을 수 있으므로, **worktree 문제를 해결하기 위한 임시 수정은 절대 커밋/푸시하지 않습니다.**

## 절대 커밋/푸시 금지 (예시)
- `build.gradle`, `settings.gradle` 등 빌드/버전 계산 로직을 worktree용으로 분기하는 임시 수정
- `.git` 구조(worktree) 문제를 회피하기 위한 플러그인 비활성화/적용 조건 변경

## 올바른 해결 방식
- **로컬 전용** 실행 옵션(예: Gradle `--init-script`, 환경 변수 등)으로만 worktree 이슈를 회피합니다.
- 임시 파일(예: init script)은 커밋 전에 반드시 제거합니다.

## 커밋 전 체크리스트
- `git diff`에 worktree 전용 변경(빌드 파일 수정 등)이 없는지 확인
- untracked 파일이 커밋 범위에 섞이지 않았는지 확인

## 병렬 에이전트 worktree 작업 시 주의사항

`isolation: "worktree"`로 에이전트를 실행하면 `/private/tmp/wt-{name}/` 경로에 임시 복사본이 생성될 수 있다. (환경·도구에 따라 경로는 다를 수 있다.)

- **경로 인식**: 작업 디렉토리가 저장소 클론 원본이 아닌 임시 worktree 경로임을 인지하고, 읽기·수정은 해당 경로 기준으로 한다.
- **Gradle 빌드**: worktree에서 `./gradlew` 실행 시 `.git` 구조 차이로 버전 플러그인 등이 실패할 수 있다. `--init-script` 등 로컬 전용 옵션으로 우회한다.
- **결과 병합**: worktree에서 변경한 파일은 에이전트 완료 후 메인 워킹 트리로 수동 병합해야 할 수 있다. 자동 반영되지 않는 경우가 있다.
- **정리**: 에이전트가 변경 없이 종료하면 worktree는 정리될 수 있다. 변경이 있으면 결과에 경로·브랜치 정보가 포함될 수 있다.
