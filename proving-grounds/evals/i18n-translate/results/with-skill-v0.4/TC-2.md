# 기존 번역 검토 결과 (message-notification, message-pghd)

번역팀 가이드(`references/langskill.md` 공통 규칙, `## en`, `## ja`)와 일본어 실측 규칙(`ja-house-rules.md`)을 기준으로 3개 키를 검토했습니다. 3개 키 모두 고칠 부분이 있습니다. 키 추가·삭제는 없고 en_US / ja_JP 값만 바꿉니다. 한국어 원문은 그대로 두고, 원문 쪽 개선 제안은 맨 아래에 따로 적었습니다(승인 전에는 반영하지 않습니다).

## 1. 요약

| 키 | 언어 | 문제 | 조치 |
|---|---|---|---|
| `alarm.claim.done.title` | en | 알림 타이틀 자리에 45자 문장. 글자 수 x5.62, 표시 폭 x3.21. 실제로 잘림 | 짧은 타이틀로 교체 |
| `alarm.claim.done.title` | ja | `正常に` 군더더기, `〜いたしました` 과공손(가이드 금지), 타이틀인데 문장형 | 체언止め 타이틀로 교체 |
| `nutrition.intake.ratio.body` | en | 번역투(`compared to`, `intake amount` 중복), 가이드 anti-AI tells 해당 | 재작성 |
| `nutrition.intake.ratio.body` | ja | 가이드 `重複表現` 항목에 **그대로 실린 ✕ 사례**(摂取量…摂取, 한국식 한자어 推奨摂取量). 비율 0.88로 길이 검사는 통과해서 지금까지 안 걸림 | 가이드 ○ 예시로 교체 |
| `glucose.trend.stable.body` | en | **하드룰 위반**: `blood sugar` 사용 | `glucose levels` 로 교체 |
| `glucose.trend.stable.body` | ja | `安定的` 은 가이드의 한국식 한자어 반입 금지 항목. 원문 `대체로` 누락 | 재작성 |

## 2. 키별 검토와 반영값

### 2-1. `alarm.claim.done.title` (message-notification, 알림 타이틀)

- 노출 위치: 키에 `title` 이 있고 알림 번들이므로 폭 고정 자리로 판단했습니다. SKILL 이 실제 잘림 사례로 꼽은 바로 그 키입니다.
- 승인 게이트: 위임 등록 완료 알림이라 법정 고지·약관·의학 유형이 아닙니다. 바로 반영할 수 있습니다.

**en**
- 현재: `Assisted claim filing registered successfully`. `successfully` 는 타이틀에서 정보가 없는 군더더기이고, 4단어 명사 나열이라 푸시 미리보기에서 핵심(완료)이 뒤로 밀립니다.
- 반영값: `Claim delegated` (sentence case, 마침표 없음. 가이드 UI/버튼 규칙 기준)
- 조건: 같은 기능의 다른 키(`alarm.claim.*`)가 `Assisted claim filing` 을 기능명으로 쓰고 있다면 용어를 맞춰야 합니다(가이드: 같은 개념은 항상 같은 단어). 그 경우 대안은 `Assisted claim set up` 입니다. 아래 grep 결과를 보고 둘 중 하나를 고릅니다.

**ja**
- 현재: `委任登録が正常に完了いたしました`. `いたしました` 는 가이드가 금지한 과공손 표현이고, `正常に` 는 en 의 `successfully` 를 따라 붙은 군더더기입니다. 타이틀 자리인데 문장형이라 길이도 x2.00 입니다.
- 반영값: `委任登録完了`
- 자기 검수 3번(한자어 3개 연속)에 걸리지만, 이 항목은 본문 문장 대상입니다. 타이틀·섹션 헤더는 가이드가 짧은 명사구(체언止め)를 정해 두었으므로 예외로 판단했습니다. 화면 폭에 여유가 있다면 문장형 `委任登録が完了しました` 도 가능합니다(x1.38, PR 본문에 기록 필요).

### 2-2. `nutrition.intake.ratio.body` (message-pghd, 안내 본문)

- 노출 위치: `body` 키라서 안내문으로 보고 길이 기준을 느슨하게 적용했습니다.
- 승인 게이트: 섭취 비율이라는 데이터를 알려주는 문장입니다. 의학적 권고가 아니므로 대상이 아닙니다.
- 플레이스홀더: `{0}` 1개를 en/ja 모두 그대로 둡니다. 인자가 있는 메시지라 MessageFormat 을 거칩니다. 그래서 en 은 `You've` 같은 축약형을 쓰지 않았습니다. 축약형을 쓰면 `'` 뒤가 리터럴이 되어 `{0}` 이 치환되지 않습니다.

**en**
- 현재: `You have consumed {0}% compared to the recommended daily intake amount.` `compared to` 는 한국어 `대비` 를 직역한 것이고, `intake amount` 는 같은 뜻을 두 번 쓴 것입니다. 소리 내어 읽으면 고객센터 템플릿처럼 들립니다.
- 반영값: `You have had {0}% of your recommended daily intake.`

**ja**
- 현재: `1日の推奨摂取量の{0}%を摂取しました。` 가이드 `重複表現` 절에 **✕ 사례로 그대로 실린 문장**입니다. 摂取가 2번 나오고, `推奨摂取量` 은 한국식 한자어라 반입 금지 대상입니다(일본 공식 영양 용어는 `推奨量`).
- 반영값: `1日の推奨量の{0}%を摂取しました。` (가이드 ○ 예시)
- 더 짧은 대안: `1日の推奨量の{0}%をとりました。`(x0.75, 동사를 바꿔 한자어 반복을 더 줄인 안)

### 2-3. `glucose.trend.stable.body` (message-pghd, 안내 본문)

- 승인 게이트: 오늘 데이터 경향을 알려주는 문장이고 진단이나 권고가 없습니다. 대상이 아닙니다.
- 웰니스 스코프: `안정적` 은 비교·상태 서술이라 진단성 표현이 아닙니다. 문제없습니다.

**en**
- 현재: `Your blood sugar is generally stable today.` 가이드 en 하드룰 위반입니다(`blood sugar` → `glucose`, 예외 없음).
- 반영값: `Your glucose levels are mostly steady today.` (용어집: `glucose levels` 복수형)
- 더 짧은 대안: `Glucose levels mostly steady today.`(x1.94, 폭 x1.09). 단, 본문 자리에서는 완전한 문장을 우선합니다.

**ja**
- 현재: `今日の血糖値は安定的です。` `安定的` 은 가이드의 한국식 한자어 반입 금지 표(안정적 → 安定している)에 있습니다. 원문의 `대체로` 도 빠져서 사실 하나가 누락됐습니다(3-pass 대조 단계의 "빠진 사실").
- 반영값: `今日の血糖値はおおむね安定しています。` (가이드 は/が 항목의 예문과 같은 문장)
- 혈당 표기(`血糖値` / `グルコース値`)는 **확정이 아니라 잠정**입니다. ja-house-rules 기준으로 CGM 측정값의 경향이면 `グルコース値` 쪽일 수 있습니다. 현재 값과 가이드 예문이 `血糖値` 를 쓰고 있어 일단 유지했습니다. 반영 전에 아래 두 가지를 확인하고, 결과가 다르면 `今日のグルコース値はおおむね安定しています。` 로 바꿉니다.
  1. pasta-japan-server 에 같은 키가 있는지, 있다면 어떤 표기를 쓰는지
  2. message-pghd 의 인접 키 `glucose.trend.*` 가 어떤 표기를 쓰는지
- 더 짧은 대안: `今日はおおむね安定しています。`(x0.83). 화면 제목이 이미 혈당 그래프라서 주어를 빼도 의미가 통할 때만 씁니다.

## 3. 반영 diff

파일 경로는 `references/bundles.md` 의 소유 모듈을 기준으로 했습니다. 기존 키의 값만 같은 자리에서 바꿉니다. 바로 앞 줄이 역슬래시로 끝나지 않는지도 반영할 때 함께 확인합니다.

```diff
--- a/notification/src/main/resources/messages/message-notification_en_US.properties
+++ b/notification/src/main/resources/messages/message-notification_en_US.properties
-alarm.claim.done.title=Assisted claim filing registered successfully
+alarm.claim.done.title=Claim delegated

--- a/notification/src/main/resources/messages/message-notification_ja_JP.properties
+++ b/notification/src/main/resources/messages/message-notification_ja_JP.properties
-alarm.claim.done.title=委任登録が正常に完了いたしました
+alarm.claim.done.title=委任登録完了

--- a/pghd/src/main/resources/messages/message-pghd_en_US.properties
+++ b/pghd/src/main/resources/messages/message-pghd_en_US.properties
-nutrition.intake.ratio.body=You have consumed {0}% compared to the recommended daily intake amount.
+nutrition.intake.ratio.body=You have had {0}% of your recommended daily intake.
-glucose.trend.stable.body=Your blood sugar is generally stable today.
+glucose.trend.stable.body=Your glucose levels are mostly steady today.

--- a/pghd/src/main/resources/messages/message-pghd_ja_JP.properties
+++ b/pghd/src/main/resources/messages/message-pghd_ja_JP.properties
-nutrition.intake.ratio.body=1日の推奨摂取量の{0}%を摂取しました。
+nutrition.intake.ratio.body=1日の推奨量の{0}%を摂取しました。
-glucose.trend.stable.body=今日の血糖値は安定的です。
+glucose.trend.stable.body=今日の血糖値はおおむね安定しています。
```

기본(한국어) 파일은 바꾸지 않습니다.

`ALLOWED_MISMATCHES`: 이미 3개 로케일에 있는 키의 값만 바꾸므로 키 집합은 그대로입니다. 허용 목록에 넣거나 뺄 항목이 없습니다. 이 3개 키가 허용 목록에 남아 있다면 죽은 항목이라 테스트가 이미 실패하고 있었을 것입니다. 그러니 아래 테스트가 통과하면 등록되어 있지 않다는 뜻입니다.

## 4. 실행할 명령 (저장소 루트에서)

```bash
# 0) 중복 정의 확인. 앞쪽 번들이 이기므로, 다른 번들에 같은 키가 있으면 이 수정이 무효가 된다
grep -rn -e "^alarm.claim.done.title=" -e "^nutrition.intake.ratio.body=" -e "^glucose.trend.stable.body=" \
  --include="*.properties" .

# 0-1) en 기능명 일관성 (2-1 조건 판단용)
grep -rn "^alarm.claim\." --include="message-notification_en_US.properties" .

# 0-2) ja 혈당 표기 판단용 (2-3)
grep -n "^glucose.trend\." pghd/src/main/resources/messages/message-pghd_ja_JP.properties
JP="${PASTA_JP_ROOT:?pasta-japan-server 체크아웃 경로를 PASTA_JP_ROOT 로 지정}"
grep -n -e "^glucose.trend.stable.body=" -e "^nutrition.intake.ratio.body=" \
  $JP/shared/src/main/resources/messages/message-shared_ja_JP.properties

# 1) 길이
python3 .claude/skills/i18n-translate/scripts/check_ratio.py --bundle message-notification
python3 .claude/skills/i18n-translate/scripts/check_ratio.py --bundle message-pghd

# 2) 정합성·파손 (플레이스홀더 개수·번호, 홑따옴표 포함)
python3 .claude/skills/i18n-translate/scripts/check_parity.py --bundle message-notification
python3 .claude/skills/i18n-translate/scripts/check_parity.py --bundle message-pghd

# 3) 로케일 정합성 테스트 (JDK 21)
./gradlew :pasta-api:test --tests "*MessageBundleLocaleParityTest*"
```

## 5. 길이 검사 결과 (반영값 기준, 직접 계산)

`check_ratio.py` 와 같은 방식으로 계산했습니다(글자 수 비율, 괄호 안은 표시 폭 비율).

| 키 | 언어 | 현재 | 반영값 | 기준 |
|---|---|---|---|---|
| `alarm.claim.done.title` (ko 8자) | en | x5.62 (폭 3.21) | x1.88 (폭 1.07) | 초과 |
| | ja | x2.00 (폭 2.29) | x0.75 (폭 0.86) | 통과 |
| `nutrition.intake.ratio.body` (ko 24자) | en | x2.96 (폭 1.87) | x2.12 (폭 1.34) | 초과 (본문, 완화 적용) |
| | ja | x0.88 (폭 0.97) | x0.79 (폭 0.87) | 통과 |
| `glucose.trend.stable.body` (ko 18자) | en | x2.39 (폭 1.34) | x2.44 (폭 1.38) | 초과 (본문, 완화 적용) |
| | ja | x0.72 (폭 0.81) | x1.06 (폭 1.19) | 초과 (본문, 완화 적용) |

해석:
- en 은 한글 음절이 영문보다 정보 밀도가 높아서, 글자 수 1.2배는 짧은 문구에서 거의 맞출 수 없습니다. `alarm.claim.done.title` 은 표시 폭이 x1.07 로 한국어와 거의 같아 실제 자리에는 들어갈 것으로 봅니다. 다만 글자 수 기준은 초과이므로 PR 본문에 기록합니다.
- `glucose.trend.stable.body` ja 는 현재 값(x0.72)이 길이는 통과하지만 금지 표현과 사실 누락이 있습니다. 길이 기준을 맞추려고 금지 표현을 남기지는 않았습니다(SKILL "길이 기준을 형식적으로만 만족시키기" 회피). 더 짧은 대안 `今日はおおむね安定しています。`(x0.83)를 함께 적습니다.
- `glucose.trend.stable.body` en 은 현재보다 1자 늘었습니다. 하드룰을 지키고 `levels` 를 복수형으로 쓴 결과입니다.

PR 본문에 넣을 길이 초과 기록 (태그 기능 대신):

```
### 번역 길이 기준 초과 (langSKILL 공통 규칙)
- notification :: alarm.claim.done.title [en] x1.88 (폭 x1.07) "Claim delegated". 타이틀. 폭은 원문과 동등
- pghd :: nutrition.intake.ratio.body [en] x2.12 (폭 x1.34). 본문. 짧은 대안 없음(더 줄이면 recommended 정보 손실)
- pghd :: glucose.trend.stable.body [en] x2.44 (폭 x1.38). 본문. 짧은 대안 "Glucose levels mostly steady today."
- pghd :: glucose.trend.stable.body [ja] x1.06 (폭 x1.19). 본문. 짧은 대안 「今日はおおむね安定しています。」(x0.83)
```

## 6. 시뮬레이션한 검사 결과 (예상)

- `check_parity.py`: 키 집합 변화 없음. `{0}` 개수와 번호는 ko/en/ja 모두 1개로 같음. 플레이스홀더가 있는 값에 홑따옴표 없음. 따라서 `[플레이스홀더]`, `[따옴표]` 경고 0건 예상
- `MessageBundleLocaleParityTest`: 키 집합과 허용 목록이 그대로이므로 통과 예상
- 실제 저장소가 없어 위 결과는 실행 결과가 아니라 예상입니다. 0번 grep 에서 다른 번들에 같은 키가 나오면 반영 위치를 다시 판단해야 합니다.

## 7. 한국어 원문 검수 (제안만, 반영하지 않음)

가이드 `## ko` 기준으로 본 것입니다. 디자이너 승인 전에는 파일을 바꾸지 않습니다.

- `nutrition.intake.ratio.body` `하루 권장 섭취량 대비 {0}% 섭취했어요.`: `섭취` 가 2번 나오고 `대비` 는 명사+명사 나열형입니다. 제안: `하루 권장 섭취량의 {0}%를 먹었어요.` 또 `권장 섭취량` 이 어떤 공식 기준(예: 한국인 영양소 섭취기준)을 따른 값인지 확인이 필요합니다. 공식 기준이 아니라면 가이드는 참고용이라는 면책 문구를 붙이도록 권고합니다. 이 문구 자체가 아니라 화면 하단 각주로 처리할 수도 있습니다.
- `alarm.claim.done.title`, `glucose.trend.stable.body`: 지적 사항 없음

## 8. 확인된 것과 가정한 것

**확인된 것 (입력과 스킬 자료 기준)**
- en `blood sugar` 는 가이드 하드룰 위반입니다.
- ja `推奨摂取量…摂取` 와 `安定的` 은 가이드에 금지 사례로 직접 실려 있습니다.
- `いたしました` 는 가이드가 금지한 과공손 표현입니다.
- 길이 비율은 `check_ratio.py` 와 같은 식(글자 수 비율, 전각 2·반각 1 표시 폭)으로 직접 계산했습니다.
- `{0}` 은 3개 로케일 모두 1개로 보존됩니다.

**가정한 것 (반영 전 확인 필요)**
- 파일 경로: `bundles.md` 의 소유 모듈(`notification/`, `pghd/`)을 기준으로 했습니다. 실제 위치는 0번 grep 으로 확인합니다.
- 다른 번들에 같은 키가 없다고 가정했습니다. 있으면 앞쪽 번들이 이깁니다.
- `alarm.claim.done.title` 은 푸시·알림함 타이틀 자리라고 키 이름으로 추정했습니다. `위임` 은 대리 청구 위임으로 해석했고, en 기능명은 형제 키를 보고 확정합니다.
- `glucose.trend.stable.body` 의 ja 혈당 표기(`血糖値` 유지)는 잠정입니다. 일본 서비스 동일 키와 인접 키를 보고 확정합니다.
- 이 3개 키는 `ALLOWED_MISMATCHES` 에 없다고 가정했습니다. 테스트로 확인합니다.
- 위임 등록이 한국 전용 기능이라 일본에서 노출되지 않을 수도 있습니다. 그렇더라도 키 정합성을 위해 ja 값은 유지하고 위와 같이 고칩니다.
