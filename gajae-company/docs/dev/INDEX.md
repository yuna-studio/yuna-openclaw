# 🗂️ 도메인 인덱스 (Domain Index): [DEV/ENGINEERING]

## 1. 개요 (Overview)
본 문서는 `docs/business/feature/gajae-bip-service/dev/` 경로에 속한 모든 기술 설계 및 구현 자산의 지도입니다.

## 2. 필수 참조 자산 (Required References)
구현 공정 착수 전, 아래 자산을 반드시 병행 탐독하여 정합성을 확보해야 한다.
- **기획**: `../po/plan_mvp_v2.md` (비즈니스 의도)
- **디자인**: `../design/UX_SPEC_V1_7.md` (1px UI 명세)
- **이관**: `../design/development-handover-v1-7.md` (기술적 구현 가이드)

## 3. 기술 구현 규율 (Engineering Discipline)
- **제 1 항 (설계 우선주의)**: 모든 코드는 승인된 `architecture-blueprint`를 1px의 오차 없이 구현한다.
- **제 2 항 (의존성 규칙)**: `PROCESS_CODING_NEXTJS.md`에 정의된 [View-Service-Repository] 레이어 분리를 사수한다.
- **제 3 항 (단수형 명명)**: 모든 폴더 및 파일 명명 시 단수형(Singular) 영문 슬러그를 사용한다.

## 4. 파일 리스트 및 정의 (File Registry)

| 파일명 (File Name) | 목적 및 내용 (Purpose) | 상위 계보 (Parent) | 후속 산출물 (Next Step) |
| :--- | :--- | :--- | :--- |
| **architecture-blueprint-v1-7.md** | UML/시퀀스 기반 초정밀 기술 설계도 | UX_SPEC_V1_7.md | src/ (Implementation) |
| **technical-implementation-spec-v1-7.md** | 기술 스택 및 데이터 페칭 알고리즘 명세 | architecture-blueprint-v1-7.md | FUE (Implementation) |

---
**DEV가재 : 아키텍처는 지능의 질서이며, 무결한 코드는 시스템의 품격입니다.** ⚔️🚀
