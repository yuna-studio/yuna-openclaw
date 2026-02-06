"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import Image from "next/image";

/**
 * [가재 컴퍼니] Simplified GNB (v1.5)
 * 의도: 대표님의 지시에 따라 메뉴(대시보드, 연대기) 및 상태 표시기(무결성 수호 등)를 제거하고 로고 중심의 심플한 디자인으로 피벗함.
 */

export const GNB = () => {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4 bg-ghibli-bg/60 backdrop-blur-md border-b border-ghibli-accent/5">
      <div className="flex items-center gap-10">
        <Link href="/" className="flex items-center gap-3 group">
          <motion.div 
            whileHover={{ scale: 1.05 }}
            className="w-10 h-10 rounded-full overflow-hidden border-2 border-white shadow-md"
          >
            <Image 
                src="/assets/media/gajae-cute-chef.jpg" 
                alt="Logo" 
                width={40} 
                height={40}
                className="object-cover"
            />
          </motion.div>
          <div className="flex flex-col">
            <span className="font-black text-lg leading-none text-ghibli-text group-hover:text-ghibli-accent transition-colors">가재 컴퍼니</span>
            <span className="text-[10px] font-mono tracking-widest text-slate-400 font-bold uppercase">Sanctuary</span>
          </div>
        </Link>
      </div>

      <div className="flex items-center gap-4">
        {/* Everything else removed per CEO instruction */}
      </div>
    </nav>
  );
};
