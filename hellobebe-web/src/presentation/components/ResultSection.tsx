"use client";

import { motion } from "framer-motion";
import { Download, Share2, RefreshCcw } from "lucide-react";

export default function ResultSection({ onReset }: { onReset: () => void }) {
  const dummyImages = [
    { title: "정면 (Frontal)", url: "https://images.unsplash.com/photo-1519689689378-b01440621473?q=80&w=1000" },
    { title: "미소 (Smiling)", url: "https://images.unsplash.com/photo-1544126592-807daa2b567b?q=80&w=1000" },
    { title: "수면 (Sleeping)", url: "https://images.unsplash.com/photo-1522771935876-2497116a7d9e?q=80&w=1000" },
  ];

  return (
    <section className="py-24 px-4 bg-white min-h-screen flex flex-col items-center">
      <motion.div 
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-16"
      >
        <h2 className="text-4xl font-serif text-[var(--color-text-main)] mb-4">
          축하합니다! <br /> 우리 아이의 선명한 첫 얼굴입니다.
        </h2>
        <p className="text-gray-500">
          가장 정교한 AI로 분석된 실사 이미지 3종입니다.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-6xl px-4 mb-20">
        {dummyImages.map((img, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.3 }}
            className="group"
          >
            <div className="relative aspect-[3/4] rounded-3xl overflow-hidden shadow-xl border border-slate-100 mb-6">
              <img src={img.url} alt={img.title} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700" />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex flex-col justify-end p-6">
                <p className="text-white font-bold text-lg">{img.title}</p>
              </div>
            </div>
            <button className="w-full py-4 border-2 border-slate-100 rounded-2xl font-bold flex items-center justify-center gap-2 hover:bg-slate-50 transition-colors">
              <Download className="w-5 h-5" />
              고해상도 저장
            </button>
          </motion.div>
        ))}
      </div>

      <div className="flex flex-col items-center gap-6">
        <button className="px-12 py-5 bg-[var(--color-accent)] text-white rounded-full font-bold text-xl shadow-xl hover:scale-105 transition-transform flex items-center gap-3">
          <Share2 className="w-6 h-6" />
          인스타그램에 자랑하기
        </button>
        <button 
          onClick={onReset}
          className="flex items-center gap-2 text-gray-400 hover:text-[var(--color-primary)] transition-colors"
        >
          <RefreshCcw className="w-4 h-4" />
          처음으로 돌아가기 (테스트 데이터 초기화)
        </button>
      </div>
    </section>
  );
}
