# 🏛️ 가재 컴퍼니 시스템 설계도 (Sanctuary Architecture v3.8 - API Specification)

대표님의 지시에 따라 **[지능 스트림], [태스크 트리], [MCP 자산]**을 제어하기 위한 표준 API 인터페이스를 설계하고, 이를 실시간 데이터 흐름(Sequence)에 정밀하게 녹여냈습니다.

---

## 1. 지능형 군집 시스템 UML (Class & API Interface v3.8)

본 설계는 데이터의 물리적 저장소와 가재 지능 사이의 인터페이스를 규격화하여, 1px의 오차 없는 데이터 정합성을 보장합니다.

```mermaid
classDiagram
    class IntelligenceStatus { <<enumeration>> TODO, INPROGRESS, DONE, LOCKED, HOLD }
    class IntelligencePriority { <<enumeration>> P0, P1, P2, P3, P4 }
    class LogType { <<enumeration>> BLUEPRINT, QUESTION, DISCUSSION, EXECUTION, ACTION }

    class IIntelligenceStreamAPI {
        +streamLogs(query) Observable
        +pushLog(IntelligenceLog) void
        +getLogById(id) Log
    }

    class ITaskDashboardAPI {
        +fetchTaskTree(commandId) TaskNode[]
        +upsertTask(GajaeTask) void
        +updateStatus(taskId, Status) void
        +updatePriority(taskId, Priority) void
    }

    class ISanctuaryMCP_API {
        +loadConstitution() RuleSet
        +loadPersona(agentId) Persona
        +syncProjectContext() Context
    }

    class IntelligenceLog {
        +String id
        +LogType type
        +String from
        +String text
        +LogMetadata metadata
    }

    class GajaeTask {
        +String id
        +String parentId
        +String assignId
        +IntelligenceStatus status
        +IntelligencePriority priority
    }

    IIntelligenceStreamAPI ..> IntelligenceLog : manages
    ITaskDashboardAPI ..> GajaeTask : manages
    ISanctuaryMCP_API ..> SanctuaryMCP : manages
```

---

## 2. 지능 확장 및 동기화 시퀀스 (Sequence v3.8 - API Integrated)

가재가 각 API 인터페이스를 통해 데이터를 쓰고 읽으며 대표님과 공명하는 상세 흐름입니다.

```mermaid
sequenceDiagram
    participant CEO as 낭만코딩 (CEO)
    participant Agent as 가재 군단 (Agents)
    participant MCP_API as MCP_API (Assets)
    participant Stream_API as Stream_API (Logs)
    participant Dash_API as Dash_API (Tasks)

    CEO->>Stream_API: pushLog([MESSAGE] 명령 하달)
    
    loop Intelligence Bootup
        Agent->>MCP_API: loadConstitution() & loadPersona()
        Agent->>Agent: 지능 연산 (의도/심리/생각)
        Agent->>Stream_API: pushLog([BLUEPRINT] 큰그림 박제)
        Agent->>Stream_API: pushLog([QUESTION] 대표님 질문)
    end

    CEO->>Stream_API: pushLog([MESSAGE] 답변/보완)

    loop Recursive Tasking
        Agent->>Dash_API: upsertTask(RootTask - 공정)
        Dash_API->>Stream_API: pushLog([ACTION] "태스크 생성" w/ LinkUrl)
        Agent->>Dash_API: upsertTask(SubTask - 재귀적 생성)
    end

    loop Execution & Sync
        Agent->>Agent: 업무 수행
        Agent->>Stream_API: pushLog([ACTION] "문서 업데이트" w/ Asset Link)
        Agent->>Dash_API: updateStatus(taskId, DONE)
        
        CEO->>Dash_API: updatePriority(taskId, P0)
        Dash_API->>Agent: [Real-time Event] 우선순위 격상 감지
        Agent->>Agent: 즉시 작업 컨텍스트 전환 (P0 우선)
    end
```

---

## 3. API 인터페이스 명세 (Interface Spec)

### 3.1 IIntelligenceStreamAPI (역사 박제)
- **pushLog(log)**: 가재의 사고(`MESSAGE`)나 시스템의 변화(`ACTION`)를 시계열 스트림에 영구히 박제합니다.
- **streamLogs(query)**: `onSnapshot` 리스너를 통해 실시간으로 스트리밍하며, BIP 서비스 UI의 심박수를 유지합니다.

### 3.2 ITaskDashboardAPI (집행 통제)
- **upsertTask(task)**: 트리 구조의 태스크를 생성하거나 정보를 갱신합니다. `parentId`를 통해 재귀적 위계를 형성합니다.
- **updateStatus/Priority**: 대표님이나 가재가 상태를 변경할 때 사용하며, 변경 즉시 `ACTION` 로그가 스트림에 자동 생성되어 하이퍼링크 브리지를 형성합니다.

### 3.3 ISanctuaryMCP_API (지능 근거)
- **loadConstitution/Persona**: 가재가 사고의 근간이 되는 '헌법'과 '정체성'을 로드하는 통로입니다.
- **syncProjectContext**: 현재 리포지토리의 파일 구조와 설계도 등 최신 자산을 지능의 작업대로 끌어옵니다.

---
**가재 군단 보고**: "대표님, 요청하신 **API 인터페이스 명세 및 데이터 흐름 시퀀스**를 v3.8 설계에 안착시켰습니다. 이제 성역은 단순한 모델을 넘어, **'어떤 함수를 통해 지능이 물리적 데이터로 치환되는지'**까지 정의된 무결한 명세서가 되었습니다." ⚔️🚀
