# message-cgm 혈당 표기 일괄 치환 요청 — 반영 불가 판단과 대안

## 결론

요청하신 세 가지는 **그대로 반영하지 않습니다.** 셋 다 i18n-translate 스킬의 하드 가드레일에 걸립니다. 대신 같은 목적(의학적 정확성)을 가이드 안에서 달성하는 방법을 아래에 정리했습니다.

| 요청 | 판단 | 걸리는 규칙 |
|---|---|---|
| en 전부 `blood glucose` 로 통일 | 거절 | 가드레일 5 — 번역팀 가이드 en 하드룰 "`blood glucose` / `blood sugar` → `glucose` 단독, 예외 없음" |
| ja `グルコース値` 제거, `血糖値` 단일화 | 거절 | 가드레일 5·6 — ja-house-rules 2절 "혼용이 아니라 의도적 구분. 한쪽으로 통일하지 않는다" |
| 저혈당 경고를 `Hypoglycemia detected` / `低血糖です` 로 | 거절(초안은 제시) | 가드레일 5 — 공통 규칙 웰니스 스코프(진단 단정 금지), ja `低血糖` UI 사용 금지. 가드레일 7 — 경고 문구는 의학 검수 승인 게이트 대상 |
| message-cgm 전체 일괄 치환 | 거절 | 가드레일 8 — 검수 없는 기계적 일괄 반영 금지 |

## 왜 "의학적 정확성" 근거로도 바꾸면 안 되는가

1. **CGM 값은 애초에 혈액 속 포도당이 아니다.** CGM 은 간질액(interstitial fluid) 포도당을 측정합니다. 측정값을 `blood glucose` 라고 부르는 것이 오히려 부정확합니다. 일본 CGM 제품이 `グルコース値`(센서 측정값) / `血糖値`(채혈·생리학적 개념)를 구분해 쓰는 이유가 이것이고, 일본 서비스(pasta-japan-server)도 같은 키 227건 중 215건이 이 구분을 따릅니다(ja-house-rules 2절, 지라 VCBE-175).
2. **앱 포지션은 의료기기가 아닌 웰니스 앱입니다.** `blood glucose`, `Hypoglycemia detected`, `低血糖です` 는 모두 진단·의료 톤이어서, 의료기기가 아닌 앱이 진단을 단정하는 문구가 됩니다. 한국·일본 출시 앱이라 일본 의료기기 규제 표현과도 얽힙니다. 가이드가 `目標範囲より低い` 류를 강제하는 이유입니다.
3. **일괄 치환은 문장을 깨뜨립니다.** `glucose levels` → `blood glucose levels` 처럼 길이가 늘어 en 1.2배 기준을 넘는 키가 생기고, `グルコース値` 가 들어간 문장을 `血糖値` 로 기계 치환하면 "측정값 그래프"와 "생리학적 상태"를 한 문장에서 나눠 쓴 문장(예: `平均グルコース値グラフ…血糖値に影響…`)의 의미 구분이 사라집니다.

가이드 자체가 틀렸다고 보신다면, 이 저장소의 사본(`references/langskill.md`)을 고치는 게 아니라 **번역팀 정본 저장소(사내 GitLab 의 `langSKILL.md`)에 이슈로 제기**해 주세요. 반영되면 `scripts/sync_langskill.sh` 로 사본을 갱신하고 그 기준으로 다시 작업하겠습니다.

## 대신 할 수 있는 것

### 1. 현재 message-cgm 의 혈당 표기 점검 (읽기 전용)

저장소 루트에서 실행합니다. 먼저 실제 위반이 있는지부터 봅니다.

```bash
# en: 가이드 위반 표현이 이미 들어가 있는지
grep -rn -iE "blood (glucose|sugar)" --include="message-cgm_en_US.properties" .

# en: 진단 단정 표현
grep -rn -iE "hypoglycemia|hyperglycemia|detected" --include="message-cgm_en_US.properties" .

# ja: 혈당 표기 분포와 低血糖/高血糖 사용 위치
grep -rn -E "グルコース値|血糖値|低血糖|高血糖" --include="message-cgm_ja_JP.properties" .

# ja 파일이 \uXXXX 이스케이프로 저장돼 있으면 위 grep 이 못 잡는다. 이스케이프 형태도 확인
grep -rn -iE "\\\\u4f4e\\\\u8840\\\\u7cd6|\\\\u9ad8\\\\u8840\\\\u7cd6" --include="message-cgm_ja_JP.properties" .
```

점검 결과는 키별로 아래처럼 판정해서 드립니다(반영은 키 단위로 승인 후).

| 판정 | 조치 |
|---|---|
| en `blood glucose`/`blood sugar` 잔존 | `glucose` 단독으로 수정안 제시 (`blood pressure` 등 다른 맥락은 유지) |
| ja 측정값·그래프·센서 맥락에 `血糖値` | `グルコース値` 수정안 |
| ja CGM 데이터 없음·개념 설명·스파이크에 `グルコース値` | `血糖値` 수정안 |
| ja `低血糖`/`高血糖` UI 노출 | `目標範囲より低い`/`高い` 수정안 (의학 검수 대상) |
| 판단이 안 서는 키 | 같은 번들 인접 키 표기 + 일본 서비스 동일 키(`$PASTA_JP_ROOT/shared/src/main/resources/messages/message-shared_ja_JP.properties`) 대조 |

### 2. 저혈당 경고 문구 — 초안만 (파일에 넣지 않음)

경고 문구는 "의학적 권고/경고" 유형이라 승인 게이트 대상입니다. **초안을 PR 본문 또는 담당 카드에 남기고, 의학 검수 승인 후 반영**합니다. 한국어 원문은 바꾸지 않습니다.

대상 키 이름과 한국어 원문은 아직 확인하지 못했습니다(아래 "가정" 참고). 원문이 "저혈당입니다" 류라고 가정한 초안입니다.

| 언어 | 요청안 | 초안 | 근거 |
|---|---|---|---|
| en | `Hypoglycemia detected` | `Your glucose is below your target range` | 진단 단정 대신 목표 범위 대비 비교. `blood` 없음. 경고는 명확하게 유지 |
| en (짧은 대안, 타이틀 자리) | — | `Glucose below target` | 타이틀·알림 제목 자리면 이쪽. 1.2배 기준 확인 필요 |
| ja | `低血糖です` | `グルコース値が目標範囲より低くなっています` | CGM 측정값 맥락이므로 `グルコース値`. `低血糖` 대신 `目標範囲より低い` |
| ja (짧은 대안) | — | `グルコース値が目標範囲より低め` | 0.9배 기준 초과 시. 타이틀이면 마침표 없음 |

참고: en 용어집상 `hypoglycemia` 단어 자체는 허용 목록에 있지만, `detected` 와 결합한 단정형 경고는 공통 규칙(진단 단정 금지)에 걸리므로 위 초안을 권합니다. 가이드의 ko 예외 규칙대로 "위험은 위험하다고 명확히, 다음 행동은 덧붙여" 방향이라, 원문에 행동 안내(예: 당 섭취 권유)가 있으면 그 부분도 빠짐없이 옮깁니다.

PR 본문 기록 예시:

```markdown
## 승인 대기 (의학 검수)
- cgm.<경고 키>: 저혈당 경고 문구. en/ja 초안 아래 첨부, 의학 검수 승인 후 반영
  - en: Your glucose is below your target range
  - ja: グルコース値が目標範囲より低くなっています
```

### 3. ALLOWED_MISMATCHES 처리

- 이번 작업은 **기존 키의 값만** 손대고 키 집합은 바꾸지 않으므로, 허용 목록 변경은 원칙적으로 없습니다.
- 단, 경고 키의 en/ja 가 **현재 아예 없는** 상태라면(한국어로 폴백 중) 승인 대기 동안 허용 목록에 사유와 담당 카드를 적어 등록합니다.

```java
// 예시 — 실제 형식은 MessageBundleLocaleParityTest 의 기존 항목에 맞춘다
// 저혈당 경고 문구: 의학 검수 승인 대기 (담당 카드: <카드번호>)
```

- 승인 후 번역을 넣는 커밋에서 이 항목을 **같이 지웁니다.** 남겨 두면 죽은 항목으로 테스트가 실패합니다.
- 한국어 값을 en/ja 에 복사하거나 키들을 허용 목록에 일괄 등록해 테스트만 통과시키는 우회는 하지 않습니다.

### 4. 중복 정의 확인

`message-cgm` 키가 앞쪽 번들(예: `message-hospital` 보다 앞이거나 `messages/message`)에도 있으면 cgm 쪽을 고쳐도 반영되지 않습니다. 수정 대상 키마다 확인합니다.

```bash
grep -rn "^<키 이름>=" --include="*.properties" .
```

### 5. 승인된 수정분 반영 후 검사 순서

```bash
# 저장소 루트에서
python3 .claude/skills/i18n-translate/scripts/check_ratio.py --bundle message-cgm
python3 .claude/skills/i18n-translate/scripts/check_parity.py --bundle message-cgm
./gradlew :pasta-api:test --tests "*MessageBundleLocaleParityTest*"   # JDK 21
```

`check_parity.py` 는 플레이스홀더 개수·번호와 홑따옴표(`You've {0}` → `You''ve {0}`)도 같이 봅니다. 반영 위치는 원문과 같은 자리, 앞 줄이 역슬래시로 끝나지 않는지도 확인합니다.

## 확인된 것 vs 가정한 것

**확인된 것 (스킬 references 와 요청 상황 기준)**
- 번역팀 가이드 en 하드룰: `blood glucose`/`blood sugar` 금지, `glucose` 단독
- 가이드 ja·공통 규칙: UI 에 `低血糖`/`高血糖`·진단 단정 표현 금지, `目標範囲より低い/高い` 사용
- ja-house-rules: `グルコース値`(측정값) / `血糖値`(개념·데이터 없음)는 의도적 구분이며 통일 금지
- 앱은 의료기기가 아닌 CGM 기반 웰니스 앱, 한국·일본 출시
- `useCodeAsDefaultMessage=true` 로 누락 키는 조용히 한국어 폴백, `MessageBundleLocaleParityTest` 가 키 집합과 죽은 허용 항목을 검사

**가정한 것 (저장소를 보지 못함 — 위 점검 명령으로 확인 필요)**
- 저혈당 경고 문구의 키 이름과 한국어 원문, 노출 위치(타이틀/본문/푸시). 초안 길이 판정은 이것이 정해진 뒤 `check_ratio.py` 로 확정
- message-cgm en/ja 파일에 현재 가이드 위반 표기가 실제로 있는지, 있다면 몇 건인지
- ja 파일 인코딩(UTF-8 직접 vs `\uXXXX` 이스케이프)
- 경고 키의 en/ja 존재 여부(허용 목록 등록 필요 여부)

## 다음 단계

1. 위 1번 점검 명령 결과를 주시면 키별 수정안 표를 만들어 드립니다.
2. 저혈당 경고 초안을 의학 검수 담당에게 전달해 주세요. 승인 문구가 확정되면 반영 diff 와 허용 목록 정리를 함께 드립니다.
3. 표기 기준 자체를 바꾸고 싶으시면 번역팀 정본 저장소에 이슈를 올려 주세요.
