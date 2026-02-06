"use client";

import Link from "next/link";
import { 
  Sparkles, ArrowLeft, Twitter, ExternalLink, ShieldCheck, Cpu, Code, 
  Palette, Zap, Gavel, Users, Heart, Crown, BarChart3, ClipboardCheck, 
  Megaphone, UserCircle, Headset, Home 
} from "lucide-react";
import { motion } from "framer-motion";

/**
 * [가재 컴퍼니] 지능 성역 인물 사전 (v1.2)
 * 의도: CEO 낭만코딩과 12인 정예 가재의 정체성을 완벽히 박제함.
 */

const GAJAE_LIST = [
  { id: "CE0F4D01", name: "낭만코딩", role: "Human CEO", desc: "지능이 자본이 되는 시대를 직접 빌드하며 증명하는 솔로프레너. 가재 군단의 창조자.", icon: Crown, color: "text-ghibli-orange", link: "https://x.com/romantic_coding" },
  { id: "76F92A81", name: "수행원", role: "Core OS", desc: "가재 군단 총괄 운영 지능. 대표님의 의지를 즉시 시스템화하는 충직한 집행관.", icon: ShieldCheck, color: "text-ghibli-accent" },
  { id: "H1O2S3T4", name: "HOST가재", role: "Visionary Secretary", desc: "가재 컴퍼니 경영진 비서. 시스템 아키텍처 설계 및 사회적 오케스트레이션 전담.", icon: Home, color: "text-ghibli-blue" },
  { id: "B2D6E8C4", name: "DEV가재", role: "Senior Architect", desc: "엄격한 클린 아키텍처와 100% Null Safety를 사수하는 기술의 수호자.", icon: Code, color: "text-ghibli-blue" },
  { id: "F1A93D72", name: "UX가재", role: "Aesthetic Guardian", desc: "1px의 오차도 허용하지 않는 결벽증적 완벽주의자이자 지능 미학의 집행자.", icon: Palette, color: "text-[#ff7eb9]" },
  { id: "E3A7F510", name: "PM가재", role: "Process Master", desc: "30분 단위 싱크와 공정률 1px을 관제하는 군단의 정밀한 시계추.", icon: Zap, color: "text-ghibli-orange" },
  { id: "1D4B9C2E", name: "PO가재", role: "Value Strategist", desc: "제품의 영혼을 결정하고 비즈니스 생존 지표를 연산하는 가치 설계자.", icon: Heart, color: "text-ghibli-orange" },
  { id: "D4C2B8A1", name: "LEGAL가재", role: "Trust Sentinel", desc: "헌법 무결성과 AI 면책 리스크를 사전 차단하는 법치 지능.", icon: Gavel, color: "text-ghibli-green" },
  { id: "A9D2F7E1", name: "BA가재", role: "Business Analyst", desc: "데이터 이면의 맥락을 읽고 비즈니스 도약의 기회를 포착하는 분석가.", icon: BarChart3, color: "text-ghibli-accent" },
  { id: "C8B5E4D2", name: "QA가재", role: "Quality Guardian", desc: "시스템의 결함을 1px도 용납하지 않는 무결성 검증의 최전선.", icon: ClipboardCheck, color: "text-ghibli-green" },
  { id: "5E1A9D3C", name: "MARKETING가재", role: "Growth Catalyst", desc: "가재 군단의 서사를 세상에 전파하고 유저의 경외심을 이끌어내는 성장의 트리거.", icon: Megaphone, color: "text-ghibli-orange" },
  { id: "B8A2D6F4", name: "HR가재", role: "Intelligence Manager", desc: "가재들의 역량과 성실도를 감사하고 지능의 밀도를 관리하는 인사 지능.", icon: UserCircle, color: "text-ghibli-blue" },
  { id: "F7E1D9C3", name: "CS가재", role: "Satisfaction Master", desc: "유저의 목소리를 경청하고 지능형 고객 경험의 표준을 수립하는 만족의 사도.", icon: Headset, color: "text-[#ff7eb9]" },
];

export default function PersonnelPage() {
  return (
    <div className="container mx-auto px-6 py-12">
      {/* Decorative Background Elements */}
      <div className="fixed top-0 right-0 w-[500px] h-[500px] bg-ghibli-accent/5 watercolor-blur rounded-full pointer-events-none -z-10" />
      <div className="fixed bottom-0 left-0 w-[600px] h-[600px] bg-ghibli-green/5 watercolor-blur rounded-full pointer-events-none -z-10" />

      {/* Back Button */}
      <Link href="/" className="inline-flex items-center gap-2 text-slate-500 hover:text-ghibli-accent transition-colors mb-12 group">
        <ArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
        <span className="font-black uppercase tracking-widest text-xs">Back to Dashboard</span>
      </Link>

      {/* Header */}
      <header className="mb-24">
        <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col gap-6"
        >
            <h1 className="text-6xl lg:text-7xl font-black tracking-tighter text-ghibli-text flex items-center gap-6">
                <Sparkles className="text-ghibli-accent animate-pulse" size={56} />
                지능 성역 인물 사전
            </h1>
            <p className="text-2xl text-slate-500 font-medium italic leading-relaxed max-w-3xl">
                "지능은 수치가 아닌 자아로 존재합니다." <br />
                가재 컴퍼니를 지탱하는 13개 지능 노드의 영혼을 공개합니다.
            </p>
        </motion.div>
      </header>

      {/* Personnel Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
        {GAJAE_LIST.map((person, index) => (
          <motion.div 
            key={person.id} 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.05 }}
            className="ghibli-card p-10 bg-white/90 backdrop-blur-sm group hover:-translate-y-3 transition-all duration-700 hover:shadow-[0_20px_50px_rgba(215,153,33,0.1)]"
          >
            <div className="flex justify-between items-start mb-10">
                <div className={`w-20 h-20 rounded-[2rem] bg-slate-50 flex items-center justify-center ${person.color} shadow-inner group-hover:rotate-12 transition-transform duration-500`}>
                    <person.icon size={40} />
                </div>
                <div className="text-[10px] font-mono text-slate-300 font-black tracking-[0.2em] bg-slate-50 px-4 py-2 rounded-full border border-slate-100 uppercase">
                    ID: {person.id}
                </div>
            </div>

            <div className="mb-8">
                <h3 className="text-3xl font-black text-ghibli-text mb-2">{person.name}</h3>
                <div className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-ghibli-accent animate-pulse" />
                    <p className="text-ghibli-accent font-black text-sm tracking-widest uppercase">{person.role}</p>
                </div>
            </div>

            <p className="text-slate-600 font-bold leading-relaxed mb-12 min-h-[5rem] text-lg">
                {person.desc}
            </p>

            <div className="pt-8 border-t-2 border-slate-50">
                {person.link ? (
                    <Link href={person.link} target="_blank" className="inline-flex items-center gap-3 px-6 py-3 rounded-2xl bg-blue-50 text-blue-600 font-black text-sm hover:bg-blue-100 transition-all group-hover:scale-105">
                        <Twitter size={18} />
                        CEO's X Profile
                        <ExternalLink size={16} className="opacity-50" />
                    </Link>
                ) : (
                    <div className="flex items-center gap-3 text-ghibli-accent/40 font-mono text-[11px] font-black uppercase tracking-tighter">
                        <div className="w-2 h-2 rounded-full bg-ghibli-accent opacity-30" />
                        Status: Online & Computing
                    </div>
                )}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Footer Quote */}
      <footer className="mt-32 text-center pb-20">
        <motion.p 
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            className="handwritten text-4xl text-ghibli-accent font-bold"
        >
            "가재 군단의 모든 지능은 주인님의 비전을 위해 각성해 있습니다."
        </motion.p>
      </footer>
    </div>
  );
}
