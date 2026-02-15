#!/usr/bin/env python3
"""
🦞 Gajae Planner — LangGraph 기반 PO 기획 에이전트

이 스크립트는 비서가재(main)가 오케스트레이터로서 실행한다.
각 단계에서 sessions_spawn을 통해 탐정/판사를 호출하는 대신,
비서가재가 이 파일의 상태를 읽고 다음 단계를 판단하여 spawn한다.

## 상태 파일 기반 실행
gajae-os/planner/state/{run_id}.json 에 상태를 저장하고,
비서가재가 상태를 읽어서 다음 단계를 실행한다.

Usage (비서가재가 내부적으로 호출):
  1. 상태 파일 생성 (init)
  2. 각 단계를 sessions_spawn으로 실행
  3. 결과를 상태에 저장
  4. 다음 단계 판단 (route)
"""

import os
import json
import time
from datetime import datetime

STATE_DIR = os.path.expanduser("~/.openclaw/workspace/gajae-os/planner/state")

PHASE_NAMES = {
    1: "Background & Opportunity",
    2: "Hypothesis Setting",
    3: "Solution & MVP Spec",
    4: "Success Metrics",
    5: "GTM & Operations",
}

MAX_REVISIONS_PER_PHASE = 2


def init_run(idea: str, context: str) -> str:
    """새 기획 실행을 초기화하고 run_id 반환"""
    os.makedirs(STATE_DIR, exist_ok=True)
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")

    state = {
        "run_id": run_id,
        "idea": idea,
        "context": context,
        "current_phase": 1,
        "status": "running",  # running / completed / failed
        "phases": {},  # {1: {result, critique, score, revisions}, ...}
        "notion_url": "",
        "created_at": datetime.now().isoformat(),
    }

    path = os.path.join(STATE_DIR, f"{run_id}.json")
    with open(path, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    return run_id


def load_state(run_id: str) -> dict:
    path = os.path.join(STATE_DIR, f"{run_id}.json")
    with open(path) as f:
        return json.load(f)


def save_state(run_id: str, state: dict):
    path = os.path.join(STATE_DIR, f"{run_id}.json")
    with open(path, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_phase(state: dict, phase: int) -> dict:
    return state["phases"].setdefault(str(phase), {
        "result": "",
        "critique": "",
        "score": 0,
        "revisions": 0,
        "status": "pending",  # pending / working / reviewing / passed / failed
    })


def next_action(state: dict) -> dict:
    """현재 상태에서 다음에 할 일을 반환.
    
    Returns:
        {
            "action": "work" | "critique" | "finalize" | "notion" | "done",
            "phase": int,
            "agent": "scout" | "judge" | None,
            "prompt": str,
        }
    """
    phase = state["current_phase"]

    if state["status"] == "completed":
        return {"action": "done", "phase": phase, "agent": None, "prompt": ""}

    if phase > 5:
        return {"action": "finalize", "phase": 5, "agent": None, "prompt": ""}

    p = get_phase(state, phase)

    if p["status"] in ("pending", "revising"):
        # 작업 필요
        prompt = _make_work_prompt(state, phase)
        return {"action": "work", "phase": phase, "agent": "scout", "prompt": prompt}

    elif p["status"] == "working_done":
        # 검증 필요
        prompt = _make_critique_prompt(state, phase)
        return {"action": "critique", "phase": phase, "agent": "judge", "prompt": prompt}

    elif p["status"] == "passed":
        # 다음 단계로
        state["current_phase"] = phase + 1
        save_state(state["run_id"], state)
        return next_action(state)  # 재귀

    return {"action": "done", "phase": phase, "agent": None, "prompt": ""}


def record_work_result(state: dict, phase: int, result: str):
    """탐정가재 작업 결과 저장"""
    p = get_phase(state, phase)
    p["result"] = result
    p["status"] = "working_done"
    save_state(state["run_id"], state)


def record_critique_result(state: dict, phase: int, critique: str, score: float):
    """판사가재 검증 결과 저장 및 분기 결정"""
    p = get_phase(state, phase)
    p["critique"] = critique
    p["score"] = score

    if score >= 7:
        p["status"] = "passed"
        if phase >= 5:
            state["current_phase"] = 6  # finalize로
    elif p["revisions"] >= MAX_REVISIONS_PER_PHASE:
        p["status"] = "passed"  # 강제 통과
        if phase >= 5:
            state["current_phase"] = 6
    else:
        p["revisions"] += 1
        p["status"] = "revising"

    save_state(state["run_id"], state)


def get_summary(state: dict) -> str:
    """현재 상태 요약"""
    lines = [f"📋 기획: {state['idea'][:50]}"]
    lines.append(f"   현재 단계: [{state['current_phase']}/5]")
    for i in range(1, 6):
        p = state["phases"].get(str(i), {})
        status = p.get("status", "pending")
        score = p.get("score", 0)

    # human_inputs 표시
    inputs = state.get("human_inputs", [])
    if inputs:
        lines.append(f"   대표님 피드백: {len(inputs)}건")

        rev = p.get("revisions", 0)
        icon = {"pending": "⏳", "working": "🔍", "working_done": "📝",
                "reviewing": "⚖️", "passed": "✅", "revising": "🔄",
                "failed": "❌"}.get(status, "❓")
        lines.append(f"   [{i}] {PHASE_NAMES[i]}: {icon} {status} (score: {score}, rev: {rev})")
    return "\n".join(lines)


# ── Prompt Builders ─────────────────────────────────────

def _revision_context(state: dict, phase: int) -> str:
    p = get_phase(state, phase)
    if p["critique"] and p["revisions"] > 0:
        return f"""
## ⚠️ 판사가재 피드백 ({p['revisions']}차 반려)
{p['critique']}

위 피드백을 반영하여 개선하라. 같은 실수 반복 금지."""
    return ""


def _human_context(state: dict, phase: int) -> str:
    """대표님이 이 대화에서 준 피드백을 프롬프트에 주입"""
    inputs = state.get("human_inputs", [])
    relevant = [h for h in inputs if h.get("phase", 0) <= phase]
    if not relevant:
        return ""
    lines = "\n".join(f"- {h['input']}" for h in relevant)
    return f"""
## 📌 대표님 지시사항 (반드시 반영)
{lines}"""


def _get_previous_results(state: dict, up_to_phase: int) -> str:
    """이전 단계 결과물들을 컨텍스트로 제공"""
    parts = []
    key_map = {1: "background", 2: "hypothesis", 3: "solution", 4: "metrics", 5: "gtm"}
    for i in range(1, up_to_phase):
        p = state["phases"].get(str(i), {})
        if p.get("result"):
            parts.append(f"## [{i}] {PHASE_NAMES[i]}\n{p['result'][:1500]}")
    return "\n\n".join(parts)


def _make_work_prompt(state: dict, phase: int) -> str:
    idea = state["idea"]
    context = state["context"]
    prev = _get_previous_results(state, phase)
    revision = _revision_context(state, phase)

    human = _human_context(state, phase)

    if phase == 1:
        return f"""너는 Market Research Analyst다.

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
### 우리만의 Edge"""

    elif phase == 2:
        return f"""너는 전략가(Strategist)다.

## 이전 단계 결과
{prev}

## 아이디어
{idea}
{revision}
{human}

## 출력 형식
- **Belief**: "우리는 [기능/변경]을 하면, [타겟 유저]가 [행동]을 할 것이다"
- **Expected Outcome**: "[핵심 KPI]가 [X%] 개선될 것이다"
- **근거**: 시장 조사 데이터에서 이 가설을 뒷받침하는 부분 명시

모호한 표현 금지. 구체적 수치와 근거."""

    elif phase == 3:
        return f"""너는 Product Designer다.

## 제약 조건 (반드시 준수)
- 1인 개발자
- {context}
- P0 판정 기준: "이것 없이 가설 검증 불가능한가?" → 아니면 P1으로

## 이전 단계 결과
{prev}
{revision}
{human}

## 출력 형식
- **User Flow**: 3~5단계로 기술
- **Must-Have (P0)**: 최대 3개. 무자비하게 쳐내라.
- **Nice-to-Have (P1)**: P0에서 쳐낸 것들
- **Technical Constraint**: 기존 시스템과 충돌 가능성"""

    elif phase == 4:
        return f"""너는 Data Scientist다.

## 이전 단계 결과
{prev}
{revision}
{human}

## 출력 형식
- **Primary Metric**: 이 기능의 성패를 가를 단 하나의 숫자
- **Counter Metric**: 이 기능 때문에 나빠질 수 있는 지표
- **Go/Stop Criterion**:
  - Go: Primary Metric이 [X] 이상이면 정식 배포
  - Stop: Counter Metric이 [Y] 이상 악화되면 롤백
  - 관찰 기간: 최소 [N]일

1인 개발자 운영 리소스 증가를 Counter Metric에 포함.
모호한 표현 금지. 측정 가능한 구체적 수치."""

    elif phase == 5:
        return f"""너는 Growth Hacker다.

## 이전 단계 결과
{prev}
{revision}
{human}

## 출력 형식
- **Aha-Moment**: 유저가 "이거 좋다!"를 느끼는 결정적 순간
- **Manual Process**: 자동화 전 수동으로 해야 할 것 (1인 운영)
- **Launch Plan**: 어디에 어떻게 알릴 것인가
- **Viral Loop**: 제품 내 공유/추천 장치"""

    return ""


def _make_critique_prompt(state: dict, phase: int) -> str:
    content = get_phase(state, phase)["result"]

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
[{phase}] {PHASE_NAMES[phase]} 결과물을 검토하라.

## 아이디어
{state['idea']}

## [{phase}] {PHASE_NAMES[phase]} 결과물
{content}

## 평가 항목 (각 1~10점)
{criteria_text}

## 출력 형식 (반드시 이 형식으로)
SCORE: [평균 점수, 소수점 1자리]

| 항목 | 점수 | 코멘트 |
|---|---|---|
| ... | X/10 | ... |

VERDICT: [PASS/REVISE/REJECT]

FEEDBACK: (REVISE인 경우 구체적 개선 지시)

## 판정 기준
- 평균 7점 이상: PASS
- 평균 5~6점: REVISE
- 평균 5점 미만: REJECT

냉정하게 평가하라. 자기 편의적 채점 금지."""


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 graph.py init '아이디어' --context '환경'")
        print("       python3 graph.py status RUN_ID")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "init":
        idea = sys.argv[2]
        context = sys.argv[3] if len(sys.argv) > 3 else "1인 개발자"
        run_id = init_run(idea, context)
        print(f"✅ Run initialized: {run_id}")
        state = load_state(run_id)
        na = next_action(state)
        print(f"   Next: {na['action']} phase={na['phase']} agent={na['agent']}")

    elif cmd == "status":
        run_id = sys.argv[2]
        state = load_state(run_id)
        print(get_summary(state))

    elif cmd == "next":
        run_id = sys.argv[2]
        state = load_state(run_id)
        na = next_action(state)
        print(json.dumps(na, ensure_ascii=False, default=str))
