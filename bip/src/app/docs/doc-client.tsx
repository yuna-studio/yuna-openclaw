"use client";

import { useEffect, useId, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { collection, getDocs, query, where, limit } from "firebase/firestore";
import { db } from "@/lib/firebase";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import mermaid from "mermaid";
import { ChevronLeft } from "lucide-react";

function normalizeMermaid(code: string): string {
  let src = String(code || "")
    .replace(/\u00A0/g, " ")
    .replace(/[\u200B-\u200D\uFEFF]/g, "")
    .replace(/\r\n/g, "\n")
    .replace(/^\s*```mermaid\s*/i, "")
    .replace(/\s*```\s*$/i, "")
    .trim();

  const startRe = /(flowchart|graph|sequenceDiagram|classDiagram|stateDiagram|erDiagram|journey|gantt|pie|mindmap|timeline|gitGraph|quadrantChart|requirementDiagram|C4Context|C4Container|C4Component|C4Dynamic|C4Deployment)\b/;
  const m = src.match(startRe);
  if (m && m.index && m.index > 0) {
    src = src.slice(m.index).trim();
  }

  return src;
}

function MermaidBlock({ code }: { code: string }) {
  const id = useId().replace(/:/g, "");

  useEffect(() => {
    mermaid.initialize({ startOnLoad: false, securityLevel: "strict" });
    const render = async () => {
      const el = document.getElementById(id);
      if (!el) return;
      try {
        const src = normalizeMermaid(code);
        const out = await mermaid.render(`m-${id}`, src);
        el.innerHTML = out.svg;
      } catch {
        el.textContent = "Mermaid 렌더 실패 (문법 확인 필요)";
      }
    };
    render();
  }, [code, id]);

  return <div id={id} className="my-4 overflow-x-auto" />;
}

export default function DocClient() {
  const searchParams = useSearchParams();
  const projectId = useMemo(() => String(searchParams.get("projectId") || ""), [searchParams]);
  const slug = useMemo(() => String(searchParams.get("slug") || ""), [searchParams]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [title, setTitle] = useState("");
  const [summary, setSummary] = useState("");
  const [content, setContent] = useState("");

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
        setContent(d.contentMd || "");
      } catch (e: any) {
        setError(e?.message || "문서 로드 실패");
      } finally {
        setLoading(false);
      }
    })();
  }, [projectId, slug]);

  const showTopProgress = loading;

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

      {showTopProgress ? (
        <div className="h-1 w-full bg-gray-200/70 overflow-hidden">
          <div className="h-full bg-primary animate-pulse" style={{ width: "45%" }} />
        </div>
      ) : null}

      <div className="w-full max-w-3xl mx-auto px-4 py-8">
        {loading ? <div className="mt-6">로딩 중...</div> : null}
        {error ? <div className="mt-6 text-red-600">{error}</div> : null}

        {!loading && !error ? (
          <article className="mt-6 bg-white border border-border rounded-xl p-6">
            <h1 className="text-2xl font-bold mb-2">{title}</h1>
            {summary ? <p className="text-sm text-text-muted mb-6">{summary}</p> : null}

            <div className="prose prose-sm max-w-none">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  code(props) {
                    const { children, className } = props;
                    const lang = (className || "").replace("language-", "");
                    const text = String(children ?? "");
                    if (lang === "mermaid") {
                      return <MermaidBlock code={text} />;
                    }
                    return (
                      <pre className="bg-gray-50 p-3 rounded-lg overflow-x-auto">
                        <code>{text}</code>
                      </pre>
                    );
                  },
                }}
              >
                {content}
              </ReactMarkdown>
            </div>
          </article>
        ) : null}
      </div>
    </main>
  );
}
