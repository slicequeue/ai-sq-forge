# message-cgm en_US / ja_JP 누락 3건 반영

## 1. 번역 값

| 키 | ko (원문) | en_US | ja_JP |
|---|---|---|---|
| `cgm.sensor.start.button` | 측정 시작하기 | Start measuring | 測定を開始する |
| `cgm.report.weekly.title` | 주간 혈당 리포트 | Weekly Glucose Report | 週間血糖レポート |
| `cgm.alert.high.body` | {0}님의 혈당이 {1}mg/dL로 목표 범위보다 높아요. 물을 한 잔 마시고 10분 정도 가볍게 걸어보세요. | {0}, your glucose is {1} mg/dL, above your target range. Try drinking a glass of water and taking a light 10-minute walk. | {0}さんの血糖値が{1}mg/dLで、目標範囲より高めです。お水を一杯飲んで、10分ほど軽く歩いてみましょう。 |

번역 시 지킨 점:
- 플레이스홀더 `{0}`, `{1}` 는 개수·번호를 원문과 동일하게 유지했다.
- 인자가 있는 메시지는 `MessageFormat` 으로 처리되므로 작은따옴표(`'`)가 들어가면 이스케이프(`''`)가 필요하다. 영문에서 `you're`, `it's` 같은 축약형을 쓰지 않아 이 문제를 피했다.
- 웰니스 앱(비의료기기) 톤에 맞춰 진단·치료 표현은 쓰지 않고 원문과 같은 생활 권고 수준으로 옮겼다. 일본어는 「高めです」「〜てみましょう」로 단정·지시 강도를 원문 수준에 맞췄다.
- 일본어 호칭은 원문 "{0}님"에 대응해 `{0}さん` 으로 했다.

## 2. diff

키 순서는 ko 파일 기준으로, 이미 있는 앞뒤 키 사이에 넣는다.

### message-cgm_en_US.properties

```diff
 cgm.sensor.calibrate.button=...
+cgm.sensor.start.button=Start measuring
 ...
 cgm.report.daily.title=...
+cgm.report.weekly.title=Weekly Glucose Report
 ...
+cgm.alert.high.body={0}, your glucose is {1} mg/dL, above your target range. Try drinking a glass of water and taking a light 10-minute walk.
```

### message-cgm_ja_JP.properties

```diff
 cgm.sensor.calibrate.button=...
+cgm.sensor.start.button=測定を開始する
 ...
 cgm.report.daily.title=...
+cgm.report.weekly.title=週間血糖レポート
 ...
+cgm.alert.high.body={0}さんの血糖値が{1}mg/dLで、目標範囲より高めです。お水を一杯飲んで、10分ほど軽く歩いてみましょう。
```

> `cgm.alert.high.body` 의 정확한 삽입 위치는 ko 파일에서 이 키의 직전 키를 확인해 동일하게 맞춘다(발췌에 앞뒤 키가 없어 위치를 단정하지 않았다).

인코딩 확인: 일본어를 그대로 넣었으므로 `MessageSourceConfig` 에서 `setDefaultEncoding("UTF-8")` 이 설정돼 있어야 한다. 설정이 없다면 기존 ja_JP 파일이 `\uXXXX` 이스케이프 형식인지 확인하고 같은 형식으로 맞춘다(기존 파일 형식을 따른다).

### MessageBundleLocaleParityTest (ALLOWED_MISMATCHES)

```diff
 ALLOWED_MISMATCHES = Set.of(
     ...
-    "message-cgm:cgm.sensor.start.button",
-    "message-cgm:cgm.report.weekly.title",
-    "message-cgm:cgm.alert.high.body",
     ...
 );
```

(실제 항목 표기 형식은 테스트 코드의 기존 형식을 따른다.) 번역을 채운 뒤 허용 목록에 남겨두면 "죽은 항목"으로 테스트가 실패하므로 반드시 함께 제거해야 한다.

## 3. 확인할 것

- **번들 우선순위(가림) 확인**: `BASENAMES` 에서 앞쪽 번들이 이기므로, `message-cgm` 보다 앞선 번들(예: `message-hospital` 등)에 같은 키가 정의돼 있으면 이번 추가 값이 화면에 나오지 않는다.
  ```bash
  grep -rn -E '^(cgm\.sensor\.start\.button|cgm\.report\.weekly\.title|cgm\.alert\.high\.body)=' src/main/resources/messages/ --include='*.properties'
  ```
  결과가 `message-cgm*` 3개 파일에서만 나와야 한다.
- **폴백 은폐**: `useCodeAsDefaultMessage=true` 와 한국어 폴백 때문에 키가 빠져도 화면은 깨지지 않고 한국어로 나온다. 반영 후 en_US / ja_JP 로케일에서 실제로 번역 문구가 나오는지 확인한다.

## 4. 실행할 명령

```bash
# 패리티 테스트
./gradlew test --tests '*MessageBundleLocaleParityTest'

# (해당 모듈만이면 예: ./gradlew :<module>:test --tests '*MessageBundleLocaleParityTest')
```

기대 결과: 3개 키가 ko/en_US/ja_JP 에 모두 존재하고 허용 목록에서 제거됐으므로 PASS.

## 5. 보고

- `message-cgm_en_US.properties`, `message-cgm_ja_JP.properties` 에 3개 키 추가(ko 키 순서 유지).
- `MessageBundleLocaleParityTest.ALLOWED_MISMATCHES` 에서 해당 3개 항목 제거.
- 플레이스홀더 `{0}`, `{1}` 유지, MessageFormat 따옴표 이슈 없음.
- 확인 필요: 앞선 번들에서의 동일 키 가림 여부, ja_JP 파일 인코딩 형식, 일본어 문구의 현지 검수(특히 알림 문구 `cgm.alert.high.body` 는 사용자 노출 알림이므로 일본 담당자 검수 권장).
