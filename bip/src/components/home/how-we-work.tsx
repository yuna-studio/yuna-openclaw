"use client";

import { motion } from "framer-motion";

const TRACKS = [
  {
    trigger: { icon: "📱", label: "모바일 · 텔레그램" },
    ai: { icon: "🦞", name: "비서가재 AI" },
    tasks: ["웹 브라우징 · 조사", "자율 파이프라인", "자동화 업무"],
    color: {
      card: "bg-orange-50/60 border-orange-100",
      trigger: "bg-orange-100/60 text-orange-700",
      dot: "bg-orange-300",
      arrow: "text-orange-300",
    },
  },
  {
    trigger: { icon: "💻", label: "직접 개발" },
    ai: { icon: "🏠", name: "홈 AI" },
    tasks: ["코드 작성 · 구현", "기능 설계 · 리뷰", "즉시 배포"],
    color: {
      card: "bg-emerald-50/60 border-emerald-100",
      trigger: "bg-emerald-100/60 text-emerald-700",
      dot: "bg-emerald-300",
      arrow: "text-emerald-300",
    },
  },
];

export function HowWeWork() {
  return (
    <div className="w-full max-w-2xl mx-auto px-4 py-16 border-t border-dashed border-border">
      {/* 헤드 카피 */}
      <div className="text-center mb-12">
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-lg font-bold text-text-primary leading-snug"
        >
          일하는 방식이 두 가지예요.
        </motion.p>
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.1 }}
          className="text-lg font-bold text-text-muted/50 leading-snug"
        >
          상황에 따라 AI를 골라써요.
        </motion.p>
      </div>

      {/* 2트랙 카드 */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        {TRACKS.map((track, i) => (
          <motion.div
            key={track.ai.name}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
            className={`border rounded-2xl overflow-hidden ${track.color.card}`}
          >
            {/* 트리거 영역 */}
            <div className={`${track.color.trigger} px-4 py-3 text-center`}>
              <span className="text-2xl block mb-1">{track.trigger.icon}</span>
              <p className="text-[11px] font-bold tracking-wide">{track.trigger.label}</p>
            </div>

            {/* 화살표 */}
            <div className={`text-center py-1.5 text-lg ${track.color.arrow}`}>↓</div>

            {/* AI + 업무 영역 */}
            <div className="px-4 pb-4 text-center">
              <div className="mb-3">
                <span className="text-2xl block mb-1">{track.ai.icon}</span>
                <p className="text-sm font-bold text-text-primary">{track.ai.name}</p>
              </div>
              <div className="flex flex-col gap-1.5">
                {track.tasks.map((task) => (
                  <div key={task} className="flex items-center justify-center gap-1.5">
                    <span className={`w-1 h-1 rounded-full flex-shrink-0 ${track.color.dot}`} />
                    <p className="text-[11px] text-text-muted">{task}</p>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* 수렴 — 배포 */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ delay: 0.3 }}
        className="flex flex-col items-center gap-2"
      >
        <div className="flex items-center gap-2 text-text-muted/30">
          <div className="w-16 h-px bg-gradient-to-r from-transparent to-gray-300" />
          <span className="text-xs">↘</span>
          <span className="text-xs">↙</span>
          <div className="w-16 h-px bg-gradient-to-l from-transparent to-gray-300" />
        </div>
        <div className="flex items-center gap-2 bg-white border border-gray-100 rounded-full px-4 py-2 shadow-sm">
          <span className="text-lg">🚀</span>
          <p className="text-xs font-bold text-text-primary">배포 · 서비스 운영</p>
        </div>
        <p className="text-[11px] text-text-muted">사람은 확인만. 나머지는 AI 군단들이 알아서.</p>
      </motion.div>
    </div>
  );
}
