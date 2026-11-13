# message-cgm en_US / ja_JP 누락 3건 처리안

## 결론 먼저

| 키 | 처리 | 이유 |
|---|---|---|
| `cgm.sensor.start.button` | **반영** (en/ja) | 일반 UI 버튼 |
| `cgm.report.weekly.title` | **반영** (en/ja), 길이 검토 대상으로 PR 본문에 기록 | 일반 UI 타이틀. 글자 수 비율 초과 |
| `cgm.alert.high.body` | **반영 보류, 초안만 제시** | 혈당 수치에 따른 행동 권고(물 섭취, 걷기)라서 스킬의 "의학적 권고" 승인 게이트에 해당 |

세 번째 키를 빼고 처리하는 것은 임의 제외가 아니고 승인 게이트 때문이다. 초안은 아래에 있고, 의학 검수 담당자가 확인하면 같은 방식으로 바로 넣을 수 있다. 잘못된 건강 권고 문구가 배포되는 것이 번역이 늦어지는 것보다 나쁘다는 판단이다. 검수 없이 지금 넣기를 원하면 말해 달라. 그 경우에도 아래 초안을 그대로 쓰면 된다.

## 확인된 사실과 가정

**확인된 사실 (요청에 나온 내용)**
- 기본 번들에 3개 키가 있고, `_en_US` / `_ja_JP` 에는 없다
- 앞뒤 키 `cgm.sensor.calibrate.button`, `cgm.report.daily.title` 은 로케일 파일에 있다
- 3개 키가 `ALLOWED_MISMATCHES` 에 등록되어 있다
- `useCodeAsDefaultMessage=true` 라서 지금은 en/ja 사용자에게 한국어가 그대로 보인다

**가정 (반영 전 확인 필요)**
- 3개 키가 다른 번들(특히 `message-cgm` 보다 앞 순서 번들)에 중복 정의되어 있지 않다. 중복이 있으면 `message-cgm` 에 넣어도 앞쪽 번들 값이 이긴다. 아래 1번 명령으로 확인한다
- `cgm.report.daily.title` 의 en/ja 값을 직접 보지 못했다. 형제 타이틀과 표기를 맞춰야 하므로 아래 2번 명령으로 확인한 뒤 weekly 값을 그 패턴에 맞춘다
- `ALLOWED_MISMATCHES` 의 실제 자료구조(Map/Set, 항목 형식)를 보지 못했다. 아래 diff 는 형식을 가정한 것이다
- `cgm.alert.high.body` 는 키 이름상 혈당 높음 알림(푸시 또는 인앱 알림) 본문으로 봤다

## 반영 전 확인 명령

```bash
# 1. 중복 정의 확인 — 다른 번들에 같은 키가 있는지
grep -rn -E "^(cgm\.sensor\.start\.button|cgm\.report\.weekly\.title|cgm\.alert\.high\.body)=" --include="*.properties" .

# 2. 형제 키 표기 확인 — weekly.title 을 daily.title 과 같은 패턴으로 맞추기 위해
grep -n -E "^(cgm\.report\.daily\.title|cgm\.sensor\.calibrate\.button)=" cgm/src/main/resources/messages/message-cgm*.properties
```

판단 기준:
- 1번에서 `cgm/` 외 다른 파일이 나오면 반영을 멈추고 어느 번들이 이기는지 먼저 정리한다
- 2번에서 daily 가 `Daily glucose report` / `デイリーグルコースレポート` 처럼 혈당 단어를 넣고 있으면 아래 값 그대로, `Daily report` / `日間レポート` 처럼 빼고 있으면 주석의 짧은 대안으로 바꿔 넣는다

## 한국어 원문 1차 검수 (langskill `## ko`)

원문은 수정하지 않는다. 검수 결과만 적는다.

| 키 | 결과 |
|---|---|
| `cgm.sensor.start.button` | 문제 없음. CTA 성격이라 `~하기` 동사형 허용 범위. 7자로 15자 권장 이내 |
| `cgm.report.weekly.title` | 문제 없음. 명사형 타이틀, 용어집의 "혈당" 사용 |
| `cgm.alert.high.body` | 문제 없음. "혈당이 높다" 단정 대신 "목표 범위보다 높아요" 로 웰니스 스코프 준수. 해요체, 안내형 요청("걸어보세요") |

## 번역 값

### 1) `cgm.sensor.start.button` = 측정 시작하기

| 언어 | 값 | 글자 수 비율 | 표시 폭 비율 | 판정 |
|---|---|---|---|---|
| en | `Start measuring` | 15/7 = 2.14 (기준 1.2) | 15/13 = 1.15 | 글자 수 초과, 표시 폭은 근접. **두 지표가 어긋나므로 화면 확인 대상** |
| ja | `測定を始める` | 6/7 = 0.86 (기준 0.9) | 12/13 = 0.92 | 통과 |

- en: 버튼은 동사로 시작, sentence case, 마침표 없음. 짧은 대안은 `Start` (5자, 0.71). 센서 화면 맥락으로 의미가 충분히 드러나면 이쪽이 낫다
- ja: 새 버튼의 기본값인 동사형 CTA. `開始` 같은 한자어 명사형보다 `始める` 가 앱 톤에 맞다

### 2) `cgm.report.weekly.title` = 주간 혈당 리포트

| 언어 | 값 | 글자 수 비율 | 표시 폭 비율 | 판정 |
|---|---|---|---|---|
| en | `Weekly glucose report` | 21/9 = 2.33 (기준 1.2) | 21/16 = 1.31 | 초과 |
| ja | `週間グルコースレポート` | 11/9 = 1.22 (기준 0.9) | 22/16 = 1.38 | 초과 |

짧은 대안:

| 언어 | 대안 | 글자 수 비율 | 표시 폭 비율 |
|---|---|---|---|
| en | `Weekly report` | 1.44 | 0.81 |
| ja | `週間レポート` | 0.67 | 0.75 |

- en: 하드룰대로 `blood glucose` 가 아니라 `glucose` 단독. sentence case, 마침표 없음
- ja: 주간 리포트는 CGM 측정값을 모은 것이므로 `ja-house-rules.md` 2절 기준 `血糖値` 가 아니라 `グルコース` 쪽. 용어집 기준 리포트는 `レポート`
- en 은 혈당 단어를 넣으면 어떤 표현이든 1.2배를 넘는다. 타이틀은 폭 고정 자리라 엄격하게 봐야 하므로, 형제 키 `daily.title` 이 짧은 형태를 쓰고 있으면 짧은 대안으로 간다. 결정은 위 2번 확인 결과를 따른다

### 3) `cgm.alert.high.body` — 초안 (파일 미반영, 의학 검수 대기)

원문: `{0}님의 혈당이 {1}mg/dL로 목표 범위보다 높아요. 물을 한 잔 마시고 10분 정도 가볍게 걸어보세요.`

| 언어 | 초안 | 글자 수 비율 | 표시 폭 비율 |
|---|---|---|---|
| en | `{0}, your glucose is {1} mg/dL, above your target range. Try a glass of water and an easy 10-minute walk.` | 1.72 | 1.12 |
| ja | `{0}さんのグルコース値が{1}mg/dLで、目標範囲より高くなっています。水を1杯飲んで、10分ほど軽く歩いてみましょう。` | 1.02 | 1.17 |

짧은 대안: en `{0}, your glucose is {1} mg/dL, above your target range. Try water and a light 10-min walk.`

검수 포인트:
- 플레이스홀더 `{0}` `{1}` 개수·종류 원문과 동일
- en: `glucose` 단독, `high blood sugar` / `hyperglycemia` 대신 `above your target range`. 핵심(수치)을 앞에 둠. 알림 본문이라 문장형이고 마침표 사용
- ja: CGM 측정값이므로 `グルコース値`. `高血糖` 대신 `目標範囲より高く`. 원문의 "높아요"는 현재 상태라 `高くなっています`(상태). 행동 요청은 `〜てみましょう`. 두 문장 모두 60자 이하, 「〜が」 1회, 한글 잔존 없음, 같은 문말 반복 없음. `{0}さん` 은 가이드의 개인화 지칭 방식
- 안내문이라 길이는 느슨하게 적용. ja 1.02 는 기준(0.9)을 조금 넘지만 의미를 줄일 데가 없어 그대로 둔다
- 의학 검수에 물어볼 것: 수치가 목표 범위 위일 때 "물 한 잔 + 10분 걷기"를 일률적으로 권하는 것이 괜찮은지. 이건 번역 문제가 아니라 원문 문제라서 ko/en/ja 모두에 걸린다

## diff

### `cgm/src/main/resources/messages/message-cgm_en_US.properties`

원문과 같은 위치(앞뒤 키 사이)에 넣는다. 파일 끝에 붙이지 않는다.

```diff
 cgm.sensor.calibrate.button=...
+cgm.sensor.start.button=Start measuring
+# length:review  ratio 2.14 / width 1.15  shorter: Start
 ...
+cgm.report.weekly.title=Weekly glucose report
+# length:review  ratio 2.33 / width 1.31  shorter: Weekly report (daily.title 패턴에 맞출 것)
 cgm.report.daily.title=...
```

### `cgm/src/main/resources/messages/message-cgm_ja_JP.properties`

```diff
 cgm.sensor.calibrate.button=...
+cgm.sensor.start.button=測定を始める
 ...
+cgm.report.weekly.title=週間グルコースレポート
+# length:review  ratio 1.22 / width 1.38  shorter: 週間レポート (daily.title 패턴에 맞출 것)
 cgm.report.daily.title=...
```

주의:
- 대안은 반드시 `#` 주석으로만 둔다. 값 줄을 두 개 쓰면 두 번째 줄이 가짜 키가 된다
- 앞 줄이 역슬래시로 끝나는 여러 줄 값이면 그 바로 뒤에 넣지 않는다. 넣을 위치의 앞 줄 끝을 확인한다
- `cgm.alert.high.body` 는 두 파일 모두 넣지 않는다

### `MessageBundleLocaleParityTest` 의 `ALLOWED_MISMATCHES`

번역을 넣은 2개 키는 허용 목록에서 지운다. 남기면 죽은 항목으로 테스트가 실패한다. 남는 1개는 사유와 담당 카드를 적는다.

```diff
-    // message-cgm: en_US/ja_JP 미번역
-    entry("messages/message-cgm", "cgm.sensor.start.button"),
-    entry("messages/message-cgm", "cgm.report.weekly.title"),
-    entry("messages/message-cgm", "cgm.alert.high.body"),
+    // message-cgm: 혈당 높음 시 행동 권고 문구. 의학 검수 승인 대기 (담당 카드: <카드 번호 기입>)
+    // 초안은 PR 본문 참고. 승인 후 en_US/ja_JP 반영과 함께 이 항목 삭제
+    entry("messages/message-cgm", "cgm.alert.high.body"),
```

실제 항목 형식은 테스트 파일의 기존 형식을 따른다. 위는 형식을 가정한 것이다. 카드 번호는 내가 지어 넣지 않았으니 채워 달라.

## 검증 명령

```bash
python3 scripts/check_ratio.py --bundle message-cgm
python3 scripts/check_parity.py --bundle message-cgm
./gradlew :pasta-api:test --tests "*MessageBundleLocaleParityTest*"   # JDK 21
```

예상 결과 (시뮬레이션):
- `check_ratio.py`: `cgm.sensor.start.button` en, `cgm.report.weekly.title` en/ja 3건이 비율 초과로 출력된다. 위 표와 같은 수치이고, PR 본문에 기록할 대상이다
- `check_parity.py`: 파손 줄 0건. 키 차이는 `cgm.alert.high.body` (en_US, ja_JP) 1건만 남는다
- 정합성 테스트: 통과. 남은 차이 1건은 허용 목록에 있고, 허용 목록에 죽은 항목이 없다

## PR 본문에 넣을 내용

```
message-cgm en_US/ja_JP 누락 3건 중 2건 반영

반영
- cgm.sensor.start.button: Start measuring / 測定を始める
- cgm.report.weekly.title: Weekly glucose report / 週間グルコースレポート

길이 검토 필요 (화면 확인 요청)
- cgm.sensor.start.button en: 글자 수 2.14배, 표시 폭 1.15배. 대안 Start
- cgm.report.weekly.title en: 2.33배 / 1.31배. 대안 Weekly report
- cgm.report.weekly.title ja: 1.22배 / 1.38배. 대안 週間レポート

보류 (의학 검수 대기, ALLOWED_MISMATCHES 에 사유와 함께 유지)
- cgm.alert.high.body: 혈당 높음 시 물 섭취·걷기 권고 문구
  en 초안: {0}, your glucose is {1} mg/dL, above your target range. Try a glass of water and an easy 10-minute walk.
  ja 초안: {0}さんのグルコース値が{1}mg/dLで、目標範囲より高くなっています。水を1杯飲んで、10分ほど軽く歩いてみましょう。
```

## 남은 결정 사항

1. `cgm.alert.high.body` 의학 검수 담당자와 카드 번호
2. weekly.title 을 전체형으로 둘지 짧은 대안으로 갈지. 형제 키 daily.title 의 현재 값에 맞추는 것을 권한다
3. button en 을 `Start measuring` 으로 둘지 `Start` 로 줄일지. 화면에서 버튼 폭을 봐야 정할 수 있다
