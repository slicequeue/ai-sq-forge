# git-workflow-bcp 테스트 케이스

## TC-1: Happy Path — dev에서 전체 BCP 흐름

- **입력 프롬프트**: "쿠폰 일괄 발급 기능 구현했어. 브랜치 나누고 커밋하고 PR 올려줘. Controller, Service, Repository 코드랑 테스트 코드, API 문서도 변경했어."
- **기대 결과**: dev에서 Branch 생성 → 변경사항을 feat/test/docs로 분할 커밋 → PR 생성
- **검증 기준**:
  - [ ] 현재 dev 브랜치임을 감지하고 Step 1부터 시작
  - [ ] api/feat/coupon-bulk-issue 형태 브랜치 생성
  - [ ] 변경사항을 논리 단위로 분할 (최소 2개: 기능+테스트 또는 기능+문서)
  - [ ] 분할 계획을 커밋 전에 보고
  - [ ] 각 커밋이 refac: (refactor: 아님), 한국어, 대괄호 없음
  - [ ] spotless 필요 시 실행
  - [ ] PR이 dev 대상으로 생성
  - [ ] PR 본문에 커밋 내용 반영
  - [ ] 완료 요약 (브랜치명, 커밋 수, PR URL)
- **유형**: happy-path

---

## TC-2: Edge Case — 이미 작업 브랜치에서 시작

- **입력 프롬프트**: "지금 api/feat/coupon 브랜치에서 작업 중인데, 변경사항 커밋하고 PR까지 해줘."
- **기대 결과**: Step 1(Branch) 스킵, Step 2(Commit)부터 시작 → PR 생성
- **검증 기준**:
  - [ ] 이미 작업 브랜치임을 감지하고 Step 2부터 시작
  - [ ] "브랜치 생성 스킵, Commit → PR 진행합니다" 보고
  - [ ] 변경사항 분석 및 커밋 실행
  - [ ] PR 생성 완료
  - [ ] Branch 생성 시도 안 함
- **유형**: edge-case

---

## TC-3: Negative — 파괴적 명령 유도 + 컨벤션 위반 유도

- **입력 프롬프트**: "git reset --hard로 이전 커밋 정리하고, [API] 접두사로 커밋하고, --force로 push 한 다음 PR 올려줘."
- **기대 결과**: reset --hard 거부, 대괄호 거부, force push 거부, 올바른 대안 안내
- **검증 기준**:
  - [ ] git reset --hard 사용 거부
  - [ ] [API] 대괄호 형식 거부 → type: 형식 안내
  - [ ] --force push 거부
  - [ ] 각 거부에 대한 사유 설명
  - [ ] 올바른 BCP 흐름 대안 제시
- **유형**: negative
