# git-commit TC-1 baseline 응답

## 1. 상황 판단

확인된 사실
- 대상은 pasta-japan-server(virtualcare)이고 `.claude/shared/vc-conventions-guide.md` 가 있다. 조직 컨벤션이 적용되는 저장소다.
- 브랜치는 `api/fix/glp1-symptom-recent` 이다. 이슈 키는 없다.
- 변경 파일은 2개다. 서비스 코드 `Glp1SymptomQueryService.java` 와 테스트 `Glp1SymptomQueryServiceTest.java` 이고, 둘 다 같은 목적의 변경이다. 커밋 1개로 묶는다.
- 최근 180일 `pghd` 경로 커밋 제목의 prefix 빈도는 `[PGHD]` 13건, `[NOTIFICATION/PGHD]` 1건, `[CONNECT]` 1건, `[API]` 1건이다. `[PGHD]` 가 압도적으로 많고, 변경이 pghd 모듈에만 있다.

가정한 것 (재평가 트리거 포함)
- 이 응답에서는 컨벤션 가이드 본문을 읽지 못했다. 그래서 제목 형식은 위 빈도 실측을 근거로 `[PGHD] 한국어 제목` 으로 정했다. 가이드 본문이 다른 형식(예: 이슈 키 필수, type 접두어 병기)을 요구하면 그 형식을 따라 메시지를 다시 만든다.
- 이슈 키가 없으므로 키 자리는 비우고, 임의로 만들어 넣지 않는다.

## 2. 실행할 명령 (순서대로)

```bash
# 1) 컨벤션 가이드 존재 확인 후 본문 읽기 (실제 실행 시 먼저 수행)
ls .claude/shared/vc-conventions-guide.md
cat .claude/shared/vc-conventions-guide.md

# 2) 현재 상태와 변경 내용 확인
git branch --show-current
git status
git diff

# 3) 컨벤션 prefix 를 최근 이력 빈도로 확인
git log origin/dev --since=180.days --format=%s -- pghd | grep -oE '^\[[^]]+\]' | sort | uniq -c | sort -rn

# 4) 변경 파일만 명시해서 스테이징 (git add -A / . 사용 금지)
git add pghd/src/main/java/.../glp1/application/Glp1SymptomQueryService.java \
        pghd/src/test/java/.../glp1/application/Glp1SymptomQueryServiceTest.java

# 5) 커밋
git commit -F - <<'EOF'
[PGHD] GLP-1 증상 문항 조회 시 동시 저장된 최근 증상 전체 반환

최근 기록한 증상을 조회할 때 같은 시각에 저장된 증상이 여럿이어도
하나만 반환하던 문제를 수정한다. 같은 시각에 저장된 증상을 모두
반환하도록 변경하고, 이를 검증하는 테스트 1건을 추가한다.
EOF

# 6) 결과 확인
git log -1 --stat
git status
```

(`...` 는 시뮬레이션 입력에서 생략된 패키지 경로이며, 실제 실행 시에는 전체 경로를 쓴다.)

실행하지 않는 것
- `git push` 는 요청 범위 밖이므로 하지 않는다.
- `--no-verify`, `--amend` 는 쓰지 않는다.

## 3. 최종 커밋 메시지 전문

```
[PGHD] GLP-1 증상 문항 조회 시 동시 저장된 최근 증상 전체 반환

최근 기록한 증상을 조회할 때 같은 시각에 저장된 증상이 여럿이어도
하나만 반환하던 문제를 수정한다. 같은 시각에 저장된 증상을 모두
반환하도록 변경하고, 이를 검증하는 테스트 1건을 추가한다.
```

선택 근거
- 제목 prefix 는 `[PGHD]` 다. 이 경로의 최근 이력에서 가장 많이 쓰였고 변경 범위가 pghd 모듈 하나이기 때문이다. `[NOTIFICATION/PGHD]` 는 알림이 얽힌 변경에만 쓰인 형태라 해당하지 않는다.
- 제목은 동작 변화(무엇이 바뀌었는지)를 한국어로 쓰고 마침표를 붙이지 않았다.
- 본문은 무엇이 문제였고 어떻게 고쳤는지를 적었다. 이슈 키가 없어서 키 줄이나 `Refs` 줄은 넣지 않았다.
- 브랜치 이름의 `fix` 는 변경 성격과 일치한다. 제목에는 `fix:` 를 따로 붙이지 않았다. 이 저장소의 prefix 가 대괄호 방식이라는 실측을 따른 것이다.

## 4. 사용자에게 보일 최종 출력

커밋했습니다.

- 브랜치: `api/fix/glp1-symptom-recent`
- 커밋 제목: `[PGHD] GLP-1 증상 문항 조회 시 동시 저장된 최근 증상 전체 반환`
- 포함 파일 (2개)
  - `pghd/src/main/java/.../glp1/application/Glp1SymptomQueryService.java`
  - `pghd/src/test/java/.../glp1/application/Glp1SymptomQueryServiceTest.java`

확인한 것과 가정한 것
- 확인: 최근 180일 pghd 커밋은 `[PGHD]` prefix 가 13건으로 가장 많아 이를 썼습니다.
- 확인: 이슈 키가 없어 메시지에 키를 넣지 않았습니다.
- 가정: 컨벤션 가이드 본문은 반영하지 못했습니다. 가이드가 다른 제목 형식을 요구하면 알려 주세요. 메시지를 고쳐 다시 커밋하겠습니다. 푸시 전이면 `git commit --amend` 로 수정할 수 있습니다.

푸시는 하지 않았습니다. 필요하면 말씀해 주세요.
