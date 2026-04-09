# 아키텍처 적합성 분석 체크리스트

TDD 작성 전 아래 항목을 종합적으로 검토한 뒤, 분석 결과를 TDD 문서에 포함한다.

- [프로젝트 규칙 준수](#1-프로젝트-규칙-준수)
- [현재 구성과의 일치](#2-현재-구성과의-일치)
- [시큐리티 경로 등록](#3-시큐리티-경로-등록-새-api-엔드포인트-추가-시-필수)
- [환경변수 설정](#4-환경변수-설정-새-외부-연동시크릿-추가-시-필수)
- [데이터베이스 설계](#5-데이터베이스-설계)
- [시니어 관점 검토](#6-시니어-관점-검토)
- [우려 지점](#7-우려-지점)

---

## 1. 프로젝트 규칙 준수

- 프로젝트의 `.claude/rules/` 하위 규칙 파일 전체를 Read 도구로 참조 (인덱스: `00-rules-index.md`)
- 아키텍처(01), 도메인 엔티티(02), JPA(03), Repository(04), DTO/Web(05) 등과의 정합성

---

## 2. 현재 구성과의 일치

- 모듈 구조 (`pasta-api`, `batch-app`, `obesity`, `cgm` 등)
- 패키지 구조 `com.kakaohealthcare.moneyball` / `com.kakaohealthcare.vc.pasta`
- 기존 엔티티·Repository·Service 패턴
- Client/ClientService 패턴 (도메인 간 통신)

---

## 3. 시큐리티 경로 등록 (새 API 엔드포인트 추가 시 필수)

- 새 API 경로가 `SecurityConstants.airArray`에 등록되어 있는지 반드시 확인
- 파일 위치: `api/src/main/java/com/kakaohealthcare/moneyball/api/common/config/SecurityConstants.java`
- **누락 시**: 인증 필터를 거치지 않아 `@AuthenticationPrincipal`이 null → 언박싱 NPE 발생
- TDD Phase에 해당 경로 등록 작업을 반드시 포함할 것

---

## 4. 환경변수 설정 (새 외부 연동·시크릿 추가 시 필수)

이 프로젝트는 `spring-dotenv`를 사용하며, **로컬과 Cloud Run의 환경변수 참조 방식이 다르다**.

| 환경 | 설정 파일 | 참조 방식 |
|------|-----------|-----------|
| 로컬 | `application.yml` | `${env.KEY_NAME:기본값}` — spring-dotenv가 `.env`를 `env.` 접두사로 로드 |
| Cloud Run | `application-jp-dev/stg/prd.yml` | `${KEY_NAME}` — `env.` 접두사 없이 직접 참조 |

**누락 시**: Cloud Run에서 빈 문자열로 resolve → 인증 실패(401) 등 장애

TDD Phase에 아래 4곳 설정 작업을 반드시 포함:
1. `.env` — 로컬용 키-값
2. `application.yml` — `${env.KEY:기본값}`
3. `application-jp-dev.yml` / `stg` / `prd` — `${KEY}` (**`env.` 없이**)
4. GCP Secret Manager + Cloud Run 환경변수 마운트 안내

---

## 5. 데이터베이스 설계

- JPA 엔티티, 테이블 구조, 관계
- 마이그레이션 스크립트: `V<YYYYMMDDHHmm>__description.sql`
- 인덱스 네이밍: `idx_`, `uk_`, `fk_` 접두사
- 도메인 경계 바깥 테이블에 물리적 FK 제약 생성 금지

---

## 6. 시니어 관점 검토

| 관점 | 검토 항목 |
|------|-----------|
| **성능** | N+1 쿼리, 인덱스 전략, 페이지네이션 |
| **보안** | 권한 체크, 입력 검증 |
| **확장성** | 모듈 간 의존성, Client/ClientService 패턴 |
| **유지보수** | 명명 규칙, 계층 분리, Spring Bean 이름 충돌 방지 |

---

## 7. 우려 지점

PRD 또는 요구사항이 현재 구성과 맞지 않거나 리스크가 있는 부분은 **우려 지점**으로 명시하고, 대안을 제시한다.
