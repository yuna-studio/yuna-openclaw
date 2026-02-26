"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { collection, getDocs, query, where, limit } from "firebase/firestore";
import { db } from "@/lib/firebase";
import { marked } from "marked";
import mermaid from "mermaid";
import { ChevronLeft } from "lucide-react";
import { TuningLoader } from "@/components/ui/tuning-loader";

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function normalizeMermaid(code: string): string {
  let src = String(code || "")
    .replace(/\u00A0/g, " ")
    .replace(/[\u200B-\u200D\uFEFF]/g, "")
    .replace(/\r\n/g, "\n")
    .trim();

  // 줄바꿈이 유실된 Mermaid(한 줄 압축) 복구
  if (!src.includes("\n")) {
    src = src
      .replace(/\s+%%\s+/g, "\n%% ")
      .replace(/\s+subgraph\s+/g, "\nsubgraph ")
      .replace(/\s+end\s+/g, "\nend\n")
      .replace(/\s+style\s+/g, "\nstyle ")
      .replace(/\s+classDef\s+/g, "\nclassDef ")
      .replace(/\s+class\s+/g, "\nclass ")
      .replace(/\s+click\s+/g, "\nclick ")
      .replace(/\s+(flowchart|graph|sequenceDiagram|classDiagram|stateDiagram|erDiagram|journey|gantt|pie|mindmap|timeline|gitGraph|quadrantChart|requirementDiagram|C4Context|C4Container|C4Component|C4Dynamic|C4Deployment)\b/g, "\n$1")
      .trim();
  }

  const startRe = /(flowchart|graph|sequenceDiagram|classDiagram|stateDiagram|erDiagram|journey|gantt|pie|mindmap|timeline|gitGraph|quadrantChart|requirementDiagram|C4Context|C4Container|C4Component|C4Dynamic|C4Deployment)\b/;
  const m = src.match(startRe);
  if (m && m.index && m.index > 0) src = src.slice(m.index).trim();

  // Notion 변환 중 잘리는 style fill:# 패턴 자동 보정
  src = src
    .replace(/fill:#(?=\s|$)/g, "fill:#f3f4f6")
    .replace(/stroke:#(?=\s|$)/g, "stroke:#334155")
    .replace(/color:#(?=\s|$)/g, "color:#334155");

  return src;
}

function compatibilityMermaid(src: string): string {
  return src
    .replace(/\p{Extended_Pictographic}/gu, "")
    .replace(/[\uFE0F\u20E3]/g, "");
}

function safeMermaid(src: string): string {
  return compatibilityMermaid(src)
    .split("\n")
    .filter((line) => {
      const t = line.trim();
      if (!t) return true;
      if (t.startsWith("%%")) return false;
      if (t.startsWith("style ")) return false;
      return true;
    })
    .join("\n");
}

function decodeHtml(s: string): string {
  return s
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'");
}

function renderMarkdown(markdown: string) {
  const mermaidBlocks: string[] = [];
  let html = String(marked.parse(String(markdown || ""), { gfm: true, breaks: true }));

  html = html
    .replace(/<pre><code class="language-mermaid">([\s\S]*?)<\/code><\/pre>/gi, (_, code) => {
      const idx = mermaidBlocks.push(normalizeMermaid(decodeHtml(code))) - 1;
      return `<div class="mermaid-slot" data-mermaid-index="${idx}"></div>`;
    })
    .replace(/<pre><code(?:\s+class="[^"]*")?>(?:mermaid\n)?([\s\S]*?)<\/code><\/pre>/gi, (full, code) => {
      const decoded = decodeHtml(String(code || ""));
      const looksLikeMermaid = /(flowchart|graph|sequenceDiagram|classDiagram|stateDiagram|erDiagram|journey|gantt|pie|mindmap|timeline|gitGraph|quadrantChart|requirementDiagram|C4Context|C4Container|C4Component|C4Dynamic|C4Deployment)\b/m.test(decoded);
      if (!looksLikeMermaid) return full;
      const idx = mermaidBlocks.push(normalizeMermaid(decoded)) - 1;
      return `<div class="mermaid-slot" data-mermaid-index="${idx}"></div>`;
    })
    .replace(/<table>/g, '<div class="table-wrap"><table>')
    .replace(/<\/table>/g, "</table></div>");

  return { html, mermaidBlocks };
}

export default function DocClient() {
  const searchParams = useSearchParams();
  const projectId = useMemo(() => String(searchParams.get("projectId") || ""), [searchParams]);
  const slug = useMemo(() => String(searchParams.get("slug") || ""), [searchParams]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [title, setTitle] = useState("");
  const [summary, setSummary] = useState("");
  const [createdDate, setCreatedDate] = useState("");
  const [content, setContent] = useState("");
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!db || !projectId || !slug) {
      setError("잘못된 문서 주소입니다.");
      setLoading(false);
      return;
    }
    (async () => {
      try {
        const q = query(
          collection(db, "projects", projectId, "docs"),
          where("slug", "==", slug),
          where("status", "==", "published"),
          limit(1)
        );
        const snap = await getDocs(q);
        if (snap.empty) {
          setError("문서를 찾을 수 없어요.");
          return;
        }
        const d = snap.docs[0].data() as any;
        setTitle(d.title || "문서");
        setSummary(d.summary || "");
        const maybeDate = d.displayDate || (d.createdAt?.toDate ? d.createdAt.toDate().toISOString().slice(0, 10) : "");
        setCreatedDate(maybeDate || "");
        setContent(d.contentMd || "");
      } catch (e: any) {
        setError(e?.message || "문서 로드 실패");
      } finally {
        setLoading(false);
      }
    })();
  }, [projectId, slug]);

  const rendered = useMemo(() => renderMarkdown(content), [content]);

  useEffect(() => {
    const root = contentRef.current;
    if (!root) return;

    mermaid.initialize({ startOnLoad: false, securityLevel: "strict", theme: "default" });
    const nodes = Array.from(root.querySelectorAll<HTMLElement>(".mermaid-slot"));

    nodes.forEach(async (node) => {
      const idx = Number(node.dataset.mermaidIndex || "-1");
      const src = rendered.mermaidBlocks[idx] || "";
      if (!src) return;
      try {
        const out = await mermaid.render(`m-${idx}-${Date.now()}`, src);
        node.innerHTML = out.svg;
      } catch {
        try {
          const fallback = compatibilityMermaid(src);
          const out = await mermaid.render(`m-${idx}-${Date.now()}-compat`, fallback);
          node.innerHTML = out.svg;
        } catch {
          try {
            const safe = safeMermaid(src);
            const out = await mermaid.render(`m-${idx}-${Date.now()}-safe`, safe);
            node.innerHTML = out.svg;
          } catch {
            node.innerHTML = `<pre><code>${escapeHtml(src)}</code></pre>`;
          }
        }
      }
    });
  }, [rendered]);

  return (
    <main className="min-h-screen bg-background text-text-primary">
      <header className="h-14 sticky top-0 z-40 flex items-center px-4 backdrop-blur-md bg-white/80 border-b border-gray-200">
        <Link href="/" className="p-2 -ml-2 text-text-secondary hover:text-text-primary transition-colors flex items-center gap-1 group w-20">
          <ChevronLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
          <span className="text-sm font-medium">홈</span>
        </Link>
        <span className="flex-1 text-center font-bold text-sm tracking-wide text-text-primary">개발문서</span>
        <div className="w-20" />
      </header>

      <div className="w-full max-w-3xl mx-auto px-4 py-8">
        {loading ? <TuningLoader className="py-20" /> : null}
        {error ? <div className="mt-6 text-red-600">{error}</div> : null}

        {!loading && !error ? (
          <article className="mt-6 bg-white border border-border rounded-xl p-6">
            <h1 className="text-2xl font-bold mb-2">{title}</h1>
            {summary ? <p className="text-sm text-text-muted mb-2">{summary}</p> : null}
            {createdDate ? <p className="text-xs text-text-muted mb-6">작성일: {createdDate}</p> : null}

            <div ref={contentRef} className="doc-content prose prose-sm max-w-none" dangerouslySetInnerHTML={{ __html: rendered.html }} />
          </article>
        ) : null}
      </div>
    </main>
  );
}
