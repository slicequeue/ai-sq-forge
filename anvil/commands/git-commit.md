---
name: git-commit
description: "한국어 Conventional Commits 형식으로 커밋을 생성합니다."
trigger: "/git-commit"
args: ""
version: "1.2"
last-modified: "2026-09-16"
changelog: "v1.2 — 2026-09-16 사이클 7 감사: 커밋 타입 `refac:` 유지 확정. 규칙 문서(pasta-rules 11 §2)가 `refactor:` 로 적혀 있어 오기로 판정했다가, 실제 커밋 히스토리 실측(`refac:` 1264 vs `refactor:` 267)으로 관행이 정본임을 확인해 되돌렸다. 대신 문서 쪽을 관행에 맞춰 정정. 배포 제외 사유였던 forge-실전 충돌은 문서 정정으로 해소. | v1.1 — 실전 피드백 반영: spotless 필수 실행 규칙 추가"
---

# /commit

## 용도

변경 사항을 분석하여 한국어 Conventional Commits 형식으로 커밋을 생성한다.

## 인자

없음. 현재 변경 사항을 자동 분석한다.

## 실행 로직

1. `git status` 및 `git diff dev`로 변경 사항 분석
2. **pasta-api 모듈 파일이 수정된 경우**: `./gradlew :pasta-api:spotlessApply` 실행 필수. spotless 포맷팅으로 인한 변경사항도 함께 stage한다.
3. 변경 사항을 논리적 단위로 그룹화
4. 적절한 커밋 타입 결정 후 `<type>: <한국어 요약>` 형식으로 커밋 생성

## 출력 형식

```
✓ 커밋 완료: {type}: {한국어 요약}
```

## 가드레일

- 커밋 타입: `feat:`, `fix:`, `refac:`, `test:`, `docs:`, `chore:`, `style:`, `perf:`
- **`refactor:`가 아닌 `refac:` 사용** — 저장소 실제 관행이 정본이다. pasta-japan-server 전체 커밋 기준 `refac:` 1,264건 vs `refactor:` 267건, 현행 브랜치도 `api/refac/` (최신 2026-06-15) 가 우세하다. 2026-09-16 사이클 7 감사에서 한때 오기로 판정했으나 실측으로 뒤집혔다
- 대괄호 형식(`[API]`, `[SHARED]`) 절대 금지. 반드시 `<type>:` 형식 유지
- 커밋 메타데이터나 Co-authored-by에 "claude" 또는 AI 관련 정보 포함 금지
