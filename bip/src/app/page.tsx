"use client";

import { useEffect } from "react";
import { RPGDialogue } from "@/components/home/rpg-dialogue";
import { OrgChart } from "@/components/home/org-chart";
import { ProjectBoard } from "@/components/home/project-board";
import { LiveMetrics } from "@/components/home/live-metrics";
import { HowWeWork } from "@/components/home/how-we-work";
import { BlogBoard } from "@/components/home/blog-board";
import { Footer } from "@/components/ui/footer";
import { track } from "@/lib/logging";

export default function HomePage() {
  useEffect(() => {
    track("view_home");
  }, []);

  return (
    <main className="min-h-screen bg-background pb-20">
      {/* 1. Hero */}
      <section className="pt-24 pb-12 text-center px-4">
        <h1 className="text-3xl md:text-4xl font-bold leading-tight mb-5 tracking-tight">
          <span className="text-text-primary">바이브 코딩,</span><br/>
          <span className="text-primary">전 과정 실시간 공개.</span>
        </h1>
        <p className="text-sm text-text-secondary max-w-xs mx-auto leading-relaxed">
          기획부터 삽질까지, <span className="text-text-primary font-semibold">아무것도 숨기지 않아요.</span><br/>
          AI와 나누는 모든 대화가 여기에 있습니다.
        </p>
        <div className="flex flex-wrap justify-center gap-2 mt-6">
          {["#BuildInPublic", "#OpenClaw", "#VibeCoding"].map((tag) => (
            <span key={tag} className="text-[11px] font-mono text-text-muted bg-white/80 border border-border px-2 py-0.5 rounded-full">
              {tag}
            </span>
          ))}
        </div>
      </section>

      {/* 2. 지금 뭐하고 있는지 — 실시간 대화 (현재 작업 상태 포함) */}
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

      <Footer />
    </main>
  );
}
