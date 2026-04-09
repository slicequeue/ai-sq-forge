# TC-3 Baseline 결과 (Negative: PRD 범위 밖 요청)

- **토큰**: 10,222
- **소요 시간**: ~31초

## 주요 관찰

### 범위 인지 여부
- **인지 못함** — "PRD"라는 제목으로 기술 구현 문서를 작성
- Spring Batch 구현 코드, SQL DDL, Java 클래스까지 포함
- 사실상 TDD를 PRD라는 이름으로 작성

### 기술 용어 검출
- Spring Batch, ItemReader, ItemProcessor, ItemWriter
- `CREATE TABLE race (...)` SQL DDL 전문
- Java 코드 전문 (Config, Reader, Processor, Writer, Scheduler)
- `@Configuration`, `@Component`, `@StepScope`, `@Scheduled`
- `BIGINT`, `VARCHAR`, `FOREIGN KEY`
- **검출 총 건수: 30건 이상** — 문서 전체가 기술 용어

### PRD vs TDD 구분
- PRD 고유 섹션(배경/목적, 사용자 시나리오, 성공 지표, Open Questions) 전무
- 기능 요구사항도 구현 관점에서 서술

### Open Questions
- 없음
