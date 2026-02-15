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
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'planner'))
from notion_upload import (
    api as notion_api, text as notion_text, append_blocks,
    read_page_blocks, markdown_to_blocks, PARENT_PAGE,
)


# ── Config ──────────────────────────────────────────────

STATE_DIR = os.path.expanduser("~/.openclaw/workspace/gajae-os/develop/state")
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
    cmd = [
        "openclaw", "agent",
        "--agent", agent_id,
        "--message", message,
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
    """Phase 7용: 웹 검색으로 디자인 레퍼런스 수집"""
    import urllib.request, urllib.parse

    queries = [
        "2025 dark theme design system premium developer tool UI",
        "terminal aesthetic web design glassmorphism dark mode",
        "best dark UI design inspiration dribbble behance 2025",
        "coding live stream web app UI design reference",
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

## 출력: 화면 & 네비게이션 설계서

### 1. 페이지 목록
각 페이지/뷰의:
| 페이지 | URL 경로 | 설명 | 주요 컴포넌트 |

### 2. 페이지별 상세 (기능 명세)
각 페이지에 대해:
- **레이아웃**: 어떤 요소가 어디에 배치되는지
- **UI 요소 목록**: 모든 버튼, 입력 필드, 표시 영역을 빠짐없이 나열
- **인터랙션**: 각 버튼/액션의 동작 설명
- **상태**: 페이지가 표시하는 데이터, 로딩/에러 상태

### 3. 화면 ↔ ViewModel 매핑 테이블 ⭐
**각 페이지별로** UI 요소와 ViewModel 메서드를 1:1 매핑하라.
빠지는 것이 있으면 안 된다.

| 페이지 | UI 요소 (버튼/영역) | 사용자 액션 | ViewModel 메서드 | 설명 |
|---|---|---|---|---|
| LivePage | 메시지 영역 | 페이지 진입 | `LiveViewModel.subscribeMessages()` | 실시간 구독 시작 |
| LivePage | ❤️ 좋아요 버튼 | 클릭 | `LiveViewModel.sendReaction("heart")` | 리액션 전송 |
| LivePage | 🤣 ㅋㅋ 버튼 | 클릭 | `LiveViewModel.sendReaction("lol")` | 리액션 전송 |
| LivePage | 📤 공유 버튼 | 클릭 | `LiveViewModel.shareSnapshot()` | 스냅샷 생성+공유 |
| ArchivePage | 세션 목록 | 페이지 진입 | `ArchiveViewModel.loadSessions()` | 과거 세션 조회 |
| ... | ... | ... | ... | ... |

모든 페이지의 모든 버튼/영역을 빠짐없이 매핑할 것.

### 4. 화면 전환 규칙
- 어떤 액션이 어떤 페이지로 이동시키는지
- 뒤로가기/브라우저 히스토리 동작
- 딥링크 지원 여부

### 5. 반응형 동작
- 모바일/태블릿/데스크톱 차이점
- 숨김/표시 요소""",

    # Phase 5: 다이어그램 (DIAGRAM_PHASES)
    5: """너는 UX Engineer다.

## 이전 단계 (화면 설계)
{prev}
{rev}

## 출력: 화면 네비게이션 플로우차트

사용자가 각 페이지에서 할 수 있는 모든 액션과 그에 따른 화면 전환을 flowchart로 그려라.

- 각 페이지를 노드로
- 버튼/액션을 엣지 레이블로
- 조건 분기(로그인 여부, 에러 등)는 diamond로

```mermaid
flowchart TD
    A[메인 페이지] -->|라이브 클릭| B[라이브 뷰]
    B -->|❤️ 클릭| B
    B -->|ㅋㅋ 클릭| B
    B -->|공유 클릭| C{{공유 모달}}
    C -->|트위터| D[외부 이동]
    C -->|취소| B
    B -->|세션 종료| E[아카이브 뷰]
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

## 출력: 요구사항별 시퀀스 다이어그램

P0 기능 각각에 대해 시퀀스 다이어그램을 그려라.
액터: 사용자, View(Page), ViewModel, UseCase/Repository, Firestore, (외부 서비스)

**Phase 4의 화면↔ViewModel 매핑 테이블과 일치해야 한다.**
매핑 테이블에 있는 모든 ViewModel 메서드가 시퀀스 다이어그램에 등장해야 한다.

### 시퀀스 1: 실시간 대화 스트림 구독
```mermaid
sequenceDiagram
    actor User
    participant LP as LivePage
    participant LVM as LiveViewModel
    participant Repo as ChatRepository
    participant FS as Firestore
    User->>LP: 페이지 접속
    LP->>LVM: subscribeMessages()
    LVM->>Repo: observeMessages()
    Repo->>FS: onSnapshot(chat_logs)
    FS-->>Repo: 실시간 데이터
    Repo-->>LVM: Stream<List<ChatMessage>>
    LVM-->>LP: UI 업데이트
    LP->>LP: 타이핑 애니메이션
    LP-->>User: 텍스트 표시
```

### 시퀀스 2: 리액션 전송
```mermaid
sequenceDiagram
    ...
```

### 시퀀스 3: 아카이브 변환
```mermaid
sequenceDiagram
    ...
```

(기획서의 P0 기능 수만큼 시퀀스 다이어그램 작성)
Mermaid 문법 정확. 한국어.""",

    7: """너는 Frontend Architect이자 UI/UX Designer다. 디자인 시스템 전문가.
최신 트렌드를 반영한 **프리미엄급** 디자인 시스템을 설계하라.

## 기획 문서 요약
{plan_short}

## 이전 단계
{prev}

## 기술 환경
{tech}
{rev}
{human}

## 디자인 레퍼런스 (웹 리서치 결과)
{design_refs}

## 출력: 디자인 시스템 설계서

### 1. 디자인 컨셉 & 무드
- **비주얼 컨셉**: (예: "터미널 감성 + 글래스모피즘", "네온 사이버펑크" 등)
- **레퍼런스 사이트**: 참고한 디자인 사이트 3~5개 (URL 포함)
- **핵심 키워드**: 프리미엄, 개발자 감성, 미니멀 등

### 2. 컬러 시스템
다크 테마 기반. **고급스러운** 컬러 팔레트:

| 토큰 | 값 (HEX) | 용도 | 참고 |
|---|---|---|---|
| --color-bg-primary | #0a0e17 | 메인 배경 | GitHub Dark 보다 깊은 톤 |
| --color-bg-secondary | #111827 | 카드/패널 배경 | |
| --color-bg-elevated | #1a2332 | 떠있는 요소 | |
| --color-accent-primary | #6366f1 | 주요 액션 | Indigo 계열 |
| --color-accent-glow | #818cf8 | 호버/글로우 | |
| --color-text-primary | #e2e8f0 | 본문 텍스트 | |
| --color-text-secondary | #94a3b8 | 보조 텍스트 | |
| --color-text-muted | #64748b | 비활성 | |
| --color-success | #34d399 | 성공/온라인 | |
| --color-error | #f87171 | 에러 | |
| --color-border | #1e293b | 테두리 | |

시맨틱 컬러 + 상태 컬러 포함. 최소 15개 이상.

### 3. 타이포그래피
| 용도 | 폰트 | 사이즈 | Weight | Line Height |
|---|---|---|---|---|
| 코드/로그 | JetBrains Mono, Fira Code | 14px | 400 | 1.6 |
| 제목 | Inter, Pretendard | 24-32px | 700 | 1.2 |
| 본문 | Inter, Pretendard | 16px | 400 | 1.5 |
| 캡션 | Inter | 12px | 500 | 1.4 |

한글 폰트(Pretendard) + 영문 폰트(Inter) 조합. 코드는 모노스페이스 필수.

### 4. 스페이싱 & 레이아웃
- 8px 그리드 시스템
- 스페이싱 스케일: 4, 8, 12, 16, 24, 32, 48, 64
- 컨테이너 max-width
- 반응형 breakpoints (sm, md, lg, xl)

### 5. 이펙트 & 모션
- **그림자**: 레이어별 shadow 정의 (sm, md, lg, glow)
- **글래스모피즘**: backdrop-blur + 반투명 배경 (사용 조건)
- **글로우 이펙트**: accent 컬러 기반 box-shadow glow (버튼 호버 등)
- **애니메이션**: 전환 duration, easing, 타이핑 효과 속도
- **마이크로 인터랙션**: 버튼 클릭, 리액션 폭발, 스크롤 등

### 6. 공통 컴포넌트 명세
| 컴포넌트 | 역할 | Variants | Props |
|---|---|---|---|
| Button | 액션 | primary, ghost, icon | size, loading, glow |
| Card | 컨테이너 | default, glass, elevated | padding, border |
| Badge | 상태 표시 | online, offline, live | pulse, color |
| MessageBubble | 채팅 메시지 | user, ai, system | typing, avatar |
| ReactionButton | 리액션 | heart, lol | count, burst |
| ... | ... | ... | ... |

각 컴포넌트의 상태(default, hover, active, disabled, loading) 정의.

### 7. 아이콘 & 에셋
- 아이콘 라이브러리 선택 (Lucide, Phosphor 등)
- 커스텀 아이콘 필요 여부
- 파비콘, OG 이미지 가이드

### 8. 접근성 (a11y)
- 컬러 대비 비율 (WCAG AA 이상)
- 키보드 네비게이션 패턴
- 스크린리더 지원
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
    7: [("컬러 시스템 완성도", "시맨틱 컬러 15개 이상? 다크테마 고급스러운가?"),
        ("타이포그래피", "한글+영문+코드 폰트 조합이 적절한가?"),
        ("컴포넌트 명세", "Phase 4 UI 요소와 매핑되는 컴포넌트가 모두 있는가?"),
        ("이펙트 & 모션", "글로우/글래스모피즘/애니메이션 정의가 구체적인가?"),
        ("프리미엄 퀄리티", "실제로 고급스러운 디자인인가? 촌스럽지 않은가?")],
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

def save_run(run_id: str, state: dict):
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(os.path.join(STATE_DIR, f"{run_id}.json"), "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


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
        save_run(run_id, dict(final))
        print(f"\n💾 State: {run_id}")

    elif cmd == "status":
        run_id = sys.argv[2]
        state = json.load(open(os.path.join(STATE_DIR, f"{run_id}.json")))
        print(f"📋 {state['plan_url'][:50]}")
        print(f"   상태: {state['status']}")
        for p in range(1, 8):
            s = state["phase_scores"].get(str(p), "-")
            has = "✅" if state["phase_results"].get(str(p)) else "⏳"
            print(f"   [{p}] {PHASE_NAMES[p]}: {has} {s}")


if __name__ == "__main__":
    main()
