"use client";

import { useState, useRef, useEffect } from "react";
import { motion, useAnimation } from "framer-motion";
import { ChevronRight } from "lucide-react";

export default function HeroSection({ onStart }: { onStart?: () => void }) {
  const [sliderPos, setSliderPos] = useState(50);
  const [isAuto, setIsAuto] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-slide animation for first 3 cycles (Simulated)
  useEffect(() => {
    if (!isAuto) return;
    
    let step = 0;
    const interval = setInterval(() => {
      step++;
      const val = 50 + Math.sin(step * 0.1) * 10;
      setSliderPos(val);
      if (step > 60) setIsAuto(false); // Stop after a while
    }, 50);

    return () => clearInterval(interval);
  }, [isAuto]);

  const handleMove = (e: React.MouseEvent | React.TouchEvent) => {
    setIsAuto(false);
    if (!containerRef.current) return;
    
    const rect = containerRef.current.getBoundingClientRect();
    const x = "touches" in e ? e.touches[0].clientX : e.clientX;
    const pos = ((x - rect.left) / rect.width) * 100;
    setSliderPos(Math.max(0, Math.min(100, pos)));
  };

  return (
    <section className="relative min-height-[80vh] flex flex-col items-center justify-center px-4 py-24 overflow-hidden">
      {/* Background radial gradient handled in globals.css */}
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1.2, ease: "easeOut", delay: 0.2 }}
        className="text-center mb-16 z-10"
      >
        <h1 className="text-5xl md:text-7xl font-serif text-[var(--color-primary)] mb-6 tracking-tight">
          태어나면 누구를 <br /> 더 닮았을까?
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto font-sans leading-relaxed">
          흐릿한 초음파 사진 너머, <br />
          처음 마주하는 우리 아이의 선명한 미소를 선물합니다.
        </p>
      </motion.div>

      <div 
        ref={containerRef}
        className="relative w-full max-w-4xl aspect-[4/3] rounded-2xl shadow-2xl overflow-hidden cursor-ew-resize select-none"
        onMouseMove={handleMove}
        onTouchMove={handleMove}
      >
        {/* Result Image (Right Side - High Fidelity) */}
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: "url('https://images.unsplash.com/photo-1519689689378-b01440621473?q=80&w=2000')" }} // Placeholder: Realistic baby
        />

        {/* Ultrasound Image (Left Side - Grainy) */}
        <div 
          className="absolute inset-0 bg-cover bg-center grayscale contrast-125 brightness-75"
          style={{ 
            backgroundImage: "url('https://images.unsplash.com/photo-1559757175-5700dde675bc?q=80&w=2000')", // Placeholder: Ultrasound vibe
            clipPath: `inset(0 ${100 - sliderPos}% 0 0)`
          }}
        />

        {/* Gold Slider Line */}
        <div 
          className="absolute top-0 bottom-0 w-1 bg-[var(--color-accent)] z-20 shadow-[0_0_15px_rgba(212,175,55,0.5)]"
          style={{ left: `${sliderPos}%` }}
        >
          {/* Slider Handle (44px hit area as per spec) */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-11 h-11 flex items-center justify-center">
            <div className="w-8 h-8 rounded-full bg-white border-2 border-[var(--color-accent)] flex items-center justify-center shadow-lg">
              <div className="w-1 h-4 bg-[var(--color-accent)] rounded-full mx-[1px]" />
              <div className="w-1 h-4 bg-[var(--color-accent)] rounded-full mx-[1px]" />
            </div>
          </div>
        </div>
      </div>

      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5 }}
        className="mt-12 flex flex-col items-center gap-4"
      >
        <button 
          onClick={onStart}
          className="px-10 py-5 bg-[var(--color-primary)] text-white rounded-full font-bold text-lg shadow-xl hover:scale-105 transition-transform flex items-center gap-2 group"
        >
          내 아이 만나러 가기
          <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
        </button>
        <p className="text-sm text-gray-500">
          커피 한 잔 가격 5,900원으로 확인하기
        </p>
      </motion.div>
    </section>
  );
}
