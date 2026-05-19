---
name: tolgee
description: "Tolgee i18n 콘솔과 properties 파일을 동기화한다. 'tolgee push', 'tolgee pull', 'tolgee diff', '톨지 푸시', '톨지 풀', '톨지 동기화', '톨지 키 등록', '톨지 정합성 검증', 'i18n 콘솔 업로드', 'i18n 키 누락 확인' 요청 시 사용한다. dev-global Tolgee 셀프호스팅(pasta-global, project id 2) 기준으로 push/pull/diff 워크플로를 표준화한다. 토큰은 프로젝트 .env에서 읽고, push는 안전을 위해 항상 키 prefix·키 목록 명시 + KEEP 모드를 기본으로 한다."
version: "0.1"
last-modified: "2026-05-19"
---

# tolgee — i18n 콘솔 동기화 스킬

> 트리거: "톨지 푸시/풀/diff", "tolgee push/pull/diff", "i18n 콘솔 업로드", "i18n 정합성 검증"

원칙: **소스 오브 트루스는 저장소 properties 파일**. 콘솔은 카피 검수/번역 협업 용도. push 시 콘솔 카피를 함부로 덮지 않도록 항상 `KEEP` 모드 + 키 명시 푸시.

## 범위 / 비범위

- **범위**: `shared/src/main/resources/messages/message-shared*.properties` 4파일 ↔ Tolgee `pasta-global`(project id 2) 동기화.
- **비범위**: 다른 모듈의 i18n 파일(예: `messages/message.properties`), 모바일 전용 키(태그 `mobile_iOS` 등) 직접 관리. (콘솔에서 수동 관리)

## Phase 0. 사전 점검

스킬 시작 시 항상 먼저 확인:

```bash
# 1) .env에 Tolgee 설정 존재 여부
grep -E "^TOLGEE_(API_URL|API_KEY|PROJECT_ID)=" .env 2>/dev/null

# 2) Node/npx 사용 가능
node --version && npm --version
```

필수 env 3개:

| 키 | 값 | 비고 |
|---|---|---|
| `TOLGEE_API_URL` | `https://dev-global.kakaohealthcare.com` | 셀프호스팅. 운영 인스턴스가 분리되면 별도 키로. |
| `TOLGEE_PROJECT_ID` | `2` | `pasta-global` 프로젝트 |
| `TOLGEE_API_KEY` | `tgpat_xxx` 또는 `tgpak_xxx` | PAT(개인) 또는 Project API Key. push/pull 권한 필요. **절대 커밋 금지**. |

없으면 사용자에게 "콘솔 → User menu → API keys / Personal access tokens에서 발급 후 .env에 추가" 안내. 작성 후 `.env`는 이미 `.gitignore`에 포함되어 있어 추적되지 않음(확인 권장).

## Phase 1. push 워크플로 — 키 명시 + KEEP 모드

새 properties 키를 콘솔에 올릴 때.

### 입력

- 키 목록(쉼표 구분) 또는 키 prefix 1개. 예: `myplan.guide.meal.v2`.
- 옵션: `--dry-run` (실제 업로드 없이 staging 파일만 확인).

### 동작 순서

1. `.env` 로드 → env 3개 export.
2. 임시 staging 디렉토리 `/tmp/tolgee-push-<timestamp>/` 생성.
3. `shared/.../message-shared{,_ko_KR,_en_US,_ja_JP}.properties` 각각에서 명시한 키만 추출 → staging의 4파일에 저장.
4. staging 파일 내용 사용자에게 보여주고 확인 요청 (dry-run이면 여기서 종료).
5. `npx @tolgee/cli@latest push` 실행 — `--force-mode KEEP` (콘솔에 이미 있는 카피는 보존), 로케일 매핑 4건.
6. 결과 출력 → 콘솔 URL과 함께 보고.

### 권장 명령(헬퍼 스크립트로 박제)

```bash
./.claude/skills/tolgee/scripts/push.sh \
  --prefix myplan.guide.meal.v2 \
  --dry-run    # 우선 dry-run으로 staging 확인
./.claude/skills/tolgee/scripts/push.sh \
  --prefix myplan.guide.meal.v2
```

또는 키 명시:

```bash
./.claude/skills/tolgee/scripts/push.sh \
  --keys "myplan.guide.meal.v2.title,myplan.guide.meal.v2.description"
```

### 가드레일

- `--force-mode OVERRIDE`는 **사용 금지**. 콘솔의 운영/디자인 수정분을 날릴 위험. 진짜 덮어쓰기가 필요하면 사용자에게 명시적 확인 받고 1회 한정으로만.
- 키 prefix가 너무 광범위하면 의도치 않은 키도 같이 올라감. `--dry-run` 결과의 키 개수가 예상과 같은지 사용자에게 확인 받기.
- 푸시 후 콘솔 UI에서 1건 이상 직접 확인하는 절차를 보고에 포함.

## Phase 2. pull 워크플로

콘솔에서 변역가가 카피를 수정했을 때 로컬 properties에 반영.

### 입력

- `--keys` 또는 `--prefix`로 범위 지정 (전체 pull은 위험하니 지양).

### 동작 순서

1. `.env` 로드.
2. `npx @tolgee/cli@latest pull --path /tmp/tolgee-pull-<timestamp>/` 실행.
3. 다운로드된 파일과 우리 properties 4파일을 **키 단위로 diff** 표시.
4. **수정 적용은 사용자 확인 후**. Edit 도구로 4파일 각각 갱신. 한꺼번에 sed/awk로 덮지 않음.
5. 변경 후 `:obesity:test` 또는 i18n을 사용하는 모듈의 테스트 1건 돌려 회귀 확인.

### 권장 명령

```bash
./.claude/skills/tolgee/scripts/pull.sh --prefix myplan.guide.meal.v2
```

## Phase 3. diff 워크플로 — 정합성 검증

저장소 properties와 콘솔 키/카피가 어긋났는지 점검.

### 입력

- `--prefix <prefix>` (예: `myplan.guide.meal.v2`).
- 옵션: `--values` 카피 본문까지 비교 (기본은 키 누락만).

### 출력 형식

| 키 | ko-KR | en-US | ja-JP | 상태 |
|---|---|---|---|---|
| `myplan.guide.meal.v2.title` | ✓ | ✓ | ✓ | OK |
| `myplan.guide.meal.v2.foo` | properties only | - | - | **콘솔 누락** |
| `myplan.guide.meal.v2.bar` | - | console only | - | **properties 누락** |

3 컬럼 모두 ✓이면 OK. 그 외는 상태 컬럼에 누락/충돌 표기.

### 권장 명령

```bash
./.claude/skills/tolgee/scripts/diff.sh --prefix myplan.guide.meal.v2
```

## 운영 가드레일

1. **토큰 보호**: `.env`는 `.gitignore` 추적 제외. SKILL.md/스크립트/커밋 메시지/로그 어디에도 토큰 평문 노출 금지. 스크립트 내부에서도 `${TOLGEE_API_KEY:0:8}…` 같은 마스킹된 형태로만 로그.
2. **콘솔이 우선인 영역 존중**: `mobile_iOS` 태그가 붙은 키(예: `myplan.guide.meal.v2.recommend_label`)는 모바일 팀 자산. 서버 스킬에서 임의로 push/pull 금지. 다룰 때는 사용자에게 알리고 확인 받기.
3. **자동 커밋 금지**: pull 적용 후 자동 커밋하지 않는다. 사용자가 검수 후 `/git-commit-workflow`로 진행.
4. **롤백 계기**: push 직후 콘솔에서 작업 이력 확인하는 절차를 보고에 포함 — 잘못 올라가면 Tolgee `Activity` 탭에서 직전 상태로 복구 가능.
5. **로케일 매핑 고정**:
   - `message-shared.properties` → Tolgee `default-locale` (= `ko-KR`. 콘솔 base와 동일하면 별도 push 불필요)
   - `message-shared_ko_KR.properties` → `ko-KR`
   - `message-shared_en_US.properties` → `en-US`
   - `message-shared_ja_JP.properties` → `ja-JP`

## 트러블슈팅

| 증상 | 원인/조치 |
|---|---|
| `401 Unauthorized` | `TOLGEE_API_KEY` 만료 또는 권한 부족. 콘솔에서 키 재발급. |
| `404 Project not found` | `TOLGEE_PROJECT_ID` 확인. `pasta-global`은 현재 `2`. |
| push가 키를 새로 만들지 않음 | `--force-mode` 또는 namespace 옵션 점검. PAT 권한 부족 가능성. |
| pull 결과 ICU placeholder가 깨짐 | `--format` 옵션이 `properties-icu` 또는 `properties-java` 인지 확인. 우리 키는 `{0}` Java MessageFormat 스타일. |
| ja 카피의 `\n` 변환 | ja는 정책상 줄바꿈 미사용. ko/en만 `\n` 유지. diff 시 의도된 차이로 표시. |

## 참고

- Tolgee CLI 공식 옵션: `npx @tolgee/cli@latest <push|pull|export> --help`로 항상 최신 옵션 재확인. 본 스킬의 스크립트 인자는 변경될 수 있다.
- 본 스킬은 `.claude/skills/`(git 추적 제외) 위치라 팀에 공유되지 않는다. 팀 공유가 필요하면 `tools/tolgee/`로 이동 + README 작성 + 토큰은 여전히 `.env`에 분리.
