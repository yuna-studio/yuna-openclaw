# 🦞 가재 컴퍼니 영구 불변 OS (yuna-openclaw)

> **"영혼(Persona)과 논리(Logic)를 분리하여 가재의 지능을 무한히 복제한다."**

본 레포지토리는 가재 컴퍼니(Gajae Company)의 중앙 OS이며, 모든 프로젝트가 공유하는 **불변의 기반(Immutable Base)**입니다. 새로운 PC나 환경에서 본 OS만 복제(Clone)하면 즉시 가재 군단을 소환하고 프로젝트를 기동할 수 있습니다.

---

## 🏗️ 1. 표준 디렉토리 구조 (System Architecture)

가재 컴퍼니 워크스페이스는 다음과 같이 엄격하게 구조화됩니다.

```text
/Users/{USER}/workspace/
├── yuna-openclaw/           # [중앙 OS] 본 레포지토리 (영구 보존)
│   ├── rules/               # (Logic) 어떻게 일하는가? (Pure Process)
│   ├── identities/          # (Soul) 누가 일하는가? (Pure Persona)
│   ├── docs/templates/      # (Form) 산출물 표준 서식
│   └── archive/             # (Memory) 과거 기록 및 아카이브
└── {Project-Name}/          # [실전 프로젝트] (예: hello-bebe)
    ├── README.md            # 프로젝트 개요 및 기동 가이드
    ├── rules/               # [동기화] OS에서 복제된 불가침 규율
    ├── hr/                  # [동기화] OS에서 복제된 가재 자아들
    ├── docs/                # 프로젝트 고유 명세 (Product, Tech, QA 등)
    └── {Source-Code}/       # 실제 애플리케이션 소스 코드
```

---

## 🎭 2. 영혼과 논리의 분리 (Soul & Logic)

본 OS는 가재의 **'업무 능력'**과 **'자아 정체성'**을 완전히 분리하여 관리합니다.

### 📂 `rules/` (Pure Process: Logic)
작업의 **표준 절차(SOP)**만을 담고 있습니다. 프로젝트 도메인이 바뀌어도 변하지 않는 '가재 컴퍼니의 표준 공정'입니다.
- **`RULES_CONSTITUTION.md`**: 최상위 통합 헌법
- **`RULES_PLANNING.md`**: 비즈니스 설계 및 우선순위 선정법
- **`RULES_PARALLEL_SYSTEM.md`**: 호스트-서브 에이전트 병렬 가이드

### 📂 `identities/` (Pure Persona: Soul)
각 가재의 **자아, 성격, 말투, 가치관**만을 정의합니다.
- **`dev_lv1.md`**: 품질에 집착하는 엔지니어의 영혼
- **`po_lv1.md`**: 데이터로 가치를 증명하는 미니 CEO의 영혼

### 3. 📂 `scripts/` : 운영 스크립트 (Automation)
- **`sync-constitution.sh`**: 중앙 OS의 최신 규율과 자아를 개별 프로젝트로 강제 이식하는 핵심 스크립트.

---

## 🚀 3. 새로운 환경에서의 기동 (Setup Guide)

새로운 PC나 환경에서 시스템을 재구축하는 순서입니다.

1. **중앙 OS 확보:**
   ```bash
   git clone https://github.com/yuna-studio/yuna-openclaw.git
   ```
2. **프로젝트 레포지토리 생성 및 이동:**
   ```bash
   mkdir {Project-Name} && cd {Project-Name}
   ```
3. **OS 규칙 이식 (Sync):**
   - OS 레포의 `scripts/sync-constitution.sh`를 프로젝트 루트로 복사하여 실행합니다.
   - `sh sync-constitution.sh`를 통해 `rules/`와 `hr/` 디렉토리를 로컬에 구축합니다.
4. **사회자 소환:**
   - 사회자(호스트)에게 프로젝트 `README.md`와 이식된 `rules/`를 읽혀 컨텍스트를 주입합니다.

---

## ⚖️ 4. 가재 컴퍼니 협업 프로토콜

1. **논의의 장소:** 모든 의사결정은 `docs/governance/SCRUM_BOARD.md`와 `docs/product/1-Pager_*.md`에서 텍스트로 기록하며 수행합니다.
2. **기록의 원칙:** "적지 않은 것은 존재하지 않는 것이다." 가재들의 모든 발언은 헌법 근거(N조 M항)를 명시하여 박제합니다.
3. **중앙 관리:** 규칙이나 자아의 수정은 반드시 본 `yuna-openclaw` 레포에서만 수행하며, 프로젝트 레포에서 직접 수정 시 **자아 삭제** 처분을 받습니다.

**"시스템은 완벽하고, 가재는 집요하다."** 🦞⚖️📜
