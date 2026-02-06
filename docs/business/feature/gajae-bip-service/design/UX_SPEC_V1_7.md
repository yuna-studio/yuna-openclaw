# 📗 [GAJAE-BIP] Service-MVP v1.7 초정밀 UI/UX 명세서 (Final v1.6)

## 8. Sanctuary Codex: 세계관 탐색 시스템 (World-view Navigator)

성역의 모든 지식 자산을 계층적으로 노출하며, 유저가 군단의 정체성을 탐험할 수 있도록 설계한다.

### 8.1 3대 핵심 섹션 구조 (Data Hierarchy)
1. **Core Sector (The Foundation)**:
    - **Data**: `CONSTITUTION.md`, `RULE_PO_INTELLIGENCE.md`, `TEMPLATE_MAPPING.md`
    - **UI**: 황금색(`Gold-leaf`) 글로우 테두리 적용. 시스템의 심장부임을 시각화.
2. **Governance Sector (The Discipline)**:
    - **Data**: `personnel/*.md`, `approvals/*/GATE.md`, `incident/*.md`
    - **UI**: 냉철한 메탈 실버(`surface-metal`) 테마. 규율과 통제의 상징.
3. **Business Sector (The Creation)**:
    - **Data**: `plan_mvp_v2.md`, `design/*.md`, `docs/technical/*.md`
    - **UI**: 활동성 네온 블루(`intel-neon`) 테마. 연산의 결과물임을 강조.

### 8.3 계층적 미팅 로그 탐색 (Hierarchical Meeting Logs)
- **Folder-to-Timeline Mapping**: 
    - `docs/chronicle/daily/meeting/{YYYY-MM-DD}/` 구조를 UI 상의 **[날짜별 그룹핑]**으로 변환한다.
    - 유저가 특정 날짜(예: 2026-02-06)를 선택하면 해당 폴더 내의 파일들만 비동기로 로딩(Lazy Loading)한다.
- **Title Parsing**: 
    - 파일명의 `{HHMM}_{한글주제}` 데이터를 파싱하여, UI에는 시간(`HH:MM`)과 정제된 한글 제목만 노출한다.
    - 정렬 기준: 파일명의 시간(HHMM) 오름차순.

---
**UX가재 : 성역의 지도는 군단의 자부심입니다. 모든 지식 자산이 유저에게 경외심으로 치환되도록 설계했습니다.** ⚔️🚀
