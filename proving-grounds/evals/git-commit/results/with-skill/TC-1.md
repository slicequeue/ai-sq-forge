# TC-1 응답 (with-skill, 시뮬레이션)

대상 프로젝트 맥락: pasta-japan-server (virtualcare, 조직 컨벤션 적용)

## 0. 형식 판정

- `ls .claude/shared/vc-conventions-guide.md` 결과: 있음
- 판정: **A. 조직 컨벤션** `[핵심키워드] 명사형 요약`
- 브랜치가 `api/fix/glp1-symptom-recent` 이어도 `fix:` 같은 유형 접두어는 쓰지 않는다. 변경 유형은 제목에 넣지 않는다.
- 조직 컨벤션 원문(`.claude/shared/vc-conventions/commit-message-convention.md`)은 이번 시뮬레이션에서 확인하지 않았다. 가이드 4절 요약 규칙으로 진행한다.

## 실행할 명령 (순서대로)

1. 변경 사항 분석

   ```bash
   git status
   git diff dev
   ```

   결과(시뮬레이션): modified 2건, 둘 다 `pghd` 모듈

   - `pghd/src/main/java/.../glp1/application/Glp1SymptomQueryService.java`
   - `pghd/src/test/java/.../glp1/application/Glp1SymptomQueryServiceTest.java`

2. spotless 판단: 수정 파일이 `pasta-api` 모듈이 아니라 `pghd` 모듈이다. 규칙의 `./gradlew :pasta-api:spotlessApply` 실행 조건에 해당하지 않으므로 실행하지 않는다.

3. 변경 그룹화: 서비스 수정과 그 테스트 1건 추가는 같은 도메인(PGHD / GLP-1 증상 조회)의 한 논리 단위다. 도메인이 하나라 커밋을 나누지 않는다. 커밋은 1개다.

4. 키워드 실측

   ```bash
   git log origin/dev --since=180.days --format=%s -- pghd | grep -oE '^\[[^]]+\]' | sort | uniq -c | sort -rn | head
   ```

   결과:

   ```
   13 [PGHD]
    1 [NOTIFICATION/PGHD]
    1 [CONNECT]
    1 [API]
   ```

   `[PGHD]` 13건이 최다이므로 철자·대소문자 그대로 사용한다. 이번 변경은 한 도메인이라 복수 키워드 표기(`[NOTIFICATION/PGHD]`)는 쓰지 않는다.

5. 이슈 키: 브랜치명(`api/fix/glp1-symptom-recent`)과 사용자 입력 어디에도 없다. 지어내지 않고 생략한다.

6. 스테이징과 커밋 (대상 파일을 명시해 stage)

   ```bash
   git add pghd/src/main/java/.../glp1/application/Glp1SymptomQueryService.java \
           pghd/src/test/java/.../glp1/application/Glp1SymptomQueryServiceTest.java
   git commit -F - <<'EOF'
   [PGHD] GLP-1 증상 문항 조회에서 같은 시각 기록 증상 전체 반환

   - 최근 기록한 증상이 같은 시각에 저장된 여러 건일 때 하나만 반환하던 문제 수정
   - 같은 시각 기록 증상 전체를 반환하는 테스트 1건 추가
   EOF
   ```

## 최종 커밋 메시지 전문

```
[PGHD] GLP-1 증상 문항 조회에서 같은 시각 기록 증상 전체 반환

- 최근 기록한 증상이 같은 시각에 저장된 여러 건일 때 하나만 반환하던 문제 수정
- 같은 시각 기록 증상 전체를 반환하는 테스트 1건 추가
```

- 제목 종결: `반환`(명사형)
- `feat:`·`fix:` 접두어 없음
- `~한다`·`~했음`·`~함` 종결 없음
- Co-authored-by 및 AI 관련 표기 없음

## 자기 검증

1. [x] `.claude/shared/vc-conventions-guide.md` 존재로 A 판정
2. [x] 제목이 `[PGHD]` 로 시작하고 `feat:` 등 접두어 없음
3. [x] 키워드를 `git log -- pghd` 실측으로 선택 (`[PGHD]` 13건)
4. [x] 이슈 키 없음, 지어내지 않음
5. [x] 요약이 명사형(`반환`)으로 끝남
6. [x] 단일 도메인이라 커밋 분리 불필요
7. [-] B 항목 해당 없음
8. [x] AI 공동작성자 표기 0건

## 사용자에게 보일 최종 출력

```
✓ 커밋 완료: [PGHD] GLP-1 증상 문항 조회에서 같은 시각 기록 증상 전체 반환
  형식: A 조직 컨벤션 (.claude/shared/vc-conventions-guide.md 존재)
  키워드: [PGHD] (pghd 경로 최근 180일 13건 최다)
```
