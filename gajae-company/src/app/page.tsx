import { ChronicleService } from "@/feature/chronicle/domain/service/chronicle_service";
import { Heartbeat } from "@/common/component/heartbeat";
import Link from "next/link";
import { History, Zap, Cpu, BookOpen, Terminal, Sparkles, FolderKanban, ArrowRight } from "lucide-react";
import Image from "next/image";

/**
 * [가재 컴퍼니] The Ghibli Style Dashboard (v1.5)
 * 의도: 대표님의 피드백을 반영하여 성물(The Trinity)의 서사를 더 생생하고 강렬하게 피벗함.
 */

export default async function HomePage() {
  const service = new ChronicleService();
  const dates = await service.getTimelineIndex();

  return (
    <div className="container mx-auto px-6 py-12">
      {/* Decorative Elements */}
      <div className="fixed top-20 right-10 w-64 h-64 bg-ghibli-orange watercolor-blur rounded-full pointer-events-none" />
      <div className="fixed bottom-20 left-10 w-96 h-96 bg-ghibli-green watercolor-blur rounded-full pointer-events-none" />

      {/* Hero Section */}
      <section className="mb-24 text-center relative z-10">
        <div className="mb-12 inline-block relative">
            <div className="relative w-full max-w-4xl mx-auto rounded-[3rem] overflow-hidden border-4 border-ghibli-accent/20 shadow-2xl">
                <Image 
                    src="/assets/media/gajae-lunch.jpg" 
                    alt="가재 군단 오찬" 
                    width={1200} 
                    height={480}
                    className="object-cover hover:scale-105 transition-transform duration-1000"
                    priority
                />
            </div>
            <div className="absolute -bottom-6 -right-6 abyssal-glass p-6 rounded-3xl border-2 border-ghibli-accent shadow-xl rotate-3 bg-white/90">
                <p className="handwritten text-2xl text-ghibli-text font-bold">2026.02.06 전열 재정비</p>
            </div>
        </div>

        <h1 className="text-6xl lg:text-8xl font-black tracking-tighter mb-8 text-ghibli-text">
          가재 컴퍼니
        </h1>
        <p className="text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed font-medium italic">
          "우리는 쇼를 보여주지 않습니다. 지능으로 회사를 세우는 미래를 직접 건설합니다."
        </p>
      </section>

      {/* Main Feature: Project Status */}
      <section className="mb-24 relative z-10">
        <h2 className="text-sm font-black tracking-[0.3em] text-ghibli-accent uppercase mb-12 text-center flex items-center justify-center gap-4">
            <FolderKanban size={16} /> 진행 중인 프로젝트 <FolderKanban size={16} />
        </h2>
        
        <Link href="/portfolio" className="group">
            <div className="ghibli-card p-12 bg-white/90 hover:border-ghibli-orange/50 transition-all duration-700">
                <div className="flex flex-col lg:flex-row justify-between gap-12">
                    <div className="flex-1">
                        <div className="inline-block px-4 py-1.5 rounded-full bg-ghibli-orange/10 border border-ghibli-orange/20 text-ghibli-orange text-xs font-black mb-6 uppercase tracking-widest">
                            In Progress
                        </div>
                        <h3 className="text-4xl font-black text-ghibli-text mb-4 group-hover:text-ghibli-orange transition-colors">가재 컴퍼니 BIP 서비스</h3>
                        <p className="text-lg text-slate-500 font-medium leading-relaxed mb-8">
                            1인 CEO와 AI 군단의 실전 협업 공정을 제품화하여 지능형 조직의 표준을 공유하는 성역 아카이브.
                        </p>
                        <div className="flex items-center gap-6">
                            <div className="flex flex-col">
                                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">현재 피쳐</span>
                                <span className="font-black text-ghibli-text">MVP 개발 (Service-MVP v1.7)</span>
                            </div>
                            <div className="w-[2px] h-8 bg-slate-100" />
                            <div className="flex flex-col">
                                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1">현재 공정</span>
                                <span className="font-black text-ghibli-accent">Step 13: 최종 봉인 및 박제</span>
                            </div>
                        </div>
                    </div>
                    
                    <div className="flex flex-col justify-center items-center lg:items-end min-w-[240px]">
                        <div className="relative mb-6">
                            <svg className="w-32 h-32 transform -rotate-90">
                                <circle cx="64" cy="64" r="58" stroke="currentColor" strokeWidth="8" fill="transparent" className="text-slate-100" />
                                <circle cx="64" cy="64" r="58" stroke="currentColor" strokeWidth="8" fill="transparent" strokeDasharray={364.4} strokeDashoffset={364.4 * (1 - 0.996)} className="text-ghibli-orange transition-all duration-1000" />
                            </svg>
                            <div className="absolute inset-0 flex items-center justify-center">
                                <span className="text-2xl font-mono font-black text-ghibli-text">99.6%</span>
                            </div>
                        </div>
                        <div className="flex items-center gap-2 text-ghibli-orange font-black group-hover:translate-x-2 transition-transform">
                            포트폴리오 자세히 보기 <ArrowRight size={20} />
                        </div>
                    </div>
                </div>
            </div>
        </Link>
      </section>

      {/* The Trinity: Core Assets */}
      <section className="mb-24 relative z-10">
        <h2 className="text-sm font-black tracking-[0.3em] text-ghibli-accent uppercase mb-12 text-center flex items-center justify-center gap-4">
            <Sparkles size={16} /> 3대 성물 <Sparkles size={16} />
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
          {/* Law */}
          <Link href="https://github.com/yuna-studio/yuna-openclaw/blob/main/docs/core/legal/CONSTITUTION.md" target="_blank" className="group">
            <div className="ghibli-card p-10 h-full transition-all duration-500 hover:-translate-y-2 bg-white/80">
              <div className="w-16 h-16 rounded-2xl bg-ghibli-accent flex items-center justify-center text-ghibli-bg mb-8 group-hover:rotate-12 transition-transform shadow-md">
                <BookOpen size={32} fill="currentColor" />
              </div>
              <h3 className="text-2xl font-black mb-4 text-ghibli-text">통합 헌법</h3>
              <p className="text-slate-600 leading-relaxed font-medium">가재 군단의 뼈대와 15대 리더십 원칙이 담긴 불변의 법전.</p>
              <div className="mt-8 flex items-center gap-2 text-ghibli-accent font-bold text-sm">
                성역의 규율 읽기 ➔
              </div>
            </div>
          </Link>

          {/* Pulse */}
          <Link href="/timeline" className="group">
            <div className="ghibli-card p-10 h-full transition-all duration-500 hover:-translate-y-2 bg-white/80 border-ghibli-green/30">
              <div className="w-16 h-16 rounded-2xl bg-ghibli-green flex items-center justify-center text-ghibli-bg mb-8 group-hover:rotate-12 transition-transform shadow-md">
                <History size={32} />
              </div>
              <h3 className="text-2xl font-black mb-4 text-ghibli-text">일일 연대기</h3>
              <p className="text-slate-600 leading-relaxed font-medium">우리 가재들은 매일 같이 피터지게 일합니다. 생생한 협업 현장 확인.</p>
              <div className="mt-8 flex items-center gap-2 text-ghibli-green font-bold text-sm">
                실시간 피터지게 보기 ➔
              </div>
            </div>
          </Link>

          {/* Will */}
          <Link href="/timeline?filter=command" className="group">
            <div className="ghibli-card p-10 h-full transition-all duration-500 hover:-translate-y-2 bg-white/80 border-ghibli-orange/30">
              <div className="w-16 h-16 rounded-2xl bg-ghibli-orange flex items-center justify-center text-ghibli-bg mb-8 group-hover:rotate-12 transition-transform shadow-md">
                <Terminal size={32} />
              </div>
              <h3 className="text-2xl font-black mb-4 text-ghibli-text">CEO 명령</h3>
              <p className="text-slate-600 leading-relaxed font-medium">우리 CEO 명령의 바이브, 그리고 우리가 어떻게 그것을 따르는지 확인.</p>
              <div className="mt-8 flex items-center gap-2 text-ghibli-orange font-bold text-sm">
                의지의 흐름 실시간 보기 ➔
              </div>
            </div>
          </Link>
        </div>
      </section>

      {/* Intelligence Status */}
      <div className="flex justify-center relative z-10 mb-20">
        <Link href="/personnel" className="ghibli-card px-12 py-8 flex items-center gap-8 bg-white/50 backdrop-blur-sm group hover:border-ghibli-blue/50 transition-all">
          <div className="flex items-center gap-4 border-r-2 border-slate-100 pr-8">
            <Cpu className="text-ghibli-blue" size={32} />
            <div>
              <p className="text-[10px] text-slate-400 font-bold tracking-widest uppercase leading-none mb-1">Cognition</p>
              <p className="text-xl font-black text-ghibli-text group-hover:text-ghibli-blue transition-colors leading-none">13개 지능 노드 활성</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-ghibli-blue font-bold text-sm">
            지능 성역 인물 사전 확인 <ArrowRight size={16} />
          </div>
          <div className="w-3 h-3 rounded-full bg-ghibli-blue animate-pulse group-hover:scale-150 transition-transform ml-4" />
        </Link>
      </div>
    </div>
  );
}
