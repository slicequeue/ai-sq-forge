# message-cgm en_US / ja_JP 누락 3건 처리안

## 결론

3건 중 **2건만 반영하고, 1건은 초안만 남긴다.**

| 키 | 처리 | 이유 |
|---|---|---|
| `cgm.sensor.start.button` | 반영 | 일반 CTA 버튼 |
| `cgm.report.weekly.title` | 반영 (길이 리뷰 표시) | 섹션 타이틀. 글자 수 비율과 표시 폭이 서로 다른 결론을 내서 화면 확인이 필요하다 |
| `cgm.alert.high.body` | **초안만, 파일 미반영** | 혈당 구간(목표 범위 초과)에 따라 수분 섭취와 걷기를 권하는 문구다. 스킬의 승인 게이트 중 "의학적 권고"(예: 임신부 혈당 구간별 운동 권고)에 해당해 의학 검수가 필요하다 |

그래서 `ALLOWED_MISMATCHES` 에서는 **button / title 의 en_US·ja_JP 항목 4개만 지우고**, `cgm.alert.high.body` 항목 2개는 사유와 담당 카드를 붙여 그대로 둔다. 3개를 다 지우면 alert 키가 누락 상태로 남아 테스트가 실패하고, 반대로 지우지 않은 채 번역만 넣으면 죽은 허용 항목이 남아 역시 실패한다.

---

## 1. 확인된 사실과 가정

**확인된 사실 (요청에 주어진 것)**
- 기본 번들에는 3개 키가 이 순서로 있다. en_US / ja_JP 에는 없고, 인접 키 `cgm.sensor.calibrate.button`, `cgm.report.daily.title` 은 있다
- `ALLOWED_MISMATCHES` 에 3개 키가 등록되어 있다
- 웰니스 앱(의료기기 아님), 한국·일본 출시

**가정 (반영 전에 아래 2절 명령으로 확인 필요)**
- 3개 키가 앞쪽 번들(`message`, `message-ai`, `message-user`)에 중복 정의되어 있지 않다. `message-cgm` 은 BASENAMES 4번째라서 앞의 세 번들에 같은 키가 있으면 여기 넣은 번역은 쓰이지 않는다
- `cgm.alert.high.body` 는 푸시 또는 인앱 알림 본문이다 (키 이름 기준 추정)
- 인접 키 `cgm.report.daily.title` 의 en/ja 값 형태를 아직 보지 못했다. weekly 타이틀은 그 형태에 맞춰야 한다
- `ALLOWED_MISMATCHES` 의 실제 표기 형식을 보지 못했다. 아래 diff 는 형식을 예시로 둔 것이다

---

## 2. 반영 전에 실행할 확인 명령

```bash
# (1) 중복 정의 함정: 다른 번들에 같은 키가 있는지
grep -rn -E "^(cgm\.sensor\.start\.button|cgm\.report\.weekly\.title|cgm\.alert\.high\.body)=" --include="*.properties" .

# (2) 형제 키의 기존 번역 형태 (타이틀 패턴·버튼 종결형 맞추기)
grep -n -E "^cgm\.(sensor\.calibrate\.button|report\.daily\.title)=" \
  cgm/src/main/resources/messages/message-cgm*.properties

# (3) 일본 서비스에 같은 키가 있는지 (있으면 그 표기를 우선 따른다)
JP=/Users/kakao/workplace-kakao/global/pasta-japan/server/pasta-japan-server
grep -n -E "^(cgm\.sensor\.start\.button|cgm\.report\.weekly\.title|cgm\.alert\.high\.body)=" \
  $JP/shared/src/main/resources/messages/message-shared_ja_JP.properties

# (4) 코드 호출부로 노출 위치 확인 (알림 타이틀/본문 자리인지)
grep -rn "cgm.alert.high.body\|cgm.report.weekly.title\|cgm.sensor.start.button" --include="*.java" .
```

판정 기준:
- (1)에서 `message-cgm` 외 번들, 특히 앞쪽 번들에 같은 키가 나오면 **여기서 멈추고** 어느 번들이 이기는지부터 정리한다
- (2)에서 `cgm.report.daily.title` 이 `Daily glucose report` 처럼 glucose 를 넣었다면 weekly 도 같은 패턴으로 맞춘다 (아래 3절의 대안 값)
- (3)에서 일본 서비스 값이 있으면 그 표기를 쓰고, 아래 제안값과 다르면 차이를 PR 에 적는다

---

## 3. 번역값

### 3-1. `cgm.sensor.start.button=측정 시작하기` — 반영

원문 7자, 표시 폭 13. 기준은 en 8자 이하(1.2배), ja 6자 이하(0.9배).

| 로케일 | 값 | 글자 수 (비율) | 표시 폭 (비율) | 판정 |
|---|---|---|---|---|
| en_US | `Start` | 5 (0.71) | 5 (0.38) | 통과 |
| ja_JP | `測定を始める` | 6 (0.86) | 12 (0.92) | 통과 |

- en: 가이드 버튼 규칙(동사로 시작, 수식어 생략, sentence case, 마침표 없음)을 따랐다. 센서 시작 화면 안의 버튼이라 `Start` 만으로 의미가 선다. 더 구체적인 `Start reading`(13자, 1.86배)은 기준을 넘으므로 쓰지 않는다
- ja: 새로 만드는 CTA 는 동사형이 기본값이다. `測定を開始する`(7자, 1.0배)는 기준 초과라 `始める` 를 썼다. 버튼이므로 마침표 없음
- 2절 (2)에서 `cgm.sensor.calibrate.button` 의 ja 가 명사형(`補正` 등)이면, 같은 화면 버튼끼리 형태를 맞출지 PR 에서 확인을 받는다

### 3-2. `cgm.report.weekly.title=주간 혈당 리포트` — 반영, 길이 리뷰 표시

원문 9자, 표시 폭 16. 기준은 en 10자 이하, ja 8자 이하. 키에 `title` 이 있어 너비가 고정된 자리로 보고 엄격하게 본다.

| 로케일 | 값 | 글자 수 (비율) | 표시 폭 (비율) | 판정 |
|---|---|---|---|---|
| en_US (제안) | `Weekly report` | 13 (1.44) | 13 (0.81) | 글자 수 초과, 표시 폭 통과. **두 수치가 어긋나므로 화면 확인 필요** |
| en_US (대안) | `Weekly glucose report` | 21 (2.33) | 21 (1.31) | 둘 다 초과 |
| ja_JP (제안) | `週間レポート` | 6 (0.67) | 12 (0.75) | 통과 |
| ja_JP (대안) | `週間グルコースレポート` | 11 (1.22) | 22 (1.38) | 둘 다 초과 |

- en: 하드룰상 `blood glucose` 는 쓰지 않는다. 10자 안에 들어가는 자연스러운 영어 타이틀이 없다. 한글은 글자 하나가 넓어서 짧은 원문은 비율이 쉽게 튄다. 그래서 표시 폭 기준으로 원문보다 좁은 `Weekly report` 를 제안하고 PR 에 길이 리뷰 대상으로 적는다
- ja: CGM 측정값을 모은 리포트이므로, 혈당을 넣는다면 `血糖` 이 아니라 `グルコース` 를 쓴다 (ja-house-rules 2절. 측정값·그래프는 グルコース値). 다만 그러면 11자로 기준을 넘는다. 리포트 화면 안의 타이틀이라 `週間レポート` 로도 뜻이 선다. `週間血糖レポート`(8자)는 길이는 통과하지만 표기 구분을 어기므로 쓰지 않는다
- **형제 키에 맞춘다.** 2절 (2)에서 `cgm.report.daily.title` 이 `Daily report` / `日間レポート` 형태면 제안값을 쓰고, `Daily glucose report` / `デイリーグルコースレポート` 처럼 혈당을 넣은 형태면 대안값으로 바꾼다. 같은 화면의 daily 와 weekly 타이틀이 서로 다른 패턴을 쓰면 안 된다

### 3-3. `cgm.alert.high.body` — 초안만 작성, 파일에 넣지 않음

원문: `{0}님의 혈당이 {1}mg/dL로 목표 범위보다 높아요. 물을 한 잔 마시고 10분 정도 가볍게 걸어보세요.` (61자, 표시 폭 94)

**넣지 않는 이유.** 앞 문장은 수치 안내지만, 뒷 문장은 혈당이 목표 범위를 넘었을 때 할 행동(수분 섭취, 10분 걷기)을 권한다. 스킬이 정한 "의학적 권고" 유형이라 의학 검수를 거친 뒤 반영한다. 일본 출시 문구라 일본 쪽 규제 표현 검토도 같은 단계에서 받는다.

PR 본문 또는 담당 카드에 남길 초안:

| 로케일 | 초안 | 글자 수 (비율) | 표시 폭 (비율) |
|---|---|---|---|
| en_US | `{0}, your glucose is {1}mg/dL, above your target range. Try a glass of water and a light 10-minute walk.` | 104 (1.70) | 104 (1.11) |
| ja_JP | `{0}さんのグルコース値が{1}mg/dLで、目標範囲より高くなっています。水を1杯飲んで、10分ほど軽く歩いてみましょう。` | 62 (1.02) | 110 (1.17) |
| ja_JP 단축안 | `{0}さん、グルコース値が{1}mg/dLで目標範囲より高いです。水を1杯飲み、10分ほど歩いてみましょう。` | 54 (0.89) | 94 (1.00) |

초안 작성 근거:
- 플레이스홀더 `{0}`, `{1}` 둘 다 유지했다. 개수와 종류가 원문과 같다
- en: 하드룰대로 `glucose` 단독으로 썼다. `high glucose` 나 `hyperglycemia` 같은 진단성 표현을 피하고 `above your target range` 로 비교형을 썼다. 알림이므로 인사말 없이 수치부터 꺼냈다. 안내문은 길이를 느슨하게 보는 자리다. 다만 1.7배라 짧게 만들려면 `a glass of` 를 빼는 정도가 한계다. `10-minute` 는 건강 정보의 명확성 규칙상 빼지 않는다
- ja: CGM 측정값이므로 `血糖値` 가 아니라 `グルコース値` 를 썼다. `高血糖` 대신 `目標範囲より高い`, 행동 제안은 `〜てみましょう` 로 했다. 숫자는 반각, `{1}mg/dL` 는 붙여 썼다
- ja 12항목 자기 검수 결과: 두 문장 모두 60자 미만이다. 「が/し/ので/ため」 연쇄, 한자어 3연속, 「の」 3연속, `することができます` 는 없다. 문말형이 `〜ています` / `〜ましょう` 로 서로 다르고, 「ね」 와 한글 잔존도 없다. 다만 본안은 0.9배를 넘어서 단축안을 같이 붙였다. 단축안은 `軽く`(가볍게)가 빠지므로 의학 검수 때 그 뉘앙스를 유지할지 함께 정한다

**한국어 원문 검수 메모 (제안만, 원문은 바꾸지 않음)**
- 해요체, 진단성 표현 회피(`목표 범위보다 높아요`), 수치 명시 모두 가이드에 맞는다
- `물을 한 잔 마시고 10분 정도 가볍게 걸어보세요` 는 근거를 밝히지 않은 건강 행동 권고다. 가이드의 "건강/일반화 주장에는 출처 근거 명시" 항목에 해당하므로, 의학 검수 때 면책 문구나 근거가 필요한지 같이 확인을 요청한다
- `{0}님의` 는 이름 호칭이라 2인칭 직접 지칭 금지 규칙에는 걸리지 않는다

---

## 4. 반영 diff

키는 원문 순서대로 인접 키 옆에 넣는다. 파일 끝에 붙이지 않는다. 각 줄은 한 줄짜리 값이라 끝에 역슬래시가 없다. 바로 앞 줄(인접 키)도 역슬래시로 끝나지 않는지 같이 확인한다.

`cgm/src/main/resources/messages/message-cgm_en_US.properties`
```diff
 cgm.sensor.calibrate.button=...
+cgm.sensor.start.button=Start
 ...
 cgm.report.daily.title=...
+cgm.report.weekly.title=Weekly report
```

`cgm/src/main/resources/messages/message-cgm_ja_JP.properties`
```diff
 cgm.sensor.calibrate.button=...
+cgm.sensor.start.button=測定を始める
 ...
 cgm.report.daily.title=...
+cgm.report.weekly.title=週間レポート
```

(ko 번들에서 `start.button` 이 `calibrate.button` 앞에 있으면 그 순서를 따른다. `weekly.title` 과 `daily.title` 의 순서도 같다.)

`MessageBundleLocaleParityTest` 의 `ALLOWED_MISMATCHES` (실제 표기 형식에 맞춰 적용)
```diff
-    "messages/message-cgm_en_US::cgm.sensor.start.button",
-    "messages/message-cgm_ja_JP::cgm.sensor.start.button",
-    "messages/message-cgm_en_US::cgm.report.weekly.title",
-    "messages/message-cgm_ja_JP::cgm.report.weekly.title",
+    // 의학 검수 대기: 혈당 목표 범위 초과 시 행동 권고 문구. 초안은 PR #<번호> 본문. 담당 카드 <카드번호>
     "messages/message-cgm_en_US::cgm.alert.high.body",
     "messages/message-cgm_ja_JP::cgm.alert.high.body",
```

`<PR 번호>` 와 `<카드번호>` 는 실제 값으로 채운다. 담당 카드가 아직 없으면 의학 검수 요청 카드를 먼저 만든다.

---

## 5. 검사 명령과 예상 결과 (시뮬레이션)

```bash
python3 scripts/check_ratio.py --bundle message-cgm
python3 scripts/check_parity.py --bundle message-cgm
./gradlew :pasta-api:test --tests "*MessageBundleLocaleParityTest*"   # JDK 21
```

| 검사 | 예상 결과 |
|---|---|
| `check_ratio` | en `cgm.report.weekly.title` 1.44배 초과 1건. 표시 폭 0.81로 수치가 어긋나며, 3-2 판단대로 PR 에 기록한다. 나머지 3건은 통과 |
| `check_parity` | `[누락] message-cgm_en_US :: cgm.alert.high.body`, `[누락] message-cgm_ja_JP :: cgm.alert.high.body` 2건이 나와 exit 1. 이 스크립트에는 허용 목록이 없어서 의도한 결과다. 이 2건 외에 `[파손]` 이나 `[고아]` 가 나오면 diff 를 잘못 넣은 것이다 |
| `MessageBundleLocaleParityTest` | 통과. alert 2건은 허용 목록에 있고, 지운 4건은 실제로 번역이 들어가 죽은 항목이 없다 |

---

## 6. PR 본문에 남길 내용

- 반영: `cgm.sensor.start.button`, `cgm.report.weekly.title` (en_US, ja_JP), `ALLOWED_MISMATCHES` 4건 제거
- **길이 리뷰 필요**: en `cgm.report.weekly.title=Weekly report` 는 글자 수 1.44배로 기준(1.2배)을 넘지만 표시 폭은 0.81배다. 화면에서 잘리는지 확인 요청. 대안은 `Weekly glucose report`(daily 타이틀이 그 형태일 때)
- **의학 검수 대기**: `cgm.alert.high.body` en/ja 초안(3-3 표)과 한국어 원문 검수 메모. 승인되면 값을 넣고 `ALLOWED_MISMATCHES` 의 해당 2건을 지운다

## 7. 남은 작업

1. 2절 확인 명령을 실행하고, 결과에 따라 weekly 타이틀을 제안값으로 둘지 대안값으로 바꿀지 정한다
2. 4절 diff 를 반영하고 5절 검사 3종을 돌린다
3. `cgm.alert.high.body` 를 의학 검수에 요청한다. 승인되면 별도 커밋으로 반영하고 허용 항목을 지운다
