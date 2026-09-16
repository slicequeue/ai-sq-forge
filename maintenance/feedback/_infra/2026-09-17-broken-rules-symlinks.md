# 2026-09-17 - forge `.claude/rules/` 심링크 13개 전량 깨짐

## 상황

- **대상**: ai-sq-forge 저장소 자체 (`.claude/rules/`)
- **발견 경위**: 배포 후 "각 리포에서 스킬이 `/` 메뉴에 안 나온다"는 사용자 제보를 조사하던 중 발견. 제보 건과는 별개 문제였다
- **영향 기간**: 심링크 생성 2026-04-09 이후, 원본 파일이 `.mdc` → `.md` 로 개명된 시점부터

## 문제

`.claude/rules/` 의 심볼릭 링크 13개(00~12)가 모두 `.mdc` 확장자를 가리키는데 원본 디렉터리(`forge/common/pasta-rules/`)의 실제 파일은 전부 `.md` 였다. `.mdc` 파일은 0건.

```
.claude/rules/01-architecture-convention.md -> ../../forge/common/pasta-rules/01-architecture-convention.mdc
                                                                                                      ^^^^ 존재하지 않음
```

심링크 14개 중 정상은 `.claude/commands -> ../anvil/commands` 하나뿐이었다.

**영향**: forge 저장소에서 작업할 때 프로젝트 규칙(4-Tier 아키텍처·도메인 엔티티·JPA·테스트 컨벤션 등 13개 문서)이 **전혀 로드되지 않았다.** 사이클 7 작업 전체가 이 규칙 없이 진행됐다.

## 원인 분석

원본 파일을 `.mdc` 에서 `.md` 로 개명할 때 심링크를 따라 갱신하지 않았다. 심링크는 깨져도 **조용히 실패**한다. 파일이 없다는 오류가 세션에 표시되지 않고, 규칙이 그냥 로드되지 않은 상태로 작업이 진행된다.

`.claude/` 가 gitignore 대상이라 git 이력으로 추적되지도 않았다.

## 조치

13개 링크를 `.md` 로 재연결. 심링크 14/14 정상 확인, 링크 경유 내용 읽기 검증 완료.

## 재발 방지

정기 점검에 심링크 무결성 검사를 포함한다.

```bash
find .claude -type l ! -exec test -e {} \; -print   # 깨진 링크 출력
```

이 검사는 `forge/protocols/maintenance.md` Phase 1.5 월 1회 점검에 포함한다. 원본 파일을 개명·이동할 때는 심링크를 함께 갱신한다.

## 미해결 — 별도 판단 필요

`forge/common/pasta-rules/` 20개 중 7개는 `.claude/rules/` 에 링크 자체가 없다.

| 미연결 | 성격 |
|--------|------|
| 13-admin-module-overview.md ~ 16-admin-static-assets-convention.md | admin 모듈 전용 |
| 17-branch-discipline.md | 브랜치 규율 |
| 18-planning-before-implementation.md | 구현 전 계획 |
| 19-architecture-boundaries.md | 아키텍처 경계 |

13~16 은 admin 전용이라 forge 자체 작업에 불필요할 수 있으나, 17~19 는 forge 작업에도 적용되는 범용 규칙이다. 의도적 제외인지 누락인지 확인이 필요하다.

## 우선순위
- [x] Major: 프로젝트 규칙 전체 미로드 상태가 5개월간 지속
