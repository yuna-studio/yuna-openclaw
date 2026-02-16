"use client";

import { RPGDialogue } from "@/components/home/rpg-dialogue";
import { OrgChart } from "@/components/home/org-chart";
import { ProjectBoard } from "@/components/home/project-board";
import { LiveMetrics } from "@/components/home/live-metrics";
import { HowWeWork } from "@/components/home/how-we-work";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background pb-20">
      {/* 1. Hero */}
      <section className="pt-24 pb-12 text-center px-4">
        <p className="text-sm text-text-muted mb-6">가재 컴퍼니 — 바이브코딩 쇼 케이스</p>
        <h1 className="text-2xl md:text-3xl font-bold text-text-primary leading-snug mb-3">
          코딩하는 모든 순간을<br/>
          <span className="text-text-muted/50">숨기지 않기로 했어요.</span>
        </h1>
        <p className="text-sm text-text-muted max-w-sm mx-auto leading-relaxed">
          기획, 설계, 개발, 삽질, 배포까지.<br/>
          가감 없이 <span className="text-primary font-bold">실시간</span>으로 공개합니다.
        </p>
        <div className="flex flex-wrap justify-center gap-2 mt-5">
          {["#BuildInPublic", "#개발과정전체공개", "#VibeCoding"].map((tag) => (
            <span key={tag} className="text-[11px] font-mono text-text-muted bg-white/80 border border-border px-2 py-0.5 rounded-full">
              {tag}
            </span>
          ))}
        </div>
      </section>

      {/* 2. 지금 뭐하고 있는지 — 실시간 대화 */}
      <RPGDialogue />

      {/* 3. 얼마나 했는지 — 숫자 */}
      <LiveMetrics />

      {/* 4. 어떻게 돌아가는지 — 시스템 */}
      <HowWeWork />

      {/* 5. 누가 하는지 — 팀 소개 */}
      <OrgChart />

      {/* 6. 뭘 만들었는지 — 포트폴리오 */}
      <ProjectBoard />

      {/* Footer */}
      <footer className="w-full max-w-2xl mx-auto px-4 py-12 border-t border-dashed border-border text-center space-y-2">
        <a
          href="https://github.com/yuna-studio/yuna-openclaw"
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1.5 text-xs text-text-muted hover:text-primary transition-colors"
        >
          <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 fill-current"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>
          소스코드 전체 공개 — 마음껏 참고하세요
        </a>
        <p className="text-[10px] text-text-muted/60">
          Built with <a href="https://openclaw.ai" target="_blank" rel="noreferrer" className="hover:text-primary transition-colors">OpenClaw</a> · © 2026 Gajae Company
        </p>
      </footer>
    </main>
  );
}
