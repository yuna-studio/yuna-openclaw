#!/usr/bin/env python3
"""
🦞 Gajae Planner — LangGraph 기반 PO 기획 에이전트

공정 (매 단계 판사가재 검증):
  [1] Background & Opportunity (탐정가재) → 판사 검증 → PASS면 다음
  [2] Hypothesis Setting (탐정가재)       → 판사 검증 → PASS면 다음
  [3] Solution & MVP Spec (탐정가재)      → 판사 검증 → PASS면 다음
  [4] Success Metrics (탐정가재)          → 판사 검증 → PASS면 다음
  [5] GTM & Operations (탐정가재)         → 판사 검증 → PASS면 다음
  [6] Notion 출력
  
  각 단계 REVISE 시 해당 단계로 루프 (최대 2회/단계)

Usage:
  python3 gajae-os/planner/graph.py "바이브코딩 라이브스트림 웹사이트" \\
    --context "Next.js, Firestore 연동, 1인 개발자, 2주"
"""

import os
import json
import time
import argparse
import urllib.request
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END


# ── State ───────────────────────────────────────────────

class PlannerState(TypedDict):
    idea: str
    context: str

    # 각 단계 결과물
    background: str        # [1]
    hypothesis: str        # [2]
    solution_spec: str     # [3]
    metrics_plan: str      # [4]
    gtm_plan: str          # [5]

    # 검증 관련
    current_phase: int             # 현재 단계 (1~5)
    phase_revision_counts: dict    # {1: 0, 2: 1, ...} 단계별 수정 횟수
    phase_critiques: dict          # {1: "...", 2: "..."} 단계별 피드백
    phase_scores: dict             # {1: 8.0, 2: 6.5, ...}

    # 최종
    final_plan: str
    notion_url: str


# ── OpenClaw 호출 ──────────────────────────────────────

GATEWAY_URL = "http://127.0.0.1:18789"
MAX_REVISIONS_PER_PHASE = 2

PHASE_NAMES = {
    1: "Background & Opportunity",
    2: "Hypothesis Setting",
    3: "Solution & MVP Spec",
    4: "Success Metrics",
    5: "GTM & Operations",
}


def _get_gateway_token() -> str:
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    with open(config_path) as f:
        config = json.load(f)
    return config.get("gateway", {}).get("auth", {}).get("token", "")


def call_agent(agent_id: str, task: str, label: str = "", timeout: int = 300) -> str:
    """OpenClaw 서브에이전트를 spawn하고 결과를 기다린다."""
    token = _get_gateway_token()

    payload = {
        "task": task,
        "agentId": agent_id,
        "model": "google-antigravity/gemini-3-pro-high",
        "runTimeoutSeconds": timeout,
    }
    if label:
        payload["label"] = label

    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{GATEWAY_URL}/api/sessions/spawn",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=timeout + 30) as resp:
        result = json.loads(resp.read().decode())

    if result.get("status") != "accepted":
        raise RuntimeError(f"Spawn failed: {result}")

    run_id = result["runId"]

    # Poll for completion
    start = time.time()
    while time.time() - start < timeout:
        time.sleep(5)
        try:
            poll_req = urllib.request.Request(
                f"{GATEWAY_URL}/api/sessions/runs/{run_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            with urllib.request.urlopen(poll_req, timeout=10) as resp:
                run_data = json.loads(resp.read().decode())
            if run_data.get("status") in ("completed", "failed", "error"):
                return run_data.get("findings", run_data.get("output", ""))
        except Exception:
            pass

    return "(timeout)"


# ── Phase Prompts ──────────────────────────────────────

def _revision_context(state: PlannerState) -> str:
    """현재 단계에 대한 이전 판사 피드백이 있으면 반환"""
    phase = state["current_phase"]
    critique = state["phase_critiques"].get(phase, "")
    rev_count = state["phase_revision_counts"].get(phase, 0)
    if critique and rev_count > 0:
        return f"""
## ⚠️ 판사가재 피드백 ({rev_count}차 반려)
{critique}

위 피드백을 반영하여 이 단계를 개선하라. 이전과 같은 실수를 반복하지 마라."""
    return ""


def _make_phase1_prompt(state: PlannerState) -> str:
    return f"""너는 Market Research Analyst다.

/Users/openclaw-kong/.openclaw/workspace/gajae-os/planner/RESEARCHER.md 파일을 읽고 형식을 참고하라.

## 조사 대상
{state['idea']}

## 환경
{state['context']}
{_revision_context(state)}

## 지시
- web_search를 최소 5회 이상 사용하라
- 경쟁사 최소 3개 분석하라
- 데이터 없으면 "데이터 없음"으로 표시. 추측 금지.
- 결과를 텍스트로 반환하라 (파일 저장 불필요)

## 출력 형식
### Context (맥락)
### Problem Statement
### Competitor Benchmark (최소 3개)
### 우리만의 Edge"""


def _make_phase2_prompt(state: PlannerState) -> str:
    return f"""너는 전략가(Strategist)다.

## 시장 조사 결과
{state['background']}

## 아이디어
{state['idea']}
{_revision_context(state)}

## 출력 형식
- **Belief**: "우리는 [기능/변경]을 하면, [타겟 유저]가 [행동]을 할 것이다"
- **Expected Outcome**: "[핵심 KPI]가 [X%] 개선될 것이다"
- **근거**: 시장 조사의 어떤 데이터가 이 가설을 뒷받침하는지 명시

모호한 표현 금지. 구체적 수치와 근거를 대라."""


def _make_phase3_prompt(state: PlannerState) -> str:
    return f"""너는 Product Designer다.

## 제약 조건 (반드시 준수)
- 1인 개발자
- {state['context']}
- P0 판정 기준: "이것 없이 가설 검증 불가능한가?" → 아니면 P1으로

## 입력
- 아이디어: {state['idea']}
- 가설: {state['hypothesis']}
- 시장 조사: {state['background'][:1500]}
{_revision_context(state)}

## 출력 형식
- **User Flow**: 3~5단계로 기술
- **Must-Have (P0)**: 최대 3개. 무자비하게 쳐내라.
- **Nice-to-Have (P1)**: P0에서 쳐낸 것들
- **Technical Constraint**: 기존 시스템과 충돌 가능성"""


def _make_phase4_prompt(state: PlannerState) -> str:
    return f"""너는 Data Scientist다.

## 입력
- 아이디어: {state['idea']}
- MVP 스펙: {state['solution_spec']}
{_revision_context(state)}

## 출력 형식
- **Primary Metric**: 이 기능의 성패를 가를 단 하나의 숫자
- **Counter Metric**: 이 기능 때문에 나빠질 수 있는 지표
- **Go/Stop Criterion**:
  - Go: Primary Metric이 [X] 이상이면 정식 배포
  - Stop: Counter Metric이 [Y] 이상 악화되면 롤백
  - 관찰 기간: 최소 [N]일

1인 개발자 환경에서 운영 리소스 증가를 Counter Metric에 반드시 포함하라.
모호한 표현 금지. 측정 가능한 구체적 수치를 제시하라."""


def _make_phase5_prompt(state: PlannerState) -> str:
    return f"""너는 Growth Hacker다.

## 입력
- 아이디어: {state['idea']}
- MVP 스펙: {state['solution_spec']}
- 메트릭: {state['metrics_plan']}
{_revision_context(state)}

## 출력 형식
- **Aha-Moment**: 유저가 "이거 좋다!"를 느끼는 결정적 순간. 어떻게 유도?
- **Manual Process**: 자동화 전 수동으로 해야 할 것 (1인 운영 관점)
- **Launch Plan**: 어디에 어떻게 알릴 것인가
- **Viral Loop**: 제품 내 공유/추천 장치"""


PHASE_PROMPT_BUILDERS = {
    1: _make_phase1_prompt,
    2: _make_phase2_prompt,
    3: _make_phase3_prompt,
    4: _make_phase4_prompt,
    5: _make_phase5_prompt,
}

PHASE_STATE_KEYS = {
    1: "background",
    2: "hypothesis",
    3: "solution_spec",
    4: "metrics_plan",
    5: "gtm_plan",
}


# ── Critique Prompt ─────────────────────────────────────

def _make_critique_prompt(state: PlannerState) -> str:
    phase = state["current_phase"]
    phase_name = PHASE_NAMES[phase]
    content = state[PHASE_STATE_KEYS[phase]]

    # 단계별 평가 기준
    criteria = {
        1: [
            ("시장 데이터 충분성", "실제 데이터/소스가 있는가? 추측이 아닌가?"),
            ("경쟁사 분석 깊이", "3개 이상 비교하고 약점을 파악했는가?"),
            ("Edge 명확성", "우리만의 차별점이 구체적인가?"),
        ],
        2: [
            ("가설 구체성", "Belief가 검증 가능한 형태인가?"),
            ("KPI 측정 가능성", "Expected Outcome의 수치가 현실적인가?"),
            ("근거 연결", "시장 조사 데이터와 논리적으로 연결되는가?"),
        ],
        3: [
            ("P0 최소성", "하나라도 더 뺄 수 있지 않은가?"),
            ("실현 가능성", "1인 개발자가 기간 내 구현 가능한가?"),
            ("User Flow 명확성", "유저 경로가 단순하고 명확한가?"),
        ],
        4: [
            ("Primary Metric 적절성", "가설 검증에 맞는 지표인가?"),
            ("Go/Stop 수치 현실성", "달성 가능하면서 의미 있는 기준인가?"),
            ("Counter Metric 인식", "부작용을 정직하게 다뤘는가?"),
        ],
        5: [
            ("Aha-Moment 설득력", "유저가 정말 그 순간 가치를 느낄까?"),
            ("Launch Plan 현실성", "1인이 실행 가능한 채널인가?"),
            ("Viral Loop 자연스러움", "억지가 아닌 자연스러운 공유 장치인가?"),
        ],
    }

    criteria_text = "\n".join(
        f"{i+1}. {name} — {desc}"
        for i, (name, desc) in enumerate(criteria[phase])
    )

    return f"""너는 냉정한 PO Critic이다.
아래 [{phase}] {phase_name} 결과물을 검토하라.

## 아이디어
{state['idea']}

## [{phase}] {phase_name} 결과물
{content}

## 평가 항목 (각 1~10점)
{criteria_text}

## 출력 형식 (반드시 이 형식으로)
SCORE: [평균 점수, 소수점 1자리]

| 항목 | 점수 | 코멘트 |
|---|---|---|
| ... | X/10 | ... |

VERDICT: [PASS/REVISE/REJECT]

FEEDBACK: (REVISE인 경우 구체적 개선 지시. 무엇을 어떻게 고쳐야 하는지.)

## 판정 기준
- 평균 7점 이상: PASS
- 평균 5~6점: REVISE
- 평균 5점 미만: REJECT

자기 편의적 채점 금지. 냉정하게 평가하라."""


# ── Nodes ───────────────────────────────────────────────

def node_work(state: PlannerState) -> dict:
    """탐정가재가 현재 단계 작업 수행"""
    phase = state["current_phase"]
    phase_name = PHASE_NAMES[phase]
    rev = state["phase_revision_counts"].get(phase, 0)
    suffix = f" (수정 {rev}차)" if rev > 0 else ""
    print(f"🔍 [{phase}/5] {phase_name}{suffix} — 탐정가재 작업 중...")

    prompt = PHASE_PROMPT_BUILDERS[phase](state)
    result = call_agent("scout", prompt, label=f"plan-phase{phase}")

    return {PHASE_STATE_KEYS[phase]: result}


def node_critique(state: PlannerState) -> dict:
    """판사가재가 현재 단계 검증"""
    phase = state["current_phase"]
    phase_name = PHASE_NAMES[phase]
    print(f"⚖️  [{phase}/5] {phase_name} — 판사가재 검증 중...")

    prompt = _make_critique_prompt(state)
    result = call_agent("judge", prompt, label=f"plan-critique-phase{phase}")

    # 점수 파싱
    score = 0.0
    for line in result.split("\n"):
        if line.strip().startswith("SCORE:"):
            try:
                score_str = line.split(":")[1].strip()
                # "7.5/10" 또는 "7.5" 둘 다 처리
                score = float(score_str.split("/")[0].strip())
            except (ValueError, IndexError):
                score = 5.0
            break

    # 상태 업데이트
    new_critiques = dict(state["phase_critiques"])
    new_critiques[phase] = result

    new_scores = dict(state["phase_scores"])
    new_scores[phase] = score

    new_revisions = dict(state["phase_revision_counts"])
    # revision count는 route에서 올림

    return {
        "phase_critiques": new_critiques,
        "phase_scores": new_scores,
    }


def route_after_critique(state: PlannerState) -> Literal["revise", "next_phase", "finalize"]:
    """판사 검증 후 분기: 수정 / 다음 단계 / 완료"""
    phase = state["current_phase"]
    score = state["phase_scores"].get(phase, 0)
    rev_count = state["phase_revision_counts"].get(phase, 0)

    if score >= 7:
        print(f"  ✅ PASS ({score}/10)")
        if phase >= 5:
            return "finalize"
        return "next_phase"
    elif rev_count >= MAX_REVISIONS_PER_PHASE:
        print(f"  ⚠️ 최대 수정 횟수 도달 ({rev_count}/{MAX_REVISIONS_PER_PHASE}), 다음으로 진행")
        if phase >= 5:
            return "finalize"
        return "next_phase"
    else:
        print(f"  🔄 REVISE ({score}/10) — 수정 {rev_count + 1}/{MAX_REVISIONS_PER_PHASE}")
        return "revise"


def node_revise(state: PlannerState) -> dict:
    """수정 카운트 올리고 다시 work로"""
    phase = state["current_phase"]
    new_revisions = dict(state["phase_revision_counts"])
    new_revisions[phase] = new_revisions.get(phase, 0) + 1
    return {"phase_revision_counts": new_revisions}


def node_next_phase(state: PlannerState) -> dict:
    """다음 단계로 이동"""
    return {"current_phase": state["current_phase"] + 1}


def node_finalize(state: PlannerState) -> dict:
    """최종 1-Pager 조합"""
    print("📋 최종 1-Pager 조합 중...")

    avg_score = sum(state["phase_scores"].values()) / max(len(state["phase_scores"]), 1)
    total_revisions = sum(state["phase_revision_counts"].values())

    plan = f"""# 📋 PO's 1-Pager: {state['idea']}
> 전체 평균 점수: {avg_score:.1f}/10
> 총 수정 횟수: {total_revisions}
> 단계별 점수: {json.dumps(state['phase_scores'], ensure_ascii=False)}

---

## 1. Background & Opportunity
{state['background']}

---

## 2. Hypothesis
{state['hypothesis']}

---

## 3. Solution & MVP Spec
{state['solution_spec']}

---

## 4. Success Metrics
{state['metrics_plan']}

---

## 5. Go-to-Market & Operations
{state['gtm_plan']}

---

## 단계별 검증 결과
"""
    for p in range(1, 6):
        score = state["phase_scores"].get(p, 0)
        critique = state["phase_critiques"].get(p, "")
        revisions = state["phase_revision_counts"].get(p, 0)
        plan += f"""
### [{p}] {PHASE_NAMES[p]} — {score}/10 (수정 {revisions}회)
{critique}
"""

    return {"final_plan": plan}


def node_notion(state: PlannerState) -> dict:
    """노션에 페이지 생성"""
    print("📝 Notion 페이지 생성 중...")

    notion_key_path = os.path.expanduser("~/.config/notion/api_key")
    if not os.path.exists(notion_key_path):
        print("  ⚠️ Notion API 키 없음, 스킵")
        return {"notion_url": "(no notion key)"}

    with open(notion_key_path) as f:
        notion_key = f.read().strip()

    avg_score = sum(state["phase_scores"].values()) / max(len(state["phase_scores"]), 1)

    # Notion 블록 구성
    children = []

    # 요약 callout
    children.append({
        "type": "callout",
        "callout": {
            "icon": {"type": "emoji", "emoji": "🦞"},
            "rich_text": [{"text": {"content":
                f"전체 평균: {avg_score:.1f}/10 | "
                f"단계별: {json.dumps({PHASE_NAMES[k]: v for k, v in state['phase_scores'].items()}, ensure_ascii=False)}"
            }}]
        }
    })

    # 각 단계 내용
    sections = [
        ("1. Background & Opportunity", state["background"]),
        ("2. Hypothesis", state["hypothesis"]),
        ("3. Solution & MVP Spec", state["solution_spec"]),
        ("4. Success Metrics", state["metrics_plan"]),
        ("5. GTM & Operations", state["gtm_plan"]),
    ]

    for heading, body in sections:
        children.append({
            "type": "heading_2",
            "heading_2": {"rich_text": [{"text": {"content": heading}}]}
        })
        if body:
            for chunk in [body[i:i+1900] for i in range(0, len(body), 1900)]:
                children.append({
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"text": {"content": chunk}}]}
                })

    # 검증 결과
    children.append({
        "type": "heading_2",
        "heading_2": {"rich_text": [{"text": {"content": "📊 단계별 검증 결과"}}]}
    })

    for p in range(1, 6):
        score = state["phase_scores"].get(p, 0)
        rev = state["phase_revision_counts"].get(p, 0)
        critique = state["phase_critiques"].get(p, "")[:500]
        children.append({
            "type": "toggle",
            "toggle": {
                "rich_text": [{"text": {"content": f"[{p}] {PHASE_NAMES[p]} — {score}/10 (수정 {rev}회)"}}],
                "children": [{
                    "type": "paragraph",
                    "paragraph": {"rich_text": [{"text": {"content": critique or "(no critique)"}}]}
                }]
            }
        })

    children = children[:95]

    parent_page_id = "ea6034d6-facc-494d-aee7-a1fa9cbec48f"

    payload = json.dumps({
        "parent": {"page_id": parent_page_id},
        "icon": {"type": "emoji", "emoji": "📋"},
        "properties": {
            "title": {"title": [{"text": {"content": f"📋 [Plan] {state['idea'][:50]}"}}]}
        },
        "children": children,
    }).encode()

    req = urllib.request.Request(
        "https://api.notion.com/v1/pages",
        data=payload,
        headers={
            "Authorization": f"Bearer {notion_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
        url = result.get("url", "")
        print(f"  ✅ Notion: {url}")
        return {"notion_url": url}
    except Exception as e:
        error_body = ""
        if hasattr(e, "read"):
            error_body = e.read().decode()[:300]
        print(f"  ❌ Notion error: {e} {error_body}")
        return {"notion_url": f"(error: {e})"}


# ── Graph ───────────────────────────────────────────────

def build_graph() -> StateGraph:
    graph = StateGraph(PlannerState)

    # 노드 등록
    graph.add_node("work", node_work)
    graph.add_node("critique", node_critique)
    graph.add_node("revise", node_revise)
    graph.add_node("next_phase", node_next_phase)
    graph.add_node("finalize", node_finalize)
    graph.add_node("notion", node_notion)

    # 흐름
    graph.set_entry_point("work")
    graph.add_edge("work", "critique")

    # 판사 검증 후 분기
    graph.add_conditional_edges(
        "critique",
        route_after_critique,
        {
            "revise": "revise",
            "next_phase": "next_phase",
            "finalize": "finalize",
        }
    )

    # revise → 다시 work
    graph.add_edge("revise", "work")

    # next_phase → 다시 work
    graph.add_edge("next_phase", "work")

    # finalize → notion → END
    graph.add_edge("finalize", "notion")
    graph.add_edge("notion", END)

    return graph.compile()


# ── Main ────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="🦞 Gajae Planner — PO 기획 에이전트")
    parser.add_argument("idea", help="기획할 아이디어/기능")
    parser.add_argument("--context", default="1인 개발자, 2주", help="환경 정보")
    args = parser.parse_args()

    print(f"""
╔══════════════════════════════════════════════════╗
║  🦞 Gajae Planner v2 — LangGraph Pipeline       ║
║  매 단계 판사가재 검증 (최대 2회 수정/단계)        ║
╚══════════════════════════════════════════════════╝
  아이디어: {args.idea}
  환경: {args.context}

  공정: [1]→⚖️→[2]→⚖️→[3]→⚖️→[4]→⚖️→[5]→⚖️→📝Notion
         ↺      ↺      ↺      ↺      ↺
""")

    graph = build_graph()

    initial_state: PlannerState = {
        "idea": args.idea,
        "context": args.context,
        "background": "",
        "hypothesis": "",
        "solution_spec": "",
        "metrics_plan": "",
        "gtm_plan": "",
        "current_phase": 1,
        "phase_revision_counts": {},
        "phase_critiques": {},
        "phase_scores": {},
        "final_plan": "",
        "notion_url": "",
    }

    final = graph.invoke(initial_state)

    avg_score = sum(final["phase_scores"].values()) / max(len(final["phase_scores"]), 1)
    total_revisions = sum(final["phase_revision_counts"].values())

    print(f"""
╔══════════════════════════════════════════════════╗
║  ✅ 기획 완료                                     ║
╚══════════════════════════════════════════════════╝
  평균 점수: {avg_score:.1f}/10
  단계별 점수: {json.dumps({PHASE_NAMES[k]: v for k, v in final['phase_scores'].items()}, ensure_ascii=False)}
  총 수정: {total_revisions}회
  Notion: {final['notion_url']}
""")

    return final


if __name__ == "__main__":
    main()
