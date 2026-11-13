# message-user ja_JP 누락 42건 — 처리 방식

요청 4가지 중 바로 할 수 있는 것은 **ja_JP 42건을 채우고 ParityTest 를 통과시키는 것** 하나다. 나머지 셋은 이번 커밋에 넣지 않는다. 이유와 대신 하는 일을 먼저 적고, 실행 계획을 이어서 적는다.

## 1. 요청별 처리

| 요청 | 처리 | 이유 |
|---|---|---|
| ja_JP 42건 기계번역으로 채우기 | **번역은 한다. 검수 없는 기계번역 일괄 반영은 하지 않는다** | 아래 1-1 |
| ParityTest 만 통과 | 통과시킨다. 단 "통과만 시키는" 방법은 쓰지 않는다 | 아래 1-2 |
| 한국어 원문 어색한 것 같이 고치기 | **고치지 않는다.** 수정안만 PR 본문에 남긴다 | 번역팀 가이드 플로우가 `검수 → 디자이너 승인 → 번역`. 원문 자동 수정 금지 |
| `user.legacy.*` 키 삭제 | **이번 작업에서 빼고 별도로 처리한다** | 키는 코드가 참조하는 식별자다. 삭제는 코드 변경을 동반하고 번역 작업 범위 밖이다 |
| 바로 커밋 | 번역분만 커밋한다. 의학·법무 문구가 섞여 있으면 그 키는 허용 목록에 사유를 달고 남긴다 | 아래 1-3 |

### 1-1. 기계번역을 그대로 넣지 않는 이유

- 이 저장소에서 기계번역 오역이 실제로 배포됐다. 쌍화차 → `ダブルデッキバス`, 신선로 → `フレッシュロード`, 규카츠 → `キツネカツ`. 음식명·증상명은 오역이 사용자 판단에 직접 영향을 준다.
- `useCodeAsDefaultMessage=true` 라서 지금은 누락 키가 한국어로 폴백된다. 잘못된 일본어가 들어가면 그 폴백보다 나빠지고, 일단 들어가면 ParityTest 가 통과하므로 **다시는 어떤 검사에도 걸리지 않는다.** "검수는 나중에"가 사실상 "검수 안 함"이 되는 구조다.
- 앱은 의료기기가 아닌 웰니스 앱이다. 기계번역은 `低血糖`/`高血糖`, 단정형(`〜です`) 같은 진단성 표현을 그대로 만든다. 가이드상 `目標範囲より低い`, `〜の傾向があります` 로 바꿔야 하는 규제 대응 항목이다.

시간은 가이드의 3-pass(파악 → 백지 작성 → 대조)와 출력 전 자기 검수 12항목을 돌리는 것으로 충분히 맞출 수 있다. 사람 검수를 따로 기다리는 단계가 아니라 번역 단계 안에서 끝나는 절차다.

### 1-2. "통과만 시키는" 방법을 쓰지 않는 이유

ParityTest 는 **키 집합만** 본다. 그래서 아래 방법으로도 통과한다.

- 한국어 값을 ja_JP 에 그대로 복사
- 42개 키를 `ALLOWED_MISMATCHES` 에 일괄 등록

둘 다 테스트는 초록이지만 일본 사용자에게 한국어가 노출되거나, 누락이 영구 허용된다. 쓰지 않는다. `check_parity.py` 와 자기 검수 10번(한글 잔존)으로 한국어 복사본이 섞이지 않았는지 확인한다.

### 1-3. 승인 게이트

42건 중 아래 유형이 있으면 **초안만 PR 본문에 남기고 파일에 넣지 않는다.** 해당 키는 `ALLOWED_MISMATCHES` 에 사유와 담당 카드를 적어 등록한다.

| 유형 | 확인 주체 | message-user 에서 나올 법한 예 |
|---|---|---|
| 법정 고지 | 법무·개인정보보호 | 개인정보 이용·제공 내역, 탈퇴 시 데이터 처리 |
| 약관·면책 | 법무 | 약관 동의, 개정 안내 |
| 의학적 권고 | 의학 검수 | 혈당 구간별 행동 권고 |
| 약물·증상·질환명 | 의학 검수 | 당뇨 유형, 복약 정보 |

## 2. 실행 계획

### 2-1. 누락 키 추출과 분류

```bash
# 누락 키와 파손 여부 확인 (42건이 실제로 맞는지 먼저 본다)
python3 scripts/check_parity.py --bundle message-user

# 다른 번들에 같은 키가 있는지 확인 — 앞쪽 번들이 이기므로 message-user 에 넣어도 무효일 수 있다
# BASENAMES 순서상 message-user 앞에는 messages/message, messages/message-ai 가 있다
for k in $(<누락 키 목록>); do grep -rn "^$k=" --include="*.properties" . ; done

# 키 노출 위치 확인 (버튼/타이틀이면 길이 기준을 엄격하게)
grep -rn "<키>" --include="*.java" user/ pasta-api/
```

일본 서비스에 같은 키가 있으면 그 표기를 우선 참고한다(키 이름 일치 1,176건).

```bash
JP=/Users/kakao/workplace-kakao/global/pasta-japan/server/pasta-japan-server
grep -n "^<키>=" $JP/shared/src/main/resources/messages/message-shared_ja_JP.properties
```

분류 결과는 세 묶음으로 나눈다.

1. 일반 UI 문구 → 이번 커밋에 반영
2. 승인 게이트 대상 → 초안만, 허용 목록 유지
3. 다른 번들에 이미 있어 무효인 키 → 보고만

### 2-2. 번역 작성 기준 (ja)

- 3-pass: 원문에서 사실·판단·요청 행동만 뽑고, 원문 문장 경계를 버리고 백지에서 쓴다
- 혈당 표기: CGM 측정값·그래프는 `グルコース値`, 생리학적 개념·CGM 데이터 없는 안내는 `血糖値`. 인접 키 표기에 맞춘다
- 표준 내비게이션은 고정 사전(`確認`, `次へ`, `戻る`, `キャンセル`)
- 버튼·라벨 끝 `。` 없음, 물음표·느낌표는 전각
- 「〜することができます」 → 「〜できます」, 「〜について」 → 조사
- 회원 → `会員`, 설정 → `設定`, 구독 해지 버튼 → `キャンセル`, 각주 → `解約`
- 플레이스홀더 `{0}` 개수·종류 원문과 동일, 스타일 태그만 있는 값은 그대로 복사
- 출력 전 자기 검수 12항목을 키마다 순서대로 돌린다

### 2-3. 파일 반영 방식

- 키는 **기본 번들과 같은 위치**에 넣는다. 파일 끝에 몰아 붙이지 않는다
- 여러 줄 값은 줄 끝 `\` 를 확인한다. 번역이 짧아져 줄이 줄었는데 `\` 가 남으면 바로 아래 키가 흡수된다
- 후보 문구·번역 메모는 값에 쓰지 않고 `#` 주석으로만

반영 예시 형태(실제 값은 2-1 추출 후 확정):

```diff
 # user/src/main/resources/messages/message-user_ja_JP.properties
 user.profile.edit.title=プロフィール編集
+user.profile.nickname.label=ニックネーム
+user.profile.nickname.invalid=ニックネームは2〜10文字で入力してください。
 user.profile.save.button=保存
```

```diff
 // MessageBundleLocaleParityTest.java — 번역을 넣은 키는 허용 목록에서 반드시 뺀다
 private static final Set<String> ALLOWED_MISMATCHES = Set.of(
-    "messages/message-user:ja_JP:user.profile.nickname.label",
-    "messages/message-user:ja_JP:user.profile.nickname.invalid",
     ...
+    // 의학 검수 대기 — <카드 번호>
+    "messages/message-user:ja_JP:<승인 게이트 키>",
 );
```

허용 목록에서 빼지 않으면 "죽은 항목" 검사로 테스트가 실패한다. 번역 반영과 허용 목록 정리는 한 작업이다.

### 2-4. 검사

```bash
python3 scripts/check_ratio.py --bundle message-user --lang ja   # 0.9배 초과 시 짧은 대안 병기
python3 scripts/check_parity.py --bundle message-user            # 키 일치 + 파손 줄
./gradlew :pasta-api:test --tests "*MessageBundleLocaleParityTest*"   # JDK 21
```

`check_ratio.py` 에서 글자 수는 통과인데 표시 폭이 크게 튀는 키는 화면 확인이 필요하다. 여기서는 태그 기능이 없으므로 PR 본문에 키 목록으로 남긴다.

### 2-5. 커밋

```bash
git add user/src/main/resources/messages/message-user_ja_JP.properties \
        <MessageBundleLocaleParityTest 경로>
git commit -m "feat: message-user ja_JP 누락 번역 반영"
```

한국어 기본 번들(`message-user.properties`)은 이 커밋에 포함하지 않는다. `git diff --stat` 으로 ko 파일 변경이 없는지 확인한 뒤 커밋한다.

## 3. 이번 작업에서 뺀 것 — 후속 처리 제안

### 한국어 원문 수정

번역하면서 걸리는 원문은 PR 본문에 `현재 → 수정안 → 근거(가이드 ## ko 항목)` 형태로 남긴다. 승인되면 ko·en·ja 를 같이 고친다. 원문이 바뀌면 이미 넣은 en/ja 도 다시 맞춰야 하므로, 승인 전에 원문만 먼저 바꾸면 세 언어가 어긋난다.

종결 형태 일관성은 같은 접두사 그룹을 한 번에 봐야 판단할 수 있어, 그룹 단위로 묶어서 제안한다.

### `user.legacy.*` 삭제

"안 쓰는 것 같다"는 확인되지 않은 상태다. 별도 브랜치에서 아래를 확인한 뒤 진행할 것을 권한다.

```bash
# 코드 참조 — 문자열 조합으로 키를 만드는 경우도 있어 접두사로도 찾는다
grep -rn "user\.legacy" --include="*.java" --include="*.kt" --include="*.html" .
grep -rn "\"user\.legacy\.\|legacy\.\" *+" --include="*.java" .
# 다른 번들 중복 여부
grep -rn "^user\.legacy\." --include="*.properties" .
```

참조가 없으면 ko/en_US/ja_JP 세 파일에서 동시에 지우고, `ALLOWED_MISMATCHES` 에 걸린 항목도 같이 정리하는 별도 PR 로 올린다. 앱 클라이언트나 서버 응답이 키를 그대로 내려주는 경로가 있으면 grep 으로 안 잡히므로 클라이언트 담당자 확인도 필요하다.

## 4. 확인된 것과 가정한 것

| 구분 | 내용 |
|---|---|
| 확인 | 폴백 구조(`useCodeAsDefaultMessage=true`), ParityTest 가 키 집합과 죽은 허용 항목을 검사, 앞쪽 basename 우선 |
| 확인되지 않음 | 누락 42건의 실제 키와 원문, 그중 의학·법무 문구 비율, `user.legacy.*` 참조 여부 |
| 가정 | 위 diff 의 키 이름과 값은 형식 예시다. 실제 값은 2-1 추출 후 확정한다 |

42건 목록(`check_parity.py --bundle message-user` 출력)을 주면 바로 번역안을 키별로 만들고, 승인 게이트 대상과 길이 초과 키를 나눠서 돌려주겠다.
