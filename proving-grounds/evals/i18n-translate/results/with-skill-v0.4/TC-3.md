# message-group_ja_JP 파손 정리 + error.hospital.staff.not-found 영어 미노출 원인

## 요약

문제는 두 개고, 원인이 서로 다릅니다.

1. **테스트가 깨지는 원인은 번역 내용이 아니라 파일 구조입니다.** `message-group_ja_JP.properties` 에 파손이 세 군데 있습니다. 줄 끝 역슬래시 때문에 키 2개가 사라졌고, 여러 줄로 붙인 후보 때문에 가짜 키 2개가 생겼고, 번역가 메모가 값에 섞여 화면에 그대로 나옵니다.
2. **영어가 안 나오는 원인은 번들 우선순위입니다.** `message-hospital` 이 `message-pasta-api` 보다 앞에 있어서 영어 요청도 hospital 번들의 한국어에서 끝납니다. pasta-api 에 넣은 영어 값에는 조회가 도달하지 않습니다. 영어 값은 **`message-hospital_en_US`** 에 넣어야 합니다.

`group.leave.notice` 는 번역가가 법무 확인을 요청한 탈퇴 시 데이터 처리 고지라서 이번에는 파일에 넣지 않습니다. 초안만 PR 본문에 남기고 허용 목록에 사유를 적어 등록합니다.

---

## 1. message-group_ja_JP — 무엇이 깨졌나

현재 파일은 Java `Properties` 가 다음처럼 읽습니다.

| 줄 | 실제 파싱 결과 | 문제 |
|---|---|---|
| `group.admin.member.body=...退会できます。\` | 다음 두 줄까지 이어서 **값 하나**가 됨 | `group.admin.body`, `group.staff.title` 이 앞 값에 흡수되어 **키가 사라짐**. 화면에는 세 문장이 이어진 값이 나옴 |
| `招待を送る` | 키 `招待を送る`, 값 빈 문자열 | **가짜 키** |
| `メンバーを招待` | 키 `メンバーを招待`, 값 빈 문자열 | **가짜 키** |
| `group.leave.notice=... 번역가 메모: 법무 확인 필요?` | 메모까지 값이 됨 | 일본어 화면에 **한글 메모가 노출** |

그래서 정합성 테스트에서 ja_JP 쪽이 ko 대비 키 2개 누락, 2개 초과로 잡힙니다. 흡수된 두 키는 파일에 글자로는 보여서 눈으로 훑으면 멀쩡해 보입니다.

추가로 `group.*` 키들이 원래 ja 미번역으로 `ALLOWED_MISMATCHES` 에 올라가 있었다면, 이번에 정상 반영된 `group.admin.member.body`, `group.invite.cta` 가 **죽은 허용 항목**이 되어 그쪽에서도 테스트가 실패합니다. "이상하게 깨진다" 는 증상은 이 두 원인이 겹친 것으로 봅니다(허용 목록 내용은 아직 보지 못했습니다. 아래 확인 명령 참고).

현재 상태에서 `check_parity.py` 를 돌리면 이렇게 나올 것입니다(시뮬레이션).

```
$ python3 .claude/skills/i18n-translate/scripts/check_parity.py --bundle message-group
[파손] message-group_ja_JP.properties:N  招待を送る
[파손] message-group_ja_JP.properties:N+1  メンバーを招待
[누락] message-group_ja_JP :: group.admin.body
[누락] message-group_ja_JP :: group.staff.title

문제 4건
```

번역 메모 혼입은 이 스크립트가 잡지 못합니다. ja 자기 검수 10번 항목(한글 잔존)으로 따로 확인했습니다.

## 2. message-group_ja_JP — 반영안

### diff

```diff
-group.admin.member.body=管理者権限の移管後、退会できます。\
-group.admin.body=管理者権限の移管後に退会できます。\
-group.staff.title=リンクされたメンバーがいます。
-group.invite.cta=招待する
-招待を送る
-メンバーを招待
-group.leave.notice=退会するとデータは削除されます 번역가 메모: 법무 확인 필요?
+group.admin.member.body=管理者権限の移管後、退会できます。
+group.admin.body=管理者権限の移管後に退会できます。
+group.staff.title=連携中のメンバーがいます
+# 후보(검토용): 招待を送る / メンバーを招待
+group.invite.cta=招待する
```

- 줄 끝 역슬래시 두 개를 지웠습니다. 세 값은 원래 각각 한 줄짜리입니다.
- 후보는 `#` 주석 한 줄로 내리고 값은 하나만 남겼습니다.
- `group.leave.notice` 줄은 ja 파일에서 뺐습니다(3절 승인 게이트). 메모는 PR 본문으로 옮깁니다.
- 키 순서는 한국어 원문과 같습니다. 반영 후 바로 앞 줄이 역슬래시로 끝나는 키는 없습니다.

### 키별 판단

| 키 | ko | ja | 글자 수 비율(폭) | 판단 |
|---|---|---|---|---|
| `group.admin.member.body` | 관리자 권한을 넘긴 뒤 탈퇴할 수 있어요. | 管理者権限の移管後、退会できます。 | 0.74 (0.87) | 번역가 값 유지. 사실·행동 보존, 12항목 통과 |
| `group.admin.body` | 관리자 권한을 넘긴 후에 탈퇴할 수 있어요. | 管理者権限の移管後に退会できます。 | 0.71 (0.83) | 번역가 값 유지 |
| `group.staff.title` | 연결된 멤버가 있어요 | 連携中のメンバーがいます | **1.09** (1.20) | 수정. 아래 참고 |
| `group.invite.cta` | 초대하기 | 招待する | **1.00** (1.00) | 번역가 첫 후보 채택 |
| `group.leave.notice` | 탈퇴하면 데이터가 삭제돼요 | (반영 보류) | - | 법무 승인 게이트 |

**`group.staff.title` 을 고친 이유**

- 키에 `title` 이 있어서 폭이 고정된 자리로 봅니다. 번역가 값 `リンクされたメンバーがいます。` 는 1.36배(폭 1.50)로 가장 많이 넘칩니다.
- 타이틀이므로 끝의 `。` 를 뺐습니다(가이드 ja: 버튼·라벨·헤더 끝 마침표 없음. 원문에도 마침표가 없습니다).
- `リンクされた` 는 한국어 피동 `연결된` 을 그대로 옮긴 형태라 `連携中の` 로 바꿨습니다. 다만 이 앱 일본어판이 계정·멤버 연결을 `連携` 과 `リンク` 중 무엇으로 부르는지는 **확인하지 못했습니다(가정)**. 아래 명령으로 일본 서비스의 같은 키와 인접 키를 보고, `リンク` 쪽이면 `リンク中のメンバーがいます` 로 맞춥니다.
- 여전히 0.9배를 넘습니다. 더 짧은 대안을 PR 본문에 같이 적습니다.
  - `連携メンバーがいます` (0.91, 폭 1.00)
  - `連携中のメンバー` (0.73, 폭 0.80). 체언止め라서 "있다" 는 뉘앙스가 약해집니다. 탈퇴를 막는 경고 다이얼로그 타이틀이면 권하지 않습니다

**`group.invite.cta`**

- CTA 는 가이드상 동사형이 기본이라 `招待する` 가 맞습니다. `招待を送る` 는 더 길고, `メンバーを招待` 는 7자(1.75배)입니다.
- 비율이 정확히 1.00 이라 0.9 를 넘지만 표시 폭은 원문과 같습니다(4자 대 4자). 짧은 대안 `招待`(0.50) 는 명사형이라 CTA 컨벤션에 어긋납니다. PR 본문에 수치만 기록하고 현재 값을 유지할 것을 권합니다.

## 3. group.leave.notice — 승인 게이트

탈퇴할 때 데이터가 어떻게 처리되는지 고지하는 문구입니다. 개인정보 보유·파기 고지 성격이고, 번역가도 법무 확인을 요청했습니다. 그래서 스킬의 승인 게이트(법정 고지)에 해당한다고 판정했습니다. 일본에서는 개인정보보호법상 보유 의무 등으로 탈퇴 후에도 일부 데이터를 남길 수 있어서, "삭제됩니다" 라고 단정하는 문구는 법무가 사실관계를 확인해야 합니다.

- **ja 파일에 넣지 않습니다.** ja_JP 의 이 키는 `ALLOWED_MISMATCHES` 에 사유와 담당 카드를 붙여 등록합니다(4절).
- PR 본문에 남길 초안:
  - 1안 `退会すると、データは削除されます。` (1.14, 폭 1.23). 안내문이라 길이를 느슨하게 적용합니다. 시스템 동작을 서술하는 문장이라 수동태가 맞습니다
  - 짧은 안 `退会後、データは削除されます。` (1.07)
- 법무가 일반 UI 안내로 판정하면 1안을 원래 자리에 넣고 허용 항목을 지우면 됩니다.
- en_US 에 이 키가 이미 들어가 있다면, 그 영어 문구도 같은 법무 확인 대상입니다. en 파일 상태는 받지 못했습니다(확인 필요).
- 한국어 원문 `탈퇴하면 데이터가 삭제돼요` 는 고치지 않았습니다.

---

## 4. error.hospital.staff.not-found — 영어가 안 나오는 이유

`BASENAMES` 순서상 `messages/message-hospital` 이 `messages/message-pasta-api`(마지막)보다 앞입니다. `ResourceBundleMessageSource` 는 basename 을 순서대로 보다가 값을 찾으면 멈춥니다.

1. en_US 요청이 오면 먼저 `message-hospital` 의 en_US 번들을 찾습니다
2. `message-hospital_en_US` 에 이 키가 없으므로 부모인 기본 번들 `message-hospital.properties` 의 `의료진 정보를 찾을 수 없어요` 를 찾고 **여기서 조회가 끝납니다**
3. `message-pasta-api_en_US` 의 `Medical staff not found` 까지는 조회가 가지 않습니다

`useCodeAsDefaultMessage=true` 와 상관없이, 키가 "있는" 상태로 한국어가 반환되기 때문에 예외도 로그도 남지 않습니다. pasta-api 에 영어를 넣어도 결과가 바뀌지 않은 이유입니다.

### 반영안

**(a) 이기는 번들인 hospital 에 로케일 값을 채웁니다.** 키는 이미 기본 번들(`message-hospital.properties:12`)에 있으므로 값만 채우는 작업이고, 키를 새로 만드는 것이 아닙니다. 원문과 같은 12번 줄 위치에 넣습니다.

```diff
# hospital/src/main/resources/messages/message-hospital_en_US.properties
+error.hospital.staff.not-found=Medical staff not found

# hospital/src/main/resources/messages/message-hospital_ja_JP.properties
+error.hospital.staff.not-found=医療スタッフが見つかりません
```

| 언어 | 값 | 비율(폭) | 근거 |
|---|---|---|---|
| en | Medical staff not found | **1.44** (0.82) | pasta-api_en_US 에 이미 있는 값을 재사용해 두 번들의 표현을 맞췄습니다. 에러 메시지라 길이는 느슨하게 보지만 수치는 PR 본문에 남깁니다. 짧은 대안 `Staff info not found` (1.25) |
| ja | 医療スタッフが見つかりません | 0.88 (1.00) | 원문에 마침표가 없어서 맞췄습니다. 인접 에러 키가 `。` 를 붙인다면 `。` 를 붙입니다(0.94). `医療スタッフの情報が…` 는 1.12배라 `情報` 를 뺐습니다. 의미(대상을 찾지 못함)는 같습니다 |

플레이스홀더와 홑따옴표는 없습니다. en 하드룰(blood glucose)과 혈당 표기는 해당 없습니다.

**(b) pasta-api 쪽 중복 정의**

grep 결과를 보면 `message-pasta-api` 에는 ko 와 en_US 만 있고 **ja_JP 가 없습니다.** 이 키가 허용 목록에 없다면 pasta-api 번들의 정합성도 깨집니다. 반대로 원래 en/ja 미번역으로 허용 목록에 있었다면, 방금 넣은 en 때문에 en 항목이 죽은 항목이 되어 실패합니다. 어느 쪽이든 정리가 필요합니다.

- 이번 커밋: 키 집합을 맞추기 위해 `message-pasta-api_ja_JP.properties` 40번 줄 위치에도 같은 ja 값을 넣고, pasta-api 의 이 키 관련 허용 항목을 지웁니다. 런타임에는 도달하지 않는 값이지만 키를 지우지 않고 정합성을 맞출 수 있습니다.
- **제안만 함(이번에 반영하지 않음)**: pasta-api 3개 파일에서 이 키를 제거해 중복 정의를 없애는 안. hospital 번들이 이기므로 런타임 동작은 바뀌지 않지만, 키 삭제라서 별도로 판단할 일입니다. 근거로 아래 grep 결과를 PR 에 첨부해 주세요.

```bash
grep -rn "error.hospital.staff.not-found" --include="*.java" --include="*.kt" .
```

---

## 5. ALLOWED_MISMATCHES 정리

허용 목록의 실제 형식은 받지 못해서 항목 단위로만 적습니다. 실제 표기에 맞춰 바꿔 주세요.

| 번들 | 키 | 로케일 | 조치 |
|---|---|---|---|
| message-group | group.admin.member.body | ja_JP | 있으면 **삭제** |
| message-group | group.admin.body | ja_JP | 있으면 **삭제** |
| message-group | group.staff.title | ja_JP | 있으면 **삭제** |
| message-group | group.invite.cta | ja_JP | 있으면 **삭제** |
| message-group | group.leave.notice | ja_JP | **유지 또는 신규 등록**. 사유: `법무 확인 대기(탈퇴 시 데이터 처리 고지)`, 담당 카드 `<카드 번호>` |
| message-hospital | error.hospital.staff.not-found | en_US, ja_JP | **삭제** (ko 만 있어서 등록돼 있었을 것) |
| message-pasta-api | error.hospital.staff.not-found | en_US, ja_JP | 있으면 **삭제** |

담당 카드 번호는 알려 주시면 채우겠습니다.

```bash
# 현재 허용 목록에 무엇이 있는지 먼저 확인
grep -rn -A2 "group\.\|error.hospital.staff.not-found" $(grep -rl "ALLOWED_MISMATCHES" --include="*.java" --include="*.kt" .)
```

---

## 6. 실행 순서

저장소 루트에서 실행합니다.

```bash
# 0) 반영 전 확인 — 다른 번들에 같은 group 키가 있는지, en_US 상태
grep -rn "^group\.\(admin\|staff\|invite\|leave\)" --include="*.properties" .

# 0-1) 일본 서비스 용어 대조 (連携 / リンク)
JP="${PASTA_JP_ROOT:?pasta-japan-server 체크아웃 경로를 PASTA_JP_ROOT 로 지정}"
grep -rn "^group\.\|連携\|リンク" $JP/shared/src/main/resources/messages/message-shared_ja_JP.properties | head -30
grep -rn "^error.hospital.staff.not-found=" $JP/shared/src/main/resources/messages/

# 1) 길이
python3 .claude/skills/i18n-translate/scripts/check_ratio.py --bundle message-group --all
python3 .claude/skills/i18n-translate/scripts/check_ratio.py --key error.hospital.staff.not-found --all

# 2) 정합성·파손
python3 .claude/skills/i18n-translate/scripts/check_parity.py --bundle message-group
python3 .claude/skills/i18n-translate/scripts/check_parity.py --bundle message-hospital
python3 .claude/skills/i18n-translate/scripts/check_parity.py --bundle message-pasta-api

# 3) 테스트 (JDK 21)
./gradlew :pasta-api:test --tests "*MessageBundleLocaleParityTest*"
```

반영 후 예상 결과(시뮬레이션):

```
$ check_ratio.py --bundle message-group --all
비교 대상 4쌍 (원문 4자 이상)        # ja 기준. en 은 기존 값에 따라 달라짐
기준 초과 2건
!x1.09 (폭 x1.20) [ja] message-group :: group.staff.title
!x1.00 (폭 x1.00) [ja] message-group :: group.invite.cta
 x0.74 (폭 x0.87) [ja] message-group :: group.admin.member.body
 x0.71 (폭 x0.83) [ja] message-group :: group.admin.body

$ check_parity.py --bundle message-group
[누락] message-group_ja_JP :: group.leave.notice      # 허용 목록 등록 대상, 의도된 것
문제 1건
```

`check_parity.py` 는 허용 목록을 모르므로 `group.leave.notice` 누락 1건은 정상입니다. 최종 판정은 3) 테스트로 합니다.

## 7. 커밋·PR

커밋 메시지 안:

```
fix: message-group 일본어 번들 파손 복구 및 의료진 미존재 에러 영어·일본어 반영

- group ja_JP: 줄 끝 역슬래시로 흡수된 키 2건 복구, 후보 다중 줄 가짜 키 2건 제거, 번역 메모 제거
- group.leave.notice ja_JP 는 법무 확인 대기로 보류하고 허용 목록에 등록
- error.hospital.staff.not-found: 우선순위가 앞인 message-hospital 에 en_US/ja_JP 반영
```

PR 본문에 넣을 것:

- 길이 초과 키(태그 기능이 없어 여기에 기록)
  - `group.staff.title` ja 1.09(폭 1.20). 대안 `連携メンバーがいます` / `連携中のメンバー`. 화면 확인 필요
  - `group.invite.cta` ja 1.00(폭 1.00). 대안 `招待`. CTA 동사형 규칙 때문에 현재 값 유지
  - `error.hospital.staff.not-found` en 1.44(폭 0.82). 대안 `Staff info not found`
- 승인 대기: `group.leave.notice` ja 초안 2개와 번역가 메모 원문(`법무 확인 필요?`)
- 후속 제안: pasta-api 의 `error.hospital.staff.not-found` 중복 정의 제거(코드 참조 grep 결과 첨부)

---

## 확인된 것과 가정한 것

**확인된 것(받은 발췌와 grep 기준)**
- ja 파일의 역슬래시 흡수 2건, 가짜 키 2건, 메모 혼입 1건
- `error.hospital.staff.not-found` 가 hospital(ko 만)과 pasta-api(ko, en_US)에 중복 정의되어 있고, hospital 이 BASENAMES 에서 앞쪽이다
- pasta-api_ja_JP 에는 이 키가 없다(grep 에 나오지 않음)

**가정한 것(확인 필요)**
- `ALLOWED_MISMATCHES` 의 현재 내용과 표기 형식. 죽은 항목이 테스트 실패에 섞여 있다는 판단은 이 가정에 기대고 있습니다
- `message-group_en_US` 는 이미 완비된 상태다. en 파일은 받지 못했습니다
- 일본어판의 "연결" 용어가 `連携` 이다. 일본 서비스 대조 전까지는 가정입니다
- `group.staff.title` 이 탈퇴를 막는 경고 다이얼로그의 타이틀이다(키 이름과 인접 키로 추정)
- hospital 의 en_US·ja_JP 파일이 존재한다(번들 지도상 3개 파일 구성)
