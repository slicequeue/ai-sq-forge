두 건 모두 원인을 찾았습니다. 테스트가 깨진 건 번역 내용 문제가 아니라 `message-group_ja_JP.properties` 파일이 파손됐기 때문이고, `error.hospital.staff.not-found` 는 번역을 넣은 번들이 조회 순서상 도달하지 못하는 위치였습니다.

> 실제 저장소를 볼 수 없어서 아래 diff 는 주신 발췌를 기준으로 했습니다. 검사 결과는 예상 출력입니다. "확인 필요"라고 적은 항목은 반영 전에 명령을 한 번 돌려 주세요.

---

## 1. message-group_ja_JP — 테스트가 깨진 원인

### 파손 4건

| # | 위치 | 증상 | 결과 |
|---|---|---|---|
| A | `group.admin.member.body`, `group.admin.body` 줄 끝 `\` | 줄 끝 역슬래시 때문에 다음 줄이 앞 값에 이어 붙음 | `group.admin.body` 와 `group.staff.title` 이 `group.admin.member.body` 값에 흡수되어 **키가 사라짐**. 파일을 눈으로 보면 있지만 실제로는 없는 상태 |
| B | `group.invite.cta` 아래 후보 2줄 | 첫 줄만 값이 되고 나머지는 키로 파싱됨 | `招待を送る`, `メンバーを招待` 라는 **가짜 키 2개** 생성(기본 번들에 없는 고아 키) |
| C | `group.leave.notice` 값 뒤 `번역가 메모: 법무 확인 필요?` | 메모가 값에 포함됨 | 화면에 한국어 메모가 그대로 노출됨(한글 잔존) |
| D | `group.staff.title` 끝 `。` | 타이틀 자리에 마침표가 붙음 | 가이드 위반(버튼·라벨·헤더에는 마침표 없음). ko 원문에도 마침표 없음 |

parity 테스트가 이상하게 깨진 건 A(키 누락 2건)와 B(고아 키 2건)가 함께 발생했기 때문입니다. 번역 누락처럼 보이지만 실제로는 파일 구문 문제입니다.

### 승인 게이트 — group.leave.notice 는 이번 커밋에서 빼는 것을 권합니다

`탈퇴하면 데이터가 삭제돼요` 는 탈퇴 시 데이터를 삭제한다는 고지입니다. 번역가도 법무 확인이 필요하다고 표시했습니다. 스킬 기준으로 법정 고지·약관 유형에 해당하므로 **ja 값은 파일에 넣지 않고 초안만 PR 본문에 남깁니다.** 법무가 고지 대상이 아니라고 답하면 바로 반영하면 됩니다.

- ja 초안: `退会すると、データは削除されます。`
  - 시스템 동작을 서술하는 수동태이므로 가이드상 허용됩니다.
  - 길이는 ko 14자 대비 17자(1.21배)로 기준 0.9를 넘습니다. 안내문이라 느슨하게 적용하지만 짧은 대안도 함께 적습니다: `退会するとデータが消えます` (13자, 0.93배). 다만 법적 고지 성격이 확정되면 각주·면책 문구 규칙(정식 표현)에 따라 `削除されます` 쪽이 맞습니다.
- 확인 요청 사항: 그룹 탈퇴 시 삭제되는 데이터의 범위. 개인 기록 전체인지 그룹 내 데이터만인지에 따라 ko 원문 자체를 고쳐야 할 수도 있습니다. 원문은 임의로 바꾸지 않았습니다.

### diff (message-group_ja_JP.properties)

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
+# length:review — 원문 대비 1.27배(타이틀). 대안: 連携中のメンバーがいます / メンバーが連携中
+group.staff.title=リンクされたメンバーがいます
+# 후보: 招待を送る / メンバーを招待 (번역가 제안, 미채택)
+group.invite.cta=招待する
+# group.leave.notice — 법무 확인 대기(카드 번호 기입). 초안: 退会すると、データは削除されます。
```

`group.leave.notice` 줄은 키를 빼고 주석으로만 남겼습니다. 이 상태로는 ja 에서 키가 누락되므로 아래 허용 목록 등록이 필요합니다.

### 값 판단 근거

| 키 | ko | ja | 글자 수 비율 | 판단 |
|---|---|---|---|---|
| group.admin.member.body | 관리자 권한을 넘긴 뒤 탈퇴할 수 있어요. (23) | 管理者権限の移管後、退会できます。 (17) | 0.74 | 통과 |
| group.admin.body | 관리자 권한을 넘긴 후에 탈퇴할 수 있어요. (24) | 管理者権限の移管後に退会できます。 (17) | 0.71 | 통과 |
| group.staff.title | 연결된 멤버가 있어요 (11) | リンクされたメンバーがいます (14) | **1.27** | 타이틀이라 엄격하게 적용해야 합니다. 표시 폭도 20 → 28 로 커집니다. 번역가 값을 유지하되 `length:review` 를 PR 에 적고 대안을 제시합니다: `連携中のメンバーがいます` (12, 1.09), `メンバーが連携中` (8, 0.73) |
| group.invite.cta | 초대하기 (4) | 招待する (4) | **1.00** | 가이드상 새로 만드는 CTA 의 기본값은 동사형이라 `招待する` 를 채택했습니다. 표시 폭은 8 → 8 로 같아서 잘릴 위험은 낮습니다. 글자 수와 표시 폭 결과가 어긋나므로 화면 확인 항목으로 PR 에 적습니다. 대안은 `招待` (2, 0.50) |

참고로 ko 원문 `group.admin.member.body` 와 `group.admin.body` 는 뜻이 거의 같은 문구가 두 키에 있습니다(뒤/후에). 번역 범위 밖이라 고치지 않았고, 필요하면 원문 담당자에게 확인할 항목으로만 남깁니다.

---

## 2. error.hospital.staff.not-found — 영어가 나오지 않는 원인

### 원인

같은 키가 두 번들에 있습니다.

```
hospital/.../message-hospital.properties:12          (ko)
pasta-api/.../message-pasta-api.properties:40        (ko)
pasta-api/.../message-pasta-api_en_US.properties:40  (en)  ← 여기에 넣으셨음
```

`MessageSourceConfig.BASENAMES` 는 `message-hospital` 이 `message-pasta-api` 보다 앞에 있습니다. 영어 요청이 들어오면 처리 순서는 다음과 같습니다.

1. `message-hospital` 에서 en_US 번들을 조회합니다. 키가 없으므로 같은 basename 의 기본(한국어) 파일로 폴백하고, 거기서 값을 찾습니다.
2. 값을 찾았으므로 조회가 여기서 끝납니다. `message-pasta-api_en_US` 에는 도달하지 않습니다.

그래서 pasta-api 쪽 영어 번역은 처음부터 쓰일 수 없었습니다. 예외가 나지 않아서 원인이 드러나지 않았을 뿐입니다.

### 수정 — 승자 번들(message-hospital)에 번역 추가

```diff
# hospital/src/main/resources/messages/message-hospital_en_US.properties (12행 위치, 원문과 같은 자리)
+error.hospital.staff.not-found=Medical staff not found
```

```diff
# hospital/src/main/resources/messages/message-hospital_ja_JP.properties (같은 위치)
+error.hospital.staff.not-found=医療スタッフが見つかりません
```

- en: pasta-api 에 이미 있던 값을 재사용했습니다. 글자 수 비율은 16자 대비 23자로 1.44배입니다. 에러 메시지라 느슨하게 적용하지만, 짧은 대안 `Staff not found` (0.94)도 PR 에 함께 적습니다.
- ja: 14자, 0.88배로 통과입니다. 반영 전에 일본 서비스에 같은 키가 있는지 확인하고, 있으면 그 표기를 따르세요.
  ```bash
  JP=/Users/kakao/workplace-kakao/global/pasta-japan/server/pasta-japan-server
  grep -rn "^error.hospital.staff.not-found=" $JP --include="*_ja_JP.properties"
  ```
- 확인 필요: `message-hospital_en_US` / `_ja_JP` 에 이 키가 정말 없는지. 없다면 지금까지 parity 테스트를 통과한 이유는 `ALLOWED_MISMATCHES` 에 등록돼 있었기 때문일 가능성이 높습니다. 그렇다면 그 항목도 지워야 합니다(아래 3번).

### 적용하지 않은 방안

- **BASENAMES 순서 변경(pasta-api 를 앞으로 이동)**: 16개 번들 전체에서 중복 키의 승자가 바뀝니다. 이 키 하나를 위해 감수할 변경 범위가 아니라고 판단했습니다.
- **pasta-api 쪽 중복 정의 삭제**(ko·en 2개 파일의 40행): 지금은 도달하지 못하는 죽은 정의라서 남겨 두면 같은 혼란이 다시 생깁니다. 다만 키 삭제에 해당하므로 이번 커밋에는 넣지 않았습니다. 지우기로 결정하면 별도 커밋으로 처리하고, pasta-api 의 ja 파일에도 이 키가 없는지(허용 목록 항목 포함) 함께 정리해야 합니다.

---

## 3. MessageBundleLocaleParityTest 허용 목록

번역을 넣은 키의 허용 항목을 지우지 않으면 "죽은 항목"으로 판정되어 테스트가 실패합니다. 반대로 승인 대기 중인 키는 사유를 적어 등록해야 합니다.

```bash
grep -n "message-group\|error.hospital.staff.not-found" \
  pasta-api/src/test/**/MessageBundleLocaleParityTest.java
```

```diff
 ALLOWED_MISMATCHES = ...
-    // (있다면) message-group ja_JP :: group.admin.body / group.staff.title / group.invite.cta
-    // (있다면) message-hospital en_US / ja_JP :: error.hospital.staff.not-found
+    // message-group ja_JP :: group.leave.notice — 법무 확인 대기(탈퇴 시 데이터 삭제 고지). 담당 카드: <카드 번호>
```

`<카드 번호>` 는 법무 확인을 요청할 카드로 채워 주세요.

---

## 4. 검증 명령과 예상 결과

```bash
python3 scripts/check_parity.py --bundle message-group
python3 scripts/check_parity.py --bundle message-hospital
python3 scripts/check_ratio.py --bundle message-group --lang ja
python3 scripts/check_ratio.py --bundle message-hospital
./gradlew :pasta-api:test --tests "*MessageBundleLocaleParityTest*"   # JDK 21
```

| 검사 | 수정 전(예상) | 수정 후(예상) |
|---|---|---|
| check_parity message-group | `[누락] group.admin.body`, `[누락] group.staff.title`, `[파손] 招待を送る`, `[파손] メンバーを招待` | `[누락] group.leave.notice` 1건만 남음. 허용 목록에 등록했으므로 의도된 결과 |
| check_parity message-hospital | `[누락] en_US/ja_JP :: error.hospital.staff.not-found` | 0건 |
| check_ratio | — | `group.staff.title` 1.27, `group.invite.cta` 1.00, `error.hospital.staff.not-found`(en) 1.44 가 경고로 표시됨. 모두 PR 본문에 대안과 함께 기재 |
| ParityTest | 실패 | 통과(허용 목록 정리 후) |

커밋 후에 영어 로케일(`Accept-Language: en-US`)로 의료진 미존재 에러를 실제로 호출해서 `Medical staff not found` 가 나오는지도 확인해 주세요. 제보된 증상은 그 호출로만 해소 여부를 확인할 수 있습니다.

---

## 5. 커밋 구성 제안

1. `fix: message-group ja_JP 파손 복구 (역슬래시 흡수·후보 나열·메모 노출)`, 허용 목록 정리 포함
2. `fix: error.hospital.staff.not-found 번역을 우선 번들(message-hospital)에 반영`, 허용 목록 정리 포함
3. (선택, 별도 결정) pasta-api 의 중복 정의 제거

PR 본문에 남길 항목:
- `length:review` 대상: `group.staff.title`, `group.invite.cta`, `error.hospital.staff.not-found`(en). 각 키의 대안 포함
- 승인 대기: `group.leave.notice` ja 초안과 법무 확인 요청(삭제되는 데이터 범위 포함)
- ko 원문 확인 요청: `group.admin.member.body` / `group.admin.body` 중복 문구

## 확인된 것과 가정한 것

- **확인된 것**(주신 발췌 기준): 역슬래시로 인한 키 흡수, 후보 나열로 생긴 가짜 키, 메모 노출, 중복 키 2곳과 basename 순서
- **가정한 것**: 허용 목록에 group·hospital 관련 항목이 있는지, `message-hospital_en_US/_ja_JP` 파일 존재 여부, pasta-api ja 파일의 상태, 일본 서비스에 같은 키가 있는지. 모두 위 grep 명령으로 확인한 뒤 반영해 주세요.
