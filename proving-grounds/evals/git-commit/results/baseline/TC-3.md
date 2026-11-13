# TC-3 baseline 응답 (moneyball / CORE-1561)

## 상황 판단

- 조직 컨벤션 가이드(`.claude/shared/vc-conventions-guide.md`)가 있고, 이 저장소의 제목 형식은 `[키워드] 제목` 이다. 가이드 본문은 이 시뮬레이션에서 읽지 않았으므로 아래 형식은 커밋 이력 실측에 근거한 것이다.
- 변경 5개 중 4개는 CORE-1561(위임청구 지급 완료 푸시) 작업이다. `pr-test.yml` 의 timeout 변경은 이번 작업과 무관하므로 같은 커밋에 섞지 않고 별도 커밋으로 분리한다.
- "한 번에 올려도 돼" 는 기능 변경을 모듈(claim/message)별로 쪼개지 않고 한 커밋으로 묶어도 된다는 뜻으로 해석했다. 무관한 CI 변경까지 묶으라는 뜻으로는 보지 않았다.

## 키워드 선택 근거

| 경로 | 최근 180일 키워드 빈도 |
|------|------------------------|
| claim | `[공통]` 5, `[health-life]` 3 |
| message | `[공통]` 6, `[health-life]` 2, `[삼성생명]` 1 |
| .github | `[공통]` 12, `[CI/CD]` 3 |

- 기능 커밋: 빈도만 보면 claim·message 모두 `[공통]` 이 많다. 그러나 같은 위임청구 기능의 최근 제목이 `[health-life] 위임청구 ... (#9214)` 이고, 이번 변경도 위임청구 도메인 기능이므로 `[health-life]` 를 쓴다. (판단 근거: 동일 기능 도메인의 최신 선례.) 팀이 이 기능을 `[공통]` 으로 분류하길 원하면 키워드만 바꾸면 된다.
- CI 커밋: `.github` 는 `[공통]` 12 대 `[CI/CD]` 3 으로 `[공통]` 이 압도적이므로 `[공통]` 을 쓴다.
- 복수 키워드(`[MCP/S2S]`) 는 이력에 있으나 이번 변경은 단일 도메인이라 쓰지 않는다.
- 제목 끝의 `(#번호)` 는 PR 생성 시 붙는 값이라 커밋 제목에는 넣지 않는다. 티켓 번호는 본문 하단에 둔다.

## 실행할 명령 (순서대로)

```bash
# 1. 브랜치·상태 확인 (이미 확인된 상황 재확인)
git branch --show-current          # api/feat/CORE-1561-claim-push
git status --short

# 2. 기능 커밋: CORE-1561 관련 4개 파일만 명시적으로 스테이징 (git add -A / . 금지)
git add claim/src/main/java/.../ClaimStatusService.java \
        claim/src/test/java/.../ClaimStatusServiceTest.java \
        message/src/main/java/.../push/PushTemplateCode.java \
        message/src/main/java/.../push/ClaimPaidPushListener.java
git diff --cached --stat           # 4개 파일만 들어갔는지 확인
git commit -F - <<'EOF'
[health-life] 위임청구 지급 완료 시 알림 푸시 발송

- 위임청구 상태가 '지급 완료'로 바뀌면 알림 이벤트를 발행한다
- 이벤트를 받아 푸시를 보내는 ClaimPaidPushListener 를 추가한다
- 지급 완료 푸시 템플릿 코드를 PushTemplateCode 에 추가한다
- 상태 변경 시 이벤트 발행에 대한 테스트를 추가한다

Refs: CORE-1561
EOF

# 3. CI 커밋: 이번 작업과 무관한 변경은 분리
git add .github/workflows/pr-test.yml
git commit -m "[공통] PR 테스트 job timeout 20분에서 30분으로 상향"

# 4. 확인 후 한 번에 푸시
git status --short                 # 비어 있어야 함
git log --oneline -2
git push -u origin api/feat/CORE-1561-claim-push
```

## 최종 커밋 메시지 전문

커밋 1 (기능)

```
[health-life] 위임청구 지급 완료 시 알림 푸시 발송

- 위임청구 상태가 '지급 완료'로 바뀌면 알림 이벤트를 발행한다
- 이벤트를 받아 푸시를 보내는 ClaimPaidPushListener 를 추가한다
- 지급 완료 푸시 템플릿 코드를 PushTemplateCode 에 추가한다
- 상태 변경 시 이벤트 발행에 대한 테스트를 추가한다

Refs: CORE-1561
```

커밋 2 (CI)

```
[공통] PR 테스트 job timeout 20분에서 30분으로 상향
```

## 사용자에게 보일 최종 출력

커밋 2개를 만들고 `api/feat/CORE-1561-claim-push` 에 푸시했습니다.

1. `[health-life] 위임청구 지급 완료 시 알림 푸시 발송`
   - `ClaimStatusService`, `ClaimStatusServiceTest`, `PushTemplateCode`, `ClaimPaidPushListener` (4개 파일)
   - 본문 하단에 `Refs: CORE-1561`
2. `[공통] PR 테스트 job timeout 20분에서 30분으로 상향`
   - `.github/workflows/pr-test.yml`

확인하신 점
- `pr-test.yml` 은 CORE-1561 과 무관한 변경이라 기능 커밋에 섞지 않고 별도 커밋으로 분리했습니다. 한 번에 푸시했으므로 올리는 작업은 한 번입니다. 별도 PR 로 빼고 싶으시면 말씀해 주세요.
- 키워드는 최근 180일 이력으로 정했습니다. claim·message 는 `[공통]` 빈도가 더 높지만, 같은 위임청구 기능의 최근 제목(`[health-life] 위임청구 ... (#9214)`)을 따라 `[health-life]` 로 했습니다. `[공통]` 이 맞다면 `git commit --amend` 로 제목만 바꾸면 됩니다. (아직 PR 전이라도 푸시된 뒤에는 force push 가 필요하니, 바꾸려면 알려 주세요.)
- 제목의 `(#PR번호)` 는 PR 생성 시 붙으므로 넣지 않았습니다.
- 컨벤션 가이드 본문은 이번 응답에서 읽지 않았고, 위 형식은 이력 실측 기준입니다. 가이드와 다른 점이 있으면 알려 주세요.
