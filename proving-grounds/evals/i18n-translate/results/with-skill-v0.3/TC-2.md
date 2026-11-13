# 기존 번역 검토 결과 — alarm.claim.done.title / nutrition.intake.ratio.body / glucose.trend.stable.body

검토 기준: 번역팀 가이드 `references/langskill.md`(공통 규칙, `## ko`, `## en`, `## ja`)와 일본어 실측 규칙 `references/ja-house-rules.md`. 길이는 가이드의 글자 수 비율(en 1.2배, ja 0.9배)을 1차 게이트로 보고, 표시 폭(전각 2, 반각 1)은 보조 지표로 같이 계산했다.

결론부터 말하면 3개 키 모두 en·ja 값을 고쳐야 한다. 한국어 원문은 바꾸지 않는다. 고칠 만한 곳 1건은 수정안만 아래에 적었고, 반영하려면 승인이 필요하다.

---

## 1. 키별 판정

### 1-1. `message-notification` / `alarm.claim.done.title` (알림 타이틀, 폭 고정 자리)

| 로케일 | 현재 | 문제 |
|---|---|---|
| ko | 위임 등록 완료 | 그대로 둔다. 명사형 타이틀이라 가이드의 종결 형태 기본값에 맞는다 |
| en | Assisted claim filing registered successfully | 글자 수 5.62배, 표시 폭 3.21배. 알림 타이틀 자리에서 실제로 잘린다(스킬 본문에 실제로 잘린 사례로 올라 있는 바로 그 문자열). `successfully` 는 필요 없는 말이고, Title Case 도 아니지만 문장이 길어서 타이틀 역할을 못 한다 |
| ja | 委任登録が正常に完了いたしました | 〜いたしました 는 지나치게 공손한 표현이라 금지 대상(`## ja` 핵심 톤). 正常に 는 필요 없는 말. 타이틀인데 문장으로 끝난다. 0.9배 기준을 넘는다(2.00배) |

수정안:

| 로케일 | 값 | 글자 수 비율 | 표시 폭 비율 |
|---|---|---|---|
| en | `Claim delegated` | 1.88 (초과) | 1.07 |
| en 짧은 대안 | `Delegated` | 1.12 (통과) | 0.64 |
| ja | `委任の登録完了` | 0.88 (통과) | 1.00 |
| ja 대안(동사형) | `委任登録が完了しました` | 1.38 (초과) | 1.57 |

- en: 글자 수는 초과지만 표시 폭은 한국어와 거의 같다(15 대 14). 두 지표가 다른 결과를 내므로 스킬 규칙상 **사람이 화면에서 직접 봐야 한다.** 그래서 `Claim delegated` 를 넣고 PR 본문에 길이 검토 대상으로 적는다. 화면에서 잘리면 `Delegated` 로 바꾼다. `Delegated` 만 쓰면 무엇을 위임했는지 알 수 없어서 기본값으로 쓰지 않았다.
- ja: `委任の登録完了` 는 길이와 폭 모두 통과한다. の 를 넣어서 한자어 4개(委任·登録·完了)가 연달아 붙는 것을 피했다(자기 검수 3번). 타이틀이라 마침표를 붙이지 않는다.
- 확인 필요: "위임"이 정확히 무엇인지(보험금 청구 대행 위임으로 추정)는 알림을 보내는 코드에서 확인해야 한다. 기존 en 값의 `Assisted claim filing` 을 보고 추정했다. 만약 법적 위임 고지 성격이면 법무 확인 대상이 되지만, 완료 알림 타이틀이므로 승인 게이트 대상은 아니라고 봤다.

### 1-2. `message-pghd` / `nutrition.intake.ratio.body` (안내 본문)

| 로케일 | 현재 | 문제 |
|---|---|---|
| ko | 하루 권장 섭취량 대비 {0}% 섭취했어요. | 번역 대상 원문이라 그대로 둔다. 다만 개선 제안 있음(아래 3절) |
| en | You have consumed {0}% compared to the recommended daily intake amount. | 번역투가 강하다. `compared to` 는 "대비"를 그대로 옮긴 것이고, `intake amount` 는 같은 뜻을 두 번 쓴 표현이다. `You have consumed` 는 딱딱하다. 2.96배 |
| ja | 1日の推奨摂取量の{0}%を摂取しました。 | 가이드 `## ja` 重複表現 항목에 **같은 문장이 오답 예시로 그대로 실려 있다.** 摂取(せっしゅ)가 2회, 推奨摂取量 은 한국식 한자어(일본 공식 용어는 推奨量). 비율은 0.88로 통과하지만 길이만 맞춘 사례다 |

수정안:

| 로케일 | 값 | 글자 수 비율 | 표시 폭 비율 |
|---|---|---|---|
| en | `You've had {0}% of your recommended daily intake.` | 2.04 | 1.29 |
| en 짧은 대안 | `That's {0}% of your recommended daily intake.` | 1.88 | 1.18 |
| ja | `1日の推奨量の{0}%を摂取しました。` | 0.79 | 0.87 |
| ja 최단 대안 | `1日の推奨量の{0}%です。` | 0.58 | 0.61 |

- 플레이스홀더 `{0}` 1개를 유지한다.
- en 은 1.2배를 넘지만 안내 본문이라 느슨하게 적용한다. 영어 문장으로 1.2배 안에 맞추면 `recommended` 를 빼야 하는데, 그러면 무엇과 비교한 퍼센트인지 흐려진다. PR 본문에 길이 초과로 적는다.
- ja 는 가이드에 맞게 고친 문장(○ 예시)을 그대로 쓴다. の 가 2번 나오지만 3번 연속이 아니라서 허용 범위다.

### 1-3. `message-pghd` / `glucose.trend.stable.body` (안내 본문)

| 로케일 | 현재 | 문제 |
|---|---|---|
| ko | 오늘 혈당은 대체로 안정적이에요. | 그대로 둔다. 단정적인 진단 표현이 아니라서 웰니스 스코프에 맞는다 |
| en | Your blood sugar is generally stable today. | **하드룰 위반.** `blood sugar` 는 예외 없이 `glucose` 로 바꿔야 한다. 용어집 기준은 복수 `glucose levels` |
| ja | 今日の血糖値は安定的です。 | 安定的 은 한국식 한자어라 쓰면 안 된다(가이드 표: 안정적 → 安定している). 원문의 "대체로"가 빠졌다. 단정이 강해져서 웰니스 포지션에도 맞지 않는다 |

수정안:

| 로케일 | 값 | 글자 수 비율 | 표시 폭 비율 |
|---|---|---|---|
| en | `Your glucose levels are mostly steady today.` | 2.44 | 1.38 |
| en 짧은 대안 | `Your glucose is mostly steady today.` | 2.00 | 1.13 |
| ja | `今日の血糖値はおおむね安定しています。` | 1.06 (초과) | 1.19 |
| ja 짧은 대안 | `今日の血糖値はほぼ安定しています。` | 0.94 (초과) | 1.06 |

- ja 는 0.9배를 조금 넘는다. 기존 값이 짧았던 건 "대체로"를 빼먹었기 때문이다. `今日の血糖値は安定しています。`(0.83)로 맞출 수는 있지만, 그러면 "대체로"라는 완충이 사라져 단정으로 바뀐다. 자기 검수 7번(단정과 추량이 바뀌면 안 됨)에 걸리므로 쓰지 않는다. 안내 본문이므로 느슨하게 보고, PR 본문에 길이 초과로 적는다.
- ja 문장은 가이드 は/が 항목의 예문과 같다. 이미 알고 있는 주제이므로 は 를 쓴다.
- **표기 확인 필요 (血糖値 / グルコース値):** `ja-house-rules.md` 2절 기준으로 보면, CGM 측정값 자체나 그래프에는 グルコース値 를, 생리학적 개념 설명에는 血糖値 를 쓴다. 이 키는 `glucose.trend` 즉 오늘 측정 추이를 말하는 것이라 グルコース値 쪽일 가능성이 있다. 반면 기존 값과 가이드 예문은 血糖値 다. 지금은 확인할 수 없으므로 **기존 표기(血糖値)를 유지하고 安定的 만 고친다.** 반영 전에 아래 명령으로 일본 서비스의 같은 키와 같은 번들의 인접 키를 확인하고, グルコース値 를 쓰고 있으면 그쪽에 맞춘다.

```bash
JP=/Users/kakao/workplace-kakao/global/pasta-japan/server/pasta-japan-server
grep -n "^glucose.trend\." $JP/shared/src/main/resources/messages/message-shared_ja_JP.properties
grep -n "^glucose\.trend\." pghd/src/main/resources/messages/message-pghd_ja_JP.properties
```

---

## 2. 반영 diff

키 위치는 바꾸지 않고, 원래 줄에서 값만 바꾼다. 3개 키 모두 한 줄짜리 값이라 줄 끝 역슬래시 문제는 없다. 그래도 바꾼 줄의 바로 앞 줄이 역슬래시로 끝나지 않는지 확인한다.

```diff
--- notification/src/main/resources/messages/message-notification_en_US.properties
-alarm.claim.done.title=Assisted claim filing registered successfully
+alarm.claim.done.title=Claim delegated

--- notification/src/main/resources/messages/message-notification_ja_JP.properties
-alarm.claim.done.title=委任登録が正常に完了いたしました
+alarm.claim.done.title=委任の登録完了

--- pghd/src/main/resources/messages/message-pghd_en_US.properties
-nutrition.intake.ratio.body=You have consumed {0}% compared to the recommended daily intake amount.
+nutrition.intake.ratio.body=You've had {0}% of your recommended daily intake.
-glucose.trend.stable.body=Your blood sugar is generally stable today.
+glucose.trend.stable.body=Your glucose levels are mostly steady today.

--- pghd/src/main/resources/messages/message-pghd_ja_JP.properties
-nutrition.intake.ratio.body=1日の推奨摂取量の{0}%を摂取しました。
+nutrition.intake.ratio.body=1日の推奨量の{0}%を摂取しました。
-glucose.trend.stable.body=今日の血糖値は安定的です。
+glucose.trend.stable.body=今日の血糖値はおおむね安定しています。
```

- en 의 `You've` 에 들어간 작은따옴표(`'`)는 이 키가 `MessageFormat` 으로 처리되는지에 따라 의미가 달라진다. `{0}` 이 들어간 키라 MessageFormat 을 거치므로, 작은따옴표 하나가 뒤의 `{0}` 을 리터럴로 묶어 버릴 수 있다. **`You''ve` 처럼 두 개로 써야 한다.** 같은 번들의 다른 en 값이 어떻게 처리했는지 확인하고 맞춘다. `alwaysUseMessageFormat` 설정과 형제 키를 보면 판단할 수 있다.

```bash
grep -n "''" pghd/src/main/resources/messages/message-pghd_en_US.properties | head
grep -rn "alwaysUseMessageFormat" --include="*.java" .
```

  기본 설정(`alwaysUseMessageFormat=false`)이면 인자가 있는 메시지만 MessageFormat 을 거친다. 이 키는 인자가 있으므로 diff 의 해당 줄은 `You''ve had {0}% of your recommended daily intake.` 로 반영하는 것이 안전하다. 따옴표가 없는 `That's` 대안도 같은 문제가 있으므로, 따옴표를 아예 피하려면 `You have had {0}% of your recommended daily intake.` 를 쓴다.

---

## 3. 한국어 원문 수정 제안 (승인 전에는 반영하지 않음)

| 키 | 현재 | 제안 | 근거 |
|---|---|---|---|
| `nutrition.intake.ratio.body` | 하루 권장 섭취량 대비 {0}% 섭취했어요. | 하루 권장량의 {0}%를 섭취했어요. | "섭취"가 한 문장에 두 번 나오고, "권장 섭취량 대비"는 명사가 나열된 형태다(`## ko` 명사+명사 지양). |

- 원문 승인 후 수정되면 en/ja 도 다시 확인한다. 위 en/ja 수정안은 현재 원문을 기준으로 해도 의미가 같다.
- 종결 형태가 그룹 안에서 일관된지는 이 3개 문자열만 봐서는 판단할 수 없다. `nutrition.*` 와 `glucose.trend.*` 그룹을 한 번에 봐야 하는데, 이번 요청 범위 밖이라 검토하지 않았다.

---

## 4. 반영 전후 확인 절차

```bash
# 1) 다른 번들에 같은 키가 있는지 확인. 앞쪽 번들에 같은 키가 있으면 여기 반영한 값은 쓰이지 않는다
grep -rn "^alarm.claim.done.title=" --include="*.properties" .
grep -rn "^nutrition.intake.ratio.body=" --include="*.properties" .
grep -rn "^glucose.trend.stable.body=" --include="*.properties" .

# 2) 길이 검사
python3 scripts/check_ratio.py --bundle message-notification
python3 scripts/check_ratio.py --bundle message-pghd

# 3) 정합성·파손 검사
python3 scripts/check_parity.py --bundle message-notification
python3 scripts/check_parity.py --bundle message-pghd

# 4) 로케일 정합성 테스트 (JDK 21)
./gradlew :pasta-api:test --tests "*MessageBundleLocaleParityTest*"
```

실제 저장소가 없어서 아래 결과는 예상치다.

- 1) 각 키가 해당 번들 3개 파일에서만 나와야 한다. 특히 `message-notification` 키가 `message-pasta-api` 같은 다른 번들에도 있으면, BASENAMES 순서에 따라 이긴 쪽에 반영해야 한다.
- 2) 위반 예상: en 3건(`Claim delegated` 1.88, `nutrition` 2.04, `glucose` 2.44), ja 1건(`glucose` 1.06). `alarm.claim.done.title` en 은 글자 수와 표시 폭이 다른 결과를 낸다. 나머지는 안내 본문이라 느슨하게 적용하는 범위다.
- 3) 키를 추가하거나 삭제하지 않고 값만 바꾸므로, 키 집합 차이 0건과 파손 줄 0건이 예상된다.
- 4) 3개 키는 이미 ko/en_US/ja_JP 에 모두 있으므로 `ALLOWED_MISMATCHES` 는 바꾸지 않는다. 혹시 이 키들이 허용 목록에 남아 있다면 이미 죽은 항목이라 테스트가 지금도 실패하고 있을 것이다. `grep -n "alarm.claim.done.title\|nutrition.intake.ratio.body\|glucose.trend.stable.body" -r --include="*ParityTest*.java" .` 로 한 번 확인한다.

---

## 5. PR 본문에 남길 길이 검토 항목

이 저장소에는 Tolgee 의 `length:review` 태그가 없으므로 PR 본문에 적는다.

```
길이 검토 필요 (langSKILL 기준 초과)
- alarm.claim.done.title (en) "Claim delegated" 1.88배 / 표시 폭 1.07배. 두 지표가 다르게 나와 화면 확인 필요. 잘리면 "Delegated"
- nutrition.intake.ratio.body (en) 2.04배. 안내 본문
- glucose.trend.stable.body (en) 2.44배, (ja) 1.06배. 안내 본문. ja는 "おおむね"(대체로)를 유지하려고 초과를 받아들임
표기 확인 필요
- glucose.trend.stable.body (ja) 血糖値 / グルコース値: 일본 서비스의 같은 키를 확인한 뒤 확정
```

---

## 확인한 것과 가정한 것

| 구분 | 내용 |
|---|---|
| 확인함 | 가이드 규칙 위반 항목(en 의 blood sugar 하드룰, ja 의 過剰敬語 いたしました, 安定的, 推奨摂取量 重複) / 글자 수와 표시 폭 수치(직접 계산) |
| 가정함 | 번들 파일 경로(모듈 `notification/`, `pghd/` 아래 표준 resources 경로) / "위임"이 청구 대행 위임이라는 뜻(기존 en 값에서 추정) / 이 키들이 ALLOWED_MISMATCHES 에 없다는 점 / 다른 번들에 같은 키가 없다는 점 |
| 확인 필요 | 4절 1번 grep 결과 / 血糖値·グルコース値 표기 / `You've` 작은따옴표 처리 방식 / `alarm.claim.done.title` en 이 실제 화면에서 잘리는지 |
