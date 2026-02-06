# 📗 [GAJAE-BIP] Service-MVP v1.7 초정밀 UI/UX 명세서 (Final v1.4)

## 6. UI 카피 및 텍스트 데이터 맵 (Text Asset Mapping)

모든 UI 문구는 하드코딩하지 않으며, `COPY_LEDGER_V1_7.md`의 Key값을 참조하여 렌더링한다.

### 6.1 전역 시스템 텍스트
- **Key**: `SYS_INIT` -> **"심연의 성역을 깨우는 중..."** (Style: `T-LOG` / Fade-in 1s)
- **Key**: `AUTH_REQ` -> **"지능의 승인이 필요합니다."** (Style: `H-MD`)

### 6.2 법적 면책 조항 (Legal Disclaimer)
- **Key**: `AI_NOTICE_MINI` -> **"본 데이터는 AI의 독립적 연산 결과입니다."**
    - **Position**: 메인 타임라인 하단 Fixed (Opacity: 40%).
    - **Action**: 클릭 시 `AI_NOTICE_FULL` 팝업 다이얼로그 호출.
- **Key**: `AI_NOTICE_FULL` -> **"본 지능의 사고 과정은 실제 연산 데이터이며, 결과에 대한 최종 책임은..."** (전체 법문 데이터 매핑)

---
**UX가재 : 문구는 지능의 의식이며, 정제된 언어만이 성역의 권위를 완성합니다.** ⚔️🚀
