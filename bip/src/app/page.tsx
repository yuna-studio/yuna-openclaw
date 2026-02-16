"use client";

import { RPGDialogue } from "@/components/home/rpg-dialogue";
import { OrgChart } from "@/components/home/org-chart";
import { ProjectBoard } from "@/components/home/project-board";
import { LiveMetrics } from "@/components/home/live-metrics";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background pb-20">
      {/* 1. Hero Section & Identity */}
      <section className="pt-20 pb-10 text-center px-4">
        <div className="mb-4 inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white border border-border shadow-sm">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span className="text-xs font-bold text-text-secondary">AI와 함께 짓는 1인 개발의 낭만</span>
        </div>
        <h1 className="text-4xl md:text-5xl font-bold text-text-primary mb-4 leading-tight tracking-tight">
          가재 컴퍼니<br/>
          <span className="text-primary">바이브코딩 쇼 케이스</span>
        </h1>
        <p className="text-text-secondary max-w-md mx-auto leading-relaxed">
          안녕하세요, <strong className="text-text-primary">가재 컴퍼니</strong>입니다. <br/>
          우당탕탕 바이브 코딩 일지를 <span className="text-primary font-bold">실시간</span>으로 공개합니다.
        </p>
        <div className="flex flex-wrap justify-center gap-2 mt-4">
          {["#BuildInPublic", "#개발과정전체공개", "#VibeCoding"].map((tag) => (
            <span key={tag} className="text-[11px] font-mono text-text-muted bg-white/80 border border-border px-2 py-0.5 rounded-full">
              {tag}
            </span>
          ))}
        </div>
      </section>

      {/* 2. RPG Dialogue Preview (Hook) */}
      <RPGDialogue />

      {/* 3. Live Metrics (Social Proof) */}
      <LiveMetrics />

      {/* 4. Company Org Chart (Lore) */}
      <OrgChart />

      {/* 5. Project Board (Portfolio) */}
      <ProjectBoard />
      
      {/* Simple Footer */}
      <footer className="text-center py-10 text-xs text-text-muted space-y-2">
        <a
          href="https://github.com/yuna-studio/yuna-openclaw"
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1.5 text-text-muted hover:text-primary transition-colors"
        >
          <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 fill-current"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>
          이 프로젝트는 오픈소스입니다
        </a>
        <p>© 2026 Gajae Company. Designed by Yuna Studio.</p>
      </footer>
    </main>
  );
}
