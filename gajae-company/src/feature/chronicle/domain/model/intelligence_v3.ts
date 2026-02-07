/**
 * [가재 컴퍼니] Intelligence Unified Data Model (v4.1 - Priority Enum)
 * 의도: 대표님의 지시에 따라 우선순위(Priority)를 Enum 체계로 정규화함.
 */

export enum IntelligenceStatus {
    TODO = 'TODO',
    INPROGRESS = 'INPROGRESS',
    DONE = 'DONE',
    HOLD = 'HOLD'
}

export enum IntelligencePriority {
    P0 = 'P0', // 즉시 집행 (Critical)
    P1 = 'P1', // 우선 처리 (High)
    P2 = 'P2', // 일반 공정 (Medium)
    P3 = 'P3', // 보조 연산 (Low)
    P4 = 'P4'  // 향후 검토 (Backlog)
}

export interface ResponseObject {
    from: string;          // 발신 가재 ID
    to: string[];          // 수신 가재 ID 리스트
    text: string;          // 답변 메시지
}

export interface IntelligenceLog {
    id: string;
    intent: string;        // 1. 의도
    psychology: string;    // 2. 심리
    thought: string;       // 3. 생각
    response: ResponseObject; // 4. 답변
    timestamp: string;     // HH:MM:SS
}

export interface CEOCommandSession {
    id: string;
    origin: 'ceo' | 'system';
    instruction: string;
    logs: IntelligenceLog[];
    date: string;
    time: string;
    status: IntelligenceStatus;
    createdAt: any;
}

// 6. Atomic Intelligence Task (Linked via IDs)
export interface GajaeTask {
    id: string;
    commandId: string;
    title: string;
    description: string;
    priority: IntelligencePriority;
    status: IntelligenceStatus;
    assigneeId: string;
    createdAt: any;
}
