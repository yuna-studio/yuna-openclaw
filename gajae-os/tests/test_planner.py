#!/usr/bin/env python3
"""Comprehensive tests for planner.py"""

import json
import sys
import os
import subprocess
from unittest.mock import patch, MagicMock, mock_open

# Mock the NOTION_KEY file read before importing (notion_upload is imported indirectly)
_mock_open_notion = mock_open(read_data="fake-notion-api-key\n")

with patch("builtins.open", _mock_open_notion):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import planner

import pytest


# ═══════════════════════════════════════════════════════
# Helper: create a valid PlannerState
# ═══════════════════════════════════════════════════════

def make_state(**overrides):
    state = {
        "idea": "Test idea for unit testing",
        "context": "1인 개발자, Next.js",
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
        "notion_score": 0.0,
        "notion_critique": "",
        "notion_revisions": 0,
        "status": "running",
        "notion_url": "",
    }
    state.update(overrides)
    return state


# ═══════════════════════════════════════════════════════
# call_agent()
# ═══════════════════════════════════════════════════════

class TestCallAgent:
    @patch("planner.subprocess.run")
    def test_success(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"result": {"payloads": [{"text": "Agent response"}]}}),
            stderr="",
        )
        result = planner.call_agent("scout", "do something")
        assert result == "Agent response"

    @patch("planner.subprocess.run")
    def test_non_zero_exit(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="command failed",
        )
        result = planner.call_agent("scout", "fail")
        assert "(error: exit 1" in result

    @patch("planner.subprocess.run")
    def test_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="test", timeout=300)
        result = planner.call_agent("scout", "slow")
        assert result == "(timeout)"

    @patch("planner.subprocess.run")
    def test_json_decode_error(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="not json at all",
            stderr="",
        )
        result = planner.call_agent("scout", "bad json")
        assert "not json" in result

    @patch("planner.subprocess.run")
    def test_json_decode_error_empty_stdout(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr="",
        )
        result = planner.call_agent("scout", "empty")
        assert result == "(empty)"

    @patch("planner.subprocess.run")
    def test_generic_exception(self, mock_run):
        mock_run.side_effect = OSError("network error")
        result = planner.call_agent("scout", "crash")
        assert "(error:" in result

    @patch("planner.subprocess.run")
    def test_result_is_string(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"result": "plain string result"}),
            stderr="",
        )
        result = planner.call_agent("scout", "test")
        assert "plain string result" in result

    @patch("planner.subprocess.run")
    def test_result_dict_no_payloads(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"result": {"other_key": "value"}}),
            stderr="",
        )
        result = planner.call_agent("scout", "test")
        # payloads is empty list → falls to str(reply)[:3000]
        assert "other_key" in result

    @patch("planner.subprocess.run")
    def test_result_dict_empty_payloads(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"result": {"payloads": []}}),
            stderr="",
        )
        result = planner.call_agent("scout", "test")
        # Empty payloads → falls through to str(reply)[:3000]
        assert isinstance(result, str)

    @patch("planner.subprocess.run")
    def test_timeout_param(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"result": {"payloads": [{"text": "ok"}]}}),
            stderr="",
        )
        planner.call_agent("scout", "test", timeout=600)
        args = mock_run.call_args
        assert args[1]["timeout"] == 630  # timeout + 30

    @patch("planner.subprocess.run")
    def test_cmd_arguments(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"result": {"payloads": [{"text": "ok"}]}}),
            stderr="",
        )
        planner.call_agent("judge", "evaluate this", timeout=180)
        cmd = mock_run.call_args[0][0]
        assert "openclaw" in cmd
        assert "--agent" in cmd
        assert "judge" in cmd
        assert "--message" in cmd
        assert "--json" in cmd

    @patch("planner.subprocess.run")
    def test_long_stderr_truncated(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=2,
            stdout="",
            stderr="x" * 500,
        )
        result = planner.call_agent("scout", "test")
        assert len(result) < 500  # stderr truncated to 200


# ═══════════════════════════════════════════════════════
# parse_score()
# ═══════════════════════════════════════════════════════

class TestParseScore:
    def test_standard_score(self):
        assert planner.parse_score("SCORE: 8.5") == 8.5

    def test_score_with_slash(self):
        assert planner.parse_score("SCORE: 8.5/10") == 8.5

    def test_no_score_line(self):
        assert planner.parse_score("no score here") == 5.0

    def test_malformed_score(self):
        assert planner.parse_score("SCORE: abc") == 5.0

    def test_multiple_score_lines(self):
        text = "SCORE: 7.0\nSCORE: 9.0"
        # Should return the first one
        assert planner.parse_score(text) == 7.0

    def test_score_with_whitespace(self):
        assert planner.parse_score("  SCORE:  8.0  ") == 8.0

    def test_score_integer(self):
        assert planner.parse_score("SCORE: 8") == 8.0

    def test_score_in_context(self):
        text = "Some evaluation\n\nSCORE: 7.5\n\nVERDICT: PASS"
        assert planner.parse_score(text) == 7.5

    def test_empty_string(self):
        assert planner.parse_score("") == 5.0

    def test_score_zero(self):
        assert planner.parse_score("SCORE: 0") == 0.0

    def test_score_ten(self):
        assert planner.parse_score("SCORE: 10") == 10.0


# ═══════════════════════════════════════════════════════
# make_work_prompt()
# ═══════════════════════════════════════════════════════

class TestMakeWorkPrompt:
    def test_phase_1(self):
        state = make_state(current_phase=1)
        prompt = planner.make_work_prompt(state)
        assert "Market Research" in prompt
        assert state["idea"] in prompt

    def test_phase_2(self):
        state = make_state(current_phase=2, phase_results={"1": "Phase 1 results"})
        prompt = planner.make_work_prompt(state)
        assert "전략가" in prompt
        assert "Phase 1 results" in prompt

    def test_phase_3(self):
        state = make_state(
            current_phase=3,
            phase_results={"1": "R1", "2": "R2"},
        )
        prompt = planner.make_work_prompt(state)
        assert "Product Designer" in prompt

    def test_phase_4(self):
        state = make_state(
            current_phase=4,
            phase_results={"1": "R1", "2": "R2", "3": "R3"},
        )
        prompt = planner.make_work_prompt(state)
        assert "Data Scientist" in prompt

    def test_phase_5(self):
        state = make_state(
            current_phase=5,
            phase_results={"1": "R1", "2": "R2", "3": "R3", "4": "R4"},
        )
        prompt = planner.make_work_prompt(state)
        assert "Growth Hacker" in prompt

    def test_with_revision_context(self):
        state = make_state(
            current_phase=2,
            phase_critiques={"2": "Needs more data"},
            phase_revisions={"2": 1},
        )
        prompt = planner.make_work_prompt(state)
        assert "피드백" in prompt
        assert "Needs more data" in prompt

    def test_without_revision_context(self):
        state = make_state(current_phase=2, phase_revisions={"2": 0})
        prompt = planner.make_work_prompt(state)
        assert "피드백" not in prompt or "반려" not in prompt

    def test_with_human_inputs(self):
        state = make_state(
            current_phase=2,
            human_inputs=[
                {"phase": 1, "input": "Focus on mobile"},
                {"phase": 2, "input": "Add gaming"},
            ],
        )
        prompt = planner.make_work_prompt(state)
        assert "Focus on mobile" in prompt
        assert "Add gaming" in prompt

    def test_without_human_inputs(self):
        state = make_state(current_phase=1, human_inputs=[])
        prompt = planner.make_work_prompt(state)
        assert "대표님 지시사항" not in prompt

    def test_human_inputs_phase_filter(self):
        state = make_state(
            current_phase=2,
            human_inputs=[
                {"phase": 1, "input": "Phase 1 input"},
                {"phase": 3, "input": "Phase 3 input"},
            ],
        )
        prompt = planner.make_work_prompt(state)
        assert "Phase 1 input" in prompt
        assert "Phase 3 input" not in prompt

    def test_previous_results_included(self):
        state = make_state(
            current_phase=3,
            phase_results={"1": "Result one", "2": "Result two"},
        )
        prompt = planner.make_work_prompt(state)
        assert "Result one" in prompt
        assert "Result two" in prompt


# ═══════════════════════════════════════════════════════
# make_critique_prompt()
# ═══════════════════════════════════════════════════════

class TestMakeCritiquePrompt:
    def test_phase_1(self):
        state = make_state(current_phase=1, phase_results={"1": "Research results"})
        prompt = planner.make_critique_prompt(state)
        assert "Research results" in prompt
        assert "시장 데이터" in prompt

    def test_phase_2(self):
        state = make_state(current_phase=2, phase_results={"2": "Hypothesis"})
        prompt = planner.make_critique_prompt(state)
        assert "가설 구체성" in prompt

    def test_phase_3(self):
        state = make_state(current_phase=3, phase_results={"3": "MVP Spec"})
        prompt = planner.make_critique_prompt(state)
        assert "P0 최소성" in prompt

    def test_phase_4(self):
        state = make_state(current_phase=4, phase_results={"4": "Metrics"})
        prompt = planner.make_critique_prompt(state)
        assert "Primary Metric" in prompt

    def test_phase_5(self):
        state = make_state(current_phase=5, phase_results={"5": "GTM plan"})
        prompt = planner.make_critique_prompt(state)
        assert "Aha-Moment" in prompt

    def test_contains_score_format(self):
        state = make_state(current_phase=1, phase_results={"1": "data"})
        prompt = planner.make_critique_prompt(state)
        assert "SCORE:" in prompt
        assert "VERDICT:" in prompt

    def test_contains_idea(self):
        state = make_state(current_phase=1, phase_results={"1": "data"})
        prompt = planner.make_critique_prompt(state)
        assert state["idea"] in prompt

    def test_empty_result(self):
        state = make_state(current_phase=1, phase_results={})
        prompt = planner.make_critique_prompt(state)
        # Should handle missing phase result gracefully
        assert "SCORE:" in prompt


# ═══════════════════════════════════════════════════════
# node_work()
# ═══════════════════════════════════════════════════════

class TestNodeWork:
    @patch("planner.call_agent")
    def test_returns_updated_results(self, mock_call):
        mock_call.return_value = "Work result for phase 1"
        state = make_state(current_phase=1)
        result = planner.node_work(state)
        assert "phase_results" in result
        assert result["phase_results"]["1"] == "Work result for phase 1"

    @patch("planner.call_agent")
    def test_preserves_other_phases(self, mock_call):
        mock_call.return_value = "Phase 2 result"
        state = make_state(
            current_phase=2,
            phase_results={"1": "Existing result"},
        )
        result = planner.node_work(state)
        assert result["phase_results"]["1"] == "Existing result"
        assert result["phase_results"]["2"] == "Phase 2 result"

    @patch("planner.call_agent")
    def test_calls_scout_agent(self, mock_call):
        mock_call.return_value = "result"
        state = make_state(current_phase=1)
        planner.node_work(state)
        mock_call.assert_called_once()
        assert mock_call.call_args[0][0] == "scout"


# ═══════════════════════════════════════════════════════
# node_critique()
# ═══════════════════════════════════════════════════════

class TestNodeCritique:
    @patch("planner.call_agent")
    def test_returns_critiques_and_scores(self, mock_call):
        mock_call.return_value = "Good work\n\nSCORE: 8.5"
        state = make_state(current_phase=1, phase_results={"1": "result"})
        result = planner.node_critique(state)
        assert "phase_critiques" in result
        assert "phase_scores" in result
        assert result["phase_scores"]["1"] == 8.5
        assert "Good work" in result["phase_critiques"]["1"]

    @patch("planner.call_agent")
    def test_calls_judge_agent(self, mock_call):
        mock_call.return_value = "SCORE: 7.0"
        state = make_state(current_phase=1, phase_results={"1": "r"})
        planner.node_critique(state)
        assert mock_call.call_args[0][0] == "judge"

    @patch("planner.call_agent")
    def test_no_score_defaults_to_5(self, mock_call):
        mock_call.return_value = "No score here"
        state = make_state(current_phase=1, phase_results={"1": "r"})
        result = planner.node_critique(state)
        assert result["phase_scores"]["1"] == 5.0


# ═══════════════════════════════════════════════════════
# route_after_critique()
# ═══════════════════════════════════════════════════════

class TestRouteAfterCritique:
    def test_pass_score_7(self):
        state = make_state(
            current_phase=1,
            phase_scores={"1": 7.0},
            phase_revisions={"1": 0},
        )
        assert planner.route_after_critique(state) == "next_phase"

    def test_pass_score_above_7(self):
        state = make_state(
            current_phase=2,
            phase_scores={"2": 9.0},
            phase_revisions={"2": 0},
        )
        assert planner.route_after_critique(state) == "next_phase"

    def test_revise_below_7(self):
        state = make_state(
            current_phase=1,
            phase_scores={"1": 6.5},
            phase_revisions={"1": 0},
        )
        assert planner.route_after_critique(state) == "revise"

    def test_max_revisions_force_pass(self):
        state = make_state(
            current_phase=1,
            phase_scores={"1": 5.0},
            phase_revisions={"1": 2},  # MAX_REVISIONS_PER_PHASE = 2
        )
        assert planner.route_after_critique(state) == "next_phase"

    def test_phase_3_pass_goes_to_diagram(self):
        state = make_state(
            current_phase=3,
            phase_scores={"3": 8.0},
            phase_revisions={"3": 0},
        )
        assert planner.route_after_critique(state) == "diagram"

    def test_phase_3_max_rev_goes_to_diagram(self):
        state = make_state(
            current_phase=3,
            phase_scores={"3": 5.0},
            phase_revisions={"3": 2},
        )
        assert planner.route_after_critique(state) == "diagram"

    def test_phase_5_pass_goes_to_notion(self):
        state = make_state(
            current_phase=5,
            phase_scores={"5": 8.0},
            phase_revisions={"5": 0},
        )
        assert planner.route_after_critique(state) == "notion_upload"

    def test_phase_5_max_rev_goes_to_notion(self):
        state = make_state(
            current_phase=5,
            phase_scores={"5": 4.0},
            phase_revisions={"5": 2},
        )
        assert planner.route_after_critique(state) == "notion_upload"

    def test_phase_4_pass(self):
        state = make_state(
            current_phase=4,
            phase_scores={"4": 7.5},
            phase_revisions={"4": 0},
        )
        assert planner.route_after_critique(state) == "next_phase"

    def test_missing_score_defaults_to_zero(self):
        state = make_state(
            current_phase=1,
            phase_scores={},
            phase_revisions={"1": 0},
        )
        # score=0, rev=0 → revise
        assert planner.route_after_critique(state) == "revise"

    def test_missing_revision_defaults_to_zero(self):
        state = make_state(
            current_phase=1,
            phase_scores={"1": 6.0},
            phase_revisions={},
        )
        assert planner.route_after_critique(state) == "revise"


# ═══════════════════════════════════════════════════════
# node_revise()
# ═══════════════════════════════════════════════════════

class TestNodeRevise:
    def test_increments_revision(self):
        state = make_state(current_phase=2, phase_revisions={"2": 0})
        result = planner.node_revise(state)
        assert result["phase_revisions"]["2"] == 1

    def test_increments_from_existing(self):
        state = make_state(current_phase=1, phase_revisions={"1": 1})
        result = planner.node_revise(state)
        assert result["phase_revisions"]["1"] == 2

    def test_missing_key(self):
        state = make_state(current_phase=3, phase_revisions={})
        result = planner.node_revise(state)
        assert result["phase_revisions"]["3"] == 1

    def test_preserves_other_phases(self):
        state = make_state(current_phase=2, phase_revisions={"1": 1, "2": 0})
        result = planner.node_revise(state)
        assert result["phase_revisions"]["1"] == 1


# ═══════════════════════════════════════════════════════
# node_next_phase()
# ═══════════════════════════════════════════════════════

class TestNodeNextPhase:
    def test_increments_phase(self):
        state = make_state(current_phase=1)
        result = planner.node_next_phase(state)
        assert result["current_phase"] == 2

    def test_phase_4_to_5(self):
        state = make_state(current_phase=4)
        result = planner.node_next_phase(state)
        assert result["current_phase"] == 5


# ═══════════════════════════════════════════════════════
# node_diagram()
# ═══════════════════════════════════════════════════════

class TestNodeDiagram:
    @patch("planner.call_agent")
    def test_parses_mermaid_blocks(self, mock_call):
        mock_call.return_value = """Here are diagrams:

```mermaid
flowchart TD
    A-->B
```

```mermaid
sequenceDiagram
    A->>B: hi
```
"""
        state = make_state(
            current_phase=3,
            phase_results={"1": "R1", "2": "R2", "3": "R3"},
        )
        result = planner.node_diagram(state)
        assert "diagrams" in result
        assert "flowchart" in result["diagrams"]
        assert "sequence" in result["diagrams"]

    @patch("planner.call_agent")
    def test_fallback_to_raw(self, mock_call):
        mock_call.return_value = "No mermaid blocks here, just text"
        state = make_state(current_phase=3, phase_results={"3": "R3"})
        result = planner.node_diagram(state)
        assert "raw" in result["diagrams"]

    @patch("planner.call_agent")
    def test_graph_type_mapped_to_flowchart(self, mock_call):
        mock_call.return_value = """```mermaid
graph TD
    A-->B
```"""
        state = make_state(current_phase=3, phase_results={"3": "R3"})
        result = planner.node_diagram(state)
        assert "flowchart" in result["diagrams"]

    @patch("planner.call_agent")
    def test_revision_context_included(self, mock_call):
        mock_call.return_value = "```mermaid\nflowchart TD\n  A-->B\n```"
        state = make_state(
            current_phase=3,
            phase_results={"3": "R3"},
            diagram_revisions=1,
            diagram_critique="Fix the flow",
        )
        planner.node_diagram(state)
        prompt = mock_call.call_args[0][1]
        assert "Fix the flow" in prompt


# ═══════════════════════════════════════════════════════
# node_diagram_critique()
# ═══════════════════════════════════════════════════════

class TestNodeDiagramCritique:
    @patch("planner.call_agent")
    def test_returns_score(self, mock_call):
        mock_call.return_value = "Good diagrams\n\nSCORE: 8.0"
        state = make_state(
            current_phase=3,
            phase_results={"3": "R3", "2": "R2"},
            diagrams={"flowchart": "flowchart TD\n  A-->B"},
        )
        result = planner.node_diagram_critique(state)
        assert result["diagram_score"] == 8.0
        assert "Good diagrams" in result["diagram_critique"]

    @patch("planner.call_agent")
    def test_no_score_defaults(self, mock_call):
        mock_call.return_value = "Missing score"
        state = make_state(
            current_phase=3,
            phase_results={"3": "R3", "2": "R2"},
            diagrams={"flowchart": "flowchart TD"},
        )
        result = planner.node_diagram_critique(state)
        assert result["diagram_score"] == 5.0


# ═══════════════════════════════════════════════════════
# route_after_diagram_critique()
# ═══════════════════════════════════════════════════════

class TestRouteAfterDiagramCritique:
    def test_pass(self):
        state = make_state(diagram_score=8.0, diagram_revisions=0)
        assert planner.route_after_diagram_critique(state) == "next_phase"

    def test_revise(self):
        state = make_state(diagram_score=5.0, diagram_revisions=0)
        assert planner.route_after_diagram_critique(state) == "diagram_revise"

    def test_max_revisions_force_pass(self):
        state = make_state(diagram_score=4.0, diagram_revisions=2)
        assert planner.route_after_diagram_critique(state) == "next_phase"

    def test_exactly_7(self):
        state = make_state(diagram_score=7.0, diagram_revisions=0)
        assert planner.route_after_diagram_critique(state) == "next_phase"

    def test_6_point_9(self):
        state = make_state(diagram_score=6.9, diagram_revisions=0)
        assert planner.route_after_diagram_critique(state) == "diagram_revise"

    def test_1_revision_under_max(self):
        state = make_state(diagram_score=5.0, diagram_revisions=1)
        assert planner.route_after_diagram_critique(state) == "diagram_revise"


# ═══════════════════════════════════════════════════════
# node_diagram_revise()
# ═══════════════════════════════════════════════════════

class TestNodeDiagramRevise:
    def test_increments(self):
        state = make_state(diagram_revisions=0)
        result = planner.node_diagram_revise(state)
        assert result["diagram_revisions"] == 1

    def test_increments_from_existing(self):
        state = make_state(diagram_revisions=1)
        result = planner.node_diagram_revise(state)
        assert result["diagram_revisions"] == 2


# ═══════════════════════════════════════════════════════
# node_notion_upload()
# ═══════════════════════════════════════════════════════

class TestNodeNotionUpload:
    @patch("notion_upload.reupload_to_notion")
    @patch("notion_upload.upload_to_notion")
    def test_new_upload(self, mock_upload, mock_reupload):
        mock_upload.return_value = ("page-id-new", "https://notion.so/xxx", 50)
        state = make_state(notion_page_id="")
        result = planner.node_notion_upload(state)
        assert result["notion_page_id"] == "page-id-new"
        assert "notion.so" in result["notion_url"]
        mock_upload.assert_called_once()
        mock_reupload.assert_not_called()

    @patch("notion_upload.reupload_to_notion")
    @patch("notion_upload.upload_to_notion")
    def test_re_upload(self, mock_upload, mock_reupload):
        mock_reupload.return_value = 40
        state = make_state(notion_page_id="existing-page-id")
        result = planner.node_notion_upload(state)
        assert "notion_url" in result
        mock_reupload.assert_called_once_with("existing-page-id", state)
        mock_upload.assert_not_called()


# ═══════════════════════════════════════════════════════
# node_notion_review()
# ═══════════════════════════════════════════════════════

class TestNodeNotionReview:
    @patch("planner.call_agent")
    @patch("notion_upload.read_page_blocks")
    def test_score_parsing(self, mock_read, mock_call):
        mock_read.return_value = "# Page content"
        mock_call.return_value = "Good page\n\nSCORE: 8.5"
        state = make_state(notion_page_id="page-123")
        result = planner.node_notion_review(state)
        assert result["notion_score"] == 8.5
        assert "Good page" in result["notion_critique"]

    @patch("planner.call_agent")
    @patch("notion_upload.read_page_blocks")
    def test_no_page_id(self, mock_read, mock_call):
        state = make_state(notion_page_id="")
        result = planner.node_notion_review(state)
        assert result["notion_score"] == 7.0
        mock_read.assert_not_called()


# ═══════════════════════════════════════════════════════
# route_after_notion_review()
# ═══════════════════════════════════════════════════════

class TestRouteAfterNotionReview:
    def test_pass(self):
        state = make_state(notion_score=8.0, notion_revisions=0)
        assert planner.route_after_notion_review(state) == "finalize"

    def test_revise(self):
        state = make_state(notion_score=5.0, notion_revisions=0)
        assert planner.route_after_notion_review(state) == "notion_revise"

    def test_max_revisions_force_pass(self):
        state = make_state(notion_score=4.0, notion_revisions=2)
        assert planner.route_after_notion_review(state) == "finalize"

    def test_exactly_7(self):
        state = make_state(notion_score=7.0, notion_revisions=0)
        assert planner.route_after_notion_review(state) == "finalize"


# ═══════════════════════════════════════════════════════
# node_notion_revise()
# ═══════════════════════════════════════════════════════

class TestNodeNotionRevise:
    def test_increments(self):
        state = make_state(notion_revisions=0)
        result = planner.node_notion_revise(state)
        assert result["notion_revisions"] == 1

    def test_increments_from_existing(self):
        state = make_state(notion_revisions=1)
        result = planner.node_notion_revise(state)
        assert result["notion_revisions"] == 2


# ═══════════════════════════════════════════════════════
# node_finalize()
# ═══════════════════════════════════════════════════════

class TestNodeFinalize:
    def test_returns_completed(self):
        state = make_state(
            phase_scores={"1": 8.0, "2": 7.5, "3": 9.0, "4": 7.0, "5": 8.0},
            phase_revisions={"1": 0, "2": 1, "3": 0, "4": 0, "5": 0},
            diagram_score=8.0,
            diagram_revisions=0,
            diagrams={"flowchart": "x"},
            notion_url="https://notion.so/xxx",
            notion_score=8.0,
        )
        result = planner.node_finalize(state)
        assert result["status"] == "completed"

    def test_with_no_diagrams(self):
        state = make_state(
            phase_scores={"1": 8.0, "2": 7.5, "3": 9.0, "4": 7.0, "5": 8.0},
            phase_revisions={"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
        )
        result = planner.node_finalize(state)
        assert result["status"] == "completed"

    def test_with_empty_notion(self):
        state = make_state(
            phase_scores={"1": 8.0, "2": 8.0, "3": 8.0, "4": 8.0, "5": 8.0},
            phase_revisions={"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
            notion_url="",
        )
        result = planner.node_finalize(state)
        assert result["status"] == "completed"


# ═══════════════════════════════════════════════════════
# build_graph()
# ═══════════════════════════════════════════════════════

class TestBuildGraph:
    def test_compiles_without_error(self):
        graph = planner.build_graph()
        assert graph is not None

    def test_graph_has_nodes(self):
        graph = planner.build_graph()
        # The compiled graph should be callable
        assert callable(getattr(graph, 'invoke', None))


# ═══════════════════════════════════════════════════════
# Private helpers
# ═══════════════════════════════════════════════════════

class TestPrivateHelpers:
    def test_human_context_empty(self):
        state = make_state(human_inputs=[])
        result = planner._human_context(state)
        assert result == ""

    def test_human_context_with_inputs(self):
        state = make_state(
            current_phase=2,
            human_inputs=[{"phase": 1, "input": "Do X"}, {"phase": 3, "input": "Later"}],
        )
        result = planner._human_context(state)
        assert "Do X" in result
        assert "Later" not in result

    def test_revision_context_no_critique(self):
        state = make_state(current_phase=1, phase_critiques={}, phase_revisions={"1": 0})
        result = planner._revision_context(state)
        assert result == ""

    def test_revision_context_with_critique_but_no_rev(self):
        state = make_state(current_phase=1, phase_critiques={"1": "Needs work"}, phase_revisions={"1": 0})
        result = planner._revision_context(state)
        assert result == ""

    def test_revision_context_with_critique_and_rev(self):
        state = make_state(current_phase=1, phase_critiques={"1": "Needs work"}, phase_revisions={"1": 1})
        result = planner._revision_context(state)
        assert "Needs work" in result

    def test_previous_results_empty(self):
        state = make_state(current_phase=1)
        result = planner._previous_results(state)
        assert result == ""

    def test_previous_results_has_content(self):
        state = make_state(
            current_phase=3,
            phase_results={"1": "Phase 1", "2": "Phase 2"},
        )
        result = planner._previous_results(state)
        assert "Phase 1" in result
        assert "Phase 2" in result

    def test_previous_results_truncates(self):
        state = make_state(
            current_phase=2,
            phase_results={"1": "x" * 2000},
        )
        result = planner._previous_results(state)
        assert len(result) <= 1600  # truncated to 1500 chars per phase + header


# ═══════════════════════════════════════════════════════
# Module constants
# ═══════════════════════════════════════════════════════

class TestConstants:
    def test_max_revisions(self):
        assert planner.MAX_REVISIONS_PER_PHASE == 2

    def test_phase_names(self):
        assert len(planner.PHASE_NAMES) == 5
        assert 1 in planner.PHASE_NAMES
        assert 5 in planner.PHASE_NAMES

    def test_work_templates(self):
        assert len(planner.WORK_TEMPLATES) == 5

    def test_critique_criteria(self):
        assert len(planner.CRITIQUE_CRITERIA) == 5
        for phase in range(1, 6):
            assert len(planner.CRITIQUE_CRITERIA[phase]) >= 3
