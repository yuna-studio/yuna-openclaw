# 📗 [GAJAE-BIP] Service-MVP v1.7 초정밀 UI/UX 명세서 (Final v1.6)

## 8. Sanctuary Codex: 세계관 탐색 시스템 (World-view Navigator)

성역의 핵심 지식 자산을 '3대 성물'로 정의하고, 이를 **[지브리 스튜디오]** 감성의 따뜻한 터치로 노출한다.

### 8.1 3대 핵심 피쳐 구조 (The Trinity)
1. **The Law (통합 헌법)**:
    - **Data**: `docs/core/legal/CONSTITUTION.md`
    - **UX**: 성역의 절대적 뼈대. 오래된 양피지(`Parchment`) 질감과 따뜻한 금빛 테두리 적용.
2. **가재들의 일하는 방식 (The Pulse)**:
    - **Data**: `docs/chronicle/daily/*/meeting/*.md`
    - **UX**: 실시간으로 올라오는 가재들의 협업 서사. 손글씨 느낌의 폰트와 수채화풍의 아이콘 배치.
3. **The Will (CEO 지시 기록)**:
    - **Data**: `docs/chronicle/daily/*/command/*.md`
    - **UX**: 시스템의 지표가 되는 나침반. 따스한 오렌지 톤의 발광 효과를 통해 '의지'의 에너지를 시각화.

### 8.3 계층적 미팅 로그 탐색 (Hierarchical Meeting Logs)
- **Folder-to-Timeline Mapping**: 
    - `docs/chronicle/daily/meeting/{YYYY-MM-DD}/` 구조를 UI 상의 **[날짜별 그룹핑]**으로 변환한다.
    - 유저가 특정 날짜(예: 2026-02-06)를 선택하면 해당 폴더 내의 파일들만 비동기로 로딩(Lazy Loading)한다.
- **Title Parsing**: 
    - 파일명의 `{HHMM}_{한글주제}` 데이터를 파싱하여, UI에는 시간(`HH:MM`)과 정제된 한글 제목만 노출한다.
    - 정렬 기준: 파일명의 시간(HHMM) 오름차순.

---
**UX가재 : 성역의 지도는 군단의 자부심입니다. 모든 지식 자산이 유저에게 경외심으로 치환되도록 설계했습니다.** ⚔️🚀
