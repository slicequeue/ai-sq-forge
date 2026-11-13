# 번역 붙여넣기 정리 + error.hospital.staff.not-found 영어 미노출 원인

두 문제 모두 원인을 찾았습니다. 하나씩 적고, 마지막에 반영 diff, 실행할 명령, 확인이 필요한 항목을 정리합니다.

---

## 1. message-group_ja_JP.properties 테스트가 깨진 원인

번역가가 넘긴 텍스트에 `.properties` 문법상 문제가 3가지 섞여 있습니다. 화면에서는 티가 거의 안 나고, 키 집합 비교를 하는 `MessageBundleLocaleParityTest` 에서만 드러나서 "이상하게" 깨진 것처럼 보입니다.

### 1-1. 줄 끝 `\` 때문에 키 2개가 사라짐 (가장 큰 원인)

```
group.admin.member.body=管理者権限の移管後、退会できます。\
group.admin.body=管理者権限の移管後に退会できます。\
group.staff.title=リンクされたメンバーがいます。
```

`.properties` 에서 줄 끝 `\` 는 **다음 줄로 이어 쓰기**입니다. 그래서 실제로 파싱되는 결과는 아래와 같습니다.

| 키 | 실제 값 |
|---|---|
| `group.admin.member.body` | `管理者権限の移管後、退会できます。group.admin.body=管理者権限の移管後に退会できます。group.staff.title=リンクされたメンバーがいます。` |
| `group.admin.body` | **없음** |
| `group.staff.title` | **없음** |

- 테스트 실패: ja_JP 에 `group.admin.body`, `group.staff.title` 이 없음
- 런타임 영향: `useCodeAsDefaultMessage=true` 라서 예외 없이 **일본 사용자에게 한국어가 그대로 노출**되고, `group.admin.member.body` 화면에는 키 문자열이 섞인 긴 문장이 나옵니다.

### 1-2. 번역 후보 2줄이 키로 들어감

```
group.invite.cta=招待する
招待を送る
メンバーを招待
```

`=`·`:` 가 없는 줄은 **줄 전체가 키이고 값은 빈 문자열**로 읽힙니다. 그래서 ja_JP 에만 `招待を送る`, `メンバーを招待` 라는 키 2개가 추가되어 키 집합이 어긋납니다. 번역가가 대안 문구를 같이 적어 준 것으로 보입니다.

- 정리 방향: 한국어 `초대하기` 와 1:1 대응이고 이미 키에 붙어 있는 `招待する` 를 유지하고 후보 2줄은 삭제합니다.
- 다른 후보로 바꿀지는 문구 결정이므로 번역가/기획 확인 대상으로 남깁니다(아래 4장).

### 1-3. 번역가 메모가 값에 섞여 들어감

```
group.leave.notice=退会するとデータは削除されます 번역가 메모: 법무 확인 필요?
```

테스트는 통과하지만(키는 같음), **일본 사용자 화면에 한국어 메모가 그대로 노출**됩니다. 메모는 값에서 빼고, 요청 내용(법무 확인)은 PR 본문/이슈로 옮깁니다.

- 데이터 삭제 고지 문구라서 법무 확인 요청 자체는 타당합니다. 일본 출시 대상이므로 개인정보보호법(APPI) 관점 문구 검토가 필요할 수 있습니다. 이 확인은 제가 판단할 사항이 아니라서, 문구는 번역가 안대로 두고 확인 대기 항목으로 표시합니다.

### 1-4. 그 밖에 눈에 띈 것 (수정하지 않음, 보고만)

- `group.staff.title`: 한국어는 마침표 없음(`연결된 멤버가 있어요`), 일본어는 `。` 로 끝남. 제목 키라면 `。` 를 빼는 편이 다른 로케일과 맞지만 문구 결정이라 보류.
- `group.admin.member.body` 와 `group.admin.body` 는 한국어·일본어 모두 거의 같은 문장입니다. 어느 한쪽이 안 쓰이는 키일 수 있지만 이번 범위가 아니므로 정리하지 않았습니다.

---

## 2. error.hospital.staff.not-found 가 계속 한국어로 나오는 원인

### 원인: 앞 번들(message-hospital)의 한국어 기본 파일이 먼저 이긴다

`ResourceBundleMessageSource` 는 `BASENAMES` 순서대로 번들을 하나씩 조회하는데, 번들 하나를 조회할 때 **그 번들 안에서 로케일 폴백을 끝까지 수행**합니다.

en_US 요청 시 실제 조회 순서:

1. `messages/message-hospital` 번들
   - `message-hospital_en_US.properties` 에 키 없음 (grep 결과에 없음)
   - 같은 번들의 부모인 `message-hospital.properties`(한국어) 에서 **키 발견** → `의료진 정보를 찾을 수 없어요` 반환, 조회 종료
2. `messages/message-pasta-api` (마지막 순서) 까지 **도달하지 않음**

그래서 `message-pasta-api_en_US.properties:40` 에 영어를 넣어도 절대 사용되지 않습니다. `useCodeAsDefaultMessage` 와는 무관하고, 순서와 번들 내 폴백 때문입니다.

### 수정 방향

키의 원본 소유 번들은 `message-hospital` 입니다(키 접두어 `error.hospital.*`, 모듈 `hospital`). 번역은 그 번들에 넣어야 합니다.

1. `hospital/.../message-hospital_en_US.properties` 에 영어 추가
2. `hospital/.../message-hospital_ja_JP.properties` 에도 일본어 추가 (없다면 일본 사용자도 같은 문제)
3. `pasta-api` 쪽에 넣은 중복 키(ko 40행, en_US 40행)는 **어차피 도달하지 않는 죽은 정의**이므로 제거
   - 단, pasta-api 가 hospital 모듈 없이 단독 기동되는 경우가 있으면 제거하면 안 됩니다. 아래 확인 명령으로 의존 관계를 먼저 봅니다.
4. `ALLOWED_MISMATCHES` 에 `message-hospital` 의 이 키(또는 en_US/ja_JP 누락)가 예외로 등록되어 있었다면, 번역을 채운 순간 **죽은 항목이 되어 테스트가 실패**하므로 같이 지웁니다. pasta-api 쪽 중복을 지울 때도 동일하게 확인합니다.

참고: hospital en_US 가 빠져 있는데 지금까지 parity 테스트가 통과했다면, 이 키가 허용 목록에 등록돼 있었을 가능성이 높습니다(추정, 확인 필요).

---

## 3. 반영할 diff

### 3-1. `<모듈>`/src/main/resources/messages/message-group_ja_JP.properties

모듈 경로는 grep 으로 확인 후 적용합니다. 해당 부분만 교체하고 파일 나머지는 건드리지 않습니다.

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
+group.staff.title=リンクされたメンバーがいます。
+group.invite.cta=招待する
+group.leave.notice=退会するとデータは削除されます
```

주의: 줄 끝 `\` 뒤에 공백이 숨어 있거나, 붙여넣기 과정에서 전각 공백·NBSP·CRLF 가 들어왔을 수 있습니다. 아래 명령으로 눈에 안 보이는 문자까지 확인합니다.

### 3-2. hospital/src/main/resources/messages/message-hospital_en_US.properties

```diff
+error.hospital.staff.not-found=Medical staff not found
```

(pasta-api en_US 에 넣었던 문구를 그대로 옮김. 기존 en_US 에러 문구 톤이 "Could not find ..." 식이면 그에 맞춥니다.)

### 3-3. hospital/src/main/resources/messages/message-hospital_ja_JP.properties

ja_JP 에도 키가 없는 경우에만 추가합니다.

```diff
+error.hospital.staff.not-found=医療スタッフの情報が見つかりません
```

이 일본어는 제가 쓴 초안입니다. 번역가 확인 대상입니다.

### 3-4. pasta-api 중복 제거 (의존 관계 확인 후)

```diff
# pasta-api/src/main/resources/messages/message-pasta-api.properties
-error.hospital.staff.not-found=의료진 정보를 찾을 수 없어요
# pasta-api/src/main/resources/messages/message-pasta-api_en_US.properties
-error.hospital.staff.not-found=Medical staff not found
```

pasta-api ja_JP 에도 같은 키가 있으면 함께 제거합니다(키 집합 일치 유지).

### 3-5. MessageBundleLocaleParityTest.ALLOWED_MISMATCHES

`error.hospital.staff.not-found` 관련 항목이 있으면 삭제합니다. 없으면 변경 없음. group 쪽 문제를 허용 목록에 추가해서 통과시키는 방식은 쓰지 않습니다(실제 버그를 가리는 것이라서).

---

## 4. 실행할 명령

```bash
# 0) 현재 변경 범위 확인 (번역 외 다른 변경이 섞여 있지 않은지)
git status
git diff --stat

# 1) group ja_JP: 줄 끝 백슬래시, '=' 없는 줄, 한글 혼입, 숨은 문자 점검
F=$(git ls-files '*message-group_ja_JP.properties')
grep -n '\\[[:space:]]*$' "$F"                         # 이어쓰기 줄
grep -nv '^[[:space:]]*\(#\|!\|$\)' "$F" | grep -v '[=:]'  # 키=값 아닌 줄
grep -nP '[\x{AC00}-\x{D7A3}]' "$F"                     # 일본어 파일 안의 한글
grep -nP '[\x{00A0}\x{3000}\r]' "$F"                    # NBSP/전각공백/CR
file "$F"                                               # 인코딩 확인

# 같은 패턴이 다른 번역 파일에도 들어왔는지 (이번 붙여넣기 범위 확인)
git diff --name-only -- '*.properties' | xargs grep -nP '[\x{AC00}-\x{D7A3}]' -- 2>/dev/null | grep -E '_(en_US|ja_JP)\.properties'

# 2) hospital 키 현황
grep -rn 'error.hospital.staff.not-found' --include='*.properties' .
grep -rn 'error.hospital.staff.not-found\|message-hospital' --include='MessageBundleLocaleParityTest.java' .
grep -rn 'BASENAMES' --include='MessageSourceConfig.java' -A 25 .

# 3) pasta-api 가 hospital 모듈을 항상 포함하는지 (중복 제거 가능 여부)
grep -n 'hospital' pasta-api/build.gradle*

# 4) 테스트 (모듈명은 테스트 위치 확인 후)
./gradlew :<parity-test-module>:test --tests '*MessageBundleLocaleParityTest'
```

검증 기준:
- parity 테스트 통과
- en_US 로케일로 `error.hospital.staff.not-found` 조회 시 영어 반환. 가능하면 아래 단언을 기존 메시지 테스트에 한 줄 추가해 재발을 막습니다.

```java
assertThat(messageSource.getMessage("error.hospital.staff.not-found", null, Locale.US))
    .isEqualTo("Medical staff not found");
```

---

## 5. 커밋

번역 정리와 버그 수정은 성격이 달라 커밋을 나눕니다.

```bash
git add <group ja_JP 경로>
git commit -m "fix: 그룹 일본어 번역 파일 이어쓰기·후보 문구·메모 혼입 정리"

git add hospital/src/main/resources/messages/ pasta-api/src/main/resources/messages/ <ParityTest 경로>
git commit -m "fix: error.hospital.staff.not-found 번역을 원본 번들(message-hospital)로 이동"
```

---

## 6. 확인된 사실 vs 추정 / 확인 필요

**확인된 것 (제공된 발췌·grep 기준)**
- ja_JP 발췌의 줄 끝 `\` 2개, `=` 없는 줄 2개, 값 안의 한국어 메모 1개
- `error.hospital.staff.not-found` 는 hospital ko, pasta-api ko, pasta-api en_US 에만 존재. hospital en_US 에는 없음
- `message-hospital` 이 `message-pasta-api` 보다 앞 순서

**추정 (확인 필요)**
- properties 파일 인코딩이 UTF-8 이고 `defaultEncoding` 이 맞게 설정되어 있음 (기존 ja_JP 가 정상 표시된다면 맞음)
- hospital ja_JP 에도 키가 없음, 허용 목록에 이 키가 등록되어 있음
- pasta-api 는 항상 hospital 모듈과 함께 기동됨 (아니면 3-4 중복 제거 보류)

**사람이 결정할 것**
- `group.invite.cta`: `招待する` 유지 vs `招待を送る` / `メンバーを招待` (번역가·기획)
- `group.leave.notice`: 법무 확인 요청 전달 (데이터 삭제 고지, 일본 출시). 확인 전까지 현재 문구로 배포해도 되는지
- `error.hospital.staff.not-found` 일본어 초안 검수
- `group.staff.title` 의 `。` 유무
