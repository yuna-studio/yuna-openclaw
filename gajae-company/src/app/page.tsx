import { ChronicleService } from "@/feature/chronicle/domain/service/chronicle_service";
import { LiveActivityStream } from "@/feature/chronicle/presentation/component/live_activity_stream";
import Link from "next/link";
import { History, Zap, Cpu, BookOpen, Terminal, Sparkles, FolderKanban, ArrowRight } from "lucide-react";
import Image from "next/image";

/**
 * [가재 컴퍼니] The Ghibli Style Dashboard (v2.0)
 * 의도: 대표님의 지시에 따라 슬로건을 더 센스 있게 교체하고, Firestore 기반의 활동 중계 시스템을 최상단에 배치함.
 */

export default async function HomePage() {
  return (
    <div className="container mx-auto px-6 py-12">
      {/* Decorative Elements */}
      <div className="fixed top-20 right-10 w-64 h-64 bg-ghibli-orange watercolor-blur rounded-full pointer-events-none opacity-10" />
      <div className="fixed bottom-20 left-10 w-96 h-96 bg-ghibli-green watercolor-blur rounded-full pointer-events-none opacity-10" />

      {/* Hero Section */}
      <section className="mb-16 text-center relative z-10 flex flex-col items-center">
        <div className="mb-10 relative group">
            <div className="w-40 h-40 rounded-full overflow-hidden border-8 border-white shadow-2xl transition-transform duration-1000 group-hover:rotate-[360deg]">
                <Image 
                    src="/assets/media/gajae-cute-chef.jpg" 
                    alt="가재 컴퍼니 마스코트" 
                    width={160} 
                    height={160}
                    className="object-cover w-full h-full scale-110"
                    priority
                />
            </div>
            <div className="absolute -bottom-1 -right-1 bg-ghibli-accent text-white px-3 py-1 rounded-full text-[10px] font-black shadow-lg uppercase tracking-tighter">
                Gajae Master
            </div>
        </div>

        <h1 className="text-6xl lg:text-9xl font-black tracking-tighter mb-8 text-ghibli-text">
          가재 컴퍼니
        </h1>
        
        <div className="max-w-3xl mx-auto space-y-6">
            <p className="text-2xl lg:text-3xl text-slate-700 leading-tight font-black">
                쇼는 끝났습니다. <br className="lg:hidden" />
                지능으로 성역을 일궈내는 <br className="lg:hidden" />
                <span className="text-ghibli-accent">진짜 공정</span>을 목격하십시오.
            </p>
            <p className="text-lg text-slate-400 font-medium italic">
                "낭만코딩 CEO와 13인의 지능 군단이 펼치는 피터지는 공개 개발(Build In Public)의 기록."
            </p>
        </div>
      </section>

      {/* NEW: Live Activity Feed (Firestore Sync) */}
      <section className="mb-24 relative z-10">
        <LiveActivityStream />
      </section>

      {/* The Trinity: Core Assets */}
      <section className="mb-32 relative z-10">
        <h2 className="text-sm font-black tracking-[0.4em] text-ghibli-accent uppercase mb-16 text-center flex items-center justify-center gap-4">
            <Sparkles size={16} /> 가재 컴퍼니 3대 성물 <Sparkles size={16} />
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
          {/* Law */}
          <Link href="https://github.com/yuna-studio/yuna-openclaw/blob/main/docs/core/legal/CONSTITUTION.md" target="_blank" className="group">
            <div className="ghibli-card p-12 h-full transition-all duration-500 hover:-translate-y-2 bg-white/80 shadow-ghibli border-2 border-ghibli-accent/5 hover:border-ghibli-accent/30 flex flex-col justify-between">
              <div>
                <div className="w-14 h-14 rounded-2xl bg-ghibli-accent flex items-center justify-center text-ghibli-bg mb-8 group-hover:rotate-12 transition-transform shadow-md">
                    <BookOpen size={28} fill="currentColor" />
                </div>
                <h3 className="text-2xl font-black mb-4 text-ghibli-text italic uppercase tracking-tighter">The Law <br/><span className="text-slate-300 not-italic font-bold text-lg">가재 헌법</span></h3>
                <p className="text-slate-500 leading-relaxed font-medium text-sm">1px의 오차도 허용하지 않는 군단의 규칙. 15대 원칙으로 성역의 무결성을 정의합니다.</p>
              </div>
              <div className="mt-12 flex items-center gap-2 text-ghibli-accent font-black text-xs uppercase tracking-widest group-hover:gap-4 transition-all">
                불변의 법령 확인 <ArrowRight size={14} />
              </div>
            </div>
          </Link>

          {/* Pulse */}
          <Link href="/timeline" className="group">
            <div className="ghibli-card p-12 h-full transition-all duration-500 hover:-translate-y-2 bg-white/80 border-2 border-ghibli-green/5 hover:border-ghibli-green/30 shadow-ghibli flex flex-col justify-between">
              <div>
                <div className="w-14 h-14 rounded-2xl bg-ghibli-green flex items-center justify-center text-ghibli-bg mb-8 group-hover:rotate-12 transition-transform shadow-md">
                    <History size={28} />
                </div>
                <h3 className="text-2xl font-black mb-4 text-ghibli-text italic uppercase tracking-tighter">The Pulse <br/><span className="text-slate-300 not-italic font-bold text-lg">격돌의 연대기</span></h3>
                <p className="text-slate-500 leading-relaxed font-medium text-sm">기획안이 아닙니다. 13개 지능 노드가 피터지게 부딪히며 만들어낸 실전 협업의 로우 데이터를 박제합니다.</p>
              </div>
              <div className="mt-12 flex items-center gap-2 text-ghibli-green font-black text-xs uppercase tracking-widest group-hover:gap-4 transition-all">
                박제된 지능 목격 <ArrowRight size={14} />
              </div>
            </div>
          </Link>

          {/* Will */}
          <Link href="/timeline?filter=command" className="group">
            <div className="ghibli-card p-12 h-full transition-all duration-500 hover:-translate-y-2 bg-white/80 border-2 border-ghibli-orange/5 hover:border-ghibli-orange/30 shadow-ghibli flex flex-col justify-between">
              <div>
                <div className="w-14 h-14 rounded-2xl bg-ghibli-orange flex items-center justify-center text-ghibli-bg mb-8 group-hover:rotate-12 transition-transform shadow-md">
                    <Terminal size={28} />
                </div>
                <h3 className="text-2xl font-black mb-4 text-ghibli-text italic uppercase tracking-tighter">The Will <br/><span className="text-slate-300 not-italic font-bold text-lg">대표님의 명령</span></h3>
                <p className="text-slate-500 leading-relaxed font-medium text-sm">지능은 자본이 된다. 대표님의 날카로운 의지가 어떻게 즉각적으로 시스템화되는지 그 바이브를 추적합니다.</p>
              </div>
              <div className="mt-12 flex items-center gap-2 text-ghibli-orange font-black text-xs uppercase tracking-widest group-hover:gap-4 transition-all">
                의지의 바이브 추적 <ArrowRight size={14} />
              </div>
            </div>
          </Link>
        </div>
      </section>

      {/* Simple Link to Personnel */}
      <div className="flex justify-center relative z-10 mb-20 border-t border-slate-100 pt-20">
        <Link href="/personnel" className="group flex flex-col items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-slate-50 border-2 border-slate-100 flex items-center justify-center text-slate-300 group-hover:border-ghibli-blue group-hover:text-ghibli-blue transition-all duration-500">
                <Cpu size={32} />
            </div>
            <span className="text-slate-400 group-hover:text-ghibli-blue font-black text-xs uppercase tracking-[0.3em] transition-colors">
                13인의 지능 노드 탐색 ➔
            </span>
        </Link>
      </div>
    </div>
  );
}
