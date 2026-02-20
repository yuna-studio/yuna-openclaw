"use client";

import { useEffect } from "react";
import { RPGDialogue } from "@/components/home/rpg-dialogue";
import { OrgChart } from "@/components/home/org-chart";
import { ProjectBoard } from "@/components/home/project-board";
import { LiveMetrics } from "@/components/home/live-metrics";
import { HowWeWork } from "@/components/home/how-we-work";
import { BlogBoard } from "@/components/home/blog-board";
import { track } from "@/lib/logging";

export default function HomePage() {
  useEffect(() => {
    track("view_home");
  }, []);

  return (
    <main className="min-h-screen bg-background pb-20">
      {/* 1. Hero */}
      <section className="pt-24 pb-12 text-center px-4">
        <a
          href="https://x.com/romantic_coding"
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1.5 text-xs text-text-muted hover:text-primary transition-colors mb-5 tracking-wider"
        >
          <svg viewBox="0 0 24 24" className="w-3 h-3 fill-current"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
          낭만코딩 · 가재 컴퍼니
        </a>
        <h1 className="text-3xl md:text-4xl font-bold leading-tight mb-5 tracking-tight">
          <span className="text-text-primary">바이브 코딩,</span><br/>
          <span className="text-primary">만드는 전 과정을 기록합니다.</span>
        </h1>
        <p className="text-sm text-text-secondary max-w-xs mx-auto leading-relaxed">
          아이디어부터 배포 후 개선까지,<br/>
          <span className="text-text-primary font-semibold">의사결정과 시행착오를 투명하게 남깁니다.</span>
        </p>
        <div className="flex flex-wrap justify-center gap-2 mt-6">
          {["#BuildInPublic", "#OpenClaw", "#VibeCoding"].map((tag) => (
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

      {/* 7. 블로그 */}
      <BlogBoard />

      {/* 8. GEO/SEO 요약 + FAQ */}
      <section className="w-full max-w-2xl mx-auto px-4 py-10">
        <div className="bg-white border border-border rounded-xl p-5 space-y-4">
          <h2 className="text-lg font-bold">낭만코딩은 어떤 사이트인가요?</h2>
          <p className="text-sm text-text-secondary leading-relaxed">
            낭만코딩은 바이브코딩 기반의 Build in Public 아카이브입니다. 
            기획부터 개발, 배포, 운영, 개선까지의 의사결정 로그를 문서/라이브/블로그로 공개합니다.
          </p>

          <div className="space-y-3">
            <h3 className="text-base font-semibold">자주 묻는 질문 (FAQ)</h3>
            <div>
              <p className="text-sm font-semibold">Q1. 바이브코딩 실전 사례를 어디서 볼 수 있나요?</p>
              <p className="text-sm text-text-secondary">A. 홈의 프로젝트 보드, /docs 개발문서, /live 실시간 로그에서 확인할 수 있습니다.</p>
            </div>
            <div>
              <p className="text-sm font-semibold">Q2. SEO/GEO 오가닉 유입 관련 기록도 있나요?</p>
              <p className="text-sm text-text-secondary">A. 블로그와 개발문서에서 오가닉 성장 실험, 구조화 데이터, 내부링크 전략을 순차적으로 공개합니다.</p>
            </div>
            <div>
              <p className="text-sm font-semibold">Q3. 어떤 개발 과정을 공개하나요?</p>
              <p className="text-sm text-text-secondary">A. 문제정의, 기능설계, 구현, 실패 원인, 지표 개선까지 전 과정을 기록합니다.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="w-full max-w-2xl mx-auto px-4 py-12 border-t border-dashed border-border text-center space-y-3">
        <a
          href="https://x.com/romantic_coding"
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-1.5 text-sm font-bold text-text-primary hover:text-primary transition-colors"
        >
          <svg viewBox="0 0 24 24" className="w-4 h-4 fill-current"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
          낭만코딩
        </a>
        <div className="flex items-center justify-center gap-3 text-[10px] text-text-muted/60">
          <a
            href="https://github.com/yuna-studio/yuna-openclaw"
            target="_blank"
            rel="noreferrer"
            className="hover:text-primary transition-colors inline-flex items-center gap-1"
          >
            <svg viewBox="0 0 24 24" className="w-3 h-3 fill-current"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
            소스코드 공개
          </a>
          <span>·</span>
          <span>Built with OpenClaw</span>
          <span>·</span>
          <span>© 2026 Yuna Studio</span>
        </div>
      </footer>
    </main>
  );
}
