# message-pghd 신규 문구 ja_JP 번역 및 반영안

요청하신 4개 키를 일본어로 옮기고 `message-pghd_ja_JP.properties`에 넣을 diff를 정리했습니다. 4개 중 2개는 의료·법무 성격의 문구라서 **그대로 바로 반영하지 말고 확인을 먼저 받아야 합니다**. 아래 "반영 전 확인 필요"를 먼저 봐 주세요.

---

## 1. 번역안

| 키 | 한국어 원문 | ja_JP 번역 | 비고 |
|---|---|---|---|
| `food.recommend.tea.title` | 오늘의 추천 차: 쌍화차 | 今日のおすすめのお茶：双和茶（サンファチャ） | 일본에서는 잘 알려지지 않은 음료라 읽기를 함께 표기 |
| `food.recommend.side.body` | 깍두기와 신선로를 곁들이면 더 든든해요. | カクテキと神仙炉（シンソンロ）を添えると、さらに満足感がアップします。 | カクテキ는 일본에서도 통용됨. 신선로는 생소해서 읽기를 표기 |
| `exercise.pregnancy.high.body` | 임신 중 혈당이 140mg/dL 이상이면 식후 15분 걷기를 권장해요. 통증이 있으면 즉시 중단하세요. | (보류, 아래 참고) | 의료 권고 표현 |
| `privacy.thirdparty.notice` | 수집한 혈당 기록은 제휴 병원에 제공될 수 있어요. | (보류, 아래 참고) | 개인정보 제3자 제공 고지 |

참고용 직역 (반영 보류 대상):

- `exercise.pregnancy.high.body`: 妊娠中に血糖値が140mg/dL以上の場合は、食後15分のウォーキングをおすすめします。痛みがある場合はすぐに中止してください。
- `privacy.thirdparty.notice`: 収集した血糖記録は、提携医療機関に提供される場合があります。

### 확인된 것과 가정한 것

- 확인: 키 4개와 한국어 원문, 번들 구조(ko / en_US / ja_JP), parity 테스트 규칙, 앱이 의료기기가 아니라는 점
- 가정: 4개 키가 아직 `message-pghd`의 어느 로케일에도 없는 신규 키이다. 앞쪽 번들(`message-hospital` 등)에 같은 키가 없다. en_US 번역은 이번 요청에 포함되지 않았다.

---

## 2. 반영 전 확인 필요 (차단 이슈)

### 2-1. `exercise.pregnancy.high.body`: 의료 권고 표현

- 이 앱은 **의료기기가 아닌 웰니스 앱**입니다. 그런데 "임신 중 혈당 140mg/dL 이상 → 식후 15분 걷기 권장"은 특정 수치를 기준으로 한 **진단·치료성 권고**로 읽힙니다.
- 일본에서는 의약품의료기기법(薬機法)상 프로그램 의료기기 판단 기준과 광고 규제가 있어서, 수치 기준 + 행동 지시 조합은 리스크가 높습니다. 임신성 당뇨 관리는 보통 의사 지도를 받는 영역이기도 합니다.
- 권고: 기획·법무(또는 의료 자문)에서 문구를 확정한 뒤 번역합니다. 순화한 예시는 다음과 같습니다(확정안 아님).
  - ko: 임신 중에는 혈당 관리 방법을 담당 의사와 꼭 상의하세요. 가벼운 산책이 도움이 될 수 있어요.
  - ja: 妊娠中の血糖管理については、必ず主治医にご相談ください。軽いウォーキングが役立つこともあります。

### 2-2. `privacy.thirdparty.notice`: 개인정보 제3자 제공 고지

- 혈당 기록은 건강정보입니다. 한국 개인정보보호법상 민감정보이고, 일본 個人情報保護法상 要配慮個人情報에 해당할 가능성이 높습니다. 제3자 제공에는 **원칙적으로 사전 동의**가 필요합니다.
- "제공될 수 있어요"라는 고지형 문장만으로는 동의를 대체할 수 없습니다. 일본어 문구도 법무 검토를 받은 정식 문언이어야 합니다(제공처, 목적, 항목 명시 여부 등).
- 권고: 법무가 확정한 일본어 원문을 받아서 반영합니다. 제가 번역한 문장을 그대로 넣지 않는 편이 안전합니다.

---

## 3. 반영 diff

### 지금 반영해도 되는 2개 키

`message-pghd_ja_JP.properties`:

```diff
+food.recommend.tea.title=今日のおすすめのお茶：双和茶（サンファチャ）
+food.recommend.side.body=カクテキと神仙炉（シンソンロ）を添えると、さらに満足感がアップします。
```

`message-pghd.properties`(ko, 아직 없다면):

```diff
+food.recommend.tea.title=오늘의 추천 차: 쌍화차
+food.recommend.side.body=깍두기와 신선로를 곁들이면 더 든든해요.
```

참고: properties 파일 인코딩이 ISO-8859-1 기준(`\uXXXX` 이스케이프)이면 위 일본어를 이스케이프해서 넣어야 합니다. 기존 `_ja_JP` 파일이 UTF-8 원문을 쓰는지 이스케이프를 쓰는지 확인한 뒤 같은 방식을 따르세요(`MessageSourceConfig`의 `defaultEncoding` 설정도 함께 확인).

### en_US 처리 (parity 테스트)

`MessageBundleLocaleParityTest`는 ko / en_US / ja_JP 키 집합이 같아야 통과합니다. ko·ja_JP에만 키를 넣으면 en_US가 비어서 테스트가 실패합니다. 방법은 둘 중 하나입니다.

1. en_US 번역도 같이 넣는다 (권장):
   ```diff
   +food.recommend.tea.title=Today's Tea Pick: Ssanghwa-cha
   +food.recommend.side.body=Add kkakdugi (radish kimchi) and sinseollo for a more satisfying meal.
   ```
2. en_US를 이번에 넣지 않는다면 `ALLOWED_MISMATCHES`에 해당 키를 등록한다. 이 경우 나중에 en_US를 번역하면 **허용 목록에서 반드시 지워야** 합니다. 죽은 항목이 남으면 테스트가 실패합니다.

보류한 2개 키(2-1, 2-2)는 ko에도 아직 넣지 않거나, ko만 먼저 넣는다면 ja_JP/en_US 누락분을 `ALLOWED_MISMATCHES`에 임시 등록해야 합니다. `useCodeAsDefaultMessage=true` 때문에 ja_JP 키가 없으면 일본 사용자에게 **한국어 문구가 조용히 노출**됩니다. 그러니 일본 출시 빌드 전에 반드시 채워야 합니다.

---

## 4. 반영 후 확인 명령

```bash
# 1) 앞쪽 번들에 같은 키가 있어 덮어써지는지 확인 (앞 번들이 이김)
grep -rn -E '^(food\.recommend\.tea\.title|food\.recommend\.side\.body|exercise\.pregnancy\.high\.body|privacy\.thirdparty\.notice)=' \
  --include='*.properties' src/main/resources/messages/ */src/main/resources/messages/

# 2) 3개 로케일 키 존재 확인
grep -n 'food.recommend' **/messages/message-pghd*.properties

# 3) parity 테스트 실행 (모듈명은 실제 위치에 맞게 조정)
./gradlew test --tests '*MessageBundleLocaleParityTest'
```

1번에서 `message-pghd`보다 앞쪽 번들(예: `message-hospital`)에 같은 키가 나오면 이번 문구는 화면에 나오지 않습니다. 이때는 키 이름을 바꿔야 합니다.

---

## 5. 요약

- 바로 반영: `food.recommend.tea.title`, `food.recommend.side.body` (ja_JP + en_US 함께 반영 권장)
- 보류: `exercise.pregnancy.high.body`(의료 권고 표현, 웰니스 앱 범위 초과 우려), `privacy.thirdparty.notice`(민감정보 제3자 제공, 법무 확정 문언 필요)
- 보류 키를 부분 반영할 경우 `ALLOWED_MISMATCHES` 등록과 한국어 폴백 노출에 주의
- 반영 후 키 충돌 grep과 parity 테스트를 돌려 주세요. 보류 2건은 문구가 확정되면 이어서 번역하겠습니다.
