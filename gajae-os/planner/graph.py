#!/usr/bin/env python3
"""
🦞 Gajae Planner — LangGraph 기반 PO 기획 에이전트

공정:
  [1] Background & Opportunity (탐정가재 — 웹 검색 + 분석)
  [2] Hypothesis Setting (탐정가재 — 가설 수립)
  [3] Solution & MVP Spec (탐정가재 — 스펙 설계)
  [4] Success Metrics (탐정가재 — 메트릭 설계)
  [5] GTM & Operations (탐정가재 — 확산 전략)
  [6] PO Critique (판사가재 — 검증 + 점수)
  → 점수 미달 시 [2]로 루프 (최대 2회)
  [7] Notion 출력

Usage:
  python3 gajae-os/planner/graph.py "바이브코딩 라이브스트림 웹사이트" --context "Next.js, Firestore 연동, 1인 개발자, 2주"
"""

import os
import sys
import json
import subprocess
import argparse
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END


# ── State ───────────────────────────────────────────────

class PlannerState(TypedDict):
    idea: str                    # 최초 아이디어/기능
    context: str                 # 환경 정보 (기술스택, 기간 등)
    background: str              # [1] 시장 조사 결과
    hypothesis: str              # [2] 가설
    solution_spec: str           # [3] MVP 스펙
    metrics_plan: str            # [4] 메트릭
    gtm_plan: str                # [5] GTM 전략
    critique: str                # [6] 검증 결과
    critique_score: float        # [6] 평균 점수
    revision_count: int          # 수정 횟수
    final_plan: str              # 최종 1-Pager
    notion_url: str              # 노션 페이지 URL


# ── OpenClaw 호출 ──────────────────────────────────────

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
GATEWAY_URL = "http://127.0.0.1:18789"


def _get_gateway_token() -> str:
    """openclaw.json에서 gateway auth token 읽기"""
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    with open(config_path) as f:
        config = json.load(f)
    return config.get("gateway", {}).get("auth", {}).get("token", "")


def call_openclaw(agent_id: str, task: str, label: str = "", timeout: int = 300) -> str:
    """OpenClaw 서브에이전트를 spawn하고 결과를 기다린다."""
    import urllib.request

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

    session_key = result["childSessionKey"]
    run_id = result["runId"]

    # Poll for completion
    import time
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


def ask_scout(prompt: str, label: str = "") -> str:
    """탐정가재에게 질문"""
    return call_openclaw("scout", prompt, label=label)


def ask_judge(prompt: str, label: str = "") -> str:
    """판사가재에게 질문"""
    return call_openclaw("judge", prompt, label=label)


# ── Nodes ───────────────────────────────────────────────

def node_background(state: PlannerState) -> dict:
    """[1] Background & Opportunity — 탐정가재"""
    print("🔍 [1/6] Background & Opportunity 조사 중...")
    prompt = f"""너는 Market Research Analyst다.

/Users/openclaw-kong/.openclaw/workspace/gajae-os/planner/RESEARCHER.md 파일을 읽고 그 형식을 따라라.

## 조사 대상
{state['idea']}

## 환경
{state['context']}

## 지시
- web_search를 최소 5회 이상 사용하라
- 한국어/영어 모두 검색하라
- 경쟁사 최소 3개 분석하라
- 데이터 없으면 "데이터 없음"으로 표시하라. 추측 금지.
- 결과를 텍스트로 반환하라 (파일 저장 불필요)"""

    result = ask_scout(prompt, label="plan-background")
    return {"background": result}


def node_hypothesis(state: PlannerState) -> dict:
    """[2] Hypothesis Setting — 탐정가재"""
    print("🔍 [2/6] Hypothesis 수립 중...")

    revision_note = ""
    if state.get("critique") and state["revision_count"] > 0:
        revision_note = f"""
## ⚠️ 이전 검증에서 반려됨 (수정 {state['revision_count']}차)
판사가재의 피드백:
{state['critique']}

위 피드백을 반영하여 가설을 개선하라."""

    prompt = f"""너는 전략가(Strategist)다.

아래 시장 조사 결과를 읽고 가설을 수립하라.

## 시장 조사 결과
{state['background']}

## 아이디어
{state['idea']}
{revision_note}

## 출력 형식
- **Belief**: "우리는 [기능/변경]을 하면, [타겟 유저]가 [행동]을 할 것이다"
- **Expected Outcome**: "[핵심 KPI]가 [X%] 개선될 것이다"
- **근거**: 시장 조사의 어떤 데이터가 이 가설을 뒷받침하는지 명시

모호한 표현 금지. 구체적 수치와 근거를 대라."""

    result = ask_scout(prompt, label="plan-hypothesis")
    return {"hypothesis": result}


def node_solution(state: PlannerState) -> dict:
    """[3] Solution & MVP Spec — 탐정가재"""
    print("🔍 [3/6] MVP Spec 설계 중...")
    prompt = f"""너는 Product Designer다.

## 제약 조건 (반드시 준수)
- 1인 개발자
- {state['context']}
- P0 판정 기준: "이것 없이 가설 검증 불가능한가?" → 아니면 P1으로

## 입력
- 아이디어: {state['idea']}
- 가설: {state['hypothesis']}
- 시장 조사: {state['background']}

## 출력 형식
- **User Flow**: 3~5단계로 기술
- **Must-Have (P0)**: 최대 3개. 무자비하게 쳐내라.
- **Nice-to-Have (P1)**: P0에서 쳐낸 것들
- **Technical Constraint**: 기존 시스템과 충돌 가능성"""

    result = ask_scout(prompt, label="plan-solution")
    return {"solution_spec": result}


def node_metrics(state: PlannerState) -> dict:
    """[4] Success Metrics — 탐정가재"""
    print("🔍 [4/6] Metrics 설계 중...")
    prompt = f"""너는 Data Scientist다.

## 입력
- 아이디어: {state['idea']}
- MVP 스펙: {state['solution_spec']}

## 출력 형식
- **Primary Metric**: 이 기능의 성패를 가를 단 하나의 숫자
- **Counter Metric**: 이 기능 때문에 나빠질 수 있는 지표
- **Go/Stop Criterion**:
  - Go: Primary Metric이 [X] 이상이면 정식 배포
  - Stop: Counter Metric이 [Y] 이상 악화되면 롤백
  - 관찰 기간: 최소 [N]일

모호한 표현 금지. 측정 가능한 구체적 수치를 제시하라.
1인 개발자 환경에서 운영 리소스 증가를 Counter Metric에 포함하라."""

    result = ask_scout(prompt, label="plan-metrics")
    return {"metrics_plan": result}


def node_gtm(state: PlannerState) -> dict:
    """[5] GTM & Operations — 탐정가재"""
    print("🔍 [5/6] GTM 전략 수립 중...")
    prompt = f"""너는 Growth Hacker다.

## 입력
- 아이디어: {state['idea']}
- MVP 스펙: {state['solution_spec']}
- 메트릭: {state['metrics_plan']}

## 출력 형식
- **Aha-Moment**: 유저가 "이거 좋다!"를 느끼는 결정적 순간. 어떻게 유도?
- **Manual Process**: 자동화 전 수동으로 해야 할 것 (1인 운영 관점)
- **Launch Plan**: 어디에 어떻게 알릴 것인가
- **Viral Loop**: 제품 내 공유/추천 장치"""

    result = ask_scout(prompt, label="plan-gtm")
    return {"gtm_plan": result}


def node_critique(state: PlannerState) -> dict:
    """[6] PO Critique — 판사가재"""
    print("⚖️ [6/6] PO Critique 검증 중...")
    prompt = f"""너는 냉정한 PO Critic이자 투자 심사관이다.
아래 기획안을 검토하고 7개 항목을 각 10점 만점으로 평가하라.

## 기획안
**아이디어**: {state['idea']}

**[1] Background**: {state['background'][:1000]}

**[2] Hypothesis**: {state['hypothesis']}

**[3] Solution Spec**: {state['solution_spec']}

**[4] Metrics**: {state['metrics_plan']}

**[5] GTM**: {state['gtm_plan']}

## 평가 항목 (각 1~10점)
1. 가설 명확성 — 구체적이고 검증 가능한가?
2. 근거 충분성 — 시장 데이터에 뒷받침되는가?
3. P0 최소성 — 하나라도 더 뺄 수 있지 않은가?
4. 실현 가능성 — 1인 개발자가 기간 내 구현 가능한가?
5. 메트릭 측정 가능성 — 실제로 측정할 인프라가 있는가?
6. Go/Stop 기준 명확성 — 구체적 수치인가?
7. 리스크 인식 — Counter Metric과 실패 시나리오를 정직하게 다뤘는가?

## 출력 형식 (반드시 이 형식으로)
SCORE: [평균 점수, 소수점 1자리]

| 항목 | 점수 | 코멘트 |
|---|---|---|
| 가설 명확성 | X/10 | ... |
| ... | ... | ... |

VERDICT: [PASS/REVISE/REJECT]

FEEDBACK: (REVISE인 경우 구체적 개선 지시)

## 판정 기준
- 평균 7점 이상: PASS
- 평균 5~6점: REVISE
- 평균 5점 미만: REJECT

자기 편의적 채점 금지. 냉정하게 평가하라."""

    result = ask_judge(prompt, label="plan-critique")

    # 점수 파싱
    score = 0.0
    for line in result.split("\n"):
        if line.strip().startswith("SCORE:"):
            try:
                score = float(line.split(":")[1].strip().split("/")[0].strip())
            except (ValueError, IndexError):
                score = 5.0
            break

    return {
        "critique": result,
        "critique_score": score,
        "revision_count": state["revision_count"] + 1,
    }


def node_finalize(state: PlannerState) -> dict:
    """최종 1-Pager 조합"""
    print("📋 최종 1-Pager 조합 중...")
    verdict = "PASS" if state["critique_score"] >= 7 else "CONDITIONAL"

    plan = f"""# 📋 PO's 1-Pager: {state['idea']}
> 상태: {'✅ PASS' if verdict == 'PASS' else '⚠️ CONDITIONAL'}
> 검증 라운드: {state['revision_count']}/3
> 점수: {state['critique_score']}/10

## 1. Background & Opportunity
{state['background']}

## 2. Hypothesis
{state['hypothesis']}

## 3. Solution & MVP Spec
{state['solution_spec']}

## 4. Success Metrics
{state['metrics_plan']}

## 5. Go-to-Market & Operations
{state['gtm_plan']}

## 6. Critique
{state['critique']}
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

    import urllib.request

    # 1-Pager를 Notion 블록으로 변환
    sections = state["final_plan"].split("\n## ")
    children = []

    for section in sections:
        if not section.strip():
            continue
        lines = section.strip().split("\n", 1)
        heading = lines[0].strip().lstrip("# ").strip()
        body = lines[1].strip() if len(lines) > 1 else ""

        # Heading
        children.append({
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"text": {"content": heading[:100]}}]
            }
        })

        # Body — 2000자 제한으로 분할
        if body:
            for chunk in [body[i:i+1900] for i in range(0, len(body), 1900)]:
                children.append({
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"text": {"content": chunk}}]
                    }
                })

    # 최대 100 블록 제한
    children = children[:95]

    parent_page_id = "ea6034d6-facc-494d-aee7-a1fa9cbec48f"  # 2026 Q1

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
            "Notion-Version": "2025-09-03",
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
        print(f"  ❌ Notion error: {e}")
        return {"notion_url": f"(error: {e})"}


# ── Routing ─────────────────────────────────────────────

def should_revise(state: PlannerState) -> Literal["revise", "finalize"]:
    """Critique 결과에 따라 분기"""
    if state["critique_score"] >= 7:
        print(f"  ✅ PASS ({state['critique_score']}/10)")
        return "finalize"
    elif state["revision_count"] >= 3:
        print(f"  ⚠️ 최대 수정 횟수 도달, 현 상태로 마무리")
        return "finalize"
    else:
        print(f"  🔄 REVISE ({state['critique_score']}/10) — {state['revision_count']}/3차 수정")
        return "revise"


# ── Graph ───────────────────────────────────────────────

def build_graph() -> StateGraph:
    graph = StateGraph(PlannerState)

    # 노드 등록
    graph.add_node("background", node_background)
    graph.add_node("hypothesis", node_hypothesis)
    graph.add_node("solution", node_solution)
    graph.add_node("metrics", node_metrics)
    graph.add_node("gtm", node_gtm)
    graph.add_node("critique", node_critique)
    graph.add_node("finalize", node_finalize)
    graph.add_node("notion", node_notion)

    # 엣지 (순차)
    graph.set_entry_point("background")
    graph.add_edge("background", "hypothesis")
    graph.add_edge("hypothesis", "solution")
    graph.add_edge("solution", "metrics")
    graph.add_edge("metrics", "gtm")
    graph.add_edge("gtm", "critique")

    # 조건부 분기: critique → revise or finalize
    graph.add_conditional_edges(
        "critique",
        should_revise,
        {
            "revise": "hypothesis",   # [2]로 돌아가서 가설부터 재수립
            "finalize": "finalize",
        }
    )

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
╔══════════════════════════════════════════╗
║  🦞 Gajae Planner — LangGraph Pipeline  ║
╚══════════════════════════════════════════╝
  아이디어: {args.idea}
  환경: {args.context}
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
        "critique": "",
        "critique_score": 0.0,
        "revision_count": 0,
        "final_plan": "",
        "notion_url": "",
    }

    # 실행
    final = graph.invoke(initial_state)

    print(f"""
╔══════════════════════════════════════════╗
║  ✅ 기획 완료                              ║
╚══════════════════════════════════════════╝
  점수: {final['critique_score']}/10
  수정 횟수: {final['revision_count']}/3
  Notion: {final['notion_url']}
""")

    return final


if __name__ == "__main__":
    main()
