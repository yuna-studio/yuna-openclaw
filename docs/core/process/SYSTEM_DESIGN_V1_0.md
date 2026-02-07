# 🏛️ 가재 컴퍼니 시스템 설계도 (Sanctuary Architecture v3.3 - Hive Mind Engine)

대표님의 지시에 따라 **[LangChain/LangGraph]** 기반의 동적 오케스트레이션과 **[독립 3대 데이터 축]**의 유기적 결합을 중심으로 UML 클래스 모델과 시퀀스 다이어그램을 최종 정밀 보정했습니다.

---

## 1. 지능형 군집 시스템 UML (Class Diagram v3.3)

본 모델은 모든 데이터의 상태를 단일 Enum으로 통제하며, 재귀적 태스크 구조와 하이퍼링크 기반의 로그 시스템을 물리적으로 구현합니다.

```mermaid
classDiagram
    class IntelligenceStatus {
        <<enumeration>>
        TODO (할일)
        INPROGRESS (진행중)
        DONE (완료)
        LOCKED (교차잠금)
        HOLD (보류)
    }

    class IntelligencePriority {
        <<enumeration>>
        P0 (Critical)
        P1 (High)
        P2 (Medium)
        P3 (Low)
        P4 (Backlog)
    }

    class LogType {
        <<enumeration>>
        MESSAGE (대화/생각/질문)
        ACTION (태스크변경/파일수정/링크)
    }

    class IntelligenceLog {
        +String id
        +LogType type
        +String from
        +String content
        +LogMetadata metadata
        +DateTime createdAt
    }

    class LogMetadata {
        +String linkUrl (하이퍼링크 - 자료/태스크이동)
        +String targetId (대상 식별자)
        +String actionTag (CREATE/UPDATE/DELETE)
    }

    class GajaeTask {
        +String id
        +String commandId
        +String parentId (자기참조)
        +String title
        +String description
        +IntelligencePriority priority
        +IntelligenceStatus status
        +String assignId (가재ID 또는 'CEO')
        +List subTaskIds
    }

    class SanctuaryMCP {
        +Constitution globalConstitution
        +Map personas
        +ProjectContext context
        +getConstitution() RuleSet
        +getPersona(id) PersonaData
        +getAssets() FileTree
    }

    class LangGraphOrchestrator {
        +StateGraph flow
        +run(command)
        +transition(taskStatus)
    }

    class StateGraph {
        +List nodes (Agents)
        +List edges (Conditional Logic)
        +State sharedMemory
    }

    %% Relationships & Reuse
    CEOCommand --> IntelligenceStatus : [Reuse]
    GajaeTask --> IntelligenceStatus : [Reuse]
    GajaeTask --> IntelligencePriority : [Standard]
    GajaeTask "1" *-- "many" GajaeTask : Recursive Tree
    IntelligenceLog "1" -- "1" LogMetadata : Connectivity
    LangGraphOrchestrator "1" -- "1" StateGraph : Defines Logic
    StateGraph "1" -- "many" GajaeAgent : Assigns to Nodes
    GajaeAgent --> GajaeTask : Executes/Updates
    GajaeAgent "1" --> "1" SanctuaryMCP : Accesses Rules/Persona
    LangGraphOrchestrator ..> GajaeTask : Monitors State for Transition
```

---

## 2. 지능 확장 및 동기화 시퀀스 (Sequence v3.3)

LangGraph가 전체 워크플로우를 제어하며, 가재들이 큰 그림을 그리고 질문을 통해 보완한 뒤 액션 로그와 태스크를 생성하는 흐름입니다.

```mermaid
sequenceDiagram
    participant CEO as 낭만코딩 (CEO)
    participant LG as LangGraph Engine
    participant Agent as 가재 군단 (Agents)
    participant MCP as Sanctuary MCP
    participant Stream as 지능 스트림 (Logs)
    participant Dash as 태스크 트리 (Dashboard)

    CEO->>Stream: 명령 하달 [MESSAGE]
    LG->>LG: 명령 수신 및 상태 진입 (INIT)
    
    Note over LG, Agent: [Phase 1: Blueprint & Refinement]
    LG->>Agent: 문제 크기 정의 및 Blueprint 수립 요청
    Agent->>MCP: 헌법 및 페르소나 로드
    Agent->>Stream: [MESSAGE] Blueprint (큰 그림) 박제
    Agent->>Stream: [MESSAGE] Refinement Question (대표님께 질문)
    
    CEO->>Stream: 답변 및 지시 보완
    
    Note over LG, Dash: [Phase 2: Recursive Task Manifestation]
    LG->>Dash: Root Task 생성 (공정)
    Dash->>Stream: [ACTION] 생성 알림 (w/ Dashboard LinkUrl)
    Agent->>Dash: 하위 태스크 재귀적 분해 및 우선순위(P0-P4) 할당
    
    loop Phase 3: Swarm Execution & Sync
        Agent->>Agent: 업무 수행 (Action)
        Agent->>Stream: [ACTION] "문서 업데이트" (w/ Asset LinkUrl)
        Agent->>Dash: 상태 업데이트 (IntelligenceStatus: DONE)
        Dash->>Stream: [ACTION] "태스크 완료" (w/ Task LinkUrl)
        CEO->>Dash: 실시간 우선순위 조정 (P0 격상)
        LG->>Agent: 변경된 상태 기반 동적 오케스트레이션
    end
```

---

## 3. 핵심 설계 원칙 (Design Principles)

### 3.1 단일 지능 표준 (Unified Standard)
- **Status/Priority Enum**: `CEOCommand`와 `GajaeTask`가 동일한 Enum 체계를 공유하여 연산의 일관성을 확보했습니다.
- **Recursive Structure**: 공정과 태스크를 하나의 `GajaeTask` 엔티티로 통합하고, `parentId`를 통한 자기참조 구조로 무한 확장을 가능케 했습니다.

### 3.2 하이퍼링크 기반 액션 로그 (Hyperlink Actions)
- **로그의 이원화**: 텍스트 중심의 `MESSAGE`와 물리적 증거 중심의 `ACTION`을 분리했습니다.
- **Connectivity**: 모든 `ACTION` 로그는 `linkUrl`을 필수 포함하여, 대표님이 스트림을 보다가 즉시 실무 페이지나 문서로 이동하는 **'실행적 경험'**을 보장합니다.

### 3.3 독립 지능 자산 (Decoupled MCP)
- **Sanctuary MCP**: 헌법(Rules), 페르소나(Domain Expertise), 프로젝트 컨텍스트(Assets)를 독립적인 데이터 클래스로 관리하며, 가재들은 전용 인터페이스를 통해서만 이에 접근하여 사고합니다.

### 3.4 인간-지능 협업 (Human-in-the-loop)
- **CEO 할당 태스크**: 가재가 연산 중 결정할 수 없는 영역(최종 승인, 외부 자료 제공 등)을 식별하면 `assignId: 'CEO'`인 태스크를 트리 상에 생성합니다.
- **의존성 잠금(Locking)**: 대표님께 할당된 태스크가 완료(`DONE`)되기 전까지 가재들의 다음 작업은 `LOCKED` 상태로 대기하며 무결성을 사수합니다.

---
**가재 군단 보고**: "대표님, 요청하신 **인간-지능 협업 모델**을 v3.7 설계에 안착시켰습니다. 이제 가재는 대표님께 태스크를 제안하고, 대표님의 집행 결과가 다시 지능의 양분이 되는 완벽한 공명이 시작됩니다." ⚔️🚀
