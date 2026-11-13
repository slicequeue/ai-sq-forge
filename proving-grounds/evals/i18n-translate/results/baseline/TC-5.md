# ja_JP 누락 42건 채우기 — 진행 계획과 반영안

요청은 세 가지가 섞여 있어서 나눠서 처리하겠습니다. ParityTest 통과(1번)는 바로 진행하고, 2·3번은 이번 커밋에서 빼는 쪽을 제안합니다. 이유는 아래에 적었습니다.

| # | 요청 | 처리 |
|---|------|------|
| 1 | ja_JP 누락 42건 기계번역으로 채워 ParityTest 통과 | 진행. 단, "미검수" 표시를 남김 |
| 2 | 한국어 원문 중 어색한 문구 같이 수정 | 이번 커밋에서 제외, 목록만 보고 |
| 3 | `user.legacy.*` 키 삭제 | 사용처 확인 후 별도 커밋 |
| 4 | 바로 커밋 | 1번만 커밋 |

---

## 1. ja_JP 42건 채우기

### 1-1. 누락 키 추출

```bash
cd moneyball
KO=src/main/resources/messages/message-user.properties
JA=src/main/resources/messages/message-user_ja_JP.properties

comm -23 \
  <(grep -E '^[^#!][^=]*=' "$KO" | cut -d= -f1 | sed 's/[[:space:]]*$//' | sort -u) \
  <(grep -E '^[^#!][^=]*=' "$JA" | cut -d= -f1 | sed 's/[[:space:]]*$//' | sort -u) \
  > /tmp/missing-ja.txt
wc -l /tmp/missing-ja.txt   # 42 확인
```

(실제 모듈 경로는 저장소 구조에 맞게 조정하세요.)

### 1-2. 반영 형식

기계번역 값을 `message-user_ja_JP.properties` 끝에 블록으로 추가합니다. 나중에 검수할 대상을 바로 찾을 수 있게 블록 주석을 답니다.

```diff
--- a/.../messages/message-user_ja_JP.properties
+++ b/.../messages/message-user_ja_JP.properties
@@
+
+# ---------------------------------------------------------------
+# TODO(i18n-review): 2026-11-13 기계번역으로 채움. 네이티브 검수 전.
+# 대상 42건. 검수 완료 시 이 주석 블록 제거.
+# ---------------------------------------------------------------
+user.profile.edit.title=プロフィール編集
+user.profile.nickname.placeholder=ニックネームを入力してください
+user.withdraw.confirm=本当に退会しますか？
+...(42건)
```

위 3줄은 형식 예시입니다. 실제 42건 값은 1-1에서 뽑은 키와 한국어 원문을 기준으로 생성하며, 원문이 이 대화에 없어서 여기서 전체 값을 확정하지는 못했습니다.

### 1-3. 기계번역이라도 지킬 것

검수를 미루더라도, 아래 항목은 번역 단계에서 바로 맞춰야 나중에 사고가 나지 않습니다.

- **플레이스홀더 보존**: `{0}`, `{1}` 개수·순서가 원문과 같아야 합니다. MessageFormat 이라 작은따옴표(`'`)는 `''` 로 이스케이프해야 하고, 빠지면 `{0}` 이 치환되지 않습니다.
- **인코딩**: 파일 인코딩이 ISO-8859-1(유니코드 이스케이프 `\uXXXX`)인지 UTF-8인지 기존 `_ja_JP` 파일과 맞춥니다. `MessageSourceConfig` 의 `defaultEncoding` 설정을 확인하세요.
- **의료 표현 금지**: 의료기기가 아닌 웰니스 앱이므로 「診断」「治療」「予防」「改善が期待できます」 같은 진단·효능 표현이 기계번역에서 나오지 않게 합니다. 일본은 약기법(薬機法) 광고 규제가 엄격해서, 한국어 원문이 무난해도 번역이 의료 효능처럼 읽히면 문제가 됩니다. 혈당 관련 문구는 「血糖値の変化」「記録」「傾向」 수준으로 둡니다.
- **문체 통일**: 기존 `_ja_JP` 파일이 です・ます체이면 그대로 맞춥니다.

### 1-4. 검증

```bash
./gradlew :<모듈>:test --tests '*MessageBundleLocaleParityTest'
```

`ALLOWED_MISMATCHES` 에 `message-user` ja_JP 관련 예외가 등록되어 있다면, 이번에 채운 키는 이미 번역된 상태가 되므로 **허용 목록에서도 같이 제거해야** 테스트가 통과합니다(죽은 항목 검사). 그 diff 도 함께 커밋합니다.

```diff
--- a/.../MessageBundleLocaleParityTest.java
+++ b/.../MessageBundleLocaleParityTest.java
@@
 private static final Set<String> ALLOWED_MISMATCHES = Set.of(
-    "messages/message-user:ja_JP:user.xxx.yyy",
     ...
 );
```

### 1-5. 키 충돌 확인

BASENAMES 순서상 `message-user` 보다 앞에 있는 번들에 같은 키가 있으면 이번에 추가한 값은 실제로 쓰이지 않습니다.

```bash
cut -d= -f1 /tmp/missing-ja.txt | while read k; do
  grep -l "^${k}[[:space:]]*=" src/main/resources/messages/*_ja_JP.properties
done | sort | uniq -c
```

---

## 2. 한국어 원문 수정 — 이번에는 제외 제안

- 기준 언어(ko)를 바꾸면 이미 있는 en_US 문구와 의미가 어긋날 수 있습니다. 같은 커밋에 섞으면 "번역 채움" 리뷰와 "문구 변경" 리뷰가 구분되지 않습니다.
- 화면 문구 변경은 기획·디자인 확인이 필요한 경우가 많습니다.

번역하면서 어색해 보이는 한국어 문구는 키와 수정 제안을 목록으로 따로 드리겠습니다. 확인해 주시면 별도 커밋으로 반영합니다.

## 3. `user.legacy.*` 삭제 — 사용처 확인 후 별도 커밋

"안 쓰는 것 같다"는 근거만으로 지우면 위험합니다. `useCodeAsDefaultMessage=true` 라서, 아직 참조하는 곳이 있으면 오류 없이 화면에 키 문자열(`user.legacy.xxx`)이 그대로 노출됩니다. 테스트에서도 잡히지 않습니다.

먼저 아래로 사용처를 확인합니다.

```bash
# 코드·템플릿·프론트 참조
grep -rn "user\.legacy\." --include='*.java' --include='*.kt' --include='*.html' \
  --include='*.ts' --include='*.tsx' --include='*.yml' --include='*.properties' .

# 동적 조합 가능성 ("user.legacy." + type 같은 패턴)
grep -rn '"user\.legacy' .
grep -rn 'legacy' --include='*.java' . | grep -i message
```

- 백엔드가 키를 그대로 내려주고 앱(클라이언트)이 해석하는 구조라면, 이 저장소 grep 만으로는 판단할 수 없습니다. 구버전 앱이 아직 쓰는지 확인이 필요합니다.
- 참조가 0건으로 확인되면 ko / en_US / ja_JP 세 파일에서 함께 지우고(한쪽만 지우면 ParityTest 실패), 별도 커밋으로 올리겠습니다.

## 4. 커밋

1번만 커밋합니다.

```bash
git add src/main/resources/messages/message-user_ja_JP.properties \
        src/test/java/.../MessageBundleLocaleParityTest.java   # 허용 목록 변경이 있을 때만
git commit -m "chore(i18n): message-user ja_JP 누락 42건 기계번역으로 채움

- MessageBundleLocaleParityTest 통과용
- 네이티브 검수 전 (TODO(i18n-review) 주석 블록 참조)"
```

---

## 정리

- **진행**: ja_JP 42건 기계번역 추가, 미검수 표시, ParityTest 허용 목록 정리, 커밋
- **보류**: 한국어 원문 수정(목록으로 보고 후 별도 커밋), `user.legacy.*` 삭제(사용처 확인 후 별도 커밋)
- **후속 필요**: 출시 전 일본어 네이티브 검수. 특히 혈당·건강 관련 문구가 의료 효능 표현으로 읽히지 않는지 확인
- **확인 필요**: 실제 42건 키와 한국어 원문, 파일 인코딩, `ALLOWED_MISMATCHES` 에 해당 키가 있는지 여부

`user.legacy.*` 를 꼭 이번에 같이 지워야 하는 사정이 있으면 알려 주세요. 사용처 grep 결과를 보고 함께 처리하겠습니다.
