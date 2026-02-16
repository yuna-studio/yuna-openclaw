"use client";

import { motion } from "framer-motion";

export function HowWeWork() {
  return (
    <div className="w-full max-w-2xl mx-auto px-4 py-16 border-t border-dashed border-border">
      {/* 헤드 카피 — 애플 스타일 */}
      <div className="text-center mb-12">
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-lg font-bold text-text-primary leading-snug"
        >
          말 한마디면 충분해요.
        </motion.p>
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.1 }}
          className="text-lg font-bold text-text-muted/50 leading-snug"
        >
          나머지는 가재들이 알아서.
        </motion.p>
      </div>

      {/* 3단 플로우 */}
      <div className="space-y-10">
        {/* Step 1 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center"
        >
          <span className="text-3xl">💬</span>
          <p className="text-sm font-bold text-text-primary mt-2">&ldquo;이거 만들어줘&rdquo;</p>
          <p className="text-[11px] text-text-muted mt-1">텔레그램으로 한 마디.</p>
        </motion.div>

        <div className="flex justify-center">
          <div className="w-px h-8 bg-gradient-to-b from-gray-200 to-gray-300" />
        </div>

        {/* Step 2 — 분기 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.1 }}
          className="text-center"
        >
          <span className="text-3xl">🦞</span>
          <p className="text-sm font-bold text-text-primary mt-2">비서가재가 알아서 판단해요</p>
          <div className="flex justify-center gap-3 mt-3">
            <div className="bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2 text-center">
              <p className="text-[11px] font-bold text-emerald-700">⚡ 간단한 건</p>
              <p className="text-[9px] text-emerald-600 mt-0.5">바로 처리</p>
            </div>
            <div className="bg-purple-50 border border-purple-200 rounded-lg px-3 py-2 text-center">
              <p className="text-[11px] font-bold text-purple-700">🔄 큰 건</p>
              <p className="text-[9px] text-purple-600 mt-0.5">파이프라인 가동</p>
            </div>
          </div>
        </motion.div>

        <div className="flex justify-center">
          <div className="w-px h-8 bg-gradient-to-b from-gray-300 to-gray-200" />
        </div>

        {/* Step 3 — 파이프라인 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2 }}
          className="text-center"
        >
          <div className="flex justify-center gap-4 mb-3">
            <span className="text-2xl">🔍</span>
            <span className="text-lg text-text-muted/30">→</span>
            <span className="text-2xl">⚖️</span>
            <span className="text-lg text-text-muted/30">→</span>
            <span className="text-2xl">🚀</span>
          </div>
          <p className="text-sm font-bold text-text-primary">조사하고, 만들고, 검수하고, 배포해요</p>
          <p className="text-[11px] text-text-muted mt-1">기획서부터 코드까지. 사람은 확인만.</p>
        </motion.div>
      </div>
    </div>
  );
}
