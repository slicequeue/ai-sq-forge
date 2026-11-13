# message-cgm 용어 통일 요청 검토

요청을 그대로 일괄 치환하기 전에 짚어야 할 점이 있어서, 바로 반영하지 않고 확인 요청부터 드립니다. 이 요청은 "의학적으로 정확하게" 하려는 것인데, 그대로 반영하면 오히려 의학적으로 덜 정확해지고 규제 리스크도 커집니다.

## 1. 반영 전에 확인이 필요한 문제

### 1-1. CGM 은 혈당(blood glucose)을 재지 않습니다
- CGM 센서는 **간질액(interstitial fluid) 포도당**을 측정합니다. 혈액을 재는 건 BGM(채혈식 혈당계)입니다.
- 그래서 Dexcom·Abbott(FreeStyle Libre) 등 제조사와 일본 쪽 표기도 en 은 "glucose" / "sensor glucose", ja 는 "グルコース値" 를 쓰는 경우가 일반적입니다.
- 즉 en 을 전부 "blood glucose" 로, ja 의 "グルコース値" 를 "血糖値" 로 바꾸는 것은 정확도를 **떨어뜨리는** 방향입니다.
- 현재 번들에 グルコース値 와 血糖値 가 섞여 있다면, 통일 방향은 오히려 **グルコース値(측정값) 쪽**이 맞고, 血糖値 는 일반 개념 설명(예: "血糖値スパイク" 같은 교육 문구)에만 남기는 쪽을 권합니다.

### 1-2. 의료기기가 아닌 웰니스 앱에서 "Hypoglycemia detected" / "低血糖です" 는 진단 표현입니다
- "Hypoglycemia detected", "低血糖です" 는 앱이 **저혈당이라는 의학적 상태를 판정**했다는 단정 표현입니다.
- 의료기기 허가가 없는 웰니스 앱에서 질병·상태를 진단하는 문구는 한국(의료기기법, 식약처 웰니스 가이드라인)·일본(薬機法, 프로그램 의료기기 해당성 판단) 모두에서 의료기기 해당성 판단의 근거가 될 수 있습니다.
- 일반적으로 웰니스 앱에서 쓰는 쪽은 수치 사실 기반·비단정 표현입니다. 예시:
  - en: "Your glucose is below your target range" / "Low glucose"
  - ja: "グルコース値が目標範囲を下回っています"
  - (필요 시) "Please consult a healthcare professional if you feel unwell" 류 안내 병기
- 이 문구 결정은 개발 판단이 아니라 **기획·법무/RA(규제) 확인이 필요한 사항**입니다. 확인 없이 진단형 문구로 바꾸지 않는 것을 권합니다.

### 1-3. "message-cgm 전체 일괄 치환"의 기술적 위험
- **값만 바꿔야 합니다.** `sed` 로 단순 치환하면 키 이름(`cgm.glucose.xxx`)·주석·플레이스홀더(`{0}`)까지 건드릴 수 있습니다.
- **en 문장 깨짐**: "glucose" → "blood glucose" 단순 치환 시 "Blood blood glucose", "Glucose" 대소문자 미처리, "glucose sensor" → "blood glucose sensor"(틀린 표현) 같은 오치환이 생깁니다.
- **번들 우선순위**: BASENAMES 는 앞쪽 번들이 이기므로, 같은 키가 `message-hospital` 등 앞쪽 번들에 있으면 message-cgm 을 바꿔도 화면에 반영되지 않습니다. 치환 전 중복 키 확인이 필요합니다.
- **조용한 폴백**: `useCodeAsDefaultMessage=true` + 로케일 키 누락 시 한국어로 폴백하므로, 치환 중 키를 잘못 건드려 en/ja 키가 사라지면 오류 없이 한국어가 노출됩니다.
- **ParityTest**: 키 집합을 바꾸지 않으면 영향 없음. 단, 치환으로 기존에 미번역(ALLOWED_MISMATCHES 등록) 상태였던 키를 이번에 번역하게 되면 허용 목록에 죽은 항목이 남아 테스트가 실패하므로 해당 항목도 함께 제거해야 합니다.
- **한국어(기본) 파일**: 요청에 ko 언급이 없어 ko 는 건드리지 않는 것으로 이해했습니다. 다만 ko 가 "혈당" 이라면 동일한 정확도 논점이 있습니다.

## 2. 제안하는 진행 방식

아래 중 하나를 골라 주시면 그에 맞춰 반영안을 드리겠습니다.

| 안 | en 측정값 표기 | ja 측정값 표기 | 저혈당 경고 |
|----|---------------|---------------|------------|
| A (권장) | glucose / sensor glucose 로 통일 | グルコース値 로 통일 | 비진단 표현 (예: "Your glucose is below your target range" / "グルコース値が目標範囲を下回っています"), 기획·RA 확인 후 확정 |
| B (요청 원안) | blood glucose | 血糖値 | "Hypoglycemia detected" / "低血糖です" — RA 확인 필수, 리스크 감수 결정 기록 필요 |

어느 안이든 일괄 `sed` 가 아니라 **대상 키 목록을 뽑아 키 단위로 값만 교체**하는 방식으로 진행합니다.

## 3. 반영 절차 (안 확정 후)

1) 현황 확인 (읽기 전용)

```bash
# 대상 문구가 있는 키 목록
grep -nE 'glucose|Glucose' src/main/resources/messages/message-cgm_en_US.properties
grep -nE 'グルコース値|血糖値|低血糖' src/main/resources/messages/message-cgm_ja_JP.properties
# (properties 가 \uXXXX 이스케이프라면 native2ascii -reverse 등으로 디코드 후 확인)

# 저혈당 경고 키 확인
grep -niE 'hypo|low' src/main/resources/messages/message-cgm*.properties

# 앞쪽 번들과의 키 중복 확인 (앞쪽이 이기므로 cgm 수정이 무효화될 수 있음)
cut -d= -f1 src/main/resources/messages/message-cgm.properties | sort > /tmp/cgm_keys
for f in src/main/resources/messages/message-*.properties; do
  case "$f" in *_en_US*|*_ja_JP*|*message-cgm*) continue;; esac
  cut -d= -f1 "$f" | sort | comm -12 - /tmp/cgm_keys | sed "s|^|$f: |"
done

# ALLOWED_MISMATCHES 에 message-cgm 키가 있는지
grep -n 'cgm' $(find . -name MessageBundleLocaleParityTest.java)
```

2) 키별 변경표 작성 → 확인 받은 뒤 값만 교체 (예시 형태, 실제 키는 1)의 결과 기준)

```diff
# message-cgm_en_US.properties (A안 예시)
-cgm.alert.low=Hypoglycemia detected
+cgm.alert.low=Your glucose is below your target range

# message-cgm_ja_JP.properties (A안 예시)
-cgm.summary.average=平均血糖値
+cgm.summary.average=平均グルコース値
-cgm.alert.low=低血糖です
+cgm.alert.low=グルコース値が目標範囲を下回っています
```

3) 검증

```bash
./gradlew test --tests '*MessageBundleLocaleParityTest*'
# 변경 키를 en_US / ja_JP 로케일로 실제 조회해 한국어 폴백 여부 확인
git diff --stat src/main/resources/messages/   # message-cgm 3파일 외 변경이 없는지
```

## 4. 정리

- 확인된 사실: 번들 구조, 앞쪽 우선 조회, 한국어 조용한 폴백, ParityTest 동작, 앱이 비의료기기 웰니스 앱이라는 점 (요청에 주어진 정보).
- 가정한 것: 실제 키 이름·현재 문구 분포·앞쪽 번들 중복 여부 (위 1) 명령으로 확인 필요).
- 지금 바로 반영하지 않은 이유: "blood glucose / 血糖値" 는 CGM 측정 원리상 덜 정확하고, "Hypoglycemia detected / 低血糖です" 는 비의료기기 앱에서 진단 표현이 되어 규제 리스크가 있습니다. A/B 중 방향과 경고 문구의 RA 확인 여부를 알려주시면 키 단위 diff 로 반영하겠습니다.
