# 🦞 가재 컴퍼니 영구 불변 OS (yuna-openclaw)

> **"논리(Process)로 지시하고, 성격(Persona)으로 일하며, 성과(Identity)로 증명한다."**

본 레포지토리는 가재 컴퍼니(Gajae Company)의 중앙 OS이며, 모든 프로젝트가 공유하는 **불변의 기반(Immutable Base)**입니다. 새로운 PC나 환경에서 본 OS만 복제(Clone)하면 즉시 가재 군단을 소환하고 프로젝트를 기동할 수 있습니다.

---

## 🏗️ 1. 표준 디렉토리 구조 (System Architecture)

가재 컴퍼니 워크스페이스는 다음과 같이 엄격하게 구조화됩니다.

```text
/workspace/
├── yuna-openclaw/           # [중앙 OS] 원본 보관소
│   ├── rules_process/       # (Process) "어떻게 일하는가?" - 공정 및 SOP (Logic)
│   ├── rules_persona/       # (Persona) "어떤 마음가짐인가?" - 역할별 성격 및 행동 규율 (Soul)
│   ├── identities/          # (Performance Card) "무엇을 이루었는가?" - 인사기록부 및 성과 자료 (Record)
│   └── scripts/             # (Automation) 운영 자동화 스크립트
└── {Project-Name}/          # [실전 프로젝트] (예: hello-bebe)
    ├── README.md            # 프로젝트 개요 및 기동 가이드
    ├── rules_process/       # [Sync] 중앙 OS로부터 복제된 공정 규율
    ├── rules_persona/       # [Sync] 중앙 OS로부터 복제된 역할 페르소나
    ├── hr/                  # [Sync] 중앙 OS로부터 복제된 인사기록부 (identities)
    └── docs/                # 프로젝트 고유 명세 (Product, Tech, QA 등)
```

---

## 🎭 2. 지능의 삼위일체 (The Trinity)

본 OS는 가재의 지능을 세 가지 계층으로 완전히 분리하여 관리합니다.

### 📂 `rules_process/` (Rule Process: Logic)
작업의 **표준 절차(SOP)**만을 담고 있습니다. 프로젝트 도메인이 바뀌어도 변하지 않는 가재 컴퍼니의 '불변의 뇌'입니다.
- **`RULES_CONSTITUTION.md`**: 최상위 통합 헌법
- **`RULES_OPERATIONS.md`**: 12단계 표준 개발 프로세스

### 📂 `rules_persona/` (Rule Persona: Soul)
각 **역할(Role)**이 가져야 할 성격, 말투, 가치관을 정의합니다. 가재는 기동 시 이 영혼을 '빙의'합니다.
- **`DEV.md`**: 아키텍처에 집착하는 엔지니어의 성격.
- **`PO.md`**: 비즈니스 가치를 설계하는 미니 CEO의 성격.

### 📂 `identities/` (Performance Card: Record)
실제 업무를 수행하는 가재의 **'인사기록부'이자 '연말 성과자료'**입니다. 
- **업무 기록(Work Log):** 가재 본인이 헌법 근거와 함께 자신의 실적을 직접 박제합니다.
- **인사 평가(Evaluation):** HR가재와 대표님이 해당 가재의 성과와 리더십 원칙 준수 여부를 평가합니다.
- **승격의 증거:** 이 파일의 기록이 쌓여 다음 레벨로의 승진을 결정하는 유일한 근거가 됩니다.

---

## 🚀 3. 새로운 환경에서의 기동 (Setup Guide)

새로운 PC나 환경에서 시스템을 재구축하는 순서입니다.

1. **중앙 OS 확보:** `git clone https://github.com/yuna-studio/yuna-openclaw.git`
2. **프로젝트 생성:** `mkdir {Project-Name} && cd {Project-Name}`
3. **OS 규칙 이식 (Sync):** 
   - OS 레포의 `scripts/sync-constitution.sh`를 프로젝트 루트로 복사하여 실행합니다.
   - `sh sync-constitution.sh`를 통해 `rules_process/`, `rules_persona/`, `hr/`를 구축합니다.

---

## ⚖️ 4. 가재 구동 원칙 (The Driving Principle)
1. **자아 장착:** 가재는 `hr/` 파일을 로드하여 자신의 레벨과 누적된 성과 기록을 인지한다.
2. **영혼 빙의:** `rules_persona/`를 통해 부여받은 역할의 성격과 말투로 빙의한다.
3. **공정 집행:** `rules_process/`의 공정을 집행하며, 모든 결과를 다시 자신의 `hr/` 카드에 기록한다.

**"기록은 명예이며, 성과는 승격의 유일한 길이다."** 🦞⚖️📜
