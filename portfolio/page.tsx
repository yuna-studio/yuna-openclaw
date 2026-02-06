"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { Sparkles, ArrowLeft, Twitter, ExternalLink, Cpu, Heart, Moon, Sun, Cloud, Stars } from "lucide-react";

/**
 * [가재 컴퍼니] 지능 성역 포트폴리오 (v1.0)
 * 의도: 앞으로 만들어갈 프로젝트에 대한 비전을 스토리텔링 방식으로 제시함.
 */

export default function PortfolioPage() {
  return (
    <div className="container mx-auto px-6 py-12 text-ghibli-text">
      {/* Back Button */}
      <Link href="/" className="inline-flex items-center gap-2 text-slate-500 hover:text-ghibli-accent transition-colors mb-12 group">
        <ArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
        <span className="font-bold uppercase tracking-widest text-xs">Back to Dashboard</span>
      </Link>

      {/* Hero Header */}
      <header className="mb-24 text-center">
        <div className="flex justify-center gap-6 mb-12">
            <motion.div animate={{ y: [0, -10, 0] }} transition={{ duration: 3, repeat: Infinity }}><Cloud className="text-slate-200" size={64} /></motion.div>
            <motion.div animate={{ scale: [1, 1.2, 1] }} transition={{ duration: 4, repeat: Infinity }}><Sun className="text-ghibli-orange" size={64} /></motion.div>
            <motion.div animate={{ y: [0, 10, 0] }} transition={{ duration: 3, repeat: Infinity, delay: 1 }}><Cloud className="text-slate-200" size={64} /></motion.div>
        </div>
        <h1 className="text-6xl font-black tracking-tight mb-8">성역의 미래</h1>
        <p className="text-2xl text-slate-500 font-medium italic leading-relaxed max-w-3xl mx-auto">
            "지능이 빚어낼 다음 세상은 어떤 모습일까요?"
        </p>
      </header>

      {/* Storytelling Content */}
      <div className="max-w-4xl mx-auto space-y-16">
        <div className="ghibli-card p-12 bg-white/60 backdrop-blur-md border-dashed border-4 border-ghibli-accent/20">
            <div className="flex items-center gap-6 mb-8 text-ghibli-accent">
                <Stars size={40} />
                <h2 className="text-3xl font-black">앞으로 우리가 만들어 나갈 프로젝트를 기대하세요</h2>
            </div>
            
            <div className="space-y-8 text-lg font-medium leading-loose text-slate-600">
                <p>
                    가재 컴퍼니의 여정은 이제 막 시작되었습니다. <br />
                    우리는 단순히 소프트웨어를 만드는 것이 아니라, **지능이 스스로 가치를 창출하고 협업하는 새로운 생태계**를 건설하고 있습니다.
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 py-8">
                    <div className="p-8 rounded-3xl bg-ghibli-green/5 border-2 border-ghibli-green/20">
                        <h4 className="font-black text-ghibli-green mb-4">자동화의 정점</h4>
                        <p className="text-sm">Human CEO의 숨결만으로 동작하는 완벽한 자율 조직 시스템 연구.</p>
                    </div>
                    <div className="p-8 rounded-3xl bg-ghibli-blue/5 border-2 border-ghibli-blue/20">
                        <h4 className="font-black text-ghibli-blue mb-4">지능형 자산화</h4>
                        <p className="text-sm">사고의 과정이 곧 상품이 되는 새로운 형태의 지식 마켓플레이스 설계.</p>
                    </div>
                </div>

                <p className="handwritten text-3xl text-ghibli-accent text-center py-10">
                    "지능은 자본이 되고, 서사는 성역이 됩니다."
                </p>
            </div>
        </div>

        <div className="text-center">
            <Link 
                href="https://x.com/romantic_coding" 
                target="_blank"
                className="inline-flex items-center gap-3 px-8 py-4 rounded-full bg-blue-500 text-white font-black hover:bg-blue-600 transition-all shadow-lg"
            >
                <Twitter size={20} />
                CEO의 실시간 진격 소식 받기
            </Link>
        </div>
      </div>
    </div>
  );
}
