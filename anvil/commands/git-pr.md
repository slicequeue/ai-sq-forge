---
name: git-pr
description: "PR 생성/갱신 — git-pr 스킬로 승격됨. 이 커맨드는 호환용 별칭."
trigger: "/git-pr"
args: ""
version: "2.1"
last-modified: "2026-11-13"
changelog: "v2.1: 스킬 v0.7 동작 설명(제목 형식 판정·맨 위 결론 블록) 반영 | v2.0: skill로 승격. 본문은 anvil/skills/git-pr/SKILL.md로 이전. 이 파일은 호환용 별칭으로만 유지"
---

# /git-pr (스킬 별칭)

이 커맨드는 **`anvil/skills/git-pr/SKILL.md` 스킬로 승격**됐습니다.

`/git-pr` 입력 시 git-pr 스킬을 호출합니다. 스킬에서 다음을 수행:
1. 변경사항 분석 → 제목 형식 판정(조직 컨벤션 적용 프로젝트는 `[핵심키워드] 명사형 요약`) → 맨 위 결론 블록 + 표준 양식으로 본문 작성
2. 신규/기존 PR 판단
3. 생성/수정 후 URL 출력

스킬 위치: `anvil/skills/git-pr/SKILL.md`

> 양식/표현 원칙/PR 본문 표준 사례는 모두 스킬 본문 참고.
