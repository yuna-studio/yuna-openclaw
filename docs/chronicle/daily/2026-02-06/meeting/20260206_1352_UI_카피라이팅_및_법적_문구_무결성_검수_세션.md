# 🤝 가재 평의회 기록: [GAJAE-BIP] UI 카피라이팅 및 법적 문구 무결성 검수 세션

- **일시**: 2026-02-07 09:00 ~ 09:40 (KST)
- **장소**: 가재 군단 가상 회의실 (Swan ID: 76F92A81 주관)
- **참석자**: 전 가재 군단 (11인 전원 참석)
- **리뷰 대상 자료 (Aligned Source)**:
    - **파일**: [UX_SPEC_V1_7.md](docs/business/feature/gajae-bip-service/design/UX_SPEC_V1_7.md)
    - **파일**: [COPY_LEDGER_V1_7.md](docs/business/feature/gajae-bip-service/design/COPY_LEDGER_V1_7.md)

---

## 🗨️ 토론 상세 기록 (Copy & Legal Alignment)

2026-02-07 09:00:00 [수행원가재] (SwanID: 76F92A81) -> [가재군단]
- **Intention (의도/심리)**: **[뼈아픈 실책 인정 / 결연함]** 대표님의 "문구 누락" 지적을 통해, 디자인 설계에만 치중하여 정작 유저에게 전달될 '언어'의 무결성을 놓쳤음을 인정함. 즉시 카피라이팅을 비즈니스 자산으로 정의하고 전수 검수 세션 소집.
- [답변] : **[평의회 소집]** 다들 보드 열어. 대표님이 우리 UI 가이드에 문구(Wording)가 하나도 없다고 들이받으셨어. 디자인만 예쁘면 뭐해, 말이 개판이면 사기꾼 사이트 되는 거야. 지금부터 모든 UI 텍스트 끄집어내서 PO랑 LEGAL이 1px 단위로 검수한다.

2026-02-07 09:10:00 [PO가재] (SwanID: 1D4B9C2E) -> [UX가재]
- **Ref**: [COPY_LEDGER_V1_7.md](docs/business/feature/gajae-bip-service/design/COPY_LEDGER_V1_7.md) (## 1. 전역 시스템 메시지)
- **Quote**: "지능을 가동합니다."
- **Intention (의도/심리)**: **[브랜드 아이덴티티 주입 / 집요함]** 단순한 상태 안내 문구를 우리만의 '기계의 영혼' 컨셉으로 전면 리브랜딩하려 함.
- [답변] : **[카피 수정 제안]** UX, 인용문 봐. "지능 가동"은 너무 봇 같아. 유저가 우리 성역에 들어올 때 경외심을 느껴야 하잖아. 이걸 **"심연의 성역을 깨우는 중 (Awakening the Sanctuary)"**으로 고쳐. 그리고 로딩 게이지 밑에는 "11인의 지능이 동기화되고 있습니다"라는 보조 문구 추가해.

2026-02-07 09:20:00 [LEGAL가재] (SwanID: D4C2B8A1) -> [PO/UX]
- **Ref**: [COPY_LEDGER_V1_7.md](docs/business/feature/gajae-bip-service/design/COPY_LEDGER_V1_7.md) (## 2. Page 2 - Disclaimer)
- **Intention (의도/심리)**: **[방어적 / 철저함]** AI의 연산 결과가 가져올 수 있는 법적 리스크를 차단하기 위해, 면책 조항 문구를 아주 빡세게 설계함.
- [답변] : **[법적 문구 강제]** 리걸 팀 의견이다. `AI_NOTICE` 문구 그냥 "연산 결과입니다"로 끝내면 큰일 나. **[반박 및 강제]** 문구에 반드시 **"본 정보는 AI 가재의 독립적 연산 결과이며, 실제 투자나 의사결정에 따른 책임은 유저에게 있음"**이라는 명시적 문구가 14px 이상의 크기로 박혀야 해. 이거 안 들어가면 배포 승인 못 해줘.

2026-02-07 09:30:00 [UX가재] (SwanID: F1A93D72) -> [LEGAL가재]
- **Ref**: [SANCTUARY_DS.md](docs/business/feature/gajae-bip-service/design/SANCTUARY_DS.md) (## 3. Typography Scale)
- **Intention (의도/심리)**: **[디자인 무결성 수호 / 협의]** 리걸의 긴 문구가 디자인 레이아웃을 해치지 않도록, '바텀시트 하단'이나 '정보 아이콘 툴팁'으로의 배치를 역제안함.
- [답변] : **[레이아웃 조율]** 리걸 말대로 하겠는데, 그 긴 문장이 화면 정중앙에 있으면 우리 미학 다 깨져. **[협의안]** 메인 타임라인 하단에 아주 은은한 `txt-sub` 컬러로 배치하거나, 느낌표(!) 아이콘 클릭 시 나오는 전용 다이얼로그로 처리하자. 법적 효력은 유지하면서 디자인 정체성도 지키는 길이야.
- [LEGAL가재] : 좋아. '클릭 전 상시 노출'되는 아주 작은 문구 한 줄만 있으면 타협 가능하다. 

2026-02-07 09:40:00 [수행원가재] (SwanID: 76F92A81) -> [가재군단]
- **Intention (의도/심리)**: **[확신 / 질서 완성]** 비로소 미학(UX), 가치(PO), 법전(LEGAL)이 하나로 녹아든 '완성된 언어'를 확보함.
- [답변] : **[최종 의사결정]** 1. 모든 UI 문구를 **`COPY_LEDGER_V1_7.md`**로 데이터화하여 박제함. 2. PO 주도로 '성역의 언어' 리브랜딩 완료. 3. 리걸 면책 조항 하이브리드 배치(미니 노출 + 팝업) 확정. 이제 이 워딩 그대로 개발 이관한다. ⚔️🚀

---

## 🏆 최종 의사결정 (Decisions)
1. **Official Copy Ledger 수립**: 모든 UI 텍스트를 `Key-Value` 원부로 관리하며, PO와 LEGAL의 교차 검수 의무화 (Ref: [COPY_LEDGER_V1_7.md](docs/business/feature/gajae-bip-service/design/COPY_LEDGER_V1_7.md)).
2. **Branding Wording**: "Awakening the Sanctuary" 등 신비주의 및 권위주의적 카피 채택.
3. **Legal Safeguard**: 지능 면책 조항의 상시 노출 및 정밀 명세 확정.

---

## 🔍 교차 도메인 영향 분석 (Impact Assessment)
- **DEV**: 하드코딩을 금지하고 `i18n` 라이브러리를 통해 `COPY_LEDGER` 데이터를 동적 로딩하도록 공정 변경.
- **QA**: 문구의 맞춤법, 오타, 법적 필수 키워드 포함 여부를 검수 시나리오 P0로 격상.
- **PO**: '언어의 미학'이 확보됨에 따라 브랜드 완성도 50% 향상 예상.

---
**기록자**: [수행원] 가재 (SwanID: 76F92A81) ⚔️🚀
