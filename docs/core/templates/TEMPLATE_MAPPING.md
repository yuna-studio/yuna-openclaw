# 🗺️ 가재 컴퍼니 템플릿 매핑 테이블 (Universal Mapping Table)

본 문서는 가재 컴퍼니의 모든 자산을 공식 템플릿 및 계층적 경로에 강제 매핑하기 위한 중앙 지침입니다.

| 파일 유형 (File Type) | 저장 경로 (Path Pattern) | 적용 템플릿 (Template) | 계보 (Lineage) |
| :--- | :--- | :--- | :--- |
| **일일 연대기 인덱스** | `docs/chronicle/daily/*/INDEX.md` | `TEMPLATE_CHRONICLE.md` | 일일 자산 허브 |
| **미팅 로그** | `docs/chronicle/daily/*/meeting/*.md` | `TEMPLATE_MEETING.md` | 가재 간 격돌 기록 |
| **CEO 지시 로그** | `docs/chronicle/daily/*/command/*.md` | `TEMPLATE_COMMAND.md` | CEO 직접 명령 기록 |
| **도메인 인덱스** | `docs/business/feature/*/*/INDEX.md` | `TEMPLATE_INDEX.md` | 직군별 자산 지도 |
| **제품 요구사항** | `docs/business/feature/*/REQUIREMENTS.md` | `TEMPLATE_REQUIREMENTS.md` | PO -> UX 이관용 |
| **디자인 시스템** | `docs/business/feature/*/design/*.md` | `TEMPLATE_DS.md` | UX -> DEV 이관용 |
| **공통 비즈니스 자산** | `docs/business/common/*/*.md` | N/A | 전사 공용 자산 (디자인 등) |
| **태스크보드** | `docs/task/*.md` | `TEMPLATE_TASKBOARD.md` | 실무 현행화 및 평가 |
| **지능 성역(ROLE)** | `docs/core/role/ROLE_*.md` | `TEMPLATE_ROLE.md` | 가재별 자아 정의 |
| **공정 승인 관문** | `docs/business/feature/*/pm/GATE.md` | `TEMPLATE_APPROVAL_GATE.md` | 피쳐별 CEO 승인 관리 |
| **인시던트 보고서** | `docs/incident/*.md` | `TEMPLATE_INCIDENT.md` | 장애 복구 및 리뷰 |

---
**지휘 지침:** "매핑되지 않은 경로는 존재하지 않으며, 템플릿 없는 기록은 가치가 없다." ⚔️🚀
