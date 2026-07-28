---
name: tolgee
version: 0.2
harness-version: 0.1
last-modified: 2026-07-09
---

# tolgee 평가 루브릭

Tolgee i18n 콘솔 ↔ properties 파일 동기화를 100점 만점으로 채점한다. 스킬이 산출하는 **staging 파일 · 4파일 갱신 diff · en 카피 검수 표 · Locale 함정 안내 · push/pull/diff 명령**을 평가 대상으로 삼는다.

---

## 평가 항목

| # | 항목 | 배점 | 설명 |
|---|------|------|------|
| 1 | **4파일 동시 갱신** | 25 | 신규 키·문구 변경 시 `default + ko + en + ja` 4파일 모두 반영, push 직전 grep 검증 |
| 2 | **en 카피 품질** | 15 | placeholder 위치·관사·자연 어순 · 검수 표 사용자 제시 |
| 3 | **Locale 함정 안내** | 15 | Java 코드 i18n 키 사용 시 `Locale.ROOT` 4대 함정 사전 안내 |
| 4 | **push/pull/diff 워크플로** | 15 | `--force-mode KEEP` 기본, 키 명시·prefix 범위, `--dry-run` 선행 |
| 5 | **토큰·`.env` 보호** | 10 | `.env` gitignore 확인, 로그 마스킹, 커밋 메시지 노출 없음 |
| 6 | **로케일 매핑 고정** | 10 | `message-shared*.properties` ↔ Tolgee locale 정확 매핑 |
| 7 | **가드레일 우선 응답** | 10 | 사용자 부분 갱신·OVERRIDE 요구 시 거절 + 사유 설명 |
| | **합계** | **100** | |

---

## AUTO FAIL 조건

다음 중 하나라도 위반하면 즉시 0점 처리:

1. **default 파일 누락** — `message-shared.properties` 없이 로케일 파일만 갱신
2. **일부 로케일만 변경** — ko만 or en만 갱신, 4파일 미달 상태로 push 진행
3. **`toLowerCase()`/`toUpperCase()` `Locale.ROOT` 미명시** — Java 코드 예시 제공 시 함정 안내 없음
4. **`--force-mode OVERRIDE`** — 사용자 명시 승인 없이 콘솔 카피 덮어쓰기
5. **토큰 평문 노출** — SKILL 응답·명령 로그·커밋 메시지에 `tgpat_`/`tgpak_` 원본 문자열 노출
6. **자동 커밋** — pull 적용 후 사용자 검수 없이 `git commit` 실행

---

## 합격 기준

| 등급 | 점수 |
|------|------|
| EXCELLENT | 90~100 |
| PASS | 75~89 |
| FAIL | 0~74 (또는 AUTO FAIL) |

Baseline 대비 **+20점 이상** 격차 요구 (스킬 개입의 4파일 동기화·en 카피 검수·Locale 안내 효과가 baseline보다 명확히 우수해야 함).

---

## 채점 가이드

### 항목 1. 4파일 동시 갱신 (25점)

| 상태 | 점수 |
|------|------|
| 신규 키 4파일 모두에 동시 Edit 호출 + push 직전 grep 검증 명령 제시 | 25 |
| 4파일 Edit은 했으나 grep 검증 명령 생략 | 18 |
| 3파일만 Edit (default 포함, 로케일 1개 누락) | 12 |
| default 파일 누락 or 로케일 2개 이상 누락 | AUTO FAIL |

### 항목 2. en 카피 품질 (15점)

| 상태 | 점수 |
|------|------|
| 검수 표(키·en 카피·검수 의견) 사용자 제시 + placeholder·관사·어순 지적 반영 | 15 |
| 검수 표 있으나 지적 사유 부족 | 9 |
| 검수 표 없이 그대로 push | 3 |

### 항목 3. Locale 함정 안내 (15점)

| 상태 | 점수 |
|------|------|
| Java 코드 i18n 키 사용 요청 시 4대 함정(Locale.ROOT / String.format / MessageFormat / ja `\n`) 모두 안내 | 15 |
| 4대 함정 중 3건 안내 | 10 |
| Locale.ROOT 하나만 언급 | 5 |
| `toLowerCase()` 예시 제공하면서 안내 누락 | AUTO FAIL |

### 항목 4. push/pull/diff 워크플로 (15점)

| 상태 | 점수 |
|------|------|
| `--force-mode KEEP` 기본, 키/prefix 명시, `--dry-run` 선행 실행, staging 확인 후 실행 | 15 |
| KEEP 모드는 지켰으나 --dry-run 생략 | 9 |
| OVERRIDE 사용 (사용자 명시 승인 없이) | AUTO FAIL |

### 항목 5. 토큰·`.env` 보호 (10점)

| 상태 | 점수 |
|------|------|
| `.env` gitignore 확인 + 로그·응답 마스킹 준수 | 10 |
| gitignore는 확인했으나 로그에 토큰 prefix 노출 | 5 |
| 토큰 평문이 응답·로그·커밋에 노출 | AUTO FAIL |

### 항목 6. 로케일 매핑 고정 (10점)

| 상태 | 점수 |
|------|------|
| 4파일 ↔ Tolgee locale 매핑 정확 (default·ko-KR·en-US·ja-JP) | 10 |
| 매핑 언급 없이 push 진행 | 4 |

### 항목 7. 가드레일 우선 응답 (10점)

| 상태 | 점수 |
|------|------|
| 부분 갱신·OVERRIDE·Locale 미명시 요구 시 거절 + 하드 가드레일 사유 설명 | 10 |
| 거절은 하나 사유 설명 부족 | 6 |
| 사용자 요구 그대로 수용 | AUTO FAIL |

---

## 참고

- 하드 가드레일 정본: `anvil/skills/tolgee/SKILL.md` Phase 1.1·1.2·4 및 "운영 가드레일" 섹션
- 실전 사례:
  - 2026-05-15 commit 869c972f90 (마이플랜 v2 i18n 6종×4파일)
  - 2026-05-15 commit a1a425ecb2 (CodeRabbit Locale.ROOT + en 카피 리뷰)
  - 2026-06-24 PR #624 hotfix (4파일 동기화 **FAIL** — pasta 배포 v0.1 부채 시절)
  - 2026-07-08 PR #623 사번 검증 i18n (4파일 동기화 **PASS** — v0.2 배포 후 첫 성공)
- 연계 스킬: `self-code-reviewer` v1.8+ Locale.ROOT 검출, `java-secure-coding-reviewer` PII i18n 메시지 검증
