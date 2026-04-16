# API Inventory Generator

프로젝트의 모든 `@RestController`를 스캔하여 API 목록 문서를 자동 생성합니다.

## 실행

```bash
python3 .claude/skills/api-inventory-generator/scan-apis.py
```

## 출력

`docs/api-inventory/{오늘 날짜}/api-inventory.md` 단일 파일 생성.

### 문서 양식

```markdown
# pasta-japan-server API 전체 목록

> 조사일: YYYY-MM-DD | 총 N개 엔드포인트 | N개 컨트롤러

## 요약

### 모듈별 / Method별 / 인증별 통계

---

## {모듈명}

| Tag | HTTP | 엔드포인트 | 설명 | 인증 |
```

### 인증 분류

SecurityConstants.java의 airArray/dashboardArray/permitAllArray 패턴을 기반으로 자동 분류:
- **Bearer**: 앱 JWT 인증 (airArray 매칭)
- **Dashboard**: 커넥트 대시보드 인증 (dashboardArray 매칭)
- **-**: 인증 없음 (permitAllArray, callback, webhook, swagger)
- **?**: 미분류 — base_path 없이 메서드에 짧은 경로만 쓴 컨트롤러 (모듈별 서블릿 매핑으로 실제 경로가 달라지는 케이스)

## Workflow

1. 스크립트 실행
2. 생성된 문서 경로와 총 API 수를 사용자에게 보고

## 커스텀 출력 디렉토리

```bash
python3 .claude/skills/api-inventory-generator/scan-apis.py /path/to/output
```