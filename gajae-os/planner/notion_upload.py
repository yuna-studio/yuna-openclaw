#!/usr/bin/env python3
"""Upload planner results to Notion."""
import json, os, sys, time, urllib.request

NOTION_KEY = open(os.path.expanduser("~/.config/notion/api_key")).read().strip()
HEADERS = {
    "Authorization": f"Bearer {NOTION_KEY}",
    "Notion-Version": "2025-09-03",
    "Content-Type": "application/json",
}
PARENT_PAGE = "ea6034d6-facc-494d-aee7-a1fa9cbec48f"  # 2026 Q1


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


def build_phase_blocks(phase_num, title, content, critique, score, revisions=0):
    blocks = []
    rev_text = f" (수정 {revisions}회)" if revisions else ""
    blocks.append({
        "type": "heading_1",
        "heading_1": {"rich_text": text(f"Phase {phase_num} — {title} ({score}/10){rev_text}")},
    })

    # Split content into paragraphs
    for para in content.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        if para.startswith("# "):
            continue  # skip top-level title
        if para.startswith("## "):
            blocks.append({"type": "heading_2", "heading_2": {"rich_text": text(para[3:])}})
        elif para.startswith("### "):
            blocks.append({"type": "heading_3", "heading_3": {"rich_text": text(para[4:])}})
        elif para.startswith("| "):
            # Table — convert to paragraph (Notion tables are complex)
            blocks.append({"type": "paragraph", "paragraph": {"rich_text": text(para[:2000])}})
        elif para.startswith("- ") or para.startswith("* "):
            for line in para.split("\n"):
                line = line.strip().lstrip("- ").lstrip("* ")
                if line:
                    blocks.append({"type": "bulleted_list_item", "bulleted_list_item": {"rich_text": text(line)}})
        elif para.startswith("1. ") or para.startswith("2. ") or para.startswith("3. "):
            for line in para.split("\n"):
                line = line.strip()
                if line and line[0].isdigit():
                    line = line.split(". ", 1)[-1]
                    blocks.append({"type": "numbered_list_item", "numbered_list_item": {"rich_text": text(line)}})
        elif para.startswith("> "):
            blocks.append({"type": "quote", "quote": {"rich_text": text(para[2:])}})
        elif para.startswith("```"):
            code = para.strip("`").strip()
            lang = ""
            if "\n" in code:
                first_line = code.split("\n")[0]
                if len(first_line) < 20 and " " not in first_line:
                    lang = first_line
                    code = code[len(first_line):].strip()
            blocks.append({"type": "code", "code": {"rich_text": text(code), "language": lang or "plain text"}})
        else:
            blocks.append({"type": "paragraph", "paragraph": {"rich_text": text(para)}})

    # Add judge critique as toggle
    blocks.append({
        "type": "callout",
        "callout": {
            "icon": {"emoji": "⚖️"},
            "rich_text": text(f"판사가재 평가: {score}/10\n\n{critique[:1900]}"),
        },
    })
    blocks.append({"type": "divider", "divider": {}})
    return blocks


PHASE_TITLES = {
    "1": "Background & Opportunity",
    "2": "Hypothesis Setting",
    "3": "Solution & MVP Spec",
    "4": "Success Metrics",
    "5": "GTM & Operations",
}


def main():
    if len(sys.argv) < 2:
        print("Usage: notion_upload.py <state_file.json>")
        sys.exit(1)

    state = json.load(open(sys.argv[1]))

    scores = state["phase_scores"]
    avg = sum(scores.values()) / len(scores)
    total_revisions = sum(state.get("phase_revisions", {}).values())

    # Create page
    page = api("POST", "pages", {
        "parent": {"page_id": PARENT_PAGE},
        "properties": {
            "title": {"title": text(f"🎬 바이브코딩 라이브스트림 Plan v2 (avg {avg:.1f}/10)")},
        },
        "icon": {"emoji": "🦞"},
    })
    page_id = page["id"]
    print(f"Created page: {page_id}")

    # Build all blocks
    all_blocks = []

    # Overview callout
    score_lines = []
    for p in ["1", "2", "3", "4", "5"]:
        rev = state.get("phase_revisions", {}).get(p, 0)
        rev_str = f" (수정 {rev}회)" if rev else ""
        star = " ⭐" if scores[p] >= 9.0 else ""
        score_lines.append(f"[{p}] {PHASE_TITLES[p]}: {scores[p]}/10{rev_str}{star}")

    overview = f"LangGraph Pipeline v2 — 평균 {avg:.1f}/10 | 총 수정 {total_revisions}회\n\n" + "\n".join(score_lines)
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
        phase_blocks = build_phase_blocks(
            p, PHASE_TITLES[p], content, critique, score, revisions
        )
        all_blocks.extend(phase_blocks)

        # Phase 3 이후: 다이어그램 섹션
        if p == "3" and state.get("diagrams"):
            diagrams = state["diagrams"]
            d_score = state.get("diagram_score", 0)
            d_rev = state.get("diagram_revisions", 0)
            d_critique = state.get("diagram_critique", "")

            all_blocks.append({
                "type": "heading_1",
                "heading_1": {"rich_text": text(f"📊 UX Diagrams ({d_score}/10)")},
            })

            for name, mermaid_code in diagrams.items():
                if name == "raw":
                    all_blocks.append({"type": "paragraph", "paragraph": {"rich_text": text(mermaid_code[:2000])}})
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

            # 다이어그램 판사 평가
            if d_critique:
                all_blocks.append({
                    "type": "callout",
                    "callout": {
                        "icon": {"emoji": "⚖️"},
                        "rich_text": text(f"판사가재 다이어그램 검증: {d_score}/10 (수정 {d_rev}회)\n\n{d_critique[:1900]}"),
                    },
                })
            all_blocks.append({"type": "divider", "divider": {}})

    # Upload
    append_blocks(page_id, all_blocks)
    print(f"✅ Uploaded {len(all_blocks)} blocks")
    print(f"https://www.notion.so/{page_id.replace('-', '')}")


if __name__ == "__main__":
    main()
