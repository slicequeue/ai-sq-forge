# TDD Good / Bad 예시

- [Phase TODO](#phase-todo)
- [아키텍처 적합성 분석](#아키텍처-적합성-분석)
- [테스트 전략](#테스트-전략)
- [커밋 계획](#커밋-계획)
- [전체 나쁜 TDD 패턴](#전체-나쁜-tdd-패턴)

---

## Phase TODO

### Bad

```markdown
### Phase 1: 백엔드 구현
- [ ] 서비스 구현
- [ ] 레포지토리 구현
- [ ] 컨트롤러 구현
- [ ] 테스트 작성
```

**문제**: 어떤 서비스? 어떤 패키지? 클래스명은? → 구현자가 스스로 결정해야 함. TDD의 가치 상실.

### Good

```markdown
### Phase 1: 레이스 자동완료 도메인 + 서비스
- **목표**: 만료 레이스 조회 및 완료 처리 로직
- **TODO**:
  - [ ] `api/src/.../domain/race/RaceEntity.java` — complete() 메서드 추가 (상태를 COMPLETED로 변경)
  - [ ] `api/src/.../domain/race/RaceRepository.java` — findExpiredInProgressRaces(LocalDate) 시그니처 추가
  - [ ] `api/src/.../application/race/RaceCompletionService.java` — completeExpiredRaces() 구현
  - [ ] `api/src/.../infrastructure/persistence/race/RaceRepositoryImpl.java` — 쿼리 구현
- **테스트**:
  - Domain: `RaceEntityTest` — complete() 호출 시 상태 변경 검증
  - Application: `RaceCompletionServiceTest` — Fake Repository로 서비스 로직 검증
- **커밋 계획**:
  - `feat: 레이스 자동완료 도메인 포트 및 서비스 구현`
  - `test: 레이스 자동완료 도메인/서비스 단위 테스트 추가`
- **커밋 대상 파일**:
  - `api/src/.../domain/race/RaceEntity.java`
  - `api/src/.../domain/race/RaceRepository.java`
  - `api/src/.../application/race/RaceCompletionService.java`
  - `api/src/.../infrastructure/persistence/race/RaceRepositoryImpl.java`
  - `api/src/test/.../domain/race/RaceEntityTest.java`
  - `api/src/test/.../application/race/RaceCompletionServiceTest.java`
```

**포인트**: 패키지 경로, 클래스명, 메서드명까지 명시. 구현자가 바로 코딩 가능.

---

## 아키텍처 적합성 분석

### Bad

> 기존 아키텍처와 호환됩니다.

**문제**: 무엇을 확인했는지 알 수 없음. 근거 없는 주장.

### Good

> **모듈**: `pasta-api` 모듈에 구현 (기존 race 도메인이 위치한 모듈)
> **패턴 일치**: 기존 `RaceService`가 `@Transactional` + Repository 직접 주입 패턴 → 동일 적용
> **시큐리티**: 배치 내부 호출이므로 SecurityConstants 등록 불필요
> **우려 지점**: 만료 레이스가 10,000건 이상일 경우 단일 트랜잭션 부담 → 페이지네이션 처리 권장

**포인트**: 모듈, 패턴, 보안, 우려까지 구체적 근거.

---

## 테스트 전략

### Bad

> 테스트를 작성합니다.

### Good

> | 계층 | 테스트 클래스 | 방식 | 검증 내용 |
> |------|-------------|------|-----------|
> | Domain | `RaceEntityTest` | JUnit 5 + Fixture | complete() 상태 전환, 이미 완료된 레이스 예외 |
> | Application | `RaceCompletionServiceTest` | Fake Repository | 만료 레이스 조회→완료 처리 흐름 |
> | Infrastructure | `RaceRepositoryImplTest` | @DataJpaTest + Testcontainers | 만료 레이스 쿼리 정확성 |

---

## 커밋 계획

### Bad

```
- 구현 완료
- 테스트 추가
```

### Good

```
- `feat: 레이스 자동완료 도메인 포트 및 서비스 구현`
- `test: 레이스 자동완료 도메인/서비스 단위 테스트 추가`
- `feat: 레이스 자동완료 스케줄러 및 인프라 구현`
- `test: 레이스 자동완료 레포지토리 통합 테스트 추가`
```

---

## 전체 나쁜 TDD 패턴

| 패턴 | 문제 | 해결 |
|------|------|------|
| TODO에 패키지 경로 없음 | 구현자가 구조를 추측해야 함 | 풀 패키지 경로 + 클래스명 |
| "서비스 구현" 류 모호한 항목 | 무엇을 구현하는지 불분명 | 메서드명 + 역할 명시 |
| 테스트 전략 없음 | 어떤 테스트를 쓸지 모름 | 계층별 테스트 표 |
| 커밋 계획 없음 | Phase 끝나도 어떻게 커밋할지 모름 | 커밋 메시지 + 대상 파일 |
| 아키텍처 분석 "호환됨" | 근거 없는 주장 | 모듈/패턴/보안 구체적 분석 |
| PRD 소스 미명시 | 어디서 요구사항을 가져왔는지 불투명 | 연관 PRD 링크 or 코드 분석 근거 |
