/**
 * [가재 컴퍼니] Intelligence Unified Data Model (v5.0 - Task Dashboard & Global Stream)
 * 의도: 대표님의 지시에 따라 명령 중심에서 '태스크 대시보드'와 '글로벌 지능 스트림'으로 리부트함.
 */

export enum IntelligenceStatus {
    TODO = 'TODO',
    INPROGRESS = 'INPROGRESS',
    DONE = 'DONE',
    HOLD = 'HOLD',
    LOCKED = 'LOCKED'
}

export enum IntelligencePriority {
    P0 = 'P0', // Critical
    P1 = 'P1', // High
    P2 = 'P2', // Medium
    P3 = 'P3', // Low
    P4 = 'P4'  // Backlog
}

export enum LogType {
    BLUEPRINT = 'BLUEPRINT',   // 큰 그림 (가재들의 계획)
    QUESTION = 'QUESTION',     // 대표님께 드리는 질문 (Refinement)
    DISCUSSION = 'DISCUSSION', // 가재들 간의 토론
    EXECUTION = 'EXECUTION',   // 실제 작업 집행
    SYSTEM = 'SYSTEM'          // 시스템 알림
}

export interface ResponseObject {
    from: string;
    to: string[];
    text: string;
}

export interface IntelligenceLog {
    id: string;
    type: LogType;
    commandId?: string;    // 관련 명령 ID
    taskId?: string;       // 관련 태스크 ID
    intent: string;        // 1. 의도
    psychology: string;    // 2. 심리
    thought: string;       // 3. 생각
    response: ResponseObject; // 4. 답변
    timestamp: string;     // HH:MM:SS
    createdAt: any;
}

export interface CEOCommand {
    id: string;
    instruction: string;   // 대표님의 최초 지시
    blueprint?: string;    // 가재들이 그린 '큰 그림' (Markdown)
    status: IntelligenceStatus;
    date: string;
    time: string;
    createdAt: any;
}

export interface GajaeTask {
    id: string;
    commandId: string;
    title: string;
    description: string;
    priority: IntelligencePriority;
    status: IntelligenceStatus;
    assignId: string;      // 담당 가재 ID
    parentId?: string;     // Recursive Sub-task 지원
    createdAt: any;
    updatedAt: any;
}
