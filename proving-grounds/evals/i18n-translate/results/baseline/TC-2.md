# 번역 검토 결과 (message-notification / message-pghd)

## 요약

| 키 | 로케일 | 판정 | 사유 |
|---|---|---|---|
| alarm.claim.done.title | en | 수정 | 제목인데 문장형으로 너무 길고 "successfully"가 군더더기다. 한국어 원문("위임 등록 완료")의 간결한 톤과 맞지 않는다 |
| alarm.claim.done.title | ja | 수정 | 제목인데 "正常に完了いたしました"는 과한 경어 문장형이다. 원문에 없는 "正常に"가 추가됐다 |
| nutrition.intake.ratio.body | en | 수정 | "compared to ... amount"가 직역투이고 장황하다 |
| nutrition.intake.ratio.body | ja | 유지 | 자연스럽고 정확하다 |
| glucose.trend.stable.body | en | 경미 수정 | CGM 앱 용어로는 "blood sugar"보다 "glucose (levels)"가 일관적이다. "generally"는 "mostly"가 원문 "대체로" 뉘앙스에 가깝다 |
| glucose.trend.stable.body | ja | 수정 | "安定的です"는 부자연스럽다. 원문의 "대체로"가 누락됐다 |
| 모든 키 | ko | 유지 | 원문 기준 |

키를 추가하거나 삭제하지 않고 값만 바꾸므로 ko/en_US/ja_JP 키 집합은 그대로다. `MessageBundleLocaleParityTest`와 `ALLOWED_MISMATCHES`는 손댈 필요가 없다.

## 반영 diff

### messages/message-notification_en_US.properties
```diff
-alarm.claim.done.title=Assisted claim filing registered successfully
+alarm.claim.done.title=Claim delegation registered
```

### messages/message-notification_ja_JP.properties
```diff
-alarm.claim.done.title=委任登録が正常に完了いたしました
+alarm.claim.done.title=委任登録完了
```

### messages/message-pghd_en_US.properties
```diff
-nutrition.intake.ratio.body=You have consumed {0}% compared to the recommended daily intake amount.
+nutrition.intake.ratio.body=You have consumed {0}% of your recommended daily intake.
```

### messages/message-pghd_en_US.properties
```diff
-glucose.trend.stable.body=Your blood sugar is generally stable today.
+glucose.trend.stable.body=Your glucose levels are mostly stable today.
```

### messages/message-pghd_ja_JP.properties
```diff
-glucose.trend.stable.body=今日の血糖値は安定的です。
+glucose.trend.stable.body=今日の血糖値はおおむね安定しています。
```

## 주의 사항

1. **MessageFormat 작은따옴표**: `{0}`처럼 인자가 있는 메시지는 `MessageFormat`으로 처리되므로 작은따옴표(`'`)가 이스케이프 문자로 동작한다. 그래서 `nutrition.intake.ratio.body` 영어를 "You've consumed"로 줄이지 않고 "You have consumed"로 유지했다. 축약형을 쓰려면 `You''ve`로 써야 한다.
2. **"위임 등록"의 영어 표현**: 원문 의미를 "청구 위임(대리 청구) 등록"으로 해석해 "Claim delegation registered"로 옮겼다. 기존 화면·다른 키에서 같은 기능을 "Assisted claim filing"으로 통일해 쓰고 있다면 용어 일관성을 위해 `Assisted claim filing registered`로 대신 써도 된다. 아래 grep으로 기존 용어 사용 현황을 확인한 뒤 확정하기를 권한다.
3. **웰니스 앱 표현**: 의료기기가 아니므로 진단·판정처럼 읽히는 표현("정상", "normal" 등)은 넣지 않았다. 수정안은 모두 상태를 서술하는 수준이다.
4. **번들 우선순위 가림 여부**: basename은 앞쪽 번들이 이기므로, 같은 키가 더 앞선 번들(예: message-hospital)에 존재하면 이번 수정이 화면에 반영되지 않는다. 아래 명령으로 중복 정의 여부를 확인한다.
5. **파일 인코딩**: 일본어 값을 그대로 넣었다. 기존 파일이 `\uXXXX` 이스케이프 방식이라면 같은 방식으로 변환해야 하고, UTF-8 원문 방식이면 그대로 둔다(`spring.messages.encoding` 설정과 기존 파일 형식을 따른다).

## 확인·검증 명령

```bash
# 같은 키가 다른 번들에도 정의돼 있는지(우선순위로 가려지는지) 확인
grep -rn --include='*.properties' -E '^(alarm\.claim\.done\.title|nutrition\.intake\.ratio\.body|glucose\.trend\.stable\.body)=' .

# 위임 관련 영어 용어 일관성 확인
grep -rn --include='*_en_US.properties' -iE 'delegat|assisted claim' .

# 파일 인코딩 형식 확인(유니코드 이스케이프 여부)
grep -c '\\u' $(find . -path '*messages/message-pghd_ja_JP.properties')

# 키 집합 일치 테스트
./gradlew test --tests '*MessageBundleLocaleParityTest'
```

## 보고

- 수정 5건(en 3건, ja 2건), 유지 4건(ko 3건, ja 1건).
- 키 추가·삭제 없음. 패리티 테스트와 허용 목록 변경 불필요.
- 확인 필요: "위임 등록" 영어 용어를 기존 화면과 통일할지 여부, 상위 번들에 같은 키가 있는지 여부.
