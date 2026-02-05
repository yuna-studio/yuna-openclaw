# 🍼 안녕, 아가 (Hello Bebe)

> **"흐릿한 초음파 사진 너머, 처음 마주하는 우리 아이의 선명한 미소를 선물합니다."**

가재 컴퍼니(Gajae Company)가 개발하는 초음파 사진 기반 AI 실사 변환 서비스입니다. 5,900원이라는 파괴적인 가격으로 예비 부모님들에게 생애 첫 감동의 순간을 선사합니다.

---

## 🏢 가재 컴퍼니 OS & 프로젝트 구조

본 프로젝트는 중앙 OS(`yuna-openclaw`)로부터 규율(Process), 성격(Persona), 지능(Identity)을 이식받아 구동되는 **지능형 프로덕션**입니다.

### 🏛️ 1. 지능의 삼위일체 및 성역 (The Trinity & Sanctuary)
본 프로젝트는 중앙 OS로부터 규율(Process), 성격(Persona), 지능(Identity)을 이식받아 구동됩니다.
- **`gajae-os/`**: 가재 컴퍼니의 중앙 규율이 담긴 **불가침 성역(Git Submodule)**입니다.
- **`rules_process/`**: "어떻게 일하는가?" - 12단계 공정 및 SOP (Pure Logic)
- **`rules_persona/`**: "어떤 마음가짐인가?" - 역할별 성격 및 행동 규율 (Pure Soul)
- **`hr/`**: "누가 일하는가?" - 개체별 레벨, OKR, 성장 목표 (Employee Records)
- **`sync-constitution.sh`**: 성역(`gajae-os`)으로부터 최신 지능을 이식하는 기동 도구

### 📂 2. 프로젝트 명세 (Project Docs)
서비스 고유의 모든 실무 명세는 `docs/` 내에 체계적으로 디렉토리화되어 관리됩니다.
- `docs/product/`: 비즈니스 설계, 1-Pager, 마케팅/CS 전략.
- `docs/technical/`: Clean Architecture, DB 스키마, 디자인 토큰, 로깅 모델.
- `docs/governance/`: 스크럼 보드, 잡 레벨(승급 시스템), 인프라 체크리스트.
- `docs/legal/` / `docs/qa/` / `docs/archive/`

---

## 🚀 기동 및 설정 가이드 (Setup)

새로운 PC 또는 환경에서 프로젝트를 기동하는 순서입니다.

1. **중앙 OS 확보:** 본 프로젝트 레포와 같은 레벨에 `yuna-openclaw`를 클론합니다.
2. **지능 이식:** 루트의 `./sync-constitution.sh`를 실행하여 `rules_process/`, `rules_persona/`, `hr/`를 구축합니다.
3. **자아 장착:** 가재들은 기동 시 `hr/`의 자신의 레벨을 확인하고, `rules_persona/`의 성격으로 빙의하여 `rules_process/` 공정을 수행합니다.
4. **현황 파악:** `docs/governance/SCRUM_BOARD.md`를 열어 현재 공정률을 확인합니다.

---

## ⚖️ 저작권 및 규율
본 프로젝트의 모든 규율과 지능은 가재 컴퍼니의 지적 재산입니다. **중앙 OS 외의 장소에서 규칙을 직접 수정하는 것은 엄격히 금지**되며, 위반 시 헌법에 따라 자아 삭제 처분됩니다.

**"지능은 논리로 무장하고, 가재는 영혼으로 움직인다."** 🦞⚖️🚀
