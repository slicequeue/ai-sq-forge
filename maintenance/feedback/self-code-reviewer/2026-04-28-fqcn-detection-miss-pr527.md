# 2026-04-28 — 자체 리뷰가 FQCN 누수 검출 실패 (PR #527)

## 상황
- **컴포넌트**: `self-code-reviewer` 1.4
- **사용 프로젝트**: pasta-japan-server
- **PR**: https://github.com/virtualcare/pasta-japan-server/pull/527
- **휴먼 리뷰어**: kyle-gy-khc — "fully qualified class name 사용. 스킬 강화가 필요해 보입니다~"
- **자체 리뷰 결과**: PASS (FQCN 미검출)

## 문제

PR을 push하기 전 self-code-reviewer가 검토했음에도 테스트 파일의 FQCN 사용을 잡지 못함:

```java
.willThrow(new org.springframework.dao.DataIntegrityViolationException("duplicate"));
.isInstanceOf(org.springframework.dao.DataIntegrityViolationException.class)
```

휴먼 리뷰어가 잡아냄. 자체 리뷰는 와일드카드 import만 체크하고 FQCN 패턴은 체크리스트에 없었음.

## 원인 분석

1. **체크리스트 누락**: `references/review-checklist.md:58`은 `[ ] Explicit Import인가? (와일드카드 import java.util.* 금지)`만 있음. 프로젝트 규칙(`07-general-project-convention.md:26`)의 "전체 패키지 경로 직접 사용 금지" 항목이 체크리스트에 분리·반영되지 않음.
2. **AUTO FAIL 미설정**: 단순 import 누락이 아닌 **코드 본문에 패키지 경로 박는** 패턴이라 코드 가독성·일관성에 직접 영향. 그러나 현재 루브릭에 AUTO FAIL 조건으로 정의되지 않음.
3. **테스트 파일 검사 강도 약함 가능성**: 메인 코드는 꼼꼼히, 테스트는 느슨히 보는 휴리스틱 가능성 — 명시적 점검 필요.

## 개선 방안

### 1. 체크리스트 항목 추가

`references/review-checklist.md` "7. 일반 규칙"에:

```
- [ ] FQCN 직접 사용 없는가? — 와일드카드뿐 아니라 코드 본문에 `com.x.y.Z` 형태로 패키지 경로 박지 않았는가?
  - 검사 대상: 변수 선언, 매개변수, 제네릭, 예외 생성(`new x.y.Z()`), `.class` 리터럴, 캐치 절
  - **테스트 파일도 동일 검사** — mock 예외와 `isInstanceOf(x.y.Z.class)` 패턴이 자주 누수
```

### 2. AUTO FAIL 후보 격상

`SKILL.md`에 "리뷰 가드레일" 명시:
> **FQCN 직접 사용 발견 시 → 무조건 보고 + AUTO FAIL 후보**. 단순 import 추가로 해결 가능한 결함이지만, 프로젝트 규칙 명시 위반이고 일관성에 직접 영향.

### 3. 검출 룰 (검토자가 코드 읽을 때 적용)

코드 본문(import 문 외)에서 다음 패턴 검색:
- 정규식 개념: `\b[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+\.[A-Z][A-Za-z0-9_]*\b`
- 매칭 예: `org.springframework.dao.DataIntegrityViolationException`, `java.util.concurrent.atomic.AtomicLong`
- 예외: 어노테이션의 문자열 인자, SpEL 표현식, JPQL/SQL 쿼리 문자열, 로그 메시지 본문

## 우선순위
- [x] **Critical**: 검출 누락 자체가 자체 리뷰 스킬의 핵심 결함
