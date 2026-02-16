"use client";

import { RPGDialogue } from "@/components/home/rpg-dialogue";
import { OrgChart } from "@/components/home/org-chart";
import { ProjectBoard } from "@/components/home/project-board";
import { LiveMetrics } from "@/components/home/live-metrics";
import { Twitter } from "lucide-react";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-background pb-20">
      {/* 1. Hero Section & Identity */}
      <section className="pt-20 pb-10 text-center px-4">
        <div className="mb-4 inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white border border-border shadow-sm">
          <span className="w-2 h-2 rounded-full bg-status-live animate-pulse" />
          <span className="text-xs font-bold text-text-secondary">AI와 함께 짓는 1인 개발의 낭만</span>
        </div>
        <h1 className="text-4xl md:text-5xl font-bold text-text-primary mb-4 leading-tight tracking-tight">
          Vibe Coding <br/>
          <span className="text-primary">Live Showcase</span>
        </h1>
        <p className="text-text-secondary max-w-md mx-auto leading-relaxed">
          안녕하세요, <strong className="text-text-primary">가재컴퍼니</strong>입니다. <br/>
          비서, 탐정, 판사가재와 함께하는 우당탕탕 개발 일지를 실시간으로 공개합니다.
        </p>
        
        {/* Twitter Link */}
        <a 
          href="https://x.com/romantic_coding" 
          target="_blank" 
          rel="noreferrer"
          className="inline-flex items-center gap-2 mt-6 text-xs text-text-muted hover:text-secondary transition-colors"
        >
          <Twitter size={14} />
          @romantic_coding 팔로우하고 소식 받기
        </a>
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
      <footer className="text-center py-10 text-xs text-text-muted">
        © 2026 Gajae Company. All rights reserved. <br/>
        Designed by Sanbaram Studio.
      </footer>
    </main>
  );
}
