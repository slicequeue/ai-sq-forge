---
name: forge-upstream
description: "실전 프로젝트에서 개선된 컴포넌트를 Forge로 역수입합니다. Deploy Registry 기반으로 연결된 프로젝트를 자동 탐색하고, diff 비교 후 선택적으로 forge에 반영합니다."
trigger: "/forge-upstream"
args: "[{소스 프로젝트 경로}] [--component 컴포넌트명] [--dry-run] [--with-feedback]"
version: "1.0"
last-modified: "2026-04-10"
changelog: "신규 생성 — 실전→forge 역수입 + --with-feedback"
---

# /forge-upstream

## 용도

실전 프로젝트(`.claude/`)에서 운영 중 개선된 컴포넌트를 **Forge(`anvil/`)로 역수입**한다. Deploy Registry를 활용해 연결된 프로젝트를 자동 탐색하고, 변경 사항을 비교하여 forge 원본에 반영한다.

## 인자

| 인자 | 필수 | 설명 | 기본값 |
|------|------|------|--------|
| `{소스 프로젝트 경로}` | 선택 | 역수입할 프로젝트 루트 경로 | Deploy Registry 전체 스캔 |
| `--component {name}` | 선택 | 특정 컴포넌트만 역수입 | 변경된 것 전체 |
| `--dry-run` | 선택 | 실제 파일 변경 없이 diff만 출력 | - |
| `--with-feedback` | 선택 | 파일 동기화 + 피드백 기록 자동 생성 (문제 원인·수정 이유 기록) | - |

---

## 실행 로직

### Phase 0. 소스 탐색

```
1. 인자로 프로젝트 경로가 주어지면 → 해당 프로젝트만 대상
2. 인자 없으면 → anvil/INDEX.md의 Deploy Registry에서 연결된 프로젝트 목록 로드
3. 각 프로젝트 경로 존재 확인
4. .claude/ 디렉토리 존재 확인

출력 예시:
  연결된 프로젝트:
  1. pasta-japan-server (/Users/kakao/.../pasta-japan-server) — 최종 배포: 2026-04-10
  
  프로젝트가 여러 개면 사용자에게 선택 요청.
```

### Phase 1. 변경 감지 (diff)

```
1. Deploy Registry에서 해당 프로젝트에 배포된 컴포넌트 목록 추출
2. 각 컴포넌트에 대해 forge ↔ 실전 프로젝트 파일 비교:

   매핑:
   anvil/skills/{name}/          ↔ {프로젝트}/.claude/skills/{name}/
   anvil/commands/{name}.md      ↔ {프로젝트}/.claude/commands/{name}.md

3. 파일별 diff 실행:
   - 동일 → [동일] 표시
   - 차이 있음 → [변경] 표시 + 변경 줄 수
   - forge에만 존재 → [forge만] (배포 후 실전에서 삭제됨)
   - 실전에만 존재 → [실전만] (실전에서 새로 추가됨)

4. --component 옵션이 있으면 해당 컴포넌트만 비교

5. 변경 감지 리포트 제시:

   변경 감지 결과:
   [변경] java-spring-coder/SKILL.md — +15줄, -3줄 (실전이 최신)
   [변경] java-spring-coder/references/four-tier-patterns.md — +8줄 (실전이 최신)
   [동일] self-code-reviewer/ — 전체 동일
   [동일] git-branch.md — 동일
   [실전만] java-spring-coder/references/admin-patterns.md — 실전에서 새로 추가

   변경된 컴포넌트: 1개 (java-spring-coder)
   역수입할까요?
```

### Phase 2. 변경 내용 상세 확인

```
1. 변경된 각 파일의 diff를 사용자에게 제시
2. 파일별로 역수입 여부를 확인:

   java-spring-coder/SKILL.md 변경 내용:
   (diff 출력)
   
   이 변경을 forge에 반영할까요?
   - 전체 반영
   - 파일별 선택
   - 취소

3. 경로 역리매핑 확인:
   - 실전 프로젝트의 .claude/rules/ 참조 → forge에서도 동일하게 유지 (변환 불필요)
   - 실전 프로젝트 전용 경로가 있으면 → forge 경로로 변환 필요 여부 확인
```

### Phase 3. forge 반영

```
1. --dry-run이면 여기서 중단

2. forge 원본 백업:
   forge/backup/{YYYY-MM-DD}/에 현재 forge 버전 백업

3. 실전 프로젝트 파일 → forge로 복사:
   - Skills: {프로젝트}/.claude/skills/{name}/ → anvil/skills/{name}/
   - Commands: {프로젝트}/.claude/commands/{name}.md → anvil/commands/{name}.md

4. 경로 역리매핑 적용 (필요 시)

5. 파일별 반영 결과 기록
```

### Phase 4. 리포트

```
forge-upstream 완료
  소스: {프로젝트 경로}
  일시: {날짜시간}

역수입된 컴포넌트:
  ✓ [skill] java-spring-coder
    - SKILL.md — +15줄, -3줄
    - references/four-tier-patterns.md — +8줄
    - references/admin-patterns.md — [신규] 추가
  
백업됨:
  forge/backup/{date}/
  - java-spring-coder/ (역수입 전 forge 버전)

스킵됨:
  - self-code-reviewer/ (변경 없음)
  - git-branch.md (변경 없음)

Deploy Registry 업데이트:
  - pasta-japan-server: 최종 동기화일 → {날짜}
```

---

## 사용자 확인 전략

- **Phase 1(변경 감지)**: 변경된 컴포넌트 목록만 보여주고 한 번 확인
- **Phase 2(상세 확인)**: 변경이 1~2개 파일이면 diff 보여주고 바로 확인. 많으면 "전체 반영 / 파일별 선택" 옵션
- **변경 없으면**: "모든 컴포넌트가 forge와 동일합니다" 보고 후 종료

## 출력 형식

```
forge-upstream 시작

Phase 0. 소스 탐색 ... ✓
  연결된 프로젝트: {N}개

Phase 1. 변경 감지 ...
  [변경] {N}개 / [동일] {M}개 / [실전만] {K}개

Phase 2. 변경 내용 확인 ... (사용자 확인 대기)

Phase 3. forge 반영 ... ✓
  파일 {N}개 반영 완료

Phase 3.5. 피드백 기록 ... (--with-feedback 시에만)
  maintenance/feedback/{component}/{date}-{설명}.md 생성
  ⚠ 누적 피드백 {N}건 (3건 이상이면 구조적 개선 권장)

Phase 4. 리포트
  (역수입/백업/스킵/피드백 항목별 결과 출력)
```

---

## 가드레일

### 하드 가드레일 (절대 위반 불가)

1. **forge 원본 백업 없이 덮어쓰기 금지** — 반영 전 반드시 forge/backup/에 현재 버전 백업
2. **사용자 확인 없이 반영 금지** — Phase 1(변경 감지), Phase 2(상세 확인) 각각에서 사용자 확인 필수
3. **proving-grounds/ 역수입 금지** — 하네스, 테스트 케이스는 forge 전용. 실전 프로젝트에서 가져오지 않음
4. **rules/ 파일 역수입 금지** — 규칙 파일은 별도 동기화 프로세스 사용 (forge-upstream 범위 밖)

### 소프트 가드레일 (권장)

- `--dry-run`으로 먼저 변경 내용 확인 후 실제 반영 권장
- 역수입 후 `/eval-harness --skip-baseline`로 품질 재검증 권장
- 대량 변경 시 컴포넌트별로 나눠서 역수입 권장

---

## --with-feedback: 피드백 기록 통합

`/forge-upstream --with-feedback`으로 실행하면 파일 동기화 후 **피드백 기록을 자동 생성**한다.

### 실행 흐름 (Phase 3 반영 후 추가)

```
Phase 3.5. 피드백 기록 생성 (--with-feedback 시에만)

1. 사용자에게 피드백 수집 (간단 Q&A):
   - "어떤 문제가 있었나요?" (증상)
   - "어떻게 수정했나요?" (수정 내용 — diff에서 자동 추출 가능)
   - "재발 방지를 위해 스킬에 반영할 사항이 있나요?" (개선 제안)

2. maintenance/feedback/{component-name}/ 디렉토리에 피드백 기록 생성:

   파일: maintenance/feedback/{component-name}/{YYYY-MM-DD}-{간단설명}.md

   내용:
   ---
   component: {컴포넌트명}
   source: {프로젝트명}
   date: {날짜}
   type: bugfix | improvement | convention-mismatch
   ---

   ## 증상
   {사용자 입력}

   ## 수정 내용
   {diff 요약 또는 사용자 입력}

   ## 개선 제안
   {사용자 입력}

   ## 변경 파일
   - {파일 목록 — Phase 1 diff에서 자동 추출}

3. 동일 컴포넌트에 피드백 3건 이상 누적 시:
   → "⚠ {component}에 피드백이 {N}건 누적되었습니다. 구조적 개선이 필요할 수 있습니다."
   → `/eval-harness {component} --skip-baseline` 재검증 권장
```

### 순환 워크플로 (with-feedback 포함)

```
1. /forge-deploy → 실전 배포
2. 실전 사용 중 문제 발생 → 현장 수정
3. /forge-upstream --with-feedback → 수정사항 + 피드백 함께 forge로 전송
4. maintenance/feedback/{component}/ 에 이력 자동 누적
5. /eval-harness --skip-baseline → 품질 재검증
6. 피드백 3건+ 누적 → 구조적 개선 검토
7. /forge-deploy --sync → 개선된 버전을 연결된 프로젝트에 재배포
```

---

## Deploy Registry 연동

역수입 완료 후 `anvil/INDEX.md`의 Deploy Registry 테이블 업데이트:
- 해당 프로젝트의 "최종 배포일"은 변경하지 않음 (배포일 ≠ 동기화일)
- 필요 시 "비고" 컬럼에 "[동기화: YYYY-MM-DD]" 기록

## forge-deploy와의 관계

```
forge-deploy: Forge → 실전 프로젝트 (배포)
forge-upstream:   실전 프로젝트 → Forge (역수입)

순환 워크플로:
1. forge에서 스킬 개발/테스트
2. /forge-deploy → 실전 프로젝트에 배포
3. 실전 사용 중 개선/수정 발생
4. /forge-upstream → forge로 역수입
5. /eval-harness → 품질 재검증
6. forge에서 추가 개선
7. /forge-deploy --sync → 연결된 프로젝트에 재배포
```
