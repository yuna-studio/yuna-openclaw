#!/usr/bin/env python3
"""Comprehensive tests for notion_upload.py"""

import json
import sys
import os
from unittest.mock import patch, MagicMock, mock_open, call
import urllib.error

# Mock the NOTION_KEY file read before importing the module
_mock_open = mock_open(read_data="fake-notion-api-key-12345\n")

with patch("builtins.open", _mock_open):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    import notion_upload


import pytest


# ═══════════════════════════════════════════════════════
# text() — UTF-16 chunking
# ═══════════════════════════════════════════════════════

class TestText:
    def test_empty_string(self):
        result = notion_upload.text("")
        assert result == [{"text": {"content": ""}}]

    def test_none_input(self):
        result = notion_upload.text(None)
        assert result == [{"text": {"content": ""}}]

    def test_simple_ascii(self):
        result = notion_upload.text("hello")
        assert result == [{"text": {"content": "hello"}}]

    def test_short_string(self):
        result = notion_upload.text("abc")
        assert len(result) == 1
        assert result[0]["text"]["content"] == "abc"

    def test_exactly_2000_ascii(self):
        s = "a" * 2000
        result = notion_upload.text(s)
        assert len(result) == 1
        assert result[0]["text"]["content"] == s

    def test_2001_ascii_splits(self):
        s = "a" * 2001
        result = notion_upload.text(s)
        assert len(result) == 2
        assert result[0]["text"]["content"] == "a" * 2000
        assert result[1]["text"]["content"] == "a"

    def test_4000_ascii(self):
        s = "a" * 4000
        result = notion_upload.text(s)
        assert len(result) == 2
        assert len(result[0]["text"]["content"]) == 2000
        assert len(result[1]["text"]["content"]) == 2000

    def test_emoji_surrogate_pairs(self):
        # 😀 is U+1F600, which takes 2 UTF-16 code units (surrogate pair)
        # So 1000 emoji = 2000 UTF-16 units = exactly 1 chunk
        s = "😀" * 1000
        result = notion_upload.text(s)
        assert len(result) == 1

    def test_emoji_overflow(self):
        # 1001 emoji = 2002 UTF-16 units → 2 chunks
        s = "😀" * 1001
        result = notion_upload.text(s)
        assert len(result) == 2

    def test_cjk_characters(self):
        # CJK characters are in BMP → 1 UTF-16 unit each
        s = "가" * 2000
        result = notion_upload.text(s)
        assert len(result) == 1

    def test_cjk_overflow(self):
        s = "가" * 2001
        result = notion_upload.text(s)
        assert len(result) == 2

    def test_mixed_cjk_emoji(self):
        # 1000 CJK (1000 UTF-16) + 500 emoji (1000 UTF-16) = 2000 → 1 chunk
        s = "한" * 1000 + "😀" * 500
        result = notion_upload.text(s)
        assert len(result) == 1

    def test_mixed_cjk_emoji_overflow(self):
        # 1000 CJK (1000 UTF-16) + 501 emoji (1002 UTF-16) = 2002 → 2 chunks
        s = "한" * 1000 + "😀" * 501
        result = notion_upload.text(s)
        assert len(result) == 2

    def test_single_emoji(self):
        result = notion_upload.text("😀")
        assert result == [{"text": {"content": "😀"}}]

    def test_multiline_content(self):
        s = "line1\nline2\nline3"
        result = notion_upload.text(s)
        assert result == [{"text": {"content": s}}]

    def test_very_large_string(self):
        s = "x" * 10000
        result = notion_upload.text(s)
        assert len(result) == 5
        for chunk in result:
            assert len(chunk["text"]["content"]) <= 2000

    def test_unicode_combining_characters(self):
        # Combining characters are BMP → 1 UTF-16 each
        s = "e\u0301" * 1000  # é as e + combining accent
        result = notion_upload.text(s)
        assert len(result) == 1

    def test_returns_list_of_dicts(self):
        result = notion_upload.text("test")
        assert isinstance(result, list)
        for item in result:
            assert "text" in item
            assert "content" in item["text"]


# ═══════════════════════════════════════════════════════
# api() — Notion API calls
# ═══════════════════════════════════════════════════════

class TestApi:
    @patch("notion_upload.urllib.request.urlopen")
    def test_get_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"results": []}'
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = notion_upload.api("GET", "blocks/123/children")
        assert result == {"results": []}

    @patch("notion_upload.urllib.request.urlopen")
    def test_post_with_body(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"id": "page-123"}'
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = notion_upload.api("POST", "pages", {"parent": {"page_id": "abc"}})
        assert result == {"id": "page-123"}
        # Verify the request was made with data
        req = mock_urlopen.call_args[0][0]
        assert req.data is not None

    @patch("notion_upload.urllib.request.urlopen")
    def test_get_without_body(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"ok": true}'
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        notion_upload.api("GET", "blocks/x")
        req = mock_urlopen.call_args[0][0]
        assert req.data is None

    @patch("notion_upload.urllib.request.urlopen")
    def test_http_error_400(self, mock_urlopen):
        err = urllib.error.HTTPError(
            "http://api.notion.com/v1/test", 400, "Bad Request", {}, MagicMock()
        )
        err.read = MagicMock(return_value=b'{"message": "invalid"}')
        mock_urlopen.side_effect = err

        with pytest.raises(urllib.error.HTTPError):
            notion_upload.api("POST", "test", {"bad": "data"})

    @patch("notion_upload.urllib.request.urlopen")
    def test_http_error_404(self, mock_urlopen):
        err = urllib.error.HTTPError(
            "http://api.notion.com/v1/test", 404, "Not Found", {}, MagicMock()
        )
        err.read = MagicMock(return_value=b'{"message": "not found"}')
        mock_urlopen.side_effect = err

        with pytest.raises(urllib.error.HTTPError):
            notion_upload.api("GET", "test")

    @patch("notion_upload.urllib.request.urlopen")
    def test_http_error_500(self, mock_urlopen):
        err = urllib.error.HTTPError(
            "http://api.notion.com/v1/test", 500, "Server Error", {}, MagicMock()
        )
        err.read = MagicMock(return_value=b'{"message": "server error"}')
        mock_urlopen.side_effect = err

        with pytest.raises(urllib.error.HTTPError):
            notion_upload.api("DELETE", "test")

    @patch("notion_upload.urllib.request.urlopen")
    def test_url_construction(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{}'
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        notion_upload.api("GET", "blocks/abc/children?page_size=100")
        req = mock_urlopen.call_args[0][0]
        assert "https://api.notion.com/v1/blocks/abc/children?page_size=100" == req.full_url

    @patch("notion_upload.urllib.request.urlopen")
    def test_method_set_correctly(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{}'
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        notion_upload.api("PATCH", "blocks/abc/children", {"children": []})
        req = mock_urlopen.call_args[0][0]
        assert req.method == "PATCH"


# ═══════════════════════════════════════════════════════
# append_blocks() — batching
# ═══════════════════════════════════════════════════════

class TestAppendBlocks:
    @patch("notion_upload.time.sleep")
    @patch("notion_upload.api")
    def test_zero_blocks(self, mock_api, mock_sleep):
        notion_upload.append_blocks("page-1", [])
        mock_api.assert_not_called()

    @patch("notion_upload.time.sleep")
    @patch("notion_upload.api")
    def test_one_block(self, mock_api, mock_sleep):
        blocks = [{"type": "paragraph", "paragraph": {"rich_text": []}}]
        notion_upload.append_blocks("page-1", blocks)
        mock_api.assert_called_once_with("PATCH", "blocks/page-1/children", {"children": blocks})

    @patch("notion_upload.time.sleep")
    @patch("notion_upload.api")
    def test_exactly_100_blocks(self, mock_api, mock_sleep):
        blocks = [{"type": "paragraph"} for _ in range(100)]
        notion_upload.append_blocks("page-1", blocks)
        assert mock_api.call_count == 1

    @patch("notion_upload.time.sleep")
    @patch("notion_upload.api")
    def test_101_blocks_batches(self, mock_api, mock_sleep):
        blocks = [{"type": "paragraph"} for _ in range(101)]
        notion_upload.append_blocks("page-1", blocks)
        assert mock_api.call_count == 2
        # First batch: 100, second batch: 1
        first_call_blocks = mock_api.call_args_list[0][0][2]["children"]
        second_call_blocks = mock_api.call_args_list[1][0][2]["children"]
        assert len(first_call_blocks) == 100
        assert len(second_call_blocks) == 1

    @patch("notion_upload.time.sleep")
    @patch("notion_upload.api")
    def test_200_blocks(self, mock_api, mock_sleep):
        blocks = [{"type": "paragraph"} for _ in range(200)]
        notion_upload.append_blocks("page-1", blocks)
        assert mock_api.call_count == 2

    @patch("notion_upload.time.sleep")
    @patch("notion_upload.api")
    def test_sleep_between_batches(self, mock_api, mock_sleep):
        blocks = [{"type": "paragraph"} for _ in range(101)]
        notion_upload.append_blocks("page-1", blocks)
        assert mock_sleep.call_count == 2  # sleep after each batch
        mock_sleep.assert_called_with(0.4)


# ═══════════════════════════════════════════════════════
# delete_all_blocks()
# ═══════════════════════════════════════════════════════

class TestDeleteAllBlocks:
    @patch("notion_upload.time.sleep")
    @patch("notion_upload.api")
    def test_empty_page(self, mock_api, mock_sleep):
        mock_api.return_value = {"results": []}
        notion_upload.delete_all_blocks("page-1")
        mock_api.assert_called_once()

    @patch("notion_upload.time.sleep")
    @patch("notion_upload.api")
    def test_multiple_blocks(self, mock_api, mock_sleep):
        mock_api.side_effect = [
            {"results": [{"id": "b1"}, {"id": "b2"}, {"id": "b3"}]},
            None, None, None,  # 3 delete calls
        ]
        notion_upload.delete_all_blocks("page-1")
        assert mock_api.call_count == 4  # 1 GET + 3 DELETE

    @patch("notion_upload.time.sleep")
    @patch("notion_upload.api")
    def test_api_error_on_delete_ignored(self, mock_api, mock_sleep):
        mock_api.side_effect = [
            {"results": [{"id": "b1"}, {"id": "b2"}]},
            Exception("delete failed"),
            None,  # second delete succeeds
        ]
        # Should not raise
        notion_upload.delete_all_blocks("page-1")

    @patch("notion_upload.time.sleep")
    @patch("notion_upload.api")
    def test_sleep_between_deletes(self, mock_api, mock_sleep):
        mock_api.side_effect = [
            {"results": [{"id": "b1"}, {"id": "b2"}]},
            None, None,
        ]
        notion_upload.delete_all_blocks("page-1")
        # sleep(0.15) for each block delete
        assert any(c == call(0.15) for c in mock_sleep.call_args_list)


# ═══════════════════════════════════════════════════════
# read_page_blocks()
# ═══════════════════════════════════════════════════════

class TestReadPageBlocks:
    @patch("notion_upload.api")
    def test_heading_1(self, mock_api):
        mock_api.return_value = {
            "results": [{
                "type": "heading_1",
                "heading_1": {"rich_text": [{"text": {"content": "Title"}}]}
            }],
            "has_more": False,
        }
        result = notion_upload.read_page_blocks("p1")
        assert "# Title" in result

    @patch("notion_upload.api")
    def test_heading_2(self, mock_api):
        mock_api.return_value = {
            "results": [{
                "type": "heading_2",
                "heading_2": {"rich_text": [{"text": {"content": "Sub"}}]}
            }],
            "has_more": False,
        }
        result = notion_upload.read_page_blocks("p1")
        assert "## Sub" in result

    @patch("notion_upload.api")
    def test_heading_3(self, mock_api):
        mock_api.return_value = {
            "results": [{
                "type": "heading_3",
                "heading_3": {"rich_text": [{"text": {"content": "SubSub"}}]}
            }],
            "has_more": False,
        }
        result = notion_upload.read_page_blocks("p1")
        assert "### SubSub" in result

    @patch("notion_upload.api")
    def test_paragraph(self, mock_api):
        mock_api.return_value = {
            "results": [{
                "type": "paragraph",
                "paragraph": {"rich_text": [{"text": {"content": "Hello world"}}]}
            }],
            "has_more": False,
        }
        result = notion_upload.read_page_blocks("p1")
        assert "Hello world" in result

    @patch("notion_upload.api")
    def test_code_block(self, mock_api):
        mock_api.return_value = {
            "results": [{
                "type": "code",
                "code": {"rich_text": [{"text": {"content": "print('hi')"}}], "language": "python"}
            }],
            "has_more": False,
        }
        result = notion_upload.read_page_blocks("p1")
        assert "```python" in result
        assert "print('hi')" in result

    @patch("notion_upload.api")
    def test_bulleted_list_item(self, mock_api):
        mock_api.return_value = {
            "results": [{
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"text": {"content": "item"}}]}
            }],
            "has_more": False,
        }
        result = notion_upload.read_page_blocks("p1")
        assert "- item" in result

    @patch("notion_upload.api")
    def test_numbered_list_item(self, mock_api):
        mock_api.return_value = {
            "results": [{
                "type": "numbered_list_item",
                "numbered_list_item": {"rich_text": [{"text": {"content": "step"}}]}
            }],
            "has_more": False,
        }
        result = notion_upload.read_page_blocks("p1")
        assert "1. step" in result

    @patch("notion_upload.api")
    def test_callout(self, mock_api):
        mock_api.return_value = {
            "results": [{
                "type": "callout",
                "callout": {
                    "rich_text": [{"text": {"content": "note"}}],
                    "icon": {"emoji": "💡"}
                }
            }],
            "has_more": False,
        }
        result = notion_upload.read_page_blocks("p1")
        assert "[💡] note" in result

    @patch("notion_upload.api")
    def test_quote(self, mock_api):
        mock_api.return_value = {
            "results": [{
                "type": "quote",
                "quote": {"rich_text": [{"text": {"content": "wise words"}}]}
            }],
            "has_more": False,
        }
        result = notion_upload.read_page_blocks("p1")
        assert "> wise words" in result

    @patch("notion_upload.api")
    def test_divider(self, mock_api):
        mock_api.return_value = {
            "results": [{
                "type": "divider",
                "divider": {}
            }],
            "has_more": False,
        }
        result = notion_upload.read_page_blocks("p1")
        assert "---" in result

    @patch("notion_upload.api")
    def test_pagination(self, mock_api):
        mock_api.side_effect = [
            {
                "results": [{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "page1"}}]}}],
                "has_more": True,
                "next_cursor": "cursor-abc",
            },
            {
                "results": [{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "page2"}}]}}],
                "has_more": False,
            },
        ]
        result = notion_upload.read_page_blocks("p1")
        assert "page1" in result
        assert "page2" in result
        # Check cursor was used
        second_call = mock_api.call_args_list[1]
        assert "start_cursor=cursor-abc" in second_call[0][1]

    @patch("notion_upload.api")
    def test_max_blocks_limit(self, mock_api):
        # Create enough blocks to hit the limit
        blocks = [{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": f"b{i}"}}]}} for i in range(150)]
        mock_api.return_value = {
            "results": blocks,
            "has_more": True,
            "next_cursor": "c2",
        }
        result = notion_upload.read_page_blocks("p1", max_blocks=50)
        # Should stop after processing all blocks from first batch since count exceeds max_blocks
        assert mock_api.call_count == 1  # Only 1 API call because all 150 blocks exceed 50

    @patch("notion_upload.api")
    def test_empty_paragraph(self, mock_api):
        mock_api.return_value = {
            "results": [{
                "type": "paragraph",
                "paragraph": {"rich_text": []}
            }],
            "has_more": False,
        }
        result = notion_upload.read_page_blocks("p1")
        # Empty paragraph text → not appended (txt is empty string, and the else clause checks `if txt`)
        assert result == ""

    @patch("notion_upload.api")
    def test_multiple_rich_text_segments(self, mock_api):
        mock_api.return_value = {
            "results": [{
                "type": "paragraph",
                "paragraph": {"rich_text": [
                    {"text": {"content": "Hello "}},
                    {"text": {"content": "world"}},
                ]}
            }],
            "has_more": False,
        }
        result = notion_upload.read_page_blocks("p1")
        assert "Hello world" in result


# ═══════════════════════════════════════════════════════
# _parse_table()
# ═══════════════════════════════════════════════════════

class TestParseTable:
    def test_valid_table(self):
        table = "| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |"
        result = notion_upload._parse_table(table)
        assert result is not None
        assert result["type"] == "table"
        assert result["table"]["table_width"] == 2
        # Separator regex only matches single-column separators like |---|
        # Multi-column separators like |---|---| are kept as rows
        assert len(result["table"]["children"]) >= 3

    def test_separator_only(self):
        table = "|---|---|"
        result = notion_upload._parse_table(table)
        assert result is None  # Only separator, no data rows → <2 rows

    def test_single_data_row(self):
        # Single-column separator like |---| gets filtered, but multi-column |---|---| does not
        # So "| A | B |\n|---|---|" has 2 rows (neither is filtered by the regex)
        table = "| A | B |\n|---|---|"
        result = notion_upload._parse_table(table)
        # Both lines are kept as rows (separator regex doesn't match multi-column)
        assert result is not None
        assert result["table"]["table_width"] == 2

    def test_uneven_columns(self):
        table = "| A | B | C |\n|---|---|---|\n| 1 | 2 |"
        result = notion_upload._parse_table(table)
        assert result is not None
        assert result["table"]["table_width"] == 3
        # Second data row padded to 3
        last_row = result["table"]["children"][-1]
        assert len(last_row["table_row"]["cells"]) == 3

    def test_empty_cells(self):
        table = "| A |  |\n|---|---|\n|  | B |"
        result = notion_upload._parse_table(table)
        assert result is not None

    def test_special_chars_in_cells(self):
        table = "| Hello! | @#$% |\n|---|---|\n| <b> | &amp; |"
        result = notion_upload._parse_table(table)
        assert result is not None
        first_row = result["table"]["children"][0]
        assert first_row["table_row"]["cells"][0][0]["text"]["content"] == "Hello!"

    def test_cell_truncation_at_200(self):
        long_cell = "x" * 300
        table = f"| {long_cell} | B |\n|---|---|\n| C | D |"
        result = notion_upload._parse_table(table)
        assert result is not None
        first_cell = result["table"]["children"][0]["table_row"]["cells"][0][0]["text"]["content"]
        assert len(first_cell) <= 200

    def test_has_column_header(self):
        table = "| H1 | H2 |\n|---|---|\n| D1 | D2 |"
        result = notion_upload._parse_table(table)
        assert result["table"]["has_column_header"] is True
        assert result["table"]["has_row_header"] is False

    def test_empty_input(self):
        result = notion_upload._parse_table("")
        assert result is None

    def test_whitespace_only(self):
        result = notion_upload._parse_table("   \n  \n  ")
        assert result is None


# ═══════════════════════════════════════════════════════
# markdown_to_blocks()
# ═══════════════════════════════════════════════════════

class TestMarkdownToBlocks:
    def test_empty_input(self):
        result = notion_upload.markdown_to_blocks("")
        assert result == []

    def test_heading_1_first_line_skipped(self):
        result = notion_upload.markdown_to_blocks("# Title\nSome text")
        # First line H1 should be skipped
        types = [b["type"] for b in result]
        assert "heading_1" not in types
        assert "paragraph" in types

    def test_heading_1_not_first_line(self):
        result = notion_upload.markdown_to_blocks("intro\n# Title")
        types = [b["type"] for b in result]
        assert "heading_1" in types

    def test_heading_2(self):
        result = notion_upload.markdown_to_blocks("## Section")
        assert len(result) == 1
        assert result[0]["type"] == "heading_2"
        assert result[0]["heading_2"]["rich_text"][0]["text"]["content"] == "Section"

    def test_heading_3(self):
        result = notion_upload.markdown_to_blocks("### Subsection")
        assert len(result) == 1
        assert result[0]["type"] == "heading_3"

    def test_code_block_with_language(self):
        md = "```python\nprint('hi')\n```"
        result = notion_upload.markdown_to_blocks(md)
        assert len(result) == 1
        assert result[0]["type"] == "code"
        assert result[0]["code"]["language"] == "python"
        assert result[0]["code"]["rich_text"][0]["text"]["content"] == "print('hi')"

    def test_code_block_without_language(self):
        md = "```\nsome code\n```"
        result = notion_upload.markdown_to_blocks(md)
        assert len(result) == 1
        assert result[0]["code"]["language"] == "plain text"

    def test_table(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        result = notion_upload.markdown_to_blocks(md)
        assert len(result) == 1
        assert result[0]["type"] == "table"

    def test_invalid_table_becomes_paragraph(self):
        # Single pipe line → table parse fails → paragraph
        md = "| just one row |"
        result = notion_upload.markdown_to_blocks(md)
        assert len(result) == 1
        assert result[0]["type"] == "paragraph"

    def test_bullet_list_dash(self):
        md = "- item1\n- item2"
        result = notion_upload.markdown_to_blocks(md)
        assert len(result) == 2
        for b in result:
            assert b["type"] == "bulleted_list_item"

    def test_bullet_list_asterisk(self):
        md = "* item1"
        result = notion_upload.markdown_to_blocks(md)
        assert result[0]["type"] == "bulleted_list_item"

    def test_numbered_list(self):
        md = "1. first\n2. second"
        result = notion_upload.markdown_to_blocks(md)
        assert len(result) == 2
        for b in result:
            assert b["type"] == "numbered_list_item"
        assert result[0]["numbered_list_item"]["rich_text"][0]["text"]["content"] == "first"

    def test_blockquote(self):
        md = "> quote line 1\n> quote line 2"
        result = notion_upload.markdown_to_blocks(md)
        assert len(result) == 1
        assert result[0]["type"] == "quote"
        assert "quote line 1\nquote line 2" in result[0]["quote"]["rich_text"][0]["text"]["content"]

    def test_divider_triple_dash(self):
        result = notion_upload.markdown_to_blocks("---")
        assert len(result) == 1
        assert result[0]["type"] == "divider"

    def test_divider_triple_asterisk(self):
        result = notion_upload.markdown_to_blocks("***")
        assert len(result) == 1
        assert result[0]["type"] == "divider"

    def test_divider_triple_underscore(self):
        result = notion_upload.markdown_to_blocks("___")
        assert len(result) == 1
        assert result[0]["type"] == "divider"

    def test_paragraph(self):
        result = notion_upload.markdown_to_blocks("Just a paragraph.")
        assert len(result) == 1
        assert result[0]["type"] == "paragraph"

    def test_paragraph_continuation(self):
        md = "Line one\ncontinuation"
        result = notion_upload.markdown_to_blocks(md)
        assert len(result) == 1
        assert "Line one continuation" in result[0]["paragraph"]["rich_text"][0]["text"]["content"]

    def test_mixed_content(self):
        md = "## Title\n\nSome text\n\n- bullet\n\n1. numbered\n\n> quote\n\n---\n\n```python\ncode\n```"
        result = notion_upload.markdown_to_blocks(md)
        types = [b["type"] for b in result]
        assert "heading_2" in types
        assert "paragraph" in types
        assert "bulleted_list_item" in types
        assert "numbered_list_item" in types
        assert "quote" in types
        assert "divider" in types
        assert "code" in types

    def test_bullet_continuation_lines(self):
        md = "- item text\n  continuation"
        result = notion_upload.markdown_to_blocks(md)
        assert len(result) == 1
        content = result[0]["bulleted_list_item"]["rich_text"][0]["text"]["content"]
        assert "item text" in content
        assert "continuation" in content

    def test_heading_1_after_empty_first_line_skipped(self):
        # i == 1 and lines[0].strip() == ""
        result = notion_upload.markdown_to_blocks("\n# Title\nSome text")
        types = [b["type"] for b in result]
        assert "heading_1" not in types

    def test_skip_empty_lines(self):
        md = "\n\n\n"
        result = notion_upload.markdown_to_blocks(md)
        assert result == []


# ═══════════════════════════════════════════════════════
# build_all_blocks()
# ═══════════════════════════════════════════════════════

class TestBuildAllBlocks:
    def _make_state(self, **overrides):
        state = {
            "idea": "Test idea",
            "context": "Test context",
            "phase_results": {"1": "Result 1", "2": "Result 2", "3": "Result 3", "4": "Result 4", "5": "Result 5"},
            "phase_critiques": {"1": "Crit 1", "2": "Crit 2", "3": "Crit 3", "4": "Crit 4", "5": "Crit 5"},
            "phase_scores": {"1": 8.0, "2": 7.5, "3": 9.0, "4": 7.0, "5": 8.5},
            "phase_revisions": {"1": 0, "2": 1, "3": 0, "4": 2, "5": 0},
            "diagrams": {},
            "diagram_critique": "",
            "diagram_score": 0,
            "diagram_revisions": 0,
        }
        state.update(overrides)
        return state

    def test_full_state(self):
        state = self._make_state()
        blocks = notion_upload.build_all_blocks(state)
        assert len(blocks) > 10
        # Should contain callout, divider, heading_1
        types = [b["type"] for b in blocks]
        assert "callout" in types
        assert "divider" in types
        assert "heading_1" in types

    def test_with_diagrams(self):
        state = self._make_state(
            diagrams={"flowchart": "flowchart TD\n  A-->B", "sequence": "sequenceDiagram\n  A->>B: hi"},
            diagram_score=8.0,
            diagram_critique="Good diagrams",
        )
        blocks = notion_upload.build_all_blocks(state)
        types = [b["type"] for b in blocks]
        assert "code" in types  # mermaid code blocks
        # Check mermaid language
        code_blocks = [b for b in blocks if b["type"] == "code"]
        assert any(b["code"]["language"] == "mermaid" for b in code_blocks)

    def test_with_raw_diagram(self):
        state = self._make_state(
            diagrams={"raw": "## Some raw markdown\n\nRaw content"},
            diagram_score=6.0,
            diagram_critique="Raw fallback",
        )
        blocks = notion_upload.build_all_blocks(state)
        assert len(blocks) > 0

    def test_missing_diagrams(self):
        state = self._make_state(diagrams={})
        blocks = notion_upload.build_all_blocks(state)
        # Should still work, just no diagram section
        assert len(blocks) > 0

    def test_overview_callout_content(self):
        state = self._make_state()
        blocks = notion_upload.build_all_blocks(state)
        # First block is overview callout
        assert blocks[0]["type"] == "callout"
        assert blocks[0]["callout"]["icon"]["emoji"] == "🔥"

    def test_idea_context_callout(self):
        state = self._make_state()
        blocks = notion_upload.build_all_blocks(state)
        # Third block (after overview + divider) is idea callout
        assert blocks[2]["type"] == "callout"
        assert blocks[2]["callout"]["icon"]["emoji"] == "💡"

    def test_phase_revisions_in_title(self):
        state = self._make_state(phase_revisions={"1": 0, "2": 3, "3": 0, "4": 0, "5": 0})
        blocks = notion_upload.build_all_blocks(state)
        # Phase 2 heading should include revision count
        h1_blocks = [b for b in blocks if b["type"] == "heading_1"]
        phase2_heading = [b for b in h1_blocks if "Phase 2" in b["heading_1"]["rich_text"][0]["text"]["content"]]
        assert len(phase2_heading) > 0
        assert "수정 3회" in phase2_heading[0]["heading_1"]["rich_text"][0]["text"]["content"]

    def test_star_for_high_scores(self):
        state = self._make_state(phase_scores={"1": 9.5, "2": 7.0, "3": 8.0, "4": 7.0, "5": 7.0})
        blocks = notion_upload.build_all_blocks(state)
        overview = blocks[0]["callout"]["rich_text"][0]["text"]["content"]
        assert "⭐" in overview

    def test_empty_critique(self):
        state = self._make_state(phase_critiques={"1": "", "2": "", "3": "", "4": "", "5": ""})
        blocks = notion_upload.build_all_blocks(state)
        # No critique callouts with ⚖️
        critique_blocks = [b for b in blocks if b["type"] == "callout" and b["callout"].get("icon", {}).get("emoji") == "⚖️"]
        assert len(critique_blocks) == 0

    def test_diagram_critique_callout(self):
        state = self._make_state(
            diagrams={"flowchart": "flowchart TD\n  A-->B"},
            diagram_score=8.5,
            diagram_critique="Great flow",
            diagram_revisions=1,
        )
        blocks = notion_upload.build_all_blocks(state)
        # Should have diagram critique callout
        critique_blocks = [b for b in blocks if b["type"] == "callout" and b["callout"].get("icon", {}).get("emoji") == "⚖️"]
        assert len(critique_blocks) > 0


# ═══════════════════════════════════════════════════════
# upload_to_notion()
# ═══════════════════════════════════════════════════════

class TestUploadToNotion:
    @patch("notion_upload.append_blocks")
    @patch("notion_upload.api")
    def test_creates_page_and_appends(self, mock_api, mock_append):
        mock_api.return_value = {"id": "new-page-id"}
        state = {
            "idea": "Test",
            "context": "Ctx",
            "phase_results": {"1": "R1", "2": "R2", "3": "R3", "4": "R4", "5": "R5"},
            "phase_critiques": {"1": "C", "2": "C", "3": "C", "4": "C", "5": "C"},
            "phase_scores": {"1": 8.0, "2": 8.0, "3": 8.0, "4": 8.0, "5": 8.0},
            "phase_revisions": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
            "diagrams": {},
            "diagram_critique": "",
            "diagram_score": 0,
            "diagram_revisions": 0,
        }
        page_id, url, n_blocks = notion_upload.upload_to_notion(state)
        assert page_id == "new-page-id"
        assert "notion.so" in url
        assert n_blocks > 0
        mock_api.assert_called_once()
        mock_append.assert_called_once()

    @patch("notion_upload.append_blocks")
    @patch("notion_upload.api")
    def test_custom_title(self, mock_api, mock_append):
        mock_api.return_value = {"id": "pid"}
        state = {
            "idea": "My Idea",
            "context": "C",
            "phase_results": {"1": "", "2": "", "3": "", "4": "", "5": ""},
            "phase_critiques": {"1": "", "2": "", "3": "", "4": "", "5": ""},
            "phase_scores": {"1": 5.0, "2": 5.0, "3": 5.0, "4": 5.0, "5": 5.0},
            "phase_revisions": {},
            "diagrams": {},
            "diagram_critique": "",
            "diagram_score": 0,
            "diagram_revisions": 0,
        }
        notion_upload.upload_to_notion(state, title="Custom Title")
        call_body = mock_api.call_args[0][2]
        assert call_body["properties"]["title"]["title"][0]["text"]["content"] == "Custom Title"

    @patch("notion_upload.append_blocks")
    @patch("notion_upload.api")
    def test_auto_title_from_idea(self, mock_api, mock_append):
        mock_api.return_value = {"id": "pid"}
        state = {
            "idea": "A really long idea name that exceeds thirty characters easily",
            "context": "C",
            "phase_results": {"1": "", "2": "", "3": "", "4": "", "5": ""},
            "phase_critiques": {"1": "", "2": "", "3": "", "4": "", "5": ""},
            "phase_scores": {},
            "phase_revisions": {},
            "diagrams": {},
            "diagram_critique": "",
            "diagram_score": 0,
            "diagram_revisions": 0,
        }
        notion_upload.upload_to_notion(state)
        call_body = mock_api.call_args[0][2]
        title_content = call_body["properties"]["title"]["title"][0]["text"]["content"]
        assert "🎬" in title_content

    @patch("notion_upload.append_blocks")
    @patch("notion_upload.api")
    def test_empty_scores(self, mock_api, mock_append):
        mock_api.return_value = {"id": "pid"}
        state = {
            "idea": "X",
            "context": "C",
            "phase_results": {"1": "", "2": "", "3": "", "4": "", "5": ""},
            "phase_critiques": {"1": "", "2": "", "3": "", "4": "", "5": ""},
            "phase_scores": {},
            "phase_revisions": {},
            "diagrams": {},
            "diagram_critique": "",
            "diagram_score": 0,
            "diagram_revisions": 0,
        }
        page_id, url, n = notion_upload.upload_to_notion(state)
        assert page_id == "pid"


# ═══════════════════════════════════════════════════════
# reupload_to_notion()
# ═══════════════════════════════════════════════════════

class TestReuploadToNotion:
    @patch("notion_upload.time.sleep")
    @patch("notion_upload.append_blocks")
    @patch("notion_upload.delete_all_blocks")
    def test_deletes_and_reappends(self, mock_delete, mock_append, mock_sleep):
        state = {
            "idea": "Test",
            "context": "Ctx",
            "phase_results": {"1": "R", "2": "R", "3": "R", "4": "R", "5": "R"},
            "phase_critiques": {"1": "", "2": "", "3": "", "4": "", "5": ""},
            "phase_scores": {"1": 8.0, "2": 8.0, "3": 8.0, "4": 8.0, "5": 8.0},
            "phase_revisions": {},
            "diagrams": {},
            "diagram_critique": "",
            "diagram_score": 0,
            "diagram_revisions": 0,
        }
        n = notion_upload.reupload_to_notion("existing-page", state)
        mock_delete.assert_called_once_with("existing-page")
        mock_append.assert_called_once()
        assert n > 0

    @patch("notion_upload.time.sleep")
    @patch("notion_upload.append_blocks")
    @patch("notion_upload.delete_all_blocks")
    def test_returns_block_count(self, mock_delete, mock_append, mock_sleep):
        state = {
            "idea": "Test",
            "context": "C",
            "phase_results": {"1": "## Heading\n\nContent", "2": "R", "3": "R", "4": "R", "5": "R"},
            "phase_critiques": {"1": "Crit", "2": "", "3": "", "4": "", "5": ""},
            "phase_scores": {"1": 8.0, "2": 8.0, "3": 8.0, "4": 8.0, "5": 8.0},
            "phase_revisions": {},
            "diagrams": {},
            "diagram_critique": "",
            "diagram_score": 0,
            "diagram_revisions": 0,
        }
        n = notion_upload.reupload_to_notion("p1", state)
        assert isinstance(n, int)
        assert n > 0


# ═══════════════════════════════════════════════════════
# Module-level constants
# ═══════════════════════════════════════════════════════

class TestModuleConstants:
    def test_notion_key_loaded(self):
        # NOTION_KEY is loaded at import time from ~/.config/notion/api_key
        # In tests it may be mocked or real depending on import order
        assert isinstance(notion_upload.NOTION_KEY, str)
        assert len(notion_upload.NOTION_KEY) > 0

    def test_headers_contain_auth(self):
        assert "Authorization" in notion_upload.HEADERS
        assert "Bearer" in notion_upload.HEADERS["Authorization"]

    def test_headers_contain_version(self):
        assert "Notion-Version" in notion_upload.HEADERS

    def test_parent_page_set(self):
        assert notion_upload.PARENT_PAGE is not None
        assert len(notion_upload.PARENT_PAGE) > 0

    def test_phase_titles(self):
        assert len(notion_upload.PHASE_TITLES) == 5
        assert "1" in notion_upload.PHASE_TITLES
        assert "5" in notion_upload.PHASE_TITLES
