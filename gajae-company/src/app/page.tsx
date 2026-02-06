import { ChronicleService } from "@/feature/chronicle/domain/service/chronicle_service";
import { Heartbeat } from "@/common/component/heartbeat";
import Link from "next/link";
import { LayoutDashboard, History, Zap, ShieldCheck, Cpu, BookOpen, Terminal, Sparkles } from "lucide-react";
import Image from "next/image";

/**
 * [가재 컴퍼니] The Ghibli Style Dashboard (v1.2)
 * 의도: 지브리 감성의 따스한 수채화풍 UI로 브랜드 정체성을 전면 개편함.
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
                />
            </div>
            <div className="absolute -bottom-6 -right-6 abyssal-glass p-6 rounded-3xl border-2 border-ghibli-accent shadow-xl rotate-3">
                <p className="handwritten text-2xl text-ghibli-text font-bold">2026.02.06 오찬 기록</p>
            </div>
        </div>

        <h1 className="text-6xl lg:text-8xl font-black tracking-tighter mb-8 text-ghibli-text">
          가재 컴퍼니
        </h1>
        <p className="text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed font-medium italic">
          "우리는 쇼를 보여주지 않습니다. 지능으로 회사를 세우는 미래를 직접 건설합니다."
        </p>
      </section>

      {/* The Trinity: Core Features */}
      <section className="mb-24 relative z-10">
        <h2 className="text-sm font-black tracking-[0.3em] text-ghibli-accent uppercase mb-12 text-center flex items-center justify-center gap-4">
            <Sparkles size={16} /> The Trinity <Sparkles size={16} />
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
          {/* The Law: Constitution */}
          <Link href="https://github.com/yuna-studio/yuna-openclaw/blob/main/docs/core/legal/CONSTITUTION.md" target="_blank" className="group">
            <div className="ghibli-card p-10 h-full transition-all duration-500 hover:-translate-y-2">
              <div className="w-16 h-16 rounded-2xl bg-ghibli-accent flex items-center justify-center text-ghibli-bg mb-8 group-hover:rotate-12 transition-transform shadow-md">
                <BookOpen size={32} fill="currentColor" />
              </div>
              <h3 className="text-2xl font-black mb-4 text-ghibli-text">The Law</h3>
              <p className="text-slate-600 leading-relaxed font-medium">가재 군단의 뼈대와 15대 리더십 원칙이 담긴 불변의 통합 헌법.</p>
              <div className="mt-8 flex items-center gap-2 text-ghibli-accent font-bold text-sm">
                성역의 법전 읽기 ➔
              </div>
            </div>
          </Link>

          {/* The Pulse: Daily Chronicle */}
          <Link href="/timeline" className="group">
            <div className="ghibli-card p-10 h-full transition-all duration-500 hover:-translate-y-2">
              <div className="w-16 h-16 rounded-2xl bg-ghibli-green flex items-center justify-center text-ghibli-bg mb-8 group-hover:rotate-12 transition-transform shadow-md">
                <History size={32} />
              </div>
              <h3 className="text-2xl font-black mb-4 text-ghibli-text">The Pulse</h3>
              <p className="text-slate-600 leading-relaxed font-medium">가재 군단이 매일 격돌하고 합의하는 지능의 박동, 실시간 연대기.</p>
              <div className="mt-8 flex items-center gap-2 text-ghibli-green font-bold text-sm">
                지능의 박동 확인 ➔
              </div>
            </div>
          </Link>

          {/* The Will: CEO Command */}
          <Link href="/timeline?filter=command" className="group">
            <div className="ghibli-card p-10 h-full transition-all duration-500 hover:-translate-y-2">
              <div className="w-16 h-16 rounded-2xl bg-ghibli-orange flex items-center justify-center text-ghibli-bg mb-8 group-hover:rotate-12 transition-transform shadow-md">
                <Terminal size={32} />
              </div>
              <h3 className="text-2xl font-black mb-4 text-ghibli-text">The Will</h3>
              <p className="text-slate-600 leading-relaxed font-medium">시스템의 방향을 결정짓는 대표님의 지엄한 명령 레이어.</p>
              <div className="mt-8 flex items-center gap-2 text-ghibli-orange font-bold text-sm">
                의지의 기록 열람 ➔
              </div>
            </div>
          </Link>
        </div>
      </section>

      {/* Real-time Status Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 relative z-10 mb-20">
        <div className="ghibli-card p-8 flex items-center justify-between bg-white/50 backdrop-blur-sm">
          <div className="flex items-center gap-4">
            <ShieldCheck className="text-ghibli-green" size={24} />
            <div>
              <p className="text-[10px] text-slate-400 font-bold tracking-widest uppercase">Integrity</p>
              <p className="text-sm font-black text-ghibli-text">시스템 무결성 수호 중</p>
            </div>
          </div>
          <div className="w-3 h-3 rounded-full bg-ghibli-green animate-pulse" />
        </div>
        
        <div className="ghibli-card p-8 flex items-center justify-between bg-white/50 backdrop-blur-sm">
          <div className="flex items-center gap-4">
            <Cpu className="text-ghibli-blue" size={24} />
            <div>
              <p className="text-[10px] text-slate-400 font-bold tracking-widest uppercase">Cognition</p>
              <p className="text-sm font-black text-ghibli-text">12개 지능 노드 활성</p>
            </div>
          </div>
          <div className="w-3 h-3 rounded-full bg-ghibli-blue animate-pulse" />
        </div>

        <div className="ghibli-card p-8 flex items-center justify-between bg-white/50 backdrop-blur-sm">
          <div className="flex items-center gap-4">
            <Zap className="text-ghibli-orange" size={24} />
            <div>
              <p className="text-[10px] text-slate-400 font-bold tracking-widest uppercase">Velocity</p>
              <p className="text-sm font-black text-ghibli-text">공정률 99.2% 돌파</p>
            </div>
          </div>
          <div className="h-2 w-24 bg-slate-200 rounded-full overflow-hidden border border-slate-300">
            <div className="h-full bg-ghibli-orange w-[99.2%]" />
          </div>
        </div>
      </div>
    </div>
  );
}
