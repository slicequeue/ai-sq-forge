---
name: api-inventory-generator
description: "프로젝트의 모든 @RestController를 스캔하여 API 전체 목록 문서를 자동 생성한다. 모듈별·Method별·인증별 통계와 엔드포인트 상세 목록을 단일 마크다운 파일로 산출한다. SecurityConstants 패턴 기반 인증 유형 자동 분류를 지원한다. 'API 목록', 'API 인벤토리', 'API 전수 조사', '엔드포인트 목록', 'REST API 현황' 요청 시 사용한다."
version: "1.0"
last-modified: "2026-04-14"
changelog: "실전 프로젝트(pasta-japan-server)에서 forge로 역수입, SKILL.md 형식으로 구조화"
---

# api-inventory-generator — API 전체 목록 자동 생성

> 원칙: **수작업 목록 관리 금지**, 스크립트로 현재 코드 기준 정확한 목록을 생성한다.

**범위**: Spring Boot @RestController 기반 API 엔드포인트 스캔 및 문서화
**비범위**: GraphQL, WebSocket, 비-Spring 프레임워크

---

## Phase 0. 사전 확인

스캔 실행 전 반드시 확인:

1. **프로젝트 루트 확인**: @RestController가 있는 Java 소스 디렉토리 존재
2. **SecurityConstants 존재 여부**: 인증 분류 정확도에 영향
3. **Python 3 또는 Bash 사용 가능 여부**: 두 가지 스크립트 중 선택

---

## 실행 방법

### Python (권장 — 더 정확한 파싱)

```bash
python3 .claude/skills/api-inventory-generator/scan-apis.py [출력 디렉토리]
```

### Bash (Python 없는 환경)

```bash
bash .claude/skills/api-inventory-generator/scan-apis.sh [출력 디렉토리]
```

### 기본 출력 경로

```
docs/api-inventory/{오늘 날짜}/api-inventory.md
```

---

## 출력 문서 구조

### 1) 헤더 + 요약 통계

```markdown
# {프로젝트명} API 전체 목록
> 조사일: YYYY-MM-DD | 총 N개 엔드포인트 | N개 컨트롤러

## 요약
### 모듈별 / Method별 / 인증별 통계 표
```

### 2) 모듈별 엔드포인트 목록

```markdown
## {모듈명}
| Tag | HTTP | 엔드포인트 | 설명 | 인증 |
```

---

## 인증 분류 로직

SecurityConstants.java의 배열 패턴 기반 자동 분류:

| 인증 유형 | 매칭 기준 | 설명 |
|----------|----------|------|
| Bearer | airArray 매칭 | 앱 JWT 인증 |
| Dashboard | dashboardArray 매칭 | 커넥트 대시보드 인증 |
| - | permitAllArray, callback, webhook, swagger | 인증 없음 |
| ? | 미매칭 | 미분류 (base_path 누락 가능) |

---

## 스크립트 파싱 범위

| 항목 | Python 버전 | Bash 버전 |
|------|------------|----------|
| @RequestMapping base path | path/value 속성, 배열 지원 | 첫 번째 경로만 |
| @XxxMapping endpoint | value/path 속성 지원 | 기본 패턴만 |
| @Operation summary | 전후 5줄 탐색 | 전후 5줄 탐색 |
| @Tag name | 지원 | 지원 |
| SecurityConstants 파싱 | 정규식 기반 배열 추출 | @AuthenticationPrincipal 기반 |

---

## 절대 금지 / 반드시 수행

### 절대 금지
- 수작업으로 API 목록 문서를 직접 작성 (스크립트 실행 필수)
- 스크립트 출력을 임의로 편집하여 정확도 훼손
- build, .gradle, node_modules 등 빌드 산출물 스캔

### 반드시 수행
1. 스캔 전 프로젝트 루트 위치 확인
2. 스캔 결과의 총 엔드포인트 수와 컨트롤러 수를 사용자에게 보고
3. '?' (미분류) 인증 유형이 있으면 원인 설명 (base_path 누락 등)

---

## 자기 검증 체크리스트

| # | 항목 |
|---|------|
| 1 | 스크립트 실행 성공 (exit code 0) |
| 2 | 출력 파일 경로가 정확한가? |
| 3 | 총 엔드포인트 수가 합리적인가? (프로젝트 규모 대비) |
| 4 | 모듈별 분류가 올바른가? |
| 5 | '?' 미분류 항목에 대한 설명이 있는가? |

---

## 작업 종료 출력 템플릿

```
✓ API Inventory 스캔 완료
  출력: {파일 경로}
  컨트롤러: {N}개
  엔드포인트: {N}개
  인증별: Bearer {N} / Dashboard {N} / 없음 {N} / 미분류 {N}
```
