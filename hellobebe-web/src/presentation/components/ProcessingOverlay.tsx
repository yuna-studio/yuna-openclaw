"use client";

import { motion } from "framer-motion";

export default function ProcessingOverlay({ progress }: { progress: number }) {
  return (
    <div className="fixed inset-0 z-50 bg-white/90 backdrop-blur-md flex flex-col items-center justify-center p-6">
      {/* Heartbeat Sphere */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          boxShadow: [
            "0 0 20px rgba(212,175,55,0.2)",
            "0 0 50px rgba(212,175,55,0.5)",
            "0 0 20px rgba(212,175,55,0.2)",
          ],
        }}
        transition={{
          duration: 0.8,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="w-40 h-40 rounded-full bg-[var(--color-accent)] flex items-center justify-center"
      >
        <span className="text-white font-serif text-3xl font-bold">
          {Math.round(progress)}%
        </span>
      </motion.div>

      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="mt-12 text-center"
      >
        <h3 className="text-2xl font-serif text-[var(--color-text-main)] mb-2">
          아기의 특징을 정밀하게 분석 중입니다...
        </h3>
        <p className="text-gray-500 animate-pulse">
          잠시만 기다려 주세요. 생애 첫 미소가 곧 완성됩니다.
        </p>
      </motion.div>

      {/* Progress Bar */}
      <div className="mt-8 w-full max-w-xs h-1 bg-slate-100 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-[var(--color-accent)]"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}
