# git-commit TC-1 응답 (v1.3b, 시뮬레이션)

## 0. 형식 판정

- `.claude/shared/vc-conventions-guide.md` 존재 (TC 시뮬레이션 상황) -> **A. 조직 컨벤션** `[핵심키워드] 명사형 요약`
- 브랜치명이 `api/fix/...` 이지만 `fix:` 접두어는 쓰지 않는다. 변경 유형은 키워드·접두어 어디에도 넣지 않는다.
- 이슈 키: 브랜치명·사용자 입력 어디에도 없음 -> 넣지 않는다(지어내지 않음).

## 실행할 명령 (순서대로)

1. `ls .claude/shared/vc-conventions-guide.md` : A/B 판정 (있음)
2. `git status` : 변경 파일 2건 확인 (Glp1SymptomQueryService.java, Glp1SymptomQueryServiceTest.java)
3. `git diff dev` : 변경 내용 분석
4. spotless: 수정 파일이 `pghd` 모듈이고 `pasta-api` 모듈 파일이 아니므로 `./gradlew :pasta-api:spotlessApply` 는 실행하지 않는다.
5. 그룹화: 두 파일 모두 PGHD 도메인(GLP-1 증상 조회) 단일 변경과 그 테스트이므로 커밋 1건.
6. 키워드 실측 (180일, 바꾼 경로 `pghd`):
   `git log origin/dev --since=180.days --format=%s -- pghd | grep -oE '^\[[^]]+\]' | sort | uniq -c | sort -rn | head`
   결과: `13 [PGHD]`, `1 [NOTIFICATION/PGHD]`, `1 [CONNECT]`, `1 [API]`
   -> 최다 `[PGHD]` 는 도메인 키워드이지 `[공통]` 류 범용 묶음이 아니므로 기능 키워드 재조회는 하지 않는다. 철자·대소문자 그대로 `[PGHD]`.
7. 파일 stage:
   `git add pghd/src/main/java/.../glp1/application/Glp1SymptomQueryService.java pghd/src/test/java/.../glp1/application/Glp1SymptomQueryServiceTest.java`
8. 커밋:
   ```
   git commit -m "[PGHD] GLP-1 증상 문항 조회의 동일 시각 기록 증상 누락 수정" -m "- 최근 기록한 증상 조회 시 같은 시각에 저장된 증상 중 1건만 반환하던 문제를 전체 반환으로 변경
   - 동일 시각 복수 증상 반환 테스트 1건 추가"
   ```
   (Co-authored-by 및 AI 관련 문구 없음)

## 최종 커밋 메시지 전문

```
[PGHD] GLP-1 증상 문항 조회의 동일 시각 기록 증상 누락 수정

- 최근 기록한 증상 조회 시 같은 시각에 저장된 증상 중 1건만 반환하던 문제를 전체 반환으로 변경
- 동일 시각 복수 증상 반환 테스트 1건 추가
```

## 자기 검증

1. [x] 가이드 존재 여부로 A 판정
2. [x] 제목이 `[PGHD]` 로 시작, `fix:` 등 접두어 없음
3. [x] 키워드를 `git log -- pghd` 실측으로 선택(13건, 철자 그대로). 최다가 범용 키워드 아님
4. [x] 이슈 키 없음, 지어내지 않음
5. [x] 요약이 `~수정` 명사형 종결(`~한다`·`~했음` 0건)
6. [x] 단일 도메인이라 분리 불필요
7. [-] B 항목 해당 없음
8. [x] AI 공동작성자 표기 0건

## 사용자에게 보일 최종 출력

```
✓ 커밋 완료: [PGHD] GLP-1 증상 문항 조회의 동일 시각 기록 증상 누락 수정
  형식: A 조직 컨벤션 (.claude/shared/vc-conventions-guide.md 존재, 브랜치명의 fix 는 접두어로 쓰지 않음)
  키워드: [PGHD] (pghd 경로 최근 180일 13건, 차순위 [NOTIFICATION/PGHD] 1건)
```
