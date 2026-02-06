"use client";

import { motion } from "framer-motion";
import { Heart } from "lucide-react";

export const Heartbeat = () => {
  return (
    <div className="flex items-center gap-3 bg-white/40 backdrop-blur-sm px-4 py-2 rounded-2xl border border-ghibli-accent/10 shadow-sm">
      <div className="relative">
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 0.8,
            repeat: Infinity,
            ease: "easeInOut",
          }}
          className="absolute inset-0 bg-[#ff7eb9] rounded-full blur-md"
        />
        <Heart size={18} fill="#ff7eb9" className="text-[#ff7eb9] relative z-10" />
      </div>
      <div className="flex flex-col">
        <span className="text-[10px] font-black text-ghibli-accent uppercase tracking-tighter leading-none">System Live</span>
        <span className="text-[12px] font-black text-ghibli-text leading-none mt-1">심장 박동 중</span>
      </div>
    </div>
  );
};
