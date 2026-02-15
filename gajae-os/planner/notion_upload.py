#!/usr/bin/env python3
"""Upload planner results to Notion. Importable from graph.py."""
import json, os, re, sys, time, urllib.request

NOTION_KEY = open(os.path.expanduser("~/.config/notion/api_key")).read().strip()
HEADERS = {
    "Authorization": f"Bearer {NOTION_KEY}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json",
}
PARENT_PAGE = "ea6034d6-facc-494d-aee7-a1fa9cbec48f"  # 2026 Q1

PHASE_TITLES = {
    "1": "Background & Opportunity",
    "2": "Hypothesis Setting",
    "3": "Solution & MVP Spec",
    "4": "Success Metrics",
    "5": "GTM & Operations",
}


# ── Notion API helpers ──────────────────────────────────

def api(method, path, body=None):
    url = f"https://api.notion.com/v1/{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def text(content):
    return [{"text": {"content": content[:2000]}}]


def append_blocks(page_id, blocks):
    """Append blocks in batches of 100 (Notion limit)."""
    for i in range(0, len(blocks), 100):
        batch = blocks[i : i + 100]
        api("PATCH", f"blocks/{page_id}/children", {"children": batch})
        time.sleep(0.4)


def delete_all_blocks(page_id):
    """Delete all children blocks from a page (for re-upload)."""
    resp = api("GET", f"blocks/{page_id}/children?page_size=100")
    for block in resp.get("results", []):
        try:
            api("DELETE", f"blocks/{block['id']}")
            time.sleep(0.15)
        except Exception:
            pass


def read_page_blocks(page_id, max_blocks=200):
    """Read all blocks from a Notion page as plain text for review."""
    lines = []
    cursor = None
    count = 0
    while count < max_blocks:
        url = f"blocks/{page_id}/children?page_size=100"
        if cursor:
            url += f"&start_cursor={cursor}"
        resp = api("GET", url)
        for block in resp.get("results", []):
            btype = block["type"]
            content = block.get(btype, {})
            # Extract text
            rt = content.get("rich_text", [])
            txt = "".join(r.get("text", {}).get("content", "") for r in rt)
            if btype == "heading_1":
                lines.append(f"# {txt}")
            elif btype == "heading_2":
                lines.append(f"## {txt}")
            elif btype == "heading_3":
                lines.append(f"### {txt}")
            elif btype == "bulleted_list_item":
                lines.append(f"- {txt}")
            elif btype == "numbered_list_item":
                lines.append(f"1. {txt}")
            elif btype == "code":
                lang = content.get("language", "")
                lines.append(f"```{lang}\n{txt}\n```")
            elif btype == "callout":
                emoji = content.get("icon", {}).get("emoji", "")
                lines.append(f"[{emoji}] {txt}")
            elif btype == "quote":
                lines.append(f"> {txt}")
            elif btype == "divider":
                lines.append("---")
            elif txt:
                lines.append(txt)
            count += 1
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return "\n".join(lines)


# ── Markdown → Notion Blocks (improved) ─────────────────

def _parse_table(table_text):
    """Parse markdown table into Notion table block."""
    lines = [l.strip() for l in table_text.strip().split("\n") if l.strip()]
    if len(lines) < 2:
        return None

    # Parse rows
    rows = []
    for line in lines:
        if re.match(r'^\|[\s\-:]+\|$', line):
            continue  # separator row
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)

    if len(rows) < 2:
        return None

    # Determine column count
    n_cols = max(len(r) for r in rows)

    table_rows = []
    for i, row in enumerate(rows):
        # Pad row to n_cols
        while len(row) < n_cols:
            row.append("")
        cells = [[{"text": {"content": cell[:200]}}] for cell in row]
        table_rows.append({"type": "table_row", "table_row": {"cells": cells}})

    return {
        "type": "table",
        "table": {
            "table_width": n_cols,
            "has_column_header": True,
            "has_row_header": False,
            "children": table_rows,
        },
    }


def markdown_to_blocks(content):
    """Convert markdown text to Notion blocks — handles tables, code, lists, headers."""
    blocks = []
    lines = content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            i += 1
            continue

        # Top-level title (skip)
        if stripped.startswith("# ") and not stripped.startswith("## "):
            # Keep as heading_1 but skip if first line
            if i == 0 or (i == 1 and not lines[0].strip()):
                i += 1
                continue
            blocks.append({"type": "heading_1", "heading_1": {"rich_text": text(stripped[2:])}})
            i += 1
            continue

        # Headings
        if stripped.startswith("### "):
            blocks.append({"type": "heading_3", "heading_3": {"rich_text": text(stripped[4:])}})
            i += 1
            continue
        if stripped.startswith("## "):
            blocks.append({"type": "heading_2", "heading_2": {"rich_text": text(stripped[3:])}})
            i += 1
            continue

        # Code blocks
        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            code_text = "\n".join(code_lines)
            notion_lang = lang if lang else "plain text"
            blocks.append({"type": "code", "code": {"rich_text": text(code_text), "language": notion_lang}})
            continue

        # Tables (collect consecutive | lines)
        if stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            table_text = "\n".join(table_lines)
            table_block = _parse_table(table_text)
            if table_block:
                blocks.append(table_block)
            else:
                blocks.append({"type": "paragraph", "paragraph": {"rich_text": text(table_text[:2000])}})
            continue

        # Bullet lists
        if stripped.startswith("- ") or stripped.startswith("* "):
            item_text = stripped[2:]
            # Collect continuation lines (indented)
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(("-", "*", "#", "|", ">", "```", "1.")):
                if lines[i].startswith("  "):
                    item_text += " " + lines[i].strip()
                else:
                    break
                i += 1
            blocks.append({"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": text(item_text)}})
            continue

        # Numbered lists
        if re.match(r'^\d+\.\s', stripped):
            item_text = re.sub(r'^\d+\.\s', '', stripped)
            i += 1
            blocks.append({"type": "numbered_list_item", "numbered_list_item": {"rich_text": text(item_text)}})
            continue

        # Blockquote
        if stripped.startswith("> "):
            quote_lines = [stripped[2:]]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("> "):
                quote_lines.append(lines[i].strip()[2:])
                i += 1
            blocks.append({"type": "quote", "quote": {"rich_text": text("\n".join(quote_lines))}})
            continue

        # Horizontal rule
        if stripped in ("---", "***", "___"):
            blocks.append({"type": "divider", "divider": {}})
            i += 1
            continue

        # Regular paragraph — collect until blank or structural line
        para_lines = [stripped]
        i += 1
        while i < len(lines):
            nl = lines[i].strip()
            if not nl or nl.startswith(("#", "|", "-", "*", ">", "```")) or re.match(r'^\d+\.\s', nl):
                break
            para_lines.append(nl)
            i += 1
        blocks.append({"type": "paragraph", "paragraph": {"rich_text": text(" ".join(para_lines))}})

    return blocks


# ── Build page content ──────────────────────────────────

def build_all_blocks(state):
    """Build complete Notion block list from planner state."""
    scores = state["phase_scores"]
    avg = sum(scores.values()) / max(len(scores), 1)
    total_revisions = sum(state.get("phase_revisions", {}).values())

    all_blocks = []

    # Overview callout
    score_lines = []
    for p in ["1", "2", "3", "4", "5"]:
        rev = state.get("phase_revisions", {}).get(p, 0)
        rev_str = f" (수정 {rev}회)" if rev else ""
        star = " ⭐" if scores.get(p, 0) >= 9.0 else ""
        score_lines.append(f"[{p}] {PHASE_TITLES[p]}: {scores.get(p, 0)}/10{rev_str}{star}")

    # Diagram score line
    d_score = state.get("diagram_score", 0)
    if d_score:
        d_rev = state.get("diagram_revisions", 0)
        d_rev_str = f" (수정 {d_rev}회)" if d_rev else ""
        score_lines.append(f"[📊] UX Diagrams: {d_score}/10{d_rev_str}")

    overview = f"LangGraph Pipeline — 평균 {avg:.1f}/10 | 총 수정 {total_revisions}회\n\n" + "\n".join(score_lines)
    all_blocks.append({
        "type": "callout",
        "callout": {"icon": {"emoji": "🔥"}, "rich_text": text(overview)},
    })
    all_blocks.append({"type": "divider", "divider": {}})

    # Idea & context
    all_blocks.append({
        "type": "callout",
        "callout": {"icon": {"emoji": "💡"}, "rich_text": text(f"아이디어: {state['idea']}\n\n환경: {state['context']}")},
    })
    all_blocks.append({"type": "divider", "divider": {}})

    # Each phase
    for p in ["1", "2", "3", "4", "5"]:
        content = state["phase_results"].get(p, "")
        critique = state["phase_critiques"].get(p, "")
        score = scores.get(p, 0)
        revisions = state.get("phase_revisions", {}).get(p, 0)

        rev_text = f" (수정 {revisions}회)" if revisions else ""
        all_blocks.append({
            "type": "heading_1",
            "heading_1": {"rich_text": text(f"Phase {p} — {PHASE_TITLES[p]} ({score}/10){rev_text}")},
        })

        # Convert markdown content to proper Notion blocks
        content_blocks = markdown_to_blocks(content)
        all_blocks.extend(content_blocks)

        # Judge critique callout
        if critique:
            all_blocks.append({
                "type": "callout",
                "callout": {
                    "icon": {"emoji": "⚖️"},
                    "rich_text": text(f"판사가재 평가: {score}/10\n\n{critique[:1900]}"),
                },
            })
        all_blocks.append({"type": "divider", "divider": {}})

        # Phase 3 이후: 다이어그램 섹션
        if p == "3" and state.get("diagrams"):
            diagrams = state["diagrams"]
            d_critique = state.get("diagram_critique", "")

            all_blocks.append({
                "type": "heading_1",
                "heading_1": {"rich_text": text(f"📊 UX Diagrams ({d_score}/10)")},
            })

            for name, mermaid_code in diagrams.items():
                if name == "raw":
                    raw_blocks = markdown_to_blocks(mermaid_code)
                    all_blocks.extend(raw_blocks)
                    continue
                label = "User Flow (Flowchart)" if name == "flowchart" else "Sequence Diagram" if name == "sequence" else name
                all_blocks.append({
                    "type": "heading_2",
                    "heading_2": {"rich_text": text(label)},
                })
                all_blocks.append({
                    "type": "code",
                    "code": {"rich_text": text(mermaid_code), "language": "mermaid"},
                })

            if d_critique:
                d_rev = state.get("diagram_revisions", 0)
                all_blocks.append({
                    "type": "callout",
                    "callout": {
                        "icon": {"emoji": "⚖️"},
                        "rich_text": text(f"판사가재 다이어그램 검증: {d_score}/10 (수정 {d_rev}회)\n\n{d_critique[:1900]}"),
                    },
                })
            all_blocks.append({"type": "divider", "divider": {}})

    return all_blocks


# ── Public API (used by graph.py) ───────────────────────

def upload_to_notion(state, title=None):
    """Create Notion page from planner state. Returns (page_id, url)."""
    scores = state.get("phase_scores", {})
    avg = sum(scores.values()) / max(len(scores), 1) if scores else 0

    if not title:
        idea_short = state.get("idea", "Plan")[:30]
        title = f"🎬 {idea_short}… (avg {avg:.1f}/10)"

    # Create page
    page = api("POST", "pages", {
        "parent": {"page_id": PARENT_PAGE},
        "properties": {
            "title": {"title": text(title)},
        },
        "icon": {"emoji": "🦞"},
    })
    page_id = page["id"]

    # Build and upload blocks
    all_blocks = build_all_blocks(state)
    append_blocks(page_id, all_blocks)

    url = f"https://www.notion.so/{page_id.replace('-', '')}"
    return page_id, url, len(all_blocks)


def reupload_to_notion(page_id, state):
    """Clear and re-upload blocks to existing page. Returns block count."""
    delete_all_blocks(page_id)
    time.sleep(0.5)
    all_blocks = build_all_blocks(state)
    append_blocks(page_id, all_blocks)
    return len(all_blocks)


# ── CLI ─────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: notion_upload.py <state_file.json>")
        sys.exit(1)

    state = json.load(open(sys.argv[1]))
    page_id, url, n_blocks = upload_to_notion(state)
    print(f"Created page: {page_id}")
    print(f"✅ Uploaded {n_blocks} blocks")
    print(url)


if __name__ == "__main__":
    main()
