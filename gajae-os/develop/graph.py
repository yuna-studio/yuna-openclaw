#!/usr/bin/env python3
"""
🦞 Gajae Developer — LangGraph 기반 개발 문서 생성 에이전트

기획 문서(노션 URL)를 읽고, 개발 문서를 자동 생성한다.
각 단계: 탐정가재(work) → 판사가재(critique) → PASS/REVISE 루프
최종: 노션에 개발 문서 업로드 + 품질 검증

Usage:
  python3 graph.py run "노션_URL" "기술환경"
  python3 graph.py status RUN_ID
"""

import os
import re
import json
import subprocess
from datetime import datetime
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

# Notion upload 공유
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'planner'))
from notion_upload import (
    api as notion_api, text as notion_text, append_blocks,
    read_page_blocks, markdown_to_blocks, PARENT_PAGE, upload_to_notion,
)


# ── Config ──────────────────────────────────────────────

STATE_DIR = os.path.expanduser("~/.openclaw/workspace/gajae-os/develop/state")
MAX_REVISIONS = 2

PHASE_NAMES = {
    1: "요구사항 분석",
    2: "아키텍처 설계",
    3: "API & 데이터 설계",
    4: "컴포넌트 & UI 설계",
    5: "구현 가이드",
}


# ── State ───────────────────────────────────────────────

class DevState(TypedDict):
    plan_url: str               # 노션 기획 문서 URL
    plan_content: str           # 기획 문서 텍스트 (노션에서 읽어온)
    tech_context: str           # 기술 환경 (Next.js, Firestore 등)
    human_inputs: list

    current_phase: int          # 1~5
    phase_results: dict
    phase_critiques: dict
    phase_scores: dict
    phase_revisions: dict

    # Diagram (Phase 2 이후)
    diagrams: dict
    diagram_critique: str
    diagram_score: float
    diagram_revisions: int

    # Notion output
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
    """노션 URL에서 page_id 추출 후 내용 읽기"""
    # URL에서 page_id 추출
    # https://www.notion.so/TITLE-32hexchars 또는 bare ID
    match = re.search(r'([0-9a-f]{32})$', url.replace('-', ''))
    if not match:
        match = re.search(r'([0-9a-f\-]{36})', url)
    if not match:
        return f"(error: 노션 URL에서 page_id를 찾을 수 없음: {url})"

    page_id_raw = match.group(1).replace('-', '')
    # Format as UUID
    page_id = f"{page_id_raw[:8]}-{page_id_raw[8:12]}-{page_id_raw[12:16]}-{page_id_raw[16:20]}-{page_id_raw[20:]}"

    try:
        content = read_page_blocks(page_id, max_blocks=300)
        return content
    except Exception as e:
        return f"(error reading notion: {e})"


# ── Prompt Builders ─────────────────────────────────────

def _human_context(state: DevState) -> str:
    inputs = state.get("human_inputs", [])
    if not inputs:
        return ""
    lines = "\n".join(f"- {h['input']}" for h in inputs)
    return f"\n## 📌 대표님 지시사항\n{lines}"


def _revision_context(state: DevState) -> str:
    phase = str(state["current_phase"])
    critique = state["phase_critiques"].get(phase, "")
    rev = state["phase_revisions"].get(phase, 0)
    if critique and rev > 0:
        return f"\n## ⚠️ 판사가재 피드백 ({rev}차 반려)\n{critique}\n\n위 피드백을 반영하여 개선하라."
    return ""


def _previous_results(state: DevState) -> str:
    parts = []
    for i in range(1, state["current_phase"]):
        result = state["phase_results"].get(str(i), "")
        if result:
            parts.append(f"## [{i}] {PHASE_NAMES[i]}\n{result[:2000]}")
    return "\n\n".join(parts)


WORK_TEMPLATES = {
    1: """너는 Senior Tech Lead다.

## 기획 문서 (노션에서 읽어옴)
{plan}

## 기술 환경
{tech}
{revision}
{human}

## 지시
기획 문서를 분석하여 개발에 필요한 핵심 요구사항을 추출하라.

## 출력 형식
### 핵심 기능 목록 (P0)
- 각 기능의 기술적 요구사항
- 입/출력 데이터

### 비기능 요구사항
- 성능 (응답속도, 동시접속)
- SEO 요구사항
- 비용 제약

### 기술적 제약 & 리스크
- 기획서에서 언급된 기술 제약
- 추가 발견된 리스크

### 용어 정의
- 도메인 용어 → 코드 네이밍 매핑""",

    2: """너는 System Architect다.

## 기획 문서 요약
{plan_summary}

## 이전 단계
{prev}

## 기술 환경
{tech}
{revision}
{human}

## 출력 형식
### 기술 스택 결정
- 각 선택의 이유 (Why)

### 시스템 아키텍처
- 전체 구조 (클라이언트 ↔ 서버 ↔ DB)
- 실시간 데이터 흐름

### 프로젝트 구조 (폴더/파일)
```
src/
├── app/           # Next.js App Router
├── components/    # UI 컴포넌트
├── lib/           # 유틸리티
└── ...
```

### DB 스키마 (Firestore)
- 컬렉션 구조
- 문서 필드 정의
- 인덱스 필요 여부

### 환경 변수
- 필요한 env vars 목록""",

    3: """너는 Backend Engineer다.

## 이전 단계
{prev}

## 기술 환경
{tech}
{revision}
{human}

## 출력 형식
### API 엔드포인트
각 엔드포인트를 표로:
| Method | Path | 설명 | Request | Response |

### TypeScript 타입 정의
```typescript
// 핵심 도메인 타입
interface ChatMessage {{...}}
interface Reaction {{...}}
```

### Firestore 보안 규칙
```
rules_version = '2';
service cloud.firestore {{...}}
```

### 실시간 구독 설계
- onSnapshot 구독 대상
- 클라이언트 캐싱 전략""",

    4: """너는 Frontend Architect다.

## 이전 단계
{prev}

## 기술 환경
{tech}
{revision}
{human}

## 출력 형식
### 페이지 구조 (App Router)
```
app/
├── page.tsx          # 메인
├── live/page.tsx     # 라이브 뷰
└── archive/[id]/     # 아카이브
```

### 컴포넌트 트리
```
<LivePage>
  ├── <StreamView>
  │   ├── <MessageBubble>
  │   └── <TypingIndicator>
  ├── <ReactionBar>
  └── <StatusBadge>
```

### 상태 관리
- 어떤 상태를 어디서 관리? (useState / Context / Firestore)
- 실시간 vs 로컬 상태 구분

### 스타일 가이드
- 컬러 팔레트 (터미널 테마)
- 폰트 (모노스페이스)
- 반응형 breakpoints""",

    5: """너는 Tech Lead + Senior Developer다.

## 이전 단계
{prev}

## 기술 환경
{tech}
{revision}
{human}

## 출력 형식
### 구현 순서 (Sprint Plan)
Day 1-2, Day 3-4, ... 순으로 구체적 태스크

### 파일별 구현 가이드
각 핵심 파일의:
- 파일 경로
- 핵심 로직 (pseudo code 또는 실제 코드 스니펫)
- 의존성

### 테스트 전략
- 무엇을 테스트? (단위/통합)
- 테스트 도구

### 배포 체크리스트
- Vercel 설정
- 환경 변수
- 도메인/DNS

### 알려진 기술 부채
- MVP에서 의도적으로 스킵한 것
- 추후 개선 포인트""",
}

CRITIQUE_CRITERIA = {
    1: [("요구사항 완전성", "기획서의 P0 기능이 모두 반영됐는가?"),
        ("기술 제약 파악", "현실적 제약을 정확히 짚었는가?"),
        ("명확성", "개발자가 바로 이해할 수 있는가?")],
    2: [("아키텍처 적절성", "기술 스택이 요구사항에 맞는가?"),
        ("폴더 구조", "확장 가능하고 관례에 맞는가?"),
        ("DB 스키마", "쿼리 패턴에 최적화되었는가?")],
    3: [("API 완전성", "모든 기능의 엔드포인트가 있는가?"),
        ("타입 정확성", "TypeScript 타입이 실용적인가?"),
        ("보안", "Firestore 규칙이 적절한가?")],
    4: [("컴포넌트 분리", "적절한 단위로 나뉘었는가?"),
        ("상태 관리", "실시간/로컬 구분이 명확한가?"),
        ("UX 반영", "기획서의 UX 요구사항이 반영됐는가?")],
    5: [("구현 순서 현실성", "1인 개발자가 기간 내 가능한가?"),
        ("코드 품질", "스니펫이 실제 동작 가능한가?"),
        ("배포 완전성", "빠뜨린 설정이 없는가?")],
}


def make_work_prompt(state: DevState) -> str:
    phase = state["current_phase"]
    plan = state["plan_content"]
    # Phase 1은 전체 기획서, 이후는 요약
    plan_text = plan if phase == 1 else plan[:1500]

    return WORK_TEMPLATES[phase].format(
        plan=plan,
        plan_summary=plan_text,
        prev=_previous_results(state),
        tech=state["tech_context"],
        revision=_revision_context(state),
        human=_human_context(state),
    )


def make_critique_prompt(state: DevState) -> str:
    phase = state["current_phase"]
    content = state["phase_results"].get(str(phase), "")
    criteria_text = "\n".join(
        f"{i+1}. {name} — {desc}"
        for i, (name, desc) in enumerate(CRITIQUE_CRITERIA[phase])
    )
    return f"""너는 Staff Engineer다. 코드 리뷰처럼 개발 문서를 검토하라.
[{phase}] {PHASE_NAMES[phase]} 결과물을 검토하라.

## 기획 문서 요약
{state['plan_content'][:1000]}

## [{phase}] {PHASE_NAMES[phase]} 결과물
{content}

## 검토 원칙
- 주니어 개발자가 이 문서만 보고 구현할 수 있는가?
- 기획서와 불일치하는 부분이 있는가?
- 실제 동작하지 않는 코드/설정이 있는가?

## 평가 항목 (각 1~10점)
{criteria_text}

## 출력 형식 (반드시)
SCORE: [평균 점수]

| 항목 | 점수 | 코멘트 |
|---|---|---|
| ... | X/10 | ... |

VERDICT: [PASS/REVISE/REJECT]

FEEDBACK: (구체적 개선 지시)

## 판정 기준
- 7점 이상: PASS
- 5~6점: REVISE
- 5점 미만: REJECT"""


# ── LangGraph Nodes ─────────────────────────────────────

def node_read_plan(state: DevState) -> dict:
    """노션에서 기획 문서 읽기"""
    print(f"\n📖 기획 문서 읽는 중: {state['plan_url'][:60]}...")
    content = read_plan_from_notion(state["plan_url"])
    print(f"  ✅ {len(content)}자 읽어옴")
    return {"plan_content": content}


def node_work(state: DevState) -> dict:
    phase = state["current_phase"]
    rev = state["phase_revisions"].get(str(phase), 0)
    suffix = f" (수정 {rev}차)" if rev > 0 else ""
    print(f"\n🔧 [{phase}/5] {PHASE_NAMES[phase]}{suffix} — 탐정가재 작업 중...")

    prompt = make_work_prompt(state)
    result = call_agent("scout", prompt, timeout=300)

    new_results = dict(state["phase_results"])
    new_results[str(phase)] = result
    print(f"  ✅ 결과 저장 ({len(result)}자)")
    return {"phase_results": new_results}


def node_critique(state: DevState) -> dict:
    phase = state["current_phase"]
    print(f"⚖️  [{phase}/5] {PHASE_NAMES[phase]} — 판사가재 검증 중...")

    prompt = make_critique_prompt(state)
    result = call_agent("judge", prompt, timeout=180)
    score = parse_score(result)

    new_critiques = dict(state["phase_critiques"])
    new_critiques[str(phase)] = result
    new_scores = dict(state["phase_scores"])
    new_scores[str(phase)] = score

    return {"phase_critiques": new_critiques, "phase_scores": new_scores}


def route_after_critique(state: DevState) -> Literal["revise", "next_phase", "diagram", "notion_upload"]:
    phase = state["current_phase"]
    score = state["phase_scores"].get(str(phase), 0)
    rev = state["phase_revisions"].get(str(phase), 0)

    passed = score >= 7 or rev >= MAX_REVISIONS
    if not passed:
        print(f"  🔄 REVISE ({score}/10) — 수정 {rev + 1}/{MAX_REVISIONS}")
        return "revise"

    if score >= 7:
        print(f"  ✅ PASS ({score}/10)")
    else:
        print(f"  ⚠️ 최대 수정, 강제 통과 ({score}/10)")

    # Phase 2 PASS → 아키텍처 다이어그램
    if phase == 2:
        return "diagram"
    # Phase 5 PASS → 노션 업로드
    if phase >= 5:
        return "notion_upload"
    return "next_phase"


def node_revise(state: DevState) -> dict:
    phase = str(state["current_phase"])
    new_rev = dict(state["phase_revisions"])
    new_rev[phase] = new_rev.get(phase, 0) + 1
    return {"phase_revisions": new_rev}


def node_next_phase(state: DevState) -> dict:
    return {"current_phase": state["current_phase"] + 1}


# ── Diagram Nodes (Phase 2 이후: 아키텍처 다이어그램) ────

def node_diagram(state: DevState) -> dict:
    """아키텍처 다이어그램 생성"""
    rev = state.get("diagram_revisions", 0)
    prev_critique = state.get("diagram_critique", "")
    suffix = f" (수정 {rev}차)" if rev > 0 else ""
    print(f"\n📊 아키텍처 다이어그램 생성{suffix} — 탐정가재...")

    revision_ctx = ""
    if rev > 0 and prev_critique:
        revision_ctx = f"\n## ⚠️ 피드백\n{prev_critique}\n수정하라."

    phase2 = state["phase_results"].get("2", "")
    phase1 = state["phase_results"].get("1", "")

    prompt = f"""너는 System Architect다.

## [1] 요구사항
{phase1[:1000]}

## [2] 아키텍처 설계
{phase2}
{revision_ctx}

## 출력 1: 시스템 아키텍처 (Flowchart)
전체 시스템 구조를 flowchart로 그려라.
- Client, Server, DB, External API 간 관계
- 실시간 데이터 흐름 표시

```mermaid
flowchart LR
    ...
```

## 출력 2: 데이터 흐름 (Sequence Diagram)
핵심 시나리오의 데이터 흐름:
- 실시간 채팅 구독
- 리액션 전송
- 아카이브 변환

```mermaid
sequenceDiagram
    ...
```

## 출력 3: ERD (Class Diagram)
Firestore 컬렉션/문서 구조:

```mermaid
classDiagram
    ...
```

Mermaid 문법 정확하게. 한국어 사용."""

    result = call_agent("scout", prompt, timeout=300)

    diagrams = {}
    mermaid_blocks = re.findall(r'```mermaid\n(.*?)```', result, re.DOTALL)
    for block in mermaid_blocks:
        block = block.strip()
        if block.startswith("flowchart") or block.startswith("graph"):
            diagrams["architecture"] = block
        elif block.startswith("sequenceDiagram"):
            diagrams["dataflow"] = block
        elif block.startswith("classDiagram"):
            diagrams["erd"] = block
    if not diagrams:
        diagrams["raw"] = result

    print(f"  ✅ 다이어그램 {len(diagrams)}개 생성")
    return {"diagrams": diagrams}


def node_diagram_critique(state: DevState) -> dict:
    print("⚖️  아키텍처 다이어그램 검증 — 판사가재...")
    phase2 = state["phase_results"].get("2", "")
    diagrams = state.get("diagrams", {})
    diagram_text = "\n".join(f"### {k}\n```mermaid\n{v}\n```" for k, v in diagrams.items())

    prompt = f"""너는 Staff Engineer다. 아키텍처 다이어그램 검증.

## 아키텍처 설계
{phase2[:2000]}

## 다이어그램
{diagram_text}

## 검증 항목 (각 1~10점)
1. **시스템 구조 정확성** — 설계와 일치하는가?
2. **데이터 흐름 완전성** — 핵심 시나리오가 빠짐없는가?
3. **ERD 정확성** — DB 스키마와 일치하는가?

SCORE: [평균]
| 항목 | 점수 | 코멘트 |
|---|---|---|
VERDICT: [PASS/REVISE]
FEEDBACK:

7점 이상: PASS, 미만: REVISE"""

    result = call_agent("judge", prompt, timeout=180)
    score = parse_score(result)
    return {"diagram_critique": result, "diagram_score": score}


def route_after_diagram_critique(state: DevState) -> Literal["diagram_revise", "next_phase"]:
    score = state.get("diagram_score", 0)
    rev = state.get("diagram_revisions", 0)
    if score >= 7 or rev >= MAX_REVISIONS:
        print(f"  ✅ 다이어그램 {'PASS' if score >= 7 else '강제 통과'} ({score}/10)")
        return "next_phase"
    print(f"  🔄 REVISE ({score}/10) — 수정 {rev + 1}/{MAX_REVISIONS}")
    return "diagram_revise"


def node_diagram_revise(state: DevState) -> dict:
    return {"diagram_revisions": (state.get("diagram_revisions", 0) + 1)}


# ── Notion Nodes ────────────────────────────────────────

def _build_dev_blocks(state: DevState):
    """개발 문서용 노션 블록 생성"""
    scores = state["phase_scores"]
    avg = sum(scores.values()) / max(len(scores), 1)

    blocks = []
    # Overview
    score_lines = "\n".join(
        f"[{p}] {PHASE_NAMES[int(p)]}: {scores.get(p, 0)}/10"
        for p in ["1", "2", "3", "4", "5"]
    )
    d_score = state.get("diagram_score", 0)
    if d_score:
        score_lines += f"\n[📊] Architecture Diagrams: {d_score}/10"

    blocks.append({
        "type": "callout",
        "callout": {"icon": {"emoji": "🔧"}, "rich_text": notion_text(
            f"Dev Doc — 평균 {avg:.1f}/10\n\n{score_lines}"
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
    for p in ["1", "2", "3", "4", "5"]:
        content = state["phase_results"].get(p, "")
        critique = state["phase_critiques"].get(p, "")
        score = scores.get(p, 0)
        rev = state.get("phase_revisions", {}).get(p, 0)
        rev_text = f" (수정 {rev}회)" if rev else ""

        blocks.append({
            "type": "heading_1",
            "heading_1": {"rich_text": notion_text(f"Phase {p} — {PHASE_NAMES[int(p)]} ({score}/10){rev_text}")},
        })
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

        # Phase 2 이후: 다이어그램
        if p == "2" and state.get("diagrams"):
            blocks.append({
                "type": "heading_1",
                "heading_1": {"rich_text": notion_text(f"📊 Architecture Diagrams ({d_score}/10)")},
            })
            label_map = {"architecture": "System Architecture", "dataflow": "Data Flow", "erd": "ERD"}
            for name, code in state["diagrams"].items():
                if name == "raw":
                    blocks.extend(markdown_to_blocks(code))
                    continue
                blocks.append({"type": "heading_2", "heading_2": {"rich_text": notion_text(label_map.get(name, name))}})
                blocks.append({"type": "code", "code": {"rich_text": notion_text(code), "language": "mermaid"}})
            blocks.append({"type": "divider", "divider": {}})

    return blocks


def node_notion_upload(state: DevState) -> dict:
    print("\n📝 노션 업로드 중...")
    from notion_upload import api as napi, append_blocks as nappend, delete_all_blocks

    existing = state.get("notion_page_id", "")
    scores = state["phase_scores"]
    avg = sum(scores.values()) / max(len(scores), 1)

    if existing:
        print(f"  ♻️ 재업로드: {existing}")
        delete_all_blocks(existing)
        import time; time.sleep(0.5)
        blocks = _build_dev_blocks(state)
        nappend(existing, blocks)
        url = f"https://www.notion.so/{existing.replace('-', '')}"
        print(f"  ✅ 재업로드 ({len(blocks)}블록)")
        return {"notion_url": url}
    else:
        page = napi("POST", "pages", {
            "parent": {"page_id": PARENT_PAGE},
            "properties": {"title": {"title": notion_text(f"🔧 Dev Doc (avg {avg:.1f}/10)")}},
            "icon": {"emoji": "🔧"},
        })
        page_id = page["id"]
        blocks = _build_dev_blocks(state)
        nappend(page_id, blocks)
        url = f"https://www.notion.so/{page_id.replace('-', '')}"
        print(f"  ✅ 생성 ({len(blocks)}블록)")
        print(f"  📎 {url}")
        return {"notion_url": url, "notion_page_id": page_id}


def node_notion_review(state: DevState) -> dict:
    print("⚖️  노션 문서 품질 검증 — 판사가재...")
    page_id = state.get("notion_page_id", "")
    if not page_id:
        return {"notion_score": 7.0, "notion_critique": "스킵"}

    page_text = read_page_blocks(page_id)
    prompt = f"""너는 기술 문서 QA 편집장이다.

## 노션 페이지 내용
{page_text[:8000]}

## 검증 항목 (각 1~10점)
1. **구조 완전성** — 5개 Phase + 다이어그램 존재?
2. **포맷 품질** — 코드블록, 테이블, 리스트 깨지지 않았는가?
3. **가독성** — 개발자가 바로 참고할 수 있는 수준?

SCORE: [평균]
VERDICT: [PASS/REVISE]
FEEDBACK:
7점 이상: PASS"""

    result = call_agent("judge", prompt, timeout=180)
    score = parse_score(result)
    return {"notion_score": score, "notion_critique": result}


def route_after_notion_review(state: DevState) -> Literal["notion_revise", "finalize"]:
    score = state.get("notion_score", 0)
    rev = state.get("notion_revisions", 0)
    if score >= 7 or rev >= MAX_REVISIONS:
        print(f"  ✅ 노션 {'PASS' if score >= 7 else '강제 통과'} ({score}/10)")
        return "finalize"
    print(f"  🔄 REVISE ({score}/10)")
    return "notion_revise"


def node_notion_revise(state: DevState) -> dict:
    return {"notion_revisions": (state.get("notion_revisions", 0) + 1)}


def node_finalize(state: DevState) -> dict:
    print("\n✅ 개발 문서 파이프라인 완료!")
    avg = sum(state["phase_scores"].values()) / max(len(state["phase_scores"]), 1)
    print(f"   평균: {avg:.1f}/10")
    for i in range(1, 6):
        s = state["phase_scores"].get(str(i), 0)
        r = state["phase_revisions"].get(str(i), 0)
        print(f"   [{i}] {PHASE_NAMES[i]}: {s}/10 (수정 {r}회)")
    d = state.get("diagram_score", 0)
    if d: print(f"   [📊] Diagrams: {d}/10")
    n = state.get("notion_score", 0)
    url = state.get("notion_url", "")
    if url: print(f"   [📝] Notion: {n}/10 → {url}")
    return {"status": "completed"}


# ── Build Graph ─────────────────────────────────────────

def build_graph():
    graph = StateGraph(DevState)

    graph.add_node("read_plan", node_read_plan)
    graph.add_node("work", node_work)
    graph.add_node("critique", node_critique)
    graph.add_node("revise", node_revise)
    graph.add_node("next_phase", node_next_phase)
    graph.add_node("diagram", node_diagram)
    graph.add_node("diagram_critique", node_diagram_critique)
    graph.add_node("diagram_revise", node_diagram_revise)
    graph.add_node("notion_upload", node_notion_upload)
    graph.add_node("notion_review", node_notion_review)
    graph.add_node("notion_revise", node_notion_revise)
    graph.add_node("finalize", node_finalize)

    # Entry: read plan → work
    graph.set_entry_point("read_plan")
    graph.add_edge("read_plan", "work")

    graph.add_edge("work", "critique")
    graph.add_conditional_edges("critique", route_after_critique, {
        "revise": "revise",
        "next_phase": "next_phase",
        "diagram": "diagram",
        "notion_upload": "notion_upload",
    })

    graph.add_edge("revise", "work")
    graph.add_edge("next_phase", "work")

    # Diagram sub-flow
    graph.add_edge("diagram", "diagram_critique")
    graph.add_conditional_edges("diagram_critique", route_after_diagram_critique, {
        "diagram_revise": "diagram_revise",
        "next_phase": "next_phase",
    })
    graph.add_edge("diagram_revise", "diagram")

    # Notion sub-flow
    graph.add_edge("notion_upload", "notion_review")
    graph.add_conditional_edges("notion_review", route_after_notion_review, {
        "notion_revise": "notion_revise",
        "finalize": "finalize",
    })
    graph.add_edge("notion_revise", "notion_upload")

    graph.add_edge("finalize", END)

    return graph.compile()


# ── State Persistence ───────────────────────────────────

def save_run(run_id: str, state: dict):
    os.makedirs(STATE_DIR, exist_ok=True)
    path = os.path.join(STATE_DIR, f"{run_id}.json")
    with open(path, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# ── Main ────────────────────────────────────────────────

def main():
    import sys as _sys

    if len(_sys.argv) < 2:
        print("""Usage:
  python3 graph.py run "노션_기획문서_URL" "기술환경"
  python3 graph.py status RUN_ID
""")
        _sys.exit(1)

    cmd = _sys.argv[1]

    if cmd == "run":
        plan_url = _sys.argv[2]
        tech = _sys.argv[3] if len(_sys.argv) > 3 else "Next.js, Firestore, Vercel, 1인 개발자"
        run_id = datetime.now().strftime("%Y%m%d-%H%M%S")

        print(f"""
╔══════════════════════════════════════════════════╗
║  🔧 Gajae Developer — LangGraph Pipeline        ║
╚══════════════════════════════════════════════════╝
  Run ID: {run_id}
  기획서: {plan_url[:60]}
  기술: {tech[:60]}
  공정: 📖→[1]→⚖️→[2]→⚖️→📊→⚖️→[3]→⚖️→[4]→⚖️→[5]→⚖️→📝→⚖️→END
""")

        initial: DevState = {
            "plan_url": plan_url,
            "plan_content": "",
            "tech_context": tech,
            "human_inputs": [],
            "current_phase": 1,
            "phase_results": {},
            "phase_critiques": {},
            "phase_scores": {},
            "phase_revisions": {},
            "diagrams": {},
            "diagram_critique": "",
            "diagram_score": 0.0,
            "diagram_revisions": 0,
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
        print(f"\n💾 State saved: {run_id}")

    elif cmd == "status":
        run_id = _sys.argv[2]
        path = os.path.join(STATE_DIR, f"{run_id}.json")
        state = json.load(open(path))
        print(f"📋 기획서: {state['plan_url'][:50]}")
        print(f"   상태: {state['status']}")
        for i in range(1, 6):
            s = state["phase_scores"].get(str(i), "-")
            r = state["phase_revisions"].get(str(i), 0)
            has = "✅" if state["phase_results"].get(str(i)) else "⏳"
            print(f"   [{i}] {PHASE_NAMES[i]}: {has} score={s} rev={r}")


if __name__ == "__main__":
    main()
