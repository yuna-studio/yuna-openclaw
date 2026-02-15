#!/usr/bin/env python3
"""
🦞 Gajae Planner — LangGraph 기반 PO 기획 에이전트

진짜 LangGraph StateGraph + compile + invoke 로 실행.
각 단계: 탐정가재(work) → 판사가재(critique) → PASS/REVISE 루프
OpenClaw CLI (openclaw agent) 로 에이전트를 호출한다.

Usage:
  python3 graph.py run "아이디어" "환경정보"
  python3 graph.py status RUN_ID
  python3 graph.py feedback RUN_ID "피드백"
"""

import os
import json
import subprocess
from datetime import datetime
from typing import TypedDict, Literal, Annotated
from langgraph.graph import StateGraph, END


# ── Config ──────────────────────────────────────────────

STATE_DIR = os.path.expanduser("~/.openclaw/workspace/gajae-os/planner/state")
MAX_REVISIONS_PER_PHASE = 2

PHASE_NAMES = {
    1: "Background & Opportunity",
    2: "Hypothesis Setting",
    3: "Solution & MVP Spec",
    4: "Success Metrics",
    5: "GTM & Operations",
}


# ── State ───────────────────────────────────────────────

class PlannerState(TypedDict):
    idea: str
    context: str
    human_inputs: list          # [{phase, input}, ...]

    current_phase: int          # 1~5
    phase_results: dict         # {"1": "...", "2": "...", ...}
    phase_critiques: dict       # {"1": "...", ...}
    phase_scores: dict          # {"1": 8.3, ...}
    phase_revisions: dict       # {"1": 0, "2": 1, ...}

    status: str                 # running / completed / failed
    notion_url: str


# ── OpenClaw CLI ────────────────────────────────────────

def call_agent(agent_id: str, message: str, timeout: int = 300) -> str:
    """openclaw agent CLI로 에이전트 호출하고 응답 텍스트 반환"""
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
    """판사 응답에서 SCORE: X.X 파싱"""
    for line in text.split("\n"):
        if line.strip().startswith("SCORE:"):
            try:
                return float(line.split(":")[1].strip().split("/")[0].strip())
            except (ValueError, IndexError):
                return 5.0
    return 5.0


# ── Prompt Builders ─────────────────────────────────────

def _human_context(state: PlannerState) -> str:
    inputs = state.get("human_inputs", [])
    phase = state["current_phase"]
    relevant = [h for h in inputs if h.get("phase", 0) <= phase]
    if not relevant:
        return ""
    lines = "\n".join(f"- {h['input']}" for h in relevant)
    return f"\n## 📌 대표님 지시사항 (반드시 반영)\n{lines}"


def _revision_context(state: PlannerState) -> str:
    phase = str(state["current_phase"])
    critique = state["phase_critiques"].get(phase, "")
    rev = state["phase_revisions"].get(phase, 0)
    if critique and rev > 0:
        return f"\n## ⚠️ 판사가재 피드백 ({rev}차 반려)\n{critique}\n\n위 피드백을 반영하여 개선하라. 같은 실수 반복 금지."
    return ""


def _previous_results(state: PlannerState) -> str:
    parts = []
    for i in range(1, state["current_phase"]):
        result = state["phase_results"].get(str(i), "")
        if result:
            parts.append(f"## [{i}] {PHASE_NAMES[i]}\n{result[:1500]}")
    return "\n\n".join(parts)


WORK_TEMPLATES = {
    1: """너는 Market Research Analyst다.

/Users/openclaw-kong/.openclaw/workspace/gajae-os/planner/RESEARCHER.md 파일을 읽고 형식을 참고하라.

## 조사 대상
{idea}

## 환경
{context}
{revision}
{human}

## 지시
- web_search를 최소 5회 이상 사용하라
- 경쟁사 최소 3개 분석하라
- 데이터 없으면 "데이터 없음"으로 표시. 추측 금지.

## 출력 형식
### Context (맥락)
### Problem Statement
### Competitor Benchmark (최소 3개, 표로)
### 우리만의 Edge""",

    2: """너는 전략가(Strategist)다.

## 이전 단계 결과
{prev}

## 아이디어
{idea}
{revision}
{human}

## 출력 형식
- **Belief**: "우리는 [기능/변경]을 하면, [타겟 유저]가 [행동]을 할 것이다"
- **Expected Outcome**: "[핵심 KPI]가 [X%] 개선될 것이다"
- **근거**: 시장 조사 데이터에서 가설을 뒷받침하는 부분 명시

모호한 표현 금지. 구체적 수치와 근거.""",

    3: """너는 Product Designer다.

## 제약 조건
- 1인 개발자
- {context}
- P0 판정: "이것 없이 가설 검증 불가능한가?" → 아니면 P1

## 이전 단계 결과
{prev}
{revision}
{human}

## 출력 형식
- **User Flow**: 3~5단계
- **Must-Have (P0)**: 최대 3개. 무자비하게 쳐내라.
- **Nice-to-Have (P1)**: P0에서 쳐낸 것들
- **Technical Constraint**: 충돌 가능성""",

    4: """너는 Data Scientist다.

## 이전 단계 결과
{prev}
{revision}
{human}

## 출력 형식
- **Primary Metric**: 성패를 가를 단 하나의 숫자
- **Counter Metric**: 나빠질 수 있는 지표
- **Go/Stop Criterion**:
  - Go: [X] 이상이면 배포
  - Stop: [Y] 이상 악화되면 롤백
  - 관찰 기간: [N]일

1인 개발자 운영 리소스를 Counter Metric에 포함.
모호한 표현 금지.""",

    5: """너는 Growth Hacker다.

## 이전 단계 결과
{prev}
{revision}
{human}

## 출력 형식
- **Aha-Moment**: 결정적 순간
- **Manual Process**: 자동화 전 수동 작업 (1인 운영)
- **Launch Plan**: 어디에 어떻게
- **Viral Loop**: 공유/추천 장치""",
}

CRITIQUE_CRITERIA = {
    1: [("시장 데이터 충분성", "실제 데이터/소스가 있는가?"),
        ("경쟁사 분석 깊이", "3개 이상 비교 + 약점 파악?"),
        ("Edge 명확성", "차별점이 구체적인가?")],
    2: [("가설 구체성", "Belief가 검증 가능한 형태?"),
        ("KPI 측정 가능성", "수치가 현실적?"),
        ("근거 연결", "데이터와 논리적 연결?")],
    3: [("P0 최소성", "더 뺄 수 있지 않은가?"),
        ("실현 가능성", "1인 개발자가 기간 내 가능?"),
        ("User Flow 명확성", "경로가 단순하고 명확?")],
    4: [("Primary Metric 적절성", "가설 검증에 맞는 지표?"),
        ("Go/Stop 수치 현실성", "달성 가능하면서 의미 있는?"),
        ("Counter Metric 인식", "부작용을 정직하게 다뤘는가?")],
    5: [("Aha-Moment 설득력", "유저가 정말 가치를 느낄까?"),
        ("Launch Plan 현실성", "1인 실행 가능?"),
        ("Viral Loop 자연스러움", "억지가 아닌 자연스러운?")],
}


def make_work_prompt(state: PlannerState) -> str:
    phase = state["current_phase"]
    return WORK_TEMPLATES[phase].format(
        idea=state["idea"],
        context=state["context"],
        prev=_previous_results(state),
        revision=_revision_context(state),
        human=_human_context(state),
    )


def make_critique_prompt(state: PlannerState) -> str:
    phase = state["current_phase"]
    content = state["phase_results"].get(str(phase), "")
    criteria_text = "\n".join(
        f"{i+1}. {name} — {desc}"
        for i, (name, desc) in enumerate(CRITIQUE_CRITERIA[phase])
    )
    return f"""너는 서울대 경영학과 창업 심사위원이다. 1억 투자 결정권자.
[{phase}] {PHASE_NAMES[phase]} 결과물을 검토하라.

## 아이디어
{state['idea']}

## [{phase}] {PHASE_NAMES[phase]} 결과물
{content}

## 채점 원칙
- 네 돈 1억 걸겠냐? No면 REVISE.
- "~로 추정됩니다" → 근거 없음, 감점
- URL/출처 없는 데이터 → 0점

## 평가 항목 (각 1~10점)
{criteria_text}

## 출력 형식 (반드시)
SCORE: [평균 점수, 소수점 1자리]

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

def node_work(state: PlannerState) -> dict:
    """탐정가재가 현재 단계 작업"""
    phase = state["current_phase"]
    rev = state["phase_revisions"].get(str(phase), 0)
    suffix = f" (수정 {rev}차)" if rev > 0 else ""
    print(f"\n🔍 [{phase}/5] {PHASE_NAMES[phase]}{suffix} — 탐정가재 작업 중...")

    prompt = make_work_prompt(state)
    result = call_agent("scout", prompt, timeout=300)

    new_results = dict(state["phase_results"])
    new_results[str(phase)] = result
    print(f"  ✅ 결과 저장 ({len(result)}자)")

    return {"phase_results": new_results}


def node_critique(state: PlannerState) -> dict:
    """판사가재가 현재 단계 검증"""
    phase = state["current_phase"]
    print(f"⚖️  [{phase}/5] {PHASE_NAMES[phase]} — 판사가재 검증 중...")

    prompt = make_critique_prompt(state)
    result = call_agent("judge", prompt, timeout=180)
    score = parse_score(result)

    new_critiques = dict(state["phase_critiques"])
    new_critiques[str(phase)] = result

    new_scores = dict(state["phase_scores"])
    new_scores[str(phase)] = score

    return {
        "phase_critiques": new_critiques,
        "phase_scores": new_scores,
    }


def route_after_critique(state: PlannerState) -> Literal["revise", "next_phase", "finalize"]:
    """판사 검증 후 분기"""
    phase = state["current_phase"]
    score = state["phase_scores"].get(str(phase), 0)
    rev = state["phase_revisions"].get(str(phase), 0)

    if score >= 7:
        print(f"  ✅ PASS ({score}/10)")
        return "finalize" if phase >= 5 else "next_phase"
    elif rev >= MAX_REVISIONS_PER_PHASE:
        print(f"  ⚠️ 최대 수정 도달, 강제 통과 ({score}/10)")
        return "finalize" if phase >= 5 else "next_phase"
    else:
        print(f"  🔄 REVISE ({score}/10) — 수정 {rev + 1}/{MAX_REVISIONS_PER_PHASE}")
        return "revise"


def node_revise(state: PlannerState) -> dict:
    """수정 카운트 증가"""
    phase = str(state["current_phase"])
    new_rev = dict(state["phase_revisions"])
    new_rev[phase] = new_rev.get(phase, 0) + 1
    return {"phase_revisions": new_rev}


def node_next_phase(state: PlannerState) -> dict:
    """다음 단계로"""
    return {"current_phase": state["current_phase"] + 1}


def node_finalize(state: PlannerState) -> dict:
    """완료 표시"""
    print("\n✅ 전체 파이프라인 완료!")
    avg = sum(state["phase_scores"].values()) / max(len(state["phase_scores"]), 1)
    total_rev = sum(state["phase_revisions"].values())
    print(f"   평균: {avg:.1f}/10 | 총 수정: {total_rev}회")
    for i in range(1, 6):
        s = state["phase_scores"].get(str(i), 0)
        r = state["phase_revisions"].get(str(i), 0)
        print(f"   [{i}] {PHASE_NAMES[i]}: {s}/10 (수정 {r}회)")
    return {"status": "completed"}


# ── Build Graph ─────────────────────────────────────────

def build_graph():
    graph = StateGraph(PlannerState)

    graph.add_node("work", node_work)
    graph.add_node("critique", node_critique)
    graph.add_node("revise", node_revise)
    graph.add_node("next_phase", node_next_phase)
    graph.add_node("finalize", node_finalize)

    graph.set_entry_point("work")
    graph.add_edge("work", "critique")

    graph.add_conditional_edges(
        "critique",
        route_after_critique,
        {
            "revise": "revise",
            "next_phase": "next_phase",
            "finalize": "finalize",
        }
    )

    graph.add_edge("revise", "work")
    graph.add_edge("next_phase", "work")
    graph.add_edge("finalize", END)

    return graph.compile()


# ── State Persistence ───────────────────────────────────

def save_run(run_id: str, state: dict):
    os.makedirs(STATE_DIR, exist_ok=True)
    path = os.path.join(STATE_DIR, f"{run_id}.json")
    with open(path, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def load_run(run_id: str) -> dict:
    path = os.path.join(STATE_DIR, f"{run_id}.json")
    with open(path) as f:
        return json.load(f)


# ── Main ────────────────────────────────────────────────

def main():
    import sys

    if len(sys.argv) < 2:
        print("""Usage:
  python3 graph.py run "아이디어" "환경정보"
  python3 graph.py status RUN_ID
  python3 graph.py feedback RUN_ID "피드백"
""")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "run":
        idea = sys.argv[2]
        context = sys.argv[3] if len(sys.argv) > 3 else "1인 개발자"
        run_id = datetime.now().strftime("%Y%m%d-%H%M%S")

        print(f"""
╔══════════════════════════════════════════════════╗
║  🦞 Gajae Planner — LangGraph Pipeline          ║
╚══════════════════════════════════════════════════╝
  Run ID: {run_id}
  아이디어: {idea[:60]}
  환경: {context[:60]}
  공정: [1]→⚖️→[2]→⚖️→[3]→⚖️→[4]→⚖️→[5]→⚖️→END
""")

        initial: PlannerState = {
            "idea": idea,
            "context": context,
            "human_inputs": [],
            "current_phase": 1,
            "phase_results": {},
            "phase_critiques": {},
            "phase_scores": {},
            "phase_revisions": {},
            "status": "running",
            "notion_url": "",
        }

        # human_inputs 파일이 있으면 로드
        hi_path = os.path.join(STATE_DIR, f"{run_id}.inputs.json")
        if os.path.exists(hi_path):
            with open(hi_path) as f:
                initial["human_inputs"] = json.load(f)

        graph = build_graph()
        final = graph.invoke(initial)

        # 결과 저장
        save_run(run_id, dict(final))
        print(f"\n💾 State saved: {run_id}")

    elif cmd == "status":
        run_id = sys.argv[2]
        state = load_run(run_id)
        print(f"📋 기획: {state['idea'][:50]}")
        print(f"   상태: {state['status']}")
        for i in range(1, 6):
            s = state["phase_scores"].get(str(i), "-")
            r = state["phase_revisions"].get(str(i), 0)
            has_result = "✅" if state["phase_results"].get(str(i)) else "⏳"
            print(f"   [{i}] {PHASE_NAMES[i]}: {has_result} score={s} rev={r}")

    elif cmd == "feedback":
        run_id = sys.argv[2]
        feedback = sys.argv[3]
        phase = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        hi_path = os.path.join(STATE_DIR, f"{run_id}.inputs.json")
        inputs = []
        if os.path.exists(hi_path):
            with open(hi_path) as f:
                inputs = json.load(f)
        inputs.append({"phase": phase, "input": feedback})
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(hi_path, "w") as f:
            json.dump(inputs, f, ensure_ascii=False, indent=2)
        print(f"✅ 피드백 추가: {feedback}")


if __name__ == "__main__":
    main()
