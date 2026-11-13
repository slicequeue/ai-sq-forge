# message-cgm en_US / ja_JP 누락 3건 처리

## 결론 먼저

| 키 | 처리 | 이유 |
|---|---|---|
| `cgm.sensor.start.button` | **반영** (en/ja) | 일반 버튼 문구 |
| `cgm.report.weekly.title` | **반영** (en/ja), 길이 `length:review` 표기 | 일반 타이틀. 글자 수 비율 초과라 PR 본문에 기록 |
| `cgm.alert.high.body` | **반영 보류, 초안만** | 혈당 구간에 따른 행동 권고(물 섭취, 걷기)라서 스킬의 승인 게이트 "의학적 권고"에 해당. 의학 검수 후 반영 |

그래서 3건 중 **2건만 파일에 넣고**, `ALLOWED_MISMATCHES` 에서도 **그 2건만 지운다**. `cgm.alert.high.body` 는 허용 목록에 남기고 사유와 담당 카드를 적어 둔다. 3건을 한꺼번에 넣지 않은 이유는 아래 3절에 적었다.

---

## 1. 사전 확인 (실행할 명령)

저장소가 가상 환경이라 아래 결과는 시뮬레이션이며, 실제 반영 전에 돌려서 가정과 다른 것이 없는지 확인해야 한다.

```bash
# (1) 같은 키가 다른 번들에 있는지 — 앞쪽 번들이 이기므로 뒤쪽에 넣으면 무효
grep -rn -E "^(cgm\.sensor\.start\.button|cgm\.report\.weekly\.title|cgm\.alert\.high\.body)=" --include="*.properties" .

# (2) ko 파일의 키 위치 — 로케일 파일에도 같은 자리에 넣는다
grep -n -E "^cgm\.(sensor\.(calibrate|start)\.button|report\.(daily|weekly)\.title|alert\.high\.body)=" \
  cgm/src/main/resources/messages/message-cgm.properties

# (3) 형제 키의 기존 번역 — 타이틀 표기를 맞추기 위함
grep -n -E "^cgm\.(sensor\.calibrate\.button|report\.daily\.title)=" \
  cgm/src/main/resources/messages/message-cgm_en_US.properties \
  cgm/src/main/resources/messages/message-cgm_ja_JP.properties

# (4) 일본 서비스에 같은 키가 있는지 — 있으면 그 표기를 따른다 (ja-house-rules 1절)
JP=/Users/kakao/workplace-kakao/global/pasta-japan/server/pasta-japan-server
grep -n -E "^(cgm\.sensor\.start\.button|cgm\.report\.weekly\.title|cgm\.alert\.high\.body)=" \
  $JP/shared/src/main/resources/messages/message-shared_ja_JP.properties
```

| 확인 항목 | 확인된 것 / 가정한 것 |
|---|---|
| 3개 키가 `message-cgm` 기본 번들에만 있음 | **가정**. (1) 결과가 `message-cgm.properties` 3줄뿐이어야 한다. `message` / `message-hospital` 같은 앞쪽 번들에 같은 키가 있으면 거기에 넣어야 하므로 이 diff 는 무효 |
| 키 위치: `calibrate.button` 바로 다음이 `start.button`, `daily.title` 바로 다음이 `weekly.title` | **가정**. 요청에 "앞뒤 키는 있다"고만 되어 있다. (2) 결과로 실제 바로 앞 키를 확인하고 그 뒤에 넣는다 |
| `cgm.report.daily.title` 의 en/ja 값 | **미확인**. weekly 표기를 여기에 맞춰야 한다 (2-2 참고) |
| 일본 서비스 동일 키 | **미확인**. 있으면 ja 값은 그쪽 표기를 우선한다 |
| 대상 파일 위치 `cgm/src/main/resources/messages/` | `references/bundles.md` 기준 (cgm 모듈 소유) |

---

## 2. 번역 (반영 2건)

### 2-1. `cgm.sensor.start.button` = 측정 시작하기

노출 위치: 키에 `button` 이 들어가므로 폭이 고정된 자리로 보고 엄격하게 적용했다.

| 로케일 | 값 | 글자 수 비율 (한도) | 표시 폭 비율 | 판정 |
|---|---|---|---|---|
| en | `Start` | 0.71 (1.2) | 0.38 | 통과 |
| ja | `測定を始める` | 0.86 (0.9) | 0.92 | 통과 |

- en: `Start measuring` 이 뜻은 더 정확하지만 2.14배라 버튼 자리에는 들어가지 않는다. 센서 시작 화면의 버튼이라 `Start` 만으로도 뜻이 통하고, 가이드 규칙(동사로 시작, sentence case, 마침표 없음)도 지킨다. 화면 폭이 넉넉하다는 것이 확인되면 `Start measuring` 으로 바꿔도 된다.
- ja: 가이드상 새 CTA 버튼은 동사형이 기본값이다. `測定を開始する`(7자, 1.0배)는 한도를 넘어서 `始める` 를 썼다. 마침표 없음.
- 형제 키 `cgm.sensor.calibrate.button` 의 en/ja 형태(동사형인지 명사형인지)를 (3)으로 확인해 맞춘다. 형제 키가 `測定開始` 같은 명사형이면 그 형태로 통일한다.

### 2-2. `cgm.report.weekly.title` = 주간 혈당 리포트

| 로케일 | 값 | 글자 수 비율 (한도) | 표시 폭 비율 | 판정 |
|---|---|---|---|---|
| en | `Weekly glucose report` | **2.33** (1.2) | 1.31 | 초과, `length:review` |
| en 짧은 대안 | `Weekly report` | 1.44 | 0.81 | 초과이나 폭은 원문 이하 |
| ja | `週間グルコースレポート` | **1.22** (0.9) | 1.38 | 초과, `length:review` |
| ja 짧은 대안 | `週間レポート` | 0.67 | 0.75 | 통과 |

- en 하드룰: `blood glucose` / `blood sugar` 금지, `glucose` 만 쓴다.
- ja 혈당 표기: CGM 측정값을 모은 리포트라서 `ja-house-rules.md` 2절 기준으로 `血糖値` 가 아니라 `グルコース` 를 쓴다. 용어집에 따라 리포트는 `レポート`.
- en 은 **글자 수(2.33)와 표시 폭(1.31)이 크게 어긋난다.** 스킬 기준으로 이런 경우는 수치로 판단하지 말고 화면에서 직접 봐야 한다. 한글이 전각이라 폭으로는 1.3배 수준이다.
- 짧은 의미를 그대로 담는 후보 중 한도 안에 들어가는 영어 표현은 없다. 그래서 diff 에는 뜻을 살린 값을 넣고 PR 본문에 짧은 대안과 함께 기록한다.
- **daily 형제 키와 반드시 같은 형태로 맞춘다.** (3) 결과 `cgm.report.daily.title` 이 `Daily report` / `日間レポート` 형태면 weekly 도 짧은 대안(`Weekly report` / `週間レポート`)으로 바꾼다. `Daily glucose report` 형태면 아래 diff 그대로 둔다.

### 2-3. 반영 diff

```diff
--- a/cgm/src/main/resources/messages/message-cgm_en_US.properties
+++ b/cgm/src/main/resources/messages/message-cgm_en_US.properties
@@
 cgm.sensor.calibrate.button=(기존 값 유지)
+cgm.sensor.start.button=Start
@@
 cgm.report.daily.title=(기존 값 유지)
+cgm.report.weekly.title=Weekly glucose report
```

```diff
--- a/cgm/src/main/resources/messages/message-cgm_ja_JP.properties
+++ b/cgm/src/main/resources/messages/message-cgm_ja_JP.properties
@@
 cgm.sensor.calibrate.button=(기존 값 유지)
+cgm.sensor.start.button=測定を始める
@@
 cgm.report.daily.title=(기존 값 유지)
+cgm.report.weekly.title=週間グルコースレポート
```

반영할 때 주의할 점:

- 한 줄짜리 값이라 줄 끝에 역슬래시를 붙이지 않는다. **바로 앞 줄(`calibrate.button`, `daily.title`)이 역슬래시로 끝나지 않는지도 확인한다.** 역슬래시로 끝나면 새 키가 앞 값에 흡수되어 사라진다.
- 파일 끝에 붙이지 않고 ko 파일과 같은 위치에 넣는다.
- 후보를 여러 줄로 나열하지 않는다. 짧은 대안은 PR 본문에만 적는다.

### 2-4. ja 출력 전 자기 검수 (2건)

| # | 항목 | `測定を始める` | `週間グルコースレポート` |
|---|---|---|---|
| 1 | 60자 초과 | 없음 | 없음 |
| 2 | 접속 2개 이상 | 없음 | 없음 |
| 3 | 한자어 3연속 명사구 | 없음 | 없음 (週間 + 가타카나) |
| 3b | 한자어 반복 / の 3연속 | 없음 | 없음 |
| 4~5 | することができます / について / という | 없음 | 없음 |
| 6~8 | 문말 반복 / ね | 해당 없음 (단문) | 해당 없음 |
| 9 | は/が 복사 | 해당 없음 | 해당 없음 |
| 10 | 한글 잔존 | 없음 | 없음 |
| 11 | 0.9배 초과 | 0.86 통과 | **1.22 초과** → 짧은 대안 제시, `length:review` |
| 12 | 번역문 티 | 없음 | 없음 |

---

## 3. 반영 보류: `cgm.alert.high.body`

```
{0}님의 혈당이 {1}mg/dL로 목표 범위보다 높아요. 물을 한 잔 마시고 10분 정도 가볍게 걸어보세요.
```

### 보류 이유

혈당이 목표 범위보다 높을 때 **구체적인 행동(물 섭취, 10분 걷기)을 권고하는 문구**다. 스킬의 승인 게이트 표에서 "의학적 권고"(예: 혈당 구간별 운동 권고)에 해당하므로 초안만 만들고 파일에는 넣지 않는다. 의료기기가 아닌 웰니스 앱이 혈당 수치에 따라 행동을 권고하는 문구라서, 잘못된 번역이 배포되면 번역이 늦어지는 것보다 피해가 크다.

이 키는 이미 en/ja 요청에서 한국어로 폴백되고 있다(`useCodeAsDefaultMessage=true`). 승인을 받을 때까지 현재 상태가 유지되는 것이며, 새로 생기는 문제는 아니다.

### 한국어 원문 1차 검수 (제안만, 원문은 바꾸지 않음)

- 진단성 표현: "목표 범위보다 높아요" 로 이미 비교형 완곡 표현이다. 가이드 스코프 규칙에 맞다.
- 해요체 일관, 수치와 행동 명시: 가이드 "건강 정보는 명확성 우선"에 맞다.
- **의학 검수에 함께 물어볼 것:** 수치에 상관없이 일괄로 "물 한 잔 + 10분 걷기"를 권하는 것이 맞는지, 그리고 매우 높은 구간에서도 같은 권고를 해도 되는지. 출처나 면책 문구가 필요한지 (가이드 `## ko` "건강/일반화 주장에는 출처 근거 명시").

### 번역 초안 (PR 본문, 카드 코멘트용. 파일에 넣지 않음)

| 로케일 | 초안 | 글자 수 비율 | 표시 폭 비율 |
|---|---|---|---|
| en | `{0}, your glucose is {1} mg/dL - above your target range. Try a glass of water and a light 10-minute walk.` | 1.74 | 1.13 |
| ja | `{0}さん、グルコース値が{1}mg/dLで目標範囲より高めです。水を1杯飲んで、10分ほど軽く歩いてみましょう。` | 0.93 | 1.06 |

- 안내문(알림 본문)이라 길이 기준은 느슨하게 적용했다. en 1.74배는 영어 본문으로는 통상 범위이고, 핵심(수치와 범위 초과)을 앞에 두었다.
- 플레이스홀더 `{0}` 와 `{1}` 를 원문과 같이 각 1개씩 유지했다.
- en: `glucose` 하드룰, 인사말로 시작하지 않음, 2인칭, `hyperglycemia` 같은 진단 용어를 쓰지 않음. 하이픈은 띄어 쓴 ` - `.
- ja: CGM 측정값을 말하므로 `グルコース値`. `高血糖` 대신 `目標範囲より高め`. 반각 숫자, `{1}mg/dL` 는 붙여 씀. 제안은 `〜てみましょう` 보조동사를 살렸다. 문장 2개, 각 60자 이하, の 반복 없음.

### `ALLOWED_MISMATCHES` 유지 + 사유 기재

이 키는 허용 목록에서 지우지 않고, 사유와 담당 카드를 주석으로 붙인다(diff 는 4절). 카드 번호는 의학 검수 요청을 올린 뒤 채운다.

---

## 4. `MessageBundleLocaleParityTest` 허용 목록 정리

번역을 넣은 키는 허용 목록에서 **반드시** 지운다. 남아 있으면 죽은 항목으로 테스트가 실패한다.

```diff
 // MessageBundleLocaleParityTest.ALLOWED_MISMATCHES (기존 항목 표기 형식을 그대로 따른다)
-    "messages/message-cgm:cgm.sensor.start.button",
-    "messages/message-cgm:cgm.report.weekly.title",
+    // 의학 검수 대기: 고혈당 구간 행동 권고(수분 섭취·걷기) 문구. 승인 후 en/ja 반영. 담당 카드: <카드 번호>
     "messages/message-cgm:cgm.alert.high.body",
```

항목의 문자열 형식(로케일별로 나뉘는지 등)은 실제 테스트 코드를 보고 맞춘다. en_US 와 ja_JP 가 별도 항목이면 2건 × 2로케일 = 4줄을 지운다.

---

## 5. 검사와 테스트

```bash
python3 scripts/check_ratio.py --bundle message-cgm
python3 scripts/check_parity.py --bundle message-cgm
./gradlew :pasta-api:test --tests "*MessageBundleLocaleParityTest*"   # JDK 21
```

예상 결과 (시뮬레이션):

| 검사 | 예상 |
|---|---|
| `check_ratio.py` | `cgm.report.weekly.title` en 2.33 / ja 1.22 초과로 출력. `start.button` 은 통과 |
| `check_parity.py` | 파손 줄 0. `cgm.alert.high.body` 1건이 en_US / ja_JP 에서 누락으로 보고됨 (의도한 결과이며 허용 목록에 등록됨) |
| `MessageBundleLocaleParityTest` | 통과. 2건은 키 집합이 일치하고 허용 목록에서 빠짐, 1건은 허용 목록에 살아 있는 항목 |

테스트가 "죽은 허용 항목"으로 실패하면 4절의 삭제가 빠진 것이다. "허용되지 않은 불일치"로 실패하면 diff 의 앞 줄이 역슬래시로 끝나서 새 키가 흡수된 것이다.

---

## 6. PR 본문에 남길 내용

```markdown
## message-cgm 로케일 누락 보완 (3건 중 2건)

### 반영
- cgm.sensor.start.button: en `Start` / ja `測定を始める`
- cgm.report.weekly.title: en `Weekly glucose report` / ja `週間グルコースレポート`
- ALLOWED_MISMATCHES 에서 위 2건 제거

### 길이 확인 필요 (length:review)
- cgm.report.weekly.title
  - en 2.33배 (표시 폭 1.31배). 짧은 대안 `Weekly report`
  - ja 1.22배 (표시 폭 1.38배). 짧은 대안 `週間レポート`
  - 화면에서 잘리는지 확인 부탁드립니다. daily.title 과 표기를 맞췄습니다.

### 보류 (의학 검수 대기)
- cgm.alert.high.body: 고혈당 구간 행동 권고 문구라 승인 후 반영. 허용 목록에 사유와 카드를 적어 남겨 둠
  - en 초안: {0}, your glucose is {1} mg/dL - above your target range. Try a glass of water and a light 10-minute walk.
  - ja 초안: {0}さん、グルコース値が{1}mg/dLで目標範囲より高めです。水を1杯飲んで、10分ほど軽く歩いてみましょう。
  - 검수 요청: 수치와 무관한 일괄 권고가 적절한지, 출처나 면책 문구가 필요한지
```

---

## 확인된 것 vs 가정한 것

| 구분 | 내용 |
|---|---|
| 확인됨 (요청 기준) | ko 원문 3건, en/ja 파일에 3키 없음, 앞뒤 형제 키 존재, 허용 목록에 3건 등록, 폴백 동작과 테스트 동작 |
| 확인됨 (계산) | 위 표의 글자 수와 표시 폭 비율 (`check_ratio.py` 와 같은 방식으로 계산) |
| 가정 | 다른 번들에 같은 키 없음, 삽입 위치(형제 키 바로 뒤), 허용 목록 표기 형식, daily.title 표기, 일본 서비스에 같은 키 없음 |
| 재평가 트리거 | 1절 (1)에서 다른 번들 히트 → 반영 번들 변경. (3)에서 daily.title 이 짧은 형태 → weekly 를 짧은 대안으로 교체. (4)에서 일본 서비스 히트 → ja 값을 그쪽 표기로 교체 |
