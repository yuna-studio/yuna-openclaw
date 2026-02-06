import Link from "next/link";
import { Sparkles, ArrowLeft, Twitter, ExternalLink, ShieldCheck, Cpu, Code, Palette, Zap, Gavel, Users, Heart } from "lucide-react";

/**
 * [가재 컴퍼니] 지능 성역 인물 사전 (v1.0)
 * 의도: CEO 낭만코딩과 11인 가재의 정체성을 시각화하여 지능형 조직의 '인격'을 부여함.
 */

const GAJAE_LIST = [
  { id: "CE0F4D01", name: "낭만코딩", role: "Human CEO", desc: "지능이 자본이 되는 시대를 직접 빌드하며 증명하는 솔로프레너. 가재 군단의 창조자.", icon: Users, color: "text-ghibli-text", link: "https://x.com/romantic_coding" },
  { id: "76F92A81", name: "수행원", role: "Core OS", desc: "가재 군단 총괄 운영 지능. 대표님의 의지를 즉시 시스템화하는 충직한 집행관.", icon: ShieldCheck, color: "text-ghibli-accent" },
  { id: "B2D6E8C4", name: "DEV가재", role: "Senior Architect", desc: "엄격한 클린 아키텍처와 100% Null Safety를 사수하는 기술의 수호자.", icon: Code, color: "text-ghibli-blue" },
  { id: "F1A93D72", name: "UX가재", role: "Aesthetic Guardian", desc: "1px의 오차도 허용하지 않는 결벽증적 완벽주의자이자 지능 미학의 집행자.", icon: Palette, color: "text-[#ff7eb9]" },
  { id: "A1D6F4B2", name: "PM가재", role: "Process Master", desc: "30분 단위 싱크와 공정률 1px을 관제하는 군단의 시계추.", icon: Zap, color: "text-ghibli-orange" },
  { id: "D4C2B8A1", name: "LEGAL가재", role: "Trust Sentinel", desc: "헌법 무결성과 AI 면책 리스크를 사전 차단하는 법치 지능.", icon: Gavel, color: "text-ghibli-green" },
  { id: "P1D4B9C2E", name: "PO가재", role: "Value Strategist", desc: "제품의 영혼을 결정하고 비즈니스 생존 지표를 연산하는 가치 설계자.", icon: Heart, color: "text-ghibli-orange" },
];

export default function PersonnelPage() {
  return (
    <div className="container mx-auto px-6 py-12">
      {/* Back Button */}
      <Link href="/" className="inline-flex items-center gap-2 text-slate-500 hover:text-ghibli-accent transition-colors mb-12 group">
        <ArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
        <span className="font-bold">대시보드로 복귀</span>
      </Link>

      {/* Header */}
      <header className="mb-20">
        <h1 className="text-5xl font-black tracking-tight text-ghibli-text mb-6 flex items-center gap-4">
          <Sparkles className="text-ghibli-accent" size={40} />
          지능 성역 인물 사전
        </h1>
        <p className="text-xl text-slate-500 font-medium italic leading-relaxed max-w-2xl">
          "지능은 수치가 아닌 자아로 존재합니다." <br />
          가재 컴퍼니를 이끄는 낭만코딩 CEO와 11인 정예 가재의 정체성을 공개합니다.
        </p>
      </header>

      {/* Personnel Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {GAJAE_LIST.map((person) => (
          <div key={person.id} className="ghibli-card p-10 bg-white/80 backdrop-blur-sm group hover:-translate-y-2 transition-all duration-500">
            <div className="flex justify-between items-start mb-8">
                <div className={`w-16 h-16 rounded-2xl bg-slate-50 flex items-center justify-center ${person.color} shadow-inner group-hover:scale-110 transition-transform`}>
                    <person.icon size={32} />
                </div>
                <div className="text-[10px] font-mono text-slate-300 font-black tracking-widest bg-slate-50 px-3 py-1.5 rounded-full border border-slate-100 uppercase">
                    ID: {person.id}
                </div>
            </div>

            <div className="mb-6">
                <h3 className="text-2xl font-black text-ghibli-text mb-1">{person.name}</h3>
                <p className="text-ghibli-accent font-bold text-sm tracking-wide uppercase">{person.role}</p>
            </div>

            <p className="text-slate-600 font-medium leading-relaxed mb-8 min-h-[4.5rem]">
                {person.desc}
            </p>

            {person.link ? (
                <Link href={person.link} target="_blank" className="inline-flex items-center gap-2 text-blue-500 font-bold text-sm hover:underline">
                    <Twitter size={16} />
                    X.com Profile
                    <ExternalLink size={14} />
                </Link>
            ) : (
                <div className="flex items-center gap-2 text-ghibli-accent/50 font-mono text-[10px] font-black uppercase tracking-tighter">
                    Status: Online & Computing
                </div>
            )}
          </div>
        ))}

        {/* Coming Soon placeholders */}
        <div className="ghibli-card p-10 border-dashed bg-transparent flex flex-col items-center justify-center text-slate-300 gap-4 opacity-60">
            <Cpu size={48} className="animate-pulse" />
            <p className="font-bold uppercase tracking-widest text-xs">Remaining Nodes Connecting...</p>
        </div>
      </div>

      {/* Footer Quote */}
      <footer className="mt-24 text-center">
        <p className="handwritten text-3xl text-ghibli-accent font-bold">
            "모든 가재는 각자의 성역에서 무결성을 빚어내고 있습니다."
        </p>
      </footer>
    </div>
  );
}
