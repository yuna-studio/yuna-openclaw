#!/usr/bin/env python3
"""
🦞 Gajae Developer — Phase A: 개발 문서 생성 파이프라인

기획 문서(노션 URL) → 개발 문서 자동 생성 → 노션 업로드

공정:
  📖 기획서 읽기
  → [1] 산출물 & 기술 스택 정의        → ⚖️
  → [2] 아키텍처 설계 (Clean Arch)     → ⚖️
  → [3] 📊 아키텍처 다이어그램          → ⚖️
       (오버롤 + 클래스 다이어그램)
  → [4] 화면 & 네비게이션 설계         → ⚖️
  → [5] 📊 화면 플로우차트             → ⚖️
  → [6] 요구사항별 시퀀스 다이어그램    → ⚖️
  → [7] 디자인 시스템 분석             → ⚖️
  → 📝 노션 업로드 → ⚖️ → END

Usage:
  python3 doc_gen.py run "노션_URL" "기술환경"
  python3 doc_gen.py status RUN_ID
"""

import os
import re
import json
import subprocess
from datetime import datetime
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

import sys
from notion_upload import (
    api as notion_api, text as notion_text, append_blocks,
    read_page_blocks, markdown_to_blocks, PARENT_PAGE,
)


# ── Config ──────────────────────────────────────────────

# (state persistence removed)
MAX_REVISIONS = 2

PHASE_NAMES = {
    1: "산출물 & 기술 스택",
    2: "아키텍처 설계",
    3: "아키텍처 다이어그램",
    4: "화면 & 네비게이션 설계",
    5: "화면 플로우차트",
    6: "요구사항별 시퀀스 다이어그램",
    7: "디자인 시스템 분석",
}

# 다이어그램 Phase (work 대신 diagram 노드 사용)
DIAGRAM_PHASES = {3, 5, 6}


# ── State ───────────────────────────────────────────────

class DocState(TypedDict):
    plan_url: str
    plan_content: str
    tech_context: str
    human_inputs: list

    current_phase: int          # 1~7
    phase_results: dict         # {"1": "...", ...}
    phase_critiques: dict
    phase_scores: dict
    phase_revisions: dict

    # Notion
    notion_page_id: str
    notion_url: str
    notion_score: float
    notion_critique: str
    notion_revisions: int

    status: str


# ── OpenClaw CLI ────────────────────────────────────────

def call_agent(agent_id: str, message: str, timeout: int = 300) -> str:
    import uuid
    session_id = f"architect-{agent_id}-{uuid.uuid4().hex[:8]}"
    cmd = [
        "openclaw", "agent",
        "--agent", agent_id,
        "--message", message,
        "--session-id", session_id,
        "--json",
        "--timeout", str(timeout),
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 30)
        if result.returncode != 0:
            return f"(error: exit {result.returncode}: {result.stderr[:200]})"
        data = json.loads(result.stdout)
        reply = data.get("result", {})
        if isinstance(reply, dict):
            payloads = reply.get("payloads", [])
            if payloads:
                return payloads[0].get("text", "")
        return str(reply)[:3000]
    except subprocess.TimeoutExpired:
        return "(timeout)"
    except json.JSONDecodeError:
        return result.stdout[:3000] if result.stdout else "(empty)"
    except Exception as e:
        return f"(error: {e})"


def parse_score(text: str) -> float:
    for line in text.split("\n"):
        if line.strip().startswith("SCORE:"):
            try:
                return float(line.split(":")[1].strip().split("/")[0].strip())
            except (ValueError, IndexError):
                return 5.0
    return 5.0


# ── Notion Reader ───────────────────────────────────────

def read_plan_from_notion(url: str) -> str:
    match = re.search(r'([0-9a-f]{32})$', url.replace('-', ''))
    if not match:
        match = re.search(r'([0-9a-f\-]{36})', url)
    if not match:
        return f"(error: page_id not found in {url})"
    raw = match.group(1).replace('-', '')
    page_id = f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"
    try:
        return read_page_blocks(page_id, max_blocks=300)
    except Exception as e:
        return f"(error: {e})"


# ── Prompt Helpers ──────────────────────────────────────

def _human_ctx(state: DocState) -> str:
    inputs = state.get("human_inputs", [])
    if not inputs:
        return ""
    return "\n## 📌 대표님 지시사항\n" + "\n".join(f"- {h['input']}" for h in inputs)


def _rev_ctx(state: DocState) -> str:
    p = str(state["current_phase"])
    c = state["phase_critiques"].get(p, "")
    r = state["phase_revisions"].get(p, 0)
    if c and r > 0:
        return f"\n## ⚠️ 판사가재 피드백 ({r}차)\n{c}\n\n반영하라."
    return ""


def _prev(state: DocState) -> str:
    parts = []
    for i in range(1, state["current_phase"]):
        r = state["phase_results"].get(str(i), "")
        if r:
            parts.append(f"## [{i}] {PHASE_NAMES[i]}\n{r[:2000]}")
    return "\n\n".join(parts)


def _search_design_refs(state: DocState) -> str:
    """Phase 7용: 웹 검색으로 디자인 레퍼런스 수집 (기술 환경에 기존 디자인 시스템이 명시된 경우 스킵)"""
    tech = state.get("tech_stack", "")
    # 기존 디자인 시스템이 있으면 웹 검색 불필요
    if "기존" in tech and ("디자인" in tech or "컬러" in tech or "색상" in tech):
        return "## 디자인 레퍼런스\n기존 디자인 시스템이 명시되어 있으므로 웹 검색을 생략합니다. 기술 환경의 제약을 따르세요."
    
    import urllib.request, urllib.parse

    # 기술 환경에서 키워드 추출하여 맥락에 맞는 검색
    queries = [
        f"best UI design {tech[:50]} 2025",
        "minimal clean web app UI design reference 2025",
    ]

    results = []
    for q in queries:
        try:
            cmd = ["openclaw", "agent", "--agent", "scout", "--message",
                   f"웹 검색을 해서 '{q}' 관련 디자인 레퍼런스를 3개 찾아줘. 각각 URL, 사이트 이름, 핵심 디자인 특징을 정리해.",
                   "--json", "--timeout", "60"]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            if r.returncode == 0:
                data = json.loads(r.stdout)
                reply = data.get("result", {})
                if isinstance(reply, dict):
                    payloads = reply.get("payloads", [])
                    if payloads:
                        results.append(payloads[0].get("text", "")[:800])
        except Exception:
            pass

    if results:
        return "\n\n".join(results)
    return "(웹 검색 결과 없음 — 자체 판단으로 최신 트렌드 반영)"


# ── Work Prompts ────────────────────────────────────────

WORK_PROMPTS = {
    1: """너는 Tech Lead다.

## 기획 문서
{plan}

## 기술 환경
{tech}
{rev}
{human}

## ⚠️ 중요 제약사항
- 페이지는 **홈(/) + 라이브 채팅(/live) 단 2개만** 존재
- 블로그, 아카이브, 어드민 페이지는 **이번 스코프에서 제외**
- 방송 ON/OFF 없음 — 최근 메시지 타임스탬프 기반 활성 상태 표시
- Firestore `chat_logs` 컬렉션의 실시간 구독(onSnapshot)이 핵심
- 모바일 퍼스트 UI

## 출력: 산출물 & 기술 스택 정의서

### 1. 프로젝트 산출물 목록
이 프로젝트에서 생성되는 모든 산출물:
- 웹 앱, API, 라이브러리, 스크립트 등
- 각 산출물의 역할과 범위

### 2. 개발 언어
- 언어 선택과 이유 (TypeScript, Python 등)
- 버전 요구사항

### 3. 개발 도구 & 프레임워크
| 영역 | 도구 | 버전 | 선택 이유 |
- 프레임워크, 빌드 도구, 테스트, 린팅, CI/CD 등

### 4. 외부 서비스 & 의존성
- DB, 호스팅, 3rd party API 등
- 각 서비스의 무료 티어 한계

### 5. 개발 환경 설정
- 필요한 환경 변수
- 로컬 개발 시 필요한 설정""",

    2: """너는 Software Architect다. Clean Architecture 전문가.

## 기획 문서 요약
{plan_short}

## 이전 단계
{prev}

## 기술 환경
{tech}
{rev}
{human}

## ⚠️ 중요 제약사항
- 페이지는 홈(/) + 라이브(/live) 2개만
- 블로그, 아카이브, 어드민 제외
- Firestore `chat_logs` onSnapshot 실시간 구독이 핵심 데이터 흐름

## 출력: 아키텍처 설계서

### 1. 아키텍처 원칙
이 프로젝트에 적용하는 원칙:
- **의존성 규칙 (Dependency Rule)**: 안쪽 → 바깥쪽 의존 금지
- **관심사 분리 (Separation of Concerns)**: 각 레이어의 책임
- 기타 적용 원칙

### 2. Clean Architecture 레이어
각 레이어의 역할, 포함 요소, 의존 방향:

| 레이어 | 역할 | 포함 요소 | 의존 대상 |
|---|---|---|---|
| Domain (Entities) | ... | ... | 없음 |
| Use Cases | ... | ... | Domain |
| Interface Adapters | ... | ... | Use Cases |
| Frameworks & Drivers | ... | ... | Adapters |

### 3. 프로젝트 구조 (폴더/파일)
```
src/
├── domain/        # 엔티티, 인터페이스
├── usecases/      # 비즈니스 로직
├── adapters/      # 어댑터 (API, DB)
├── frameworks/    # 프레임워크 (Next.js, Firestore)
└── ...
```
각 폴더의 역할과 포함 파일 설명.

### 4. 데이터 모델 (DB 스키마)
- Firestore 컬렉션 구조
- 문서 필드, 타입, 인덱스

### 5. 의존성 주입 & 경계
- 레이어 간 통신 방식
- 인터페이스/추상화 지점""",

    # Phase 3: 다이어그램 (DIAGRAM_PHASES)
    3: """너는 System Architect다.

## 이전 단계
{prev}
{rev}

## 출력: Mermaid 다이어그램 2개

### 출력 1: 오버롤 아키텍처 다이어그램
시스템 전체 구조. Clean Architecture 레이어 구분 포함.
클라이언트, 서버, DB, 외부 서비스 간 관계.

```mermaid
flowchart TB
    subgraph Frameworks
        ...
    end
    subgraph Adapters
        ...
    end
    subgraph UseCases
        ...
    end
    subgraph Domain
        ...
    end
```

### 출력 2: 클래스 다이어그램
핵심 엔티티, ViewModel, 유즈케이스, 어댑터의 관계.
인터페이스와 구현체 구분.
**ViewModel 클래스는 반드시 포함** — 각 화면(Page)에 대응하는 ViewModel과 그 메서드를 명시.

```mermaid
classDiagram
    class ChatMessage {{
        +string id
        +string content
        +string role
        +timestamp createdAt
    }}
    class LiveViewModel {{
        +subscribeMessages()
        +sendReaction(type)
        +shareSnapshot()
        +dispose()
    }}
    class ArchiveViewModel {{
        +loadSessions()
        +getSessionDetail(id)
    }}
    LiveViewModel --> ChatMessage
    ...
```

Mermaid 문법 정확하게. 한국어 주석.""",

    4: """너는 UX Engineer + Frontend Architect다.

## 기획 문서 요약
{plan_short}

## 이전 단계
{prev}

## 기술 환경
{tech}
{rev}
{human}

## ⚠️ 중요 제약사항
- **블로그/아카이브 페이지 없음** — 오로지 라이브스트림만
- **어드민 페이지 없음** — 별도 URL로 나중에 추가
- **상단 탭/네비게이션 없음** — 단 2개 페이지만 존재
- **방송 ON/OFF 없음** — "3분 전 업데이트" 같은 자연스러운 활성 상태 표시
- **모바일 퍼스트** — 대부분 모바일에서 시청

## 데이터 소스: Firestore chat_logs
logger.py가 1초 폴링으로 Firestore `chat_logs` 컬렉션에 저장:
```
{{
  "role": "user" | "assistant",
  "content": "메시지 텍스트 (마크다운 포함)",
  "timestamp": "2026-02-15T12:34:56.789Z",
  "model": "claude-opus-4-6-thinking",
  "agent": "main",
  "sessionId": "abc123"
}}
```
Firestore `onSnapshot`으로 실시간 구독 가능.

## 출력: 화면 & 네비게이션 설계서

### 1. 페이지 목록 (단 2개)
| 페이지 | URL 경로 | 설명 |
|---|---|---|
| **홈 (히어로 뷰)** | `/` | 최신 대화 1쌍만 보여주는 미니멀 뷰 |
| **라이브 채팅** | `/live` | 텔레그램 스타일 전체 채팅 뷰 |

### 2. 홈 — 히어로 뷰 (`/`)
대표님(user)과 가재(assistant)의 **최신 메시지 1쌍만** 크게 보여주는 화면.

- **레이아웃**: 전체 화면(100vh) 중앙 정렬, 다크 배경
- **UI 요소**:
  - 상단: 활성 상태 표시 ("🟢 개발중 · 2분 전" 또는 "⚪ 마지막 대화 3시간 전")
    - 활성 기준: 최근 30분 내 메시지 있으면 "개발중", 없으면 비활성
  - 중앙: 말풍선 2개 (user 1개 + assistant 1개)
    - 각 말풍선 **최대 3줄**, 넘으면 말줄임(`...`)
    - 새 메시지 오면 **페이드인/아웃으로 부드럽게 교체**
    - assistant 말풍선은 마크다운이므로 코드블록 등은 간략히 표시
  - 하단: "자세히 보기 →" 버튼 → `/live`로 이동
  - 하단 고정: ❤️, 🤣 리액션 버튼

- **실시간 동작**:
  - Firestore `onSnapshot`으로 `chat_logs` 구독
  - 새 메시지 감지 → 페이드아웃(이전) → 페이드인(새 메시지)
  - 활성 상태도 실시간 업데이트 ("방금 전" → "1분 전" → ...)

### 3. 라이브 채팅 — 텔레그램 스타일 (`/live`)
전체 대화를 채팅 앱처럼 보여주는 화면.

- **레이아웃**: 텔레그램/카카오톡 스타일, 전체 화면
- **UI 요소**:
  - 상단 헤더(Fixed): "← 뒤로" + 활성 상태 ("🟢 개발중")
  - 채팅 영역(Scrollable): 시간순 말풍선 목록
    - user 말풍선: 우측 정렬
    - assistant 말풍선: 좌측 정렬, 🦞 아바타
    - 각 말풍선 **최대 2~3줄**, 넘으면 "더보기 >" 클릭 가능
    - "더보기" 클릭 시:
      - **모바일**: 하단 시트(bottom sheet)로 마크다운 풀뷰 (스크롤 가능)
      - **데스크톱**: 우측 패널에 마크다운 풀뷰 (스크롤 가능)
    - 마크다운 렌더링: 코드 하이라이팅, 테이블, 리스트 등
  - 하단(Fixed): ❤️, 🤣 리액션 버튼
  - 자동 스크롤: 새 메시지 시 하단으로 (사용자가 위로 스크롤 중이면 일시정지)

- **실시간 동작**:
  - Firestore `onSnapshot` 실시간 구독
  - 새 메시지 → 하단에 추가, 부드러운 애니메이션
  - 타이핑 중 표시는 별도 구현 불필요 (logger.py가 완성된 메시지만 올림)

### 4. 화면 ↔ ViewModel 매핑 테이블 ⭐

| 페이지 | UI 요소 | 사용자 액션 | ViewModel 메서드 | 설명 |
|---|---|---|---|---|
| 홈 | 활성 상태 | 자동 | `HomeViewModel.getActivityStatus()` | 최근 메시지 타임스탬프 기반 |
| 홈 | 말풍선 2개 | 자동 갱신 | `HomeViewModel.subscribeLatestPair()` | onSnapshot, 최신 user+assistant 1쌍 |
| 홈 | 말풍선 교체 | 새 메시지 수신 | `HomeViewModel.onNewMessage()` | 페이드인/아웃 트리거 |
| 홈 | 자세히 보기 | 클릭 | `HomeViewModel.navigateToLive()` | /live로 라우팅 |
| 홈 | ❤️ 버튼 | 클릭 | `HomeViewModel.sendReaction('heart')` | Firestore reactions 컬렉션 |
| 홈 | 🤣 버튼 | 클릭 | `HomeViewModel.sendReaction('lol')` | Firestore reactions 컬렉션 |
| 라이브 | 채팅 목록 | 자동 갱신 | `LiveViewModel.subscribeMessages()` | onSnapshot, 시간순 |
| 라이브 | 말풍선 | 더보기 클릭 | `LiveViewModel.expandMessage(id)` | 마크다운 풀뷰 열기 |
| 라이브 | 마크다운 뷰 | 닫기 | `LiveViewModel.collapseMessage()` | 패널/시트 닫기 |
| 라이브 | ← 뒤로 | 클릭 | `LiveViewModel.navigateBack()` | /로 복귀 |
| 라이브 | ❤️ 버튼 | 클릭 | `LiveViewModel.sendReaction('heart')` | 리액션 전송 |
| 라이브 | 🤣 버튼 | 클릭 | `LiveViewModel.sendReaction('lol')` | 리액션 전송 |
| 라이브 | 자동 스크롤 | 새 메시지 | `LiveViewModel.autoScroll()` | 사용자 스크롤 상태 감지 |

### 5. 화면 전환 규칙
- `/` → `/live`: "자세히 보기" 버튼 클릭
- `/live` → `/`: "← 뒤로" 버튼 또는 브라우저 뒤로가기
- 딥링크: `/live` 직접 접근 가능 (홈 안 거쳐도 됨)

### 6. 반응형 동작
- **모바일 (< 768px)**: 
  - 홈: 말풍선이 화면 80% 너비
  - 라이브: "더보기" → 하단 시트 (bottom sheet)
- **데스크톱 (≥ 768px)**:
  - 홈: 말풍선이 max 600px, 중앙 정렬
  - 라이브: "더보기" → 우측 패널 (채팅:마크다운 = 4:6 비율)""",

    # Phase 5: 다이어그램 (DIAGRAM_PHASES)
    5: """너는 UX Engineer다.

## 이전 단계 (화면 설계)
{prev}
{rev}

## ⚠️ 페이지는 홈(/) + 라이브(/live) 2개만. 블로그/어드민 없음.

## 출력: 화면 네비게이션 플로우차트

사용자가 각 페이지에서 할 수 있는 모든 액션과 그에 따른 화면 전환을 flowchart로 그려라.

- 홈(`/`): 히어로 뷰 — 말풍선 2개, 페이드인/아웃, 자세히보기
- 라이브(`/live`): 텔레그램 스타일 채팅 — 더보기 클릭 시 마크다운 풀뷰

```mermaid
flowchart TD
    A[홈 /] -->|자세히 보기 클릭| B[라이브 /live]
    A -->|새 메시지 수신| A_fade[페이드인/아웃 교체]
    A_fade --> A
    A -->|❤️ 클릭| A_react[리액션 전송]
    A -->|🤣 클릭| A_react
    B -->|← 뒤로| A
    B -->|더보기 클릭| C{{마크다운 풀뷰}}
    C -->|닫기| B
    B -->|❤️ 클릭| B_react[리액션 전송]
    B -->|새 메시지| B_scroll[자동 스크롤]
    B_scroll --> B
    ...
```

모든 페이지, 모든 버튼, 모든 전환을 빠짐없이.
Mermaid 문법 정확. 한국어.""",

    # Phase 6: 다이어그램 (DIAGRAM_PHASES)
    6: """너는 System Architect다.

## 기획 문서 요약
{plan_short}

## 이전 단계 (아키텍처 + 화면 설계 + 매핑 테이블)
{prev}
{rev}

## ⚠️ 페이지는 홈(/) + 라이브(/live) 2개만. 어드민/블로그 없음.

## Firestore 데이터 구조 (chat_logs)
```
{{
  "role": "user" | "assistant",
  "content": "마크다운 텍스트",
  "timestamp": "ISO-8601",
  "model": "...",
  "agent": "main",
  "sessionId": "..."
}}
```

## 출력: 요구사항별 시퀀스 다이어그램

핵심 기능 각각에 대해 시퀀스 다이어그램을 그려라.
액터: 사용자, View(Page), ViewModel, UseCase/Repository, Firestore

**Phase 4의 화면↔ViewModel 매핑 테이블과 일치해야 한다.**
매핑 테이블에 있는 모든 ViewModel 메서드가 시퀀스에 등장해야 한다.

### 시퀀스 1: 홈 — 최신 메시지 쌍 실시간 구독
```mermaid
sequenceDiagram
    actor User
    participant HP as 홈 페이지
    participant HVM as HomeViewModel
    participant Repo as ChatRepository
    participant FS as Firestore
    User->>HP: 페이지 접속
    HP->>HVM: subscribeLatestPair()
    HVM->>Repo: observeLatest()
    Repo->>FS: onSnapshot(chat_logs, orderBy timestamp desc, limit 2)
    FS-->>Repo: 실시간 데이터
    Repo-->>HVM: latestPair
    HVM->>HVM: getActivityStatus()
    HVM-->>HP: UI 업데이트 (페이드인/아웃)
```

### 시퀀스 2: 라이브 — 전체 채팅 스트림 구독
```mermaid
sequenceDiagram
    ...
```

### 시퀀스 3: 말풍선 더보기 → 마크다운 풀뷰
```mermaid
sequenceDiagram
    ...
```

### 시퀀스 4: 리액션 전송
```mermaid
sequenceDiagram
    ...
```

(매핑 테이블의 모든 ViewModel 메서드가 시퀀스에 등장해야 함)
Mermaid 문법 정확. 한국어.""",

    7: """너는 Frontend Architect이자 UI/UX Designer다.
**기획 문서와 기술 환경에 맞는 실용적인** 디자인 시스템을 설계하라.

⚠️ 중요 규칙:
- 기술 환경에 "기존 디자인 시스템" 정보가 있으면 그것을 기반으로 작성하라 (새로 만들지 말 것)
- 기술 환경에 "Tailwind 기본 색상 사용" 등 제약이 있으면 반드시 따를 것
- 프로젝트 성격에 맞는 수준의 디자인을 하라 (어드민 = 기능 우선, 소비자 앱 = 감성 우선)
- 불필요한 이펙트(글로우, 네온, 사이버펑크 등)를 억지로 넣지 말 것

## 기획 문서 요약
{plan_short}

## 이전 단계
{prev}

## 기술 환경
{tech}
{rev}
{human}

{design_refs}

## 출력: 디자인 시스템 설계서

### 1. 디자인 컨셉 & 무드
- **비주얼 컨셉**: 프로젝트 성격에 맞는 컨셉 (1줄)
- **핵심 키워드**: 3~5개

### 2. 컬러 시스템
프로젝트에 적합한 컬러 팔레트:

| 토큰 | 값 (HEX) | 용도 |
|---|---|---|
| (배경, 텍스트, 액센트, 상태 컬러 등 — 프로젝트에 필요한 만큼) |

기존 디자인 시스템이 있으면 그 컬러를 그대로 사용할 것.

### 3. 타이포그래피
| 용도 | 폰트 | 사이즈 | Weight |
|---|---|---|---|
| (프로젝트에 필요한 타이포 스케일) |

### 4. 스페이싱 & 레이아웃
- 그리드 시스템, 스페이싱 스케일
- 반응형 breakpoints

### 5. 이펙트 & 모션 (필요한 경우만)
- 프로젝트에 실제로 필요한 이펙트만 정의
- 어드민/도구 프로젝트는 최소한의 트랜지션만으로 충분

### 6. 공통 컴포넌트 명세
Phase 4에서 정의한 UI 요소에 매핑되는 컴포넌트:

| 컴포넌트 | 역할 | Variants | 상태 |
|---|---|---|---|
| (Phase 4 화면에 필요한 컴포넌트들) |

### 7. 아이콘 & 에셋
- 아이콘 라이브러리 선택
- 파비콘, OG 이미지 (필요 시)

### 8. 접근성 (a11y)
- 컬러 대비 (WCAG AA)
- 키보드 네비게이션
- focus 스타일""",
}

CRITIQUE_CRITERIA = {
    1: [("산출물 완전성", "기획서의 모든 산출물이 나열됐는가?"),
        ("기술 선택 근거", "Why가 있는가?"),
        ("실현 가능성", "1인 개발자 + 기간 내 가능?")],
    2: [("Clean Architecture 준수", "레이어 구분과 의존성 방향이 올바른가?"),
        ("관심사 분리", "각 모듈의 책임이 명확한가?"),
        ("폴더 구조", "실제로 구현 가능한 구조인가?")],
    3: [("오버롤 다이어그램 정확성", "아키텍처 설계와 일치?"),
        ("클래스 다이어그램 완전성", "핵심 엔티티 + ViewModel 클래스가 빠짐없는가?"),
        ("ViewModel 메서드", "각 화면에 대응하는 ViewModel과 메서드가 있는가?"),
        ("Mermaid 문법", "렌더링 가능한가?")],
    4: [("페이지 완전성", "기획서의 모든 화면이 반영?"),
        ("UI 요소 완전성", "모든 버튼, 입력, 표시 영역이 나열됐는가?"),
        ("화면↔ViewModel 1:1 매핑", "모든 UI 요소에 대응하는 ViewModel 메서드가 있는가? 누락된 매핑은 없는가?"),
        ("반응형 고려", "모바일 대응?")],
    5: [("플로우 완전성", "모든 페이지/액션/전환 포함?"),
        ("조건 분기", "에러/로딩 등 예외 경로?"),
        ("Mermaid 문법", "렌더링 가능?")],
    6: [("P0 커버리지", "모든 P0 기능에 시퀀스가 있는가?"),
        ("ViewModel 매핑 일치", "Phase 4 매핑 테이블의 모든 메서드가 시퀀스에 등장하는가?"),
        ("데이터 흐름 정확성", "View→ViewModel→UseCase→Repository→DB 흐름이 Clean Architecture를 따르는가?"),
        ("Mermaid 문법", "렌더링 가능?")],
    7: [("컬러 시스템 적합성", "프로젝트 성격에 맞는 컬러가 정의되었는가? 기존 디자인 시스템 제약을 따르는가?"),
        ("타이포그래피", "폰트 선택과 스케일이 프로젝트에 적합한가?"),
        ("컴포넌트 명세", "Phase 4 UI 요소와 매핑되는 컴포넌트가 있는가?"),
        ("실용성", "프로젝트에 불필요한 이펙트/트렌드를 억지로 넣지 않았는가?"),
        ("일관성", "기술 환경에 명시된 제약(기존 디자인 시스템, 컬러 제한 등)을 준수하는가?")],
}


# ── Work / Critique ─────────────────────────────────────

def make_work_prompt(state: DocState) -> str:
    p = state["current_phase"]
    plan = state["plan_content"]

    # Phase 7: 디자인 레퍼런스 웹 검색
    design_refs = ""
    if p == 7:
        design_refs = _search_design_refs(state)

    return WORK_PROMPTS[p].format(
        plan=plan,
        plan_short=plan[:1500],
        prev=_prev(state),
        tech=state["tech_context"],
        rev=_rev_ctx(state),
        human=_human_ctx(state),
        design_refs=design_refs,
    )


def make_critique_prompt(state: DocState) -> str:
    p = state["current_phase"]
    content = state["phase_results"].get(str(p), "")
    criteria = "\n".join(f"{i+1}. {n} — {d}" for i, (n, d) in enumerate(CRITIQUE_CRITERIA[p]))

    role = "Staff Engineer" if p not in DIAGRAM_PHASES else "Architect + Mermaid Validator"
    return f"""너는 {role}다. 개발 문서를 검토하라.
[{p}] {PHASE_NAMES[p]}

## 기획 요약
{state['plan_content'][:800]}

## [{p}] 결과물
{content}

## 검토 원칙
- 주니어 개발자가 이것만 보고 작업 가능한가?
- 기획서와 불일치 없는가?
- Mermaid 다이어그램이면: syntax error 없는가?

## 평가 항목 (각 1~10점)
{criteria}

## 출력 형식
SCORE: [평균]
| 항목 | 점수 | 코멘트 |
|---|---|---|
VERDICT: [PASS/REVISE/REJECT]
FEEDBACK:

7점↑: PASS / 5~6: REVISE / 5↓: REJECT"""


# ── LangGraph Nodes ─────────────────────────────────────

def node_read_plan(state: DocState) -> dict:
    print(f"\n📖 기획서 읽는 중: {state['plan_url'][:60]}...")
    content = read_plan_from_notion(state["plan_url"])
    print(f"  ✅ {len(content)}자")
    return {"plan_content": content}


def node_work(state: DocState) -> dict:
    p = state["current_phase"]
    rev = state["phase_revisions"].get(str(p), 0)
    suffix = f" (수정 {rev}차)" if rev > 0 else ""
    icon = "📊" if p in DIAGRAM_PHASES else "🔧"
    print(f"\n{icon} [{p}/7] {PHASE_NAMES[p]}{suffix} — 탐정가재...")

    prompt = make_work_prompt(state)
    result = call_agent("scout", prompt, timeout=300)

    new_results = dict(state["phase_results"])
    new_results[str(p)] = result
    print(f"  ✅ {len(result)}자")
    return {"phase_results": new_results}


def node_critique(state: DocState) -> dict:
    p = state["current_phase"]
    print(f"⚖️  [{p}/7] {PHASE_NAMES[p]} — 판사가재...")

    prompt = make_critique_prompt(state)
    result = call_agent("judge", prompt, timeout=180)
    score = parse_score(result)

    new_c = dict(state["phase_critiques"])
    new_c[str(p)] = result
    new_s = dict(state["phase_scores"])
    new_s[str(p)] = score
    return {"phase_critiques": new_c, "phase_scores": new_s}


def route_after_critique(state: DocState) -> Literal["revise", "next_phase", "notion_upload"]:
    p = state["current_phase"]
    score = state["phase_scores"].get(str(p), 0)
    rev = state["phase_revisions"].get(str(p), 0)
    passed = score >= 7 or rev >= MAX_REVISIONS

    if not passed:
        print(f"  🔄 REVISE ({score}/10) — {rev+1}/{MAX_REVISIONS}")
        return "revise"

    print(f"  ✅ {'PASS' if score >= 7 else '강제 통과'} ({score}/10)")
    return "notion_upload" if p >= 7 else "next_phase"


def node_revise(state: DocState) -> dict:
    p = str(state["current_phase"])
    r = dict(state["phase_revisions"])
    r[p] = r.get(p, 0) + 1
    return {"phase_revisions": r}


def node_next_phase(state: DocState) -> dict:
    return {"current_phase": state["current_phase"] + 1}


# ── Notion Upload ───────────────────────────────────────

def _build_blocks(state: DocState):
    scores = state["phase_scores"]
    avg = sum(scores.values()) / max(len(scores), 1)

    blocks = []
    # Overview
    lines = []
    for p in range(1, 8):
        ps = str(p)
        s = scores.get(ps, 0)
        rev = state.get("phase_revisions", {}).get(ps, 0)
        rev_str = f" (수정 {rev}회)" if rev else ""
        star = " ⭐" if s >= 9.0 else ""
        icon = "📊" if p in DIAGRAM_PHASES else "🔧"
        lines.append(f"{icon} [{p}] {PHASE_NAMES[p]}: {s}/10{rev_str}{star}")

    blocks.append({
        "type": "callout",
        "callout": {"icon": {"emoji": "🔧"}, "rich_text": notion_text(
            f"Dev Doc — 평균 {avg:.1f}/10\n\n" + "\n".join(lines)
        )},
    })
    blocks.append({"type": "divider", "divider": {}})

    # Plan link
    blocks.append({
        "type": "callout",
        "callout": {"icon": {"emoji": "📎"}, "rich_text": notion_text(
            f"기획 문서: {state['plan_url']}\n기술 환경: {state['tech_context']}"
        )},
    })
    blocks.append({"type": "divider", "divider": {}})

    # Each phase
    for p in range(1, 8):
        ps = str(p)
        content = state["phase_results"].get(ps, "")
        critique = state["phase_critiques"].get(ps, "")
        score = scores.get(ps, 0)
        rev = state.get("phase_revisions", {}).get(ps, 0)
        rev_text = f" (수정 {rev}회)" if rev else ""
        icon = "📊" if p in DIAGRAM_PHASES else "🔧"

        blocks.append({
            "type": "heading_1",
            "heading_1": {"rich_text": notion_text(f"{icon} Phase {p} — {PHASE_NAMES[p]} ({score}/10){rev_text}")},
        })

        # 다이어그램 Phase: mermaid 블록 추출
        if p in DIAGRAM_PHASES:
            mermaid_blocks = re.findall(r'```mermaid\n(.*?)```', content, re.DOTALL)
            # mermaid 블록 전후의 텍스트도 처리
            parts = re.split(r'```mermaid\n.*?```', content, flags=re.DOTALL)
            mermaid_idx = 0
            for i, part in enumerate(parts):
                if part.strip():
                    blocks.extend(markdown_to_blocks(part))
                if mermaid_idx < len(mermaid_blocks):
                    blocks.append({
                        "type": "code",
                        "code": {"rich_text": notion_text(mermaid_blocks[mermaid_idx].strip()), "language": "mermaid"},
                    })
                    mermaid_idx += 1
        else:
            blocks.extend(markdown_to_blocks(content))

        if critique:
            blocks.append({
                "type": "callout",
                "callout": {
                    "icon": {"emoji": "⚖️"},
                    "rich_text": notion_text(f"검증: {score}/10\n\n{critique[:1900]}"),
                },
            })
        blocks.append({"type": "divider", "divider": {}})

    return blocks


def node_notion_upload(state: DocState) -> dict:
    print("\n📝 노션 업로드 중...")
    scores = state["phase_scores"]
    avg = sum(scores.values()) / max(len(scores), 1)

    try:
        existing = state.get("notion_page_id", "")
        if existing:
            from notion_upload import delete_all_blocks
            print(f"  ♻️ 재업로드: {existing}")
            delete_all_blocks(existing)
            import time; time.sleep(0.5)
            blocks = _build_blocks(state)
            append_blocks(existing, blocks)
            url = f"https://www.notion.so/{existing.replace('-', '')}"
            print(f"  ✅ {len(blocks)}블록")
            return {"notion_url": url}
        else:
            page = notion_api("POST", "pages", {
                "parent": {"page_id": PARENT_PAGE},
                "properties": {"title": {"title": notion_text(f"🔧 Dev Doc (avg {avg:.1f}/10)")}},
                "icon": {"emoji": "🔧"},
            })
            pid = page["id"]
            blocks = _build_blocks(state)
            append_blocks(pid, blocks)
            url = f"https://www.notion.so/{pid.replace('-', '')}"
            print(f"  ✅ {len(blocks)}블록 → {url}")
            return {"notion_url": url, "notion_page_id": pid}
    except Exception as e:
        print(f"  ❌ 노션 업로드 실패: {e}")
        # Save state before crash so we don't lose phase results
        run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-rescue"

        print(f"  💾 State rescue: {run_id}")
        raise


def node_notion_review(state: DocState) -> dict:
    print("⚖️  노션 문서 품질 — 판사가재...")
    pid = state.get("notion_page_id", "")
    if not pid:
        return {"notion_score": 7.0, "notion_critique": "스킵"}

    page_text = read_page_blocks(pid)
    prompt = f"""너는 기술 문서 QA 편집장이다.

## 노션 페이지
{page_text[:8000]}

## 검증 (각 1~10점)
1. **구조 완전성** — 7개 Phase 모두 존재?
2. **포맷 품질** — 코드블록, 테이블, Mermaid 깨지지 않았는가?
3. **가독성** — 개발자가 바로 참고 가능?

SCORE: [평균]
VERDICT: [PASS/REVISE]
FEEDBACK:
7점↑: PASS"""

    result = call_agent("judge", prompt, timeout=180)
    score = parse_score(result)
    return {"notion_score": score, "notion_critique": result}


def route_notion(state: DocState) -> Literal["notion_revise", "finalize"]:
    s = state.get("notion_score", 0)
    r = state.get("notion_revisions", 0)
    if s >= 7 or r >= MAX_REVISIONS:
        print(f"  ✅ 노션 {'PASS' if s >= 7 else '강제'} ({s}/10)")
        return "finalize"
    print(f"  🔄 REVISE ({s}/10)")
    return "notion_revise"


def node_notion_revise(state: DocState) -> dict:
    return {"notion_revisions": (state.get("notion_revisions", 0) + 1)}


def node_finalize(state: DocState) -> dict:
    print("\n✅ 개발 문서 생성 완료!")
    scores = state["phase_scores"]
    avg = sum(scores.values()) / max(len(scores), 1)
    total_rev = sum(state.get("phase_revisions", {}).values())
    print(f"   평균: {avg:.1f}/10 | 수정: {total_rev}회")
    for p in range(1, 8):
        s = scores.get(str(p), 0)
        r = state.get("phase_revisions", {}).get(str(p), 0)
        icon = "📊" if p in DIAGRAM_PHASES else "🔧"
        print(f"   {icon} [{p}] {PHASE_NAMES[p]}: {s}/10 (수정 {r}회)")
    url = state.get("notion_url", "")
    ns = state.get("notion_score", 0)
    if url:
        print(f"   [📝] Notion: {ns}/10 → {url}")
    return {"status": "completed"}


# ── Build Graph ─────────────────────────────────────────

def build_graph():
    g = StateGraph(DocState)

    g.add_node("read_plan", node_read_plan)
    g.add_node("work", node_work)
    g.add_node("critique", node_critique)
    g.add_node("revise", node_revise)
    g.add_node("next_phase", node_next_phase)
    g.add_node("notion_upload", node_notion_upload)
    g.add_node("notion_review", node_notion_review)
    g.add_node("notion_revise", node_notion_revise)
    g.add_node("finalize", node_finalize)

    g.set_entry_point("read_plan")
    g.add_edge("read_plan", "work")
    g.add_edge("work", "critique")

    g.add_conditional_edges("critique", route_after_critique, {
        "revise": "revise",
        "next_phase": "next_phase",
        "notion_upload": "notion_upload",
    })
    g.add_edge("revise", "work")
    g.add_edge("next_phase", "work")

    g.add_edge("notion_upload", "notion_review")
    g.add_conditional_edges("notion_review", route_notion, {
        "notion_revise": "notion_revise",
        "finalize": "finalize",
    })
    g.add_edge("notion_revise", "notion_upload")
    g.add_edge("finalize", END)

    return g.compile()


# ── State Persistence ───────────────────────────────────


# ── Main ────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("""Usage:
  python3 doc_gen.py run "노션_기획서_URL" "기술환경"
  python3 doc_gen.py status RUN_ID""")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "run":
        plan_url = sys.argv[2]
        tech = sys.argv[3] if len(sys.argv) > 3 else "Next.js, Firestore, Vercel, 1인 개발자"
        run_id = datetime.now().strftime("%Y%m%d-%H%M%S")

        print(f"""
╔══════════════════════════════════════════════════╗
║  🔧 Gajae Developer — Doc Gen Pipeline          ║
╚══════════════════════════════════════════════════╝
  Run ID: {run_id}
  기획서: {plan_url[:60]}
  기술: {tech[:60]}
  공정: 📖→[1]⚖️→[2]⚖️→[3]📊⚖️→[4]⚖️→[5]📊⚖️→[6]📊⚖️→[7]⚖️→📝⚖️→END
""")

        initial: DocState = {
            "plan_url": plan_url,
            "plan_content": "",
            "tech_context": tech,
            "human_inputs": [],
            "current_phase": 1,
            "phase_results": {},
            "phase_critiques": {},
            "phase_scores": {},
            "phase_revisions": {},
            "notion_page_id": "",
            "notion_url": "",
            "notion_score": 0.0,
            "notion_critique": "",
            "notion_revisions": 0,
            "status": "running",
        }

        graph = build_graph()
        final = graph.invoke(initial)

        print(f"\n💾 State: {run_id}")

if __name__ == "__main__":
    main()
