#!/usr/bin/env python3
"""Comprehensive tests for architect.py"""

import json
import sys
import os
import subprocess
from unittest.mock import patch, MagicMock, mock_open

# Mock the NOTION_KEY file read before importing (notion_upload is imported by architect)
_mock_open_notion = mock_open(read_data="fake-notion-api-key\n")

with patch("builtins.open", _mock_open_notion):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import architect

import pytest


# ═══════════════════════════════════════════════════════
# Helper: create a valid DocState
# ═══════════════════════════════════════════════════════

def make_state(**overrides):
    state = {
        "plan_url": "https://www.notion.so/test-page-ea6034d6facc494daee7a1fa9cbec48f",
        "plan_content": "Test planning document content for unit testing.",
        "tech_context": "Next.js, Firestore, Vercel",
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
    state.update(overrides)
    return state


# ═══════════════════════════════════════════════════════
# call_agent()
# ═══════════════════════════════════════════════════════

class TestCallAgent:
    @patch("architect.subprocess.run")
    def test_success(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"result": {"payloads": [{"text": "Agent response"}]}}),
            stderr="",
        )
        result = architect.call_agent("scout", "do something")
        assert result == "Agent response"

    @patch("architect.subprocess.run")
    def test_non_zero_exit(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="command failed",
        )
        result = architect.call_agent("scout", "fail")
        assert "(error: exit 1" in result

    @patch("architect.subprocess.run")
    def test_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="test", timeout=300)
        result = architect.call_agent("scout", "slow")
        assert result == "(timeout)"

    @patch("architect.subprocess.run")
    def test_json_decode_error_with_stdout(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="not json",
            stderr="",
        )
        result = architect.call_agent("scout", "bad json")
        assert "not json" in result

    @patch("architect.subprocess.run")
    def test_json_decode_error_empty(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
            stderr="",
        )
        result = architect.call_agent("scout", "empty")
        assert result == "(empty)"

    @patch("architect.subprocess.run")
    def test_generic_exception(self, mock_run):
        mock_run.side_effect = OSError("fail")
        result = architect.call_agent("scout", "crash")
        assert "(error:" in result

    @patch("architect.subprocess.run")
    def test_result_not_dict(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"result": "string result"}),
            stderr="",
        )
        result = architect.call_agent("scout", "test")
        assert "string result" in result

    @patch("architect.subprocess.run")
    def test_result_dict_no_payloads(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"result": {"no_payloads": True}}),
            stderr="",
        )
        result = architect.call_agent("scout", "test")
        assert isinstance(result, str)

    @patch("architect.subprocess.run")
    def test_result_dict_empty_payloads(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"result": {"payloads": []}}),
            stderr="",
        )
        result = architect.call_agent("scout", "test")
        assert isinstance(result, str)


# ═══════════════════════════════════════════════════════
# parse_score()
# ═══════════════════════════════════════════════════════

class TestParseScore:
    def test_standard_score(self):
        assert architect.parse_score("SCORE: 8.5") == 8.5

    def test_score_with_slash(self):
        assert architect.parse_score("SCORE: 9.0/10") == 9.0

    def test_no_score(self):
        assert architect.parse_score("nothing here") == 5.0

    def test_malformed(self):
        assert architect.parse_score("SCORE: xyz") == 5.0

    def test_multiple_lines(self):
        assert architect.parse_score("text\nSCORE: 7.5\nmore") == 7.5

    def test_empty_string(self):
        assert architect.parse_score("") == 5.0

    def test_integer_score(self):
        assert architect.parse_score("SCORE: 9") == 9.0

    def test_score_with_context(self):
        text = "Evaluation report\n\nSCORE: 6.8\n\nVERDICT: REVISE"
        assert architect.parse_score(text) == 6.8


# ═══════════════════════════════════════════════════════
# make_work_prompt() — renamed from make_phase_prompt
# ═══════════════════════════════════════════════════════

class TestMakeWorkPrompt:
    def test_phase_1(self):
        state = make_state(current_phase=1)
        prompt = architect.make_work_prompt(state)
        assert "Tech Lead" in prompt
        assert state["plan_content"] in prompt

    def test_phase_2(self):
        state = make_state(current_phase=2, phase_results={"1": "Phase 1 output"})
        prompt = architect.make_work_prompt(state)
        assert "Software Architect" in prompt
        assert "Phase 1 output" in prompt

    def test_phase_3_diagram(self):
        state = make_state(
            current_phase=3,
            phase_results={"1": "R1", "2": "R2"},
        )
        prompt = architect.make_work_prompt(state)
        assert "System Architect" in prompt
        assert "Mermaid" in prompt

    def test_phase_4(self):
        state = make_state(
            current_phase=4,
            phase_results={"1": "R1", "2": "R2", "3": "R3"},
        )
        prompt = architect.make_work_prompt(state)
        assert "UX Engineer" in prompt

    def test_phase_5_diagram(self):
        state = make_state(
            current_phase=5,
            phase_results={"1": "R1", "2": "R2", "3": "R3", "4": "R4"},
        )
        prompt = architect.make_work_prompt(state)
        assert "UX Engineer" in prompt
        assert "flowchart" in prompt.lower() or "플로우차트" in prompt

    def test_phase_6_diagram(self):
        state = make_state(
            current_phase=6,
            phase_results={"1": "R1", "2": "R2", "3": "R3", "4": "R4", "5": "R5"},
        )
        prompt = architect.make_work_prompt(state)
        assert "시퀀스" in prompt or "sequenceDiagram" in prompt

    @patch("architect._search_design_refs")
    def test_phase_7(self, mock_search):
        mock_search.return_value = "Design ref results"
        state = make_state(
            current_phase=7,
            phase_results={"1": "R1", "2": "R2", "3": "R3", "4": "R4", "5": "R5", "6": "R6"},
        )
        prompt = architect.make_work_prompt(state)
        assert "디자인 시스템" in prompt or "Design" in prompt
        assert "Design ref results" in prompt

    def test_with_revision_context(self):
        state = make_state(
            current_phase=2,
            phase_critiques={"2": "Need improvement"},
            phase_revisions={"2": 1},
        )
        prompt = architect.make_work_prompt(state)
        assert "Need improvement" in prompt

    def test_without_revision_context(self):
        state = make_state(current_phase=1, phase_revisions={})
        prompt = architect.make_work_prompt(state)
        # No revision feedback marker
        assert "반려" not in prompt

    def test_with_human_inputs(self):
        state = make_state(
            current_phase=1,
            human_inputs=[{"input": "Use TypeScript"}],
        )
        prompt = architect.make_work_prompt(state)
        assert "Use TypeScript" in prompt

    def test_without_human_inputs(self):
        state = make_state(current_phase=1, human_inputs=[])
        prompt = architect.make_work_prompt(state)
        assert "대표님 지시사항" not in prompt


# ═══════════════════════════════════════════════════════
# make_critique_prompt()
# ═══════════════════════════════════════════════════════

class TestMakeCritiquePrompt:
    def test_phase_1(self):
        state = make_state(current_phase=1, phase_results={"1": "Tech stack"})
        prompt = architect.make_critique_prompt(state)
        assert "산출물 완전성" in prompt
        assert "SCORE:" in prompt

    def test_phase_2(self):
        state = make_state(current_phase=2, phase_results={"2": "Architecture"})
        prompt = architect.make_critique_prompt(state)
        assert "Clean Architecture" in prompt

    def test_phase_3_diagram_role(self):
        state = make_state(current_phase=3, phase_results={"3": "Diagram"})
        prompt = architect.make_critique_prompt(state)
        assert "Mermaid" in prompt
        assert "Architect" in prompt

    def test_phase_4(self):
        state = make_state(current_phase=4, phase_results={"4": "UI design"})
        prompt = architect.make_critique_prompt(state)
        assert "페이지 완전성" in prompt

    def test_phase_5_diagram(self):
        state = make_state(current_phase=5, phase_results={"5": "Flowchart"})
        prompt = architect.make_critique_prompt(state)
        assert "Mermaid" in prompt

    def test_phase_6_diagram(self):
        state = make_state(current_phase=6, phase_results={"6": "Sequence"})
        prompt = architect.make_critique_prompt(state)
        assert "Mermaid" in prompt

    def test_phase_7(self):
        state = make_state(current_phase=7, phase_results={"7": "Design system"})
        prompt = architect.make_critique_prompt(state)
        assert "컬러 시스템" in prompt or "프리미엄" in prompt

    def test_non_diagram_phase_role(self):
        state = make_state(current_phase=1, phase_results={"1": "data"})
        prompt = architect.make_critique_prompt(state)
        assert "Staff Engineer" in prompt

    def test_diagram_phase_role(self):
        state = make_state(current_phase=3, phase_results={"3": "data"})
        prompt = architect.make_critique_prompt(state)
        assert "Architect + Mermaid Validator" in prompt

    def test_contains_plan_content(self):
        state = make_state(current_phase=1, phase_results={"1": "r"})
        prompt = architect.make_critique_prompt(state)
        assert state["plan_content"][:100] in prompt


# ═══════════════════════════════════════════════════════
# node_work()
# ═══════════════════════════════════════════════════════

class TestNodeWork:
    @patch("architect.call_agent")
    def test_regular_phase(self, mock_call):
        mock_call.return_value = "Phase 1 result"
        state = make_state(current_phase=1)
        result = architect.node_work(state)
        assert result["phase_results"]["1"] == "Phase 1 result"

    @patch("architect.call_agent")
    def test_diagram_phase(self, mock_call):
        mock_call.return_value = "```mermaid\nflowchart TD\n  A-->B\n```"
        state = make_state(current_phase=3, phase_results={"1": "R1", "2": "R2"})
        result = architect.node_work(state)
        assert result["phase_results"]["3"] == mock_call.return_value

    @patch("architect.call_agent")
    def test_preserves_other_phases(self, mock_call):
        mock_call.return_value = "New result"
        state = make_state(
            current_phase=2,
            phase_results={"1": "Old result"},
        )
        result = architect.node_work(state)
        assert result["phase_results"]["1"] == "Old result"
        assert result["phase_results"]["2"] == "New result"

    @patch("architect.call_agent")
    def test_calls_scout(self, mock_call):
        mock_call.return_value = "ok"
        state = make_state(current_phase=1)
        architect.node_work(state)
        assert mock_call.call_args[0][0] == "scout"


# ═══════════════════════════════════════════════════════
# node_critique()
# ═══════════════════════════════════════════════════════

class TestNodeCritique:
    @patch("architect.call_agent")
    def test_returns_critique_and_score(self, mock_call):
        mock_call.return_value = "Review\n\nSCORE: 8.0"
        state = make_state(current_phase=1, phase_results={"1": "result"})
        result = architect.node_critique(state)
        assert result["phase_critiques"]["1"] == mock_call.return_value
        assert result["phase_scores"]["1"] == 8.0

    @patch("architect.call_agent")
    def test_calls_judge(self, mock_call):
        mock_call.return_value = "SCORE: 7.0"
        state = make_state(current_phase=1, phase_results={"1": "r"})
        architect.node_critique(state)
        assert mock_call.call_args[0][0] == "judge"

    @patch("architect.call_agent")
    def test_no_score_defaults(self, mock_call):
        mock_call.return_value = "No score"
        state = make_state(current_phase=2, phase_results={"2": "r"})
        result = architect.node_critique(state)
        assert result["phase_scores"]["2"] == 5.0

    @patch("architect.call_agent")
    def test_preserves_previous_critiques(self, mock_call):
        mock_call.return_value = "SCORE: 8.0"
        state = make_state(
            current_phase=2,
            phase_results={"2": "r"},
            phase_critiques={"1": "Old critique"},
            phase_scores={"1": 7.0},
        )
        result = architect.node_critique(state)
        assert result["phase_critiques"]["1"] == "Old critique"
        assert result["phase_scores"]["1"] == 7.0


# ═══════════════════════════════════════════════════════
# route_after_critique()
# ═══════════════════════════════════════════════════════

class TestRouteAfterCritique:
    def test_pass(self):
        state = make_state(current_phase=1, phase_scores={"1": 7.5}, phase_revisions={"1": 0})
        assert architect.route_after_critique(state) == "next_phase"

    def test_revise(self):
        state = make_state(current_phase=1, phase_scores={"1": 5.0}, phase_revisions={"1": 0})
        assert architect.route_after_critique(state) == "revise"

    def test_max_revisions(self):
        state = make_state(current_phase=1, phase_scores={"1": 4.0}, phase_revisions={"1": 2})
        assert architect.route_after_critique(state) == "next_phase"

    def test_last_phase_goes_to_notion(self):
        state = make_state(current_phase=7, phase_scores={"7": 8.0}, phase_revisions={"7": 0})
        assert architect.route_after_critique(state) == "notion_upload"

    def test_last_phase_max_rev_goes_to_notion(self):
        state = make_state(current_phase=7, phase_scores={"7": 4.0}, phase_revisions={"7": 2})
        assert architect.route_after_critique(state) == "notion_upload"

    def test_phase_6_pass(self):
        state = make_state(current_phase=6, phase_scores={"6": 8.0}, phase_revisions={"6": 0})
        assert architect.route_after_critique(state) == "next_phase"

    def test_exactly_7(self):
        state = make_state(current_phase=3, phase_scores={"3": 7.0}, phase_revisions={"3": 0})
        assert architect.route_after_critique(state) == "next_phase"

    def test_missing_score(self):
        state = make_state(current_phase=1, phase_scores={}, phase_revisions={"1": 0})
        assert architect.route_after_critique(state) == "revise"

    def test_missing_revision(self):
        state = make_state(current_phase=1, phase_scores={"1": 5.0}, phase_revisions={})
        assert architect.route_after_critique(state) == "revise"


# ═══════════════════════════════════════════════════════
# node_revise()
# ═══════════════════════════════════════════════════════

class TestNodeRevise:
    def test_increments(self):
        state = make_state(current_phase=2, phase_revisions={"2": 0})
        result = architect.node_revise(state)
        assert result["phase_revisions"]["2"] == 1

    def test_increments_from_existing(self):
        state = make_state(current_phase=1, phase_revisions={"1": 1})
        result = architect.node_revise(state)
        assert result["phase_revisions"]["1"] == 2

    def test_missing_key(self):
        state = make_state(current_phase=3, phase_revisions={})
        result = architect.node_revise(state)
        assert result["phase_revisions"]["3"] == 1

    def test_preserves_others(self):
        state = make_state(current_phase=2, phase_revisions={"1": 1, "2": 0})
        result = architect.node_revise(state)
        assert result["phase_revisions"]["1"] == 1
        assert result["phase_revisions"]["2"] == 1


# ═══════════════════════════════════════════════════════
# node_next_phase()
# ═══════════════════════════════════════════════════════

class TestNodeNextPhase:
    def test_increments(self):
        state = make_state(current_phase=1)
        result = architect.node_next_phase(state)
        assert result["current_phase"] == 2

    def test_phase_6_to_7(self):
        state = make_state(current_phase=6)
        result = architect.node_next_phase(state)
        assert result["current_phase"] == 7

    def test_phase_3_to_4(self):
        state = make_state(current_phase=3)
        result = architect.node_next_phase(state)
        assert result["current_phase"] == 4


# ═══════════════════════════════════════════════════════
# _build_blocks()
# ═══════════════════════════════════════════════════════

class TestBuildBlocks:
    def _full_state(self, **overrides):
        state = make_state(
            phase_results={str(i): f"Phase {i} content" for i in range(1, 8)},
            phase_critiques={str(i): f"Critique {i}" for i in range(1, 8)},
            phase_scores={str(i): 8.0 for i in range(1, 8)},
            phase_revisions={str(i): 0 for i in range(1, 8)},
        )
        state.update(overrides)
        return state

    def test_builds_blocks(self):
        state = self._full_state()
        blocks = architect._build_blocks(state)
        assert len(blocks) > 10
        types = [b["type"] for b in blocks]
        assert "callout" in types
        assert "divider" in types
        assert "heading_1" in types

    def test_overview_callout(self):
        state = self._full_state()
        blocks = architect._build_blocks(state)
        assert blocks[0]["type"] == "callout"
        assert blocks[0]["callout"]["icon"]["emoji"] == "🔧"
        content = blocks[0]["callout"]["rich_text"][0]["text"]["content"]
        assert "Dev Doc" in content

    def test_plan_link_callout(self):
        state = self._full_state()
        blocks = architect._build_blocks(state)
        assert blocks[2]["type"] == "callout"
        assert blocks[2]["callout"]["icon"]["emoji"] == "📎"

    def test_diagram_phases_extract_mermaid(self):
        state = self._full_state(
            phase_results={
                "1": "Phase 1",
                "2": "Phase 2",
                "3": "Text\n```mermaid\nflowchart TD\n  A-->B\n```\nMore text",
                "4": "Phase 4",
                "5": "```mermaid\nflowchart TD\n  X-->Y\n```",
                "6": "```mermaid\nsequenceDiagram\n  A->>B: hi\n```",
                "7": "Phase 7",
            }
        )
        blocks = architect._build_blocks(state)
        code_blocks = [b for b in blocks if b["type"] == "code"]
        mermaid_blocks = [b for b in code_blocks if b["code"]["language"] == "mermaid"]
        assert len(mermaid_blocks) >= 3

    def test_critique_callouts(self):
        state = self._full_state()
        blocks = architect._build_blocks(state)
        critique_blocks = [b for b in blocks if b["type"] == "callout"
                          and b.get("callout", {}).get("icon", {}).get("emoji") == "⚖️"]
        assert len(critique_blocks) == 7  # one per phase

    def test_empty_critique(self):
        state = self._full_state(phase_critiques={str(i): "" for i in range(1, 8)})
        blocks = architect._build_blocks(state)
        critique_blocks = [b for b in blocks if b["type"] == "callout"
                          and b.get("callout", {}).get("icon", {}).get("emoji") == "⚖️"]
        assert len(critique_blocks) == 0

    def test_star_for_high_scores(self):
        state = self._full_state(phase_scores={str(i): 9.5 for i in range(1, 8)})
        blocks = architect._build_blocks(state)
        overview = blocks[0]["callout"]["rich_text"][0]["text"]["content"]
        assert "⭐" in overview

    def test_revision_count_in_overview(self):
        state = self._full_state(phase_revisions={"1": 2, "2": 0, "3": 1, "4": 0, "5": 0, "6": 0, "7": 0})
        blocks = architect._build_blocks(state)
        overview = blocks[0]["callout"]["rich_text"][0]["text"]["content"]
        assert "수정 2회" in overview

    def test_diagram_icon_in_overview(self):
        state = self._full_state()
        blocks = architect._build_blocks(state)
        overview = blocks[0]["callout"]["rich_text"][0]["text"]["content"]
        assert "📊" in overview  # diagram phases


# ═══════════════════════════════════════════════════════
# node_notion_upload()
# ═══════════════════════════════════════════════════════

class TestNodeNotionUpload:
    @patch("architect.append_blocks")
    @patch("architect.notion_api")
    def test_new_upload(self, mock_api, mock_append):
        mock_api.return_value = {"id": "new-page-id"}
        state = make_state(
            notion_page_id="",
            phase_results={str(i): f"R{i}" for i in range(1, 8)},
            phase_critiques={str(i): f"C{i}" for i in range(1, 8)},
            phase_scores={str(i): 8.0 for i in range(1, 8)},
            phase_revisions={str(i): 0 for i in range(1, 8)},
        )
        result = architect.node_notion_upload(state)
        assert result["notion_page_id"] == "new-page-id"
        assert "notion.so" in result["notion_url"]
        mock_api.assert_called_once()
        mock_append.assert_called_once()

    @patch("time.sleep")
    @patch("architect.append_blocks")
    @patch("notion_upload.delete_all_blocks")
    def test_re_upload(self, mock_delete, mock_append, mock_sleep):
        state = make_state(
            notion_page_id="existing-page",
            phase_results={str(i): f"R{i}" for i in range(1, 8)},
            phase_critiques={str(i): "" for i in range(1, 8)},
            phase_scores={str(i): 7.0 for i in range(1, 8)},
            phase_revisions={str(i): 0 for i in range(1, 8)},
        )
        result = architect.node_notion_upload(state)
        mock_delete.assert_called_once_with("existing-page")
        mock_append.assert_called_once()
        assert "notion.so" in result["notion_url"]
        assert "notion_page_id" not in result  # re-upload doesn't change page_id

    @patch("architect.append_blocks")
    @patch("architect.notion_api")
    def test_upload_error_raises(self, mock_api, mock_append):
        mock_api.side_effect = Exception("API down")
        state = make_state(
            notion_page_id="",
            phase_results={str(i): f"R{i}" for i in range(1, 8)},
            phase_critiques={str(i): "" for i in range(1, 8)},
            phase_scores={str(i): 7.0 for i in range(1, 8)},
            phase_revisions={str(i): 0 for i in range(1, 8)},
        )
        with pytest.raises(Exception, match="API down"):
            architect.node_notion_upload(state)


# ═══════════════════════════════════════════════════════
# node_notion_review()
# ═══════════════════════════════════════════════════════

class TestNodeNotionReview:
    @patch("architect.call_agent")
    @patch("architect.read_page_blocks")
    def test_success(self, mock_read, mock_call):
        mock_read.return_value = "Page content"
        mock_call.return_value = "Good\n\nSCORE: 8.5"
        state = make_state(notion_page_id="page-123")
        result = architect.node_notion_review(state)
        assert result["notion_score"] == 8.5
        assert "Good" in result["notion_critique"]

    @patch("architect.call_agent")
    @patch("architect.read_page_blocks")
    def test_no_page_id(self, mock_read, mock_call):
        state = make_state(notion_page_id="")
        result = architect.node_notion_review(state)
        assert result["notion_score"] == 7.0
        mock_read.assert_not_called()

    @patch("architect.call_agent")
    @patch("architect.read_page_blocks")
    def test_calls_judge(self, mock_read, mock_call):
        mock_read.return_value = "content"
        mock_call.return_value = "SCORE: 7.0"
        state = make_state(notion_page_id="p1")
        architect.node_notion_review(state)
        assert mock_call.call_args[0][0] == "judge"


# ═══════════════════════════════════════════════════════
# route_notion() (route_after_notion_review)
# ═══════════════════════════════════════════════════════

class TestRouteNotion:
    def test_pass(self):
        state = make_state(notion_score=8.0, notion_revisions=0)
        assert architect.route_notion(state) == "finalize"

    def test_revise(self):
        state = make_state(notion_score=5.0, notion_revisions=0)
        assert architect.route_notion(state) == "notion_revise"

    def test_max_revisions(self):
        state = make_state(notion_score=4.0, notion_revisions=2)
        assert architect.route_notion(state) == "finalize"

    def test_exactly_7(self):
        state = make_state(notion_score=7.0, notion_revisions=0)
        assert architect.route_notion(state) == "finalize"

    def test_one_revision_still_revise(self):
        state = make_state(notion_score=5.0, notion_revisions=1)
        assert architect.route_notion(state) == "notion_revise"


# ═══════════════════════════════════════════════════════
# node_notion_revise()
# ═══════════════════════════════════════════════════════

class TestNodeNotionRevise:
    def test_increments(self):
        state = make_state(notion_revisions=0)
        result = architect.node_notion_revise(state)
        assert result["notion_revisions"] == 1

    def test_increments_from_1(self):
        state = make_state(notion_revisions=1)
        result = architect.node_notion_revise(state)
        assert result["notion_revisions"] == 2


# ═══════════════════════════════════════════════════════
# node_finalize()
# ═══════════════════════════════════════════════════════

class TestNodeFinalize:
    def test_returns_completed(self):
        state = make_state(
            phase_scores={str(i): 8.0 for i in range(1, 8)},
            phase_revisions={str(i): 0 for i in range(1, 8)},
            notion_url="https://notion.so/xxx",
            notion_score=8.0,
        )
        result = architect.node_finalize(state)
        assert result["status"] == "completed"

    def test_with_empty_notion_url(self):
        state = make_state(
            phase_scores={str(i): 7.0 for i in range(1, 8)},
            phase_revisions={str(i): 0 for i in range(1, 8)},
            notion_url="",
        )
        result = architect.node_finalize(state)
        assert result["status"] == "completed"

    def test_prints_all_phases(self, capsys):
        state = make_state(
            phase_scores={str(i): 8.0 + i * 0.1 for i in range(1, 8)},
            phase_revisions={str(i): i % 2 for i in range(1, 8)},
            notion_url="https://notion.so/xxx",
            notion_score=8.5,
        )
        architect.node_finalize(state)
        output = capsys.readouterr().out
        assert "완료" in output


# ═══════════════════════════════════════════════════════
# build_graph()
# ═══════════════════════════════════════════════════════

class TestBuildGraph:
    def test_compiles(self):
        graph = architect.build_graph()
        assert graph is not None

    def test_has_invoke(self):
        graph = architect.build_graph()
        assert callable(getattr(graph, 'invoke', None))


# ═══════════════════════════════════════════════════════
# node_read_plan()
# ═══════════════════════════════════════════════════════

class TestNodeReadPlan:
    @patch("architect.read_plan_from_notion")
    def test_reads_plan(self, mock_read):
        mock_read.return_value = "Plan content from Notion"
        state = make_state()
        result = architect.node_read_plan(state)
        assert result["plan_content"] == "Plan content from Notion"

    @patch("architect.read_plan_from_notion")
    def test_error_reading(self, mock_read):
        mock_read.return_value = "(error: page_id not found)"
        state = make_state()
        result = architect.node_read_plan(state)
        assert "error" in result["plan_content"]


# ═══════════════════════════════════════════════════════
# read_plan_from_notion()
# ═══════════════════════════════════════════════════════

class TestReadPlanFromNotion:
    @patch("architect.read_page_blocks")
    def test_valid_url_32_hex(self, mock_read):
        mock_read.return_value = "Content"
        url = "https://www.notion.so/ea6034d6facc494daee7a1fa9cbec48f"
        result = architect.read_plan_from_notion(url)
        assert result == "Content"

    @patch("architect.read_page_blocks")
    def test_valid_url_with_dashes(self, mock_read):
        mock_read.return_value = "Content"
        url = "https://www.notion.so/ea6034d6-facc-494d-aee7-a1fa9cbec48f"
        result = architect.read_plan_from_notion(url)
        assert result == "Content"

    def test_invalid_url(self):
        result = architect.read_plan_from_notion("https://example.com/nope")
        assert "error" in result

    @patch("architect.read_page_blocks")
    def test_api_error(self, mock_read):
        mock_read.side_effect = Exception("API failed")
        url = "https://www.notion.so/ea6034d6facc494daee7a1fa9cbec48f"
        result = architect.read_plan_from_notion(url)
        assert "error" in result


# ═══════════════════════════════════════════════════════
# Private helpers
# ═══════════════════════════════════════════════════════

class TestPrivateHelpers:
    def test_human_ctx_empty(self):
        state = make_state(human_inputs=[])
        assert architect._human_ctx(state) == ""

    def test_human_ctx_with_inputs(self):
        state = make_state(human_inputs=[{"input": "Do X"}])
        result = architect._human_ctx(state)
        assert "Do X" in result
        assert "대표님" in result

    def test_rev_ctx_no_critique(self):
        state = make_state(current_phase=1, phase_critiques={}, phase_revisions={"1": 0})
        assert architect._rev_ctx(state) == ""

    def test_rev_ctx_with_critique_no_rev(self):
        state = make_state(current_phase=1, phase_critiques={"1": "Bad"}, phase_revisions={"1": 0})
        assert architect._rev_ctx(state) == ""

    def test_rev_ctx_with_critique_and_rev(self):
        state = make_state(current_phase=1, phase_critiques={"1": "Improve X"}, phase_revisions={"1": 1})
        result = architect._rev_ctx(state)
        assert "Improve X" in result

    def test_prev_empty(self):
        state = make_state(current_phase=1)
        assert architect._prev(state) == ""

    def test_prev_with_results(self):
        state = make_state(
            current_phase=3,
            phase_results={"1": "Result 1", "2": "Result 2"},
        )
        result = architect._prev(state)
        assert "Result 1" in result
        assert "Result 2" in result

    def test_prev_truncates(self):
        state = make_state(
            current_phase=2,
            phase_results={"1": "x" * 3000},
        )
        result = architect._prev(state)
        assert len(result) <= 2100  # truncated to 2000 per phase + header


# ═══════════════════════════════════════════════════════
# Module constants
# ═══════════════════════════════════════════════════════

class TestConstants:
    def test_max_revisions(self):
        assert architect.MAX_REVISIONS == 2

    def test_phase_names_count(self):
        assert len(architect.PHASE_NAMES) == 7

    def test_diagram_phases(self):
        assert architect.DIAGRAM_PHASES == {3, 5, 6}

    def test_work_prompts_count(self):
        assert len(architect.WORK_PROMPTS) == 7

    def test_critique_criteria_count(self):
        assert len(architect.CRITIQUE_CRITERIA) == 7
        for phase in range(1, 8):
            assert len(architect.CRITIQUE_CRITERIA[phase]) >= 3


# ═══════════════════════════════════════════════════════
# _search_design_refs()
# ═══════════════════════════════════════════════════════

class TestSearchDesignRefs:
    @patch("architect.subprocess.run")
    def test_success(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({"result": {"payloads": [{"text": "Design ref found"}]}}),
        )
        state = make_state()
        result = architect._search_design_refs(state)
        assert "Design ref found" in result

    @patch("architect.subprocess.run")
    def test_all_fail(self, mock_run):
        mock_run.side_effect = Exception("network error")
        state = make_state()
        result = architect._search_design_refs(state)
        assert "웹 검색 결과 없음" in result

    @patch("architect.subprocess.run")
    def test_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="test", timeout=90)
        state = make_state()
        result = architect._search_design_refs(state)
        assert "웹 검색 결과 없음" in result

    @patch("architect.subprocess.run")
    def test_non_zero_exit(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="err")
        state = make_state()
        result = architect._search_design_refs(state)
        assert "웹 검색 결과 없음" in result
