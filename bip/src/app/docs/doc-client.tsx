"use client";

import { useEffect, useId, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { collection, getDocs, query, where, limit } from "firebase/firestore";
import { db } from "@/lib/firebase";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import mermaid from "mermaid";

function MermaidBlock({ code }: { code: string }) {
  const id = useId().replace(/:/g, "");

  useEffect(() => {
    mermaid.initialize({ startOnLoad: false, securityLevel: "strict" });
    const render = async () => {
      const el = document.getElementById(id);
      if (!el) return;
      try {
        const out = await mermaid.render(`m-${id}`, code);
        el.innerHTML = out.svg;
      } catch {
        el.textContent = "Mermaid 렌더 실패";
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

  return (
    <main className="min-h-screen bg-background text-text-primary">
      <div className="w-full max-w-3xl mx-auto px-4 py-10">
        <Link href="/" className="text-xs text-text-muted hover:text-primary">← 홈으로</Link>

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
