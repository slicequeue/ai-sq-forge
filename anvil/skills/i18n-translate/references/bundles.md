# 메시지 번들 지도

`MessageSourceConfig.BASENAMES` 에 등록된 16개가 전부다. 번들을 추가·제거하면 이 상수만 고치면 되고, 정합성 검증 테스트가 그 목록을 그대로 순회한다.

## 번들과 소유 모듈

| basename | 파일 위치 |
|---|---|
| `messages/message` | `api/src/main/resources/messages/` |
| `messages/message-ai` | `ai/` |
| `messages/message-user` | `user/` |
| `messages/message-cgm` | `cgm/` |
| `messages/message-community` | `commerce/` |
| `messages/message-social` | `social/` |
| `messages/message-shared` | `shared/` |
| `messages/message-notification` | `notification/` |
| `messages/message-analysis` | `analysis/` |
| `messages/message-pghd` | `pghd/` |
| `messages/message-hospital` | `hospital/` |
| `messages/message-commerce` | `commerce/` |
| `messages/message-group` | `group/` |
| `messages/message-obesity` | `obesity/` |
| `messages/message-obesity-nudging` | `obesity/` |
| `messages/message-pasta-api` | `pasta-api/` |

각 번들은 기본(한국어), `_en_US`, `_ja_JP` 세 파일을 갖는다. 키를 추가할 때 세 파일을 동시에 손대야 한다.

## 함정 셋

**basename 순서가 중복 키의 승자를 정한다.** `setBasenames` 에 등록된 순서대로 조회하고, 앞쪽에서 값을 찾으면 멈춘다. 같은 키가 두 번들에 있으면 뒤쪽 번들의 번역은 절대 도달하지 못한다.

실제 사례로 `error.hospital.staff.not-found` 가 `message-hospital`(한국어만)과 `message-pasta-api`(3개 로케일)에 모두 있었다. hospital 이 앞이라 영어 요청이 hospital 에서 한국어로 폴백하고 끝났다. pasta-api 의 영어 번역은 쓰이지 않았다. 번역을 넣기 전에 다른 번들에 같은 키가 있는지 먼저 확인한다.

```bash
grep -rn "키이름" --include="*.properties" .
```

**`messages/message` 는 `api` 와 `batch` 두 모듈에 파일이 있다.** 클래스패스에 어느 쪽이 먼저 오느냐로 승자가 갈린다. pasta-api 런타임에서는 `api` 쪽이 쓰인다. `batch` 쪽을 고쳐도 API 응답에는 반영되지 않는다.

**`messages/message-obesity-nudging` 은 세 파일 모두 0바이트다.** 넛징 문구는 `obesity_nudging_message` 테이블의 `message` / `message_en` / `message_ja` 컬럼으로 옮겨갔다. 이 번들에 키를 넣지 말고 DB 쪽을 본다.

## 폴백 동작

`ResourceBundleMessageSource` 에 `useCodeAsDefaultMessage=true` 가 걸려 있다. 로케일 번들에 키가 없으면 예외 없이 기본(한국어) 번들 값을 돌려준다. 그래서 번역 누락이 빌드·테스트·런타임 어디에서도 드러나지 않는다. 파일을 직접 비교하는 것 말고는 잡을 방법이 없고, 그래서 `MessageBundleLocaleParityTest` 가 있다.

## DB 쪽 다국어

메시지 번들 말고 DB 컬럼으로 다국어를 갖는 곳이 따로 있다. 언어 키 JSON(`{"ko":..,"en":..,"ja":..}`), 언어코드 접미 컬럼(`_en`, `_ja`), 행 단위 언어 분리 세 가지 방식이 혼재한다. 번들과 규칙이 다르니 노션 `DB 다국어 필드 조사` 문서를 본다.

특히 `pghd_food.language_names` 는 **언어 키를 비워 두는 것이 검색 색인에서 제외하는 장치**다. 한국 프랜차이즈 메뉴와 GS1 바코드 상품은 의도적으로 번역하지 않는다. 결손으로 오해하고 채우면 해외 사용자 검색에 한국 전용 항목이 노출된다.
