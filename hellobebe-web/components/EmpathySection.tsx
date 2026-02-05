"use client";

import { motion } from "framer-motion";

export default function EmpathySection() {
  return (
    <section className="py-24 px-4 bg-white">
      <div className="max-w-4xl mx-auto text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <span className="text-[var(--color-primary)] font-bold tracking-widest text-sm uppercase">
            The Precious Connection
          </span>
          <h2 className="mt-4 text-4xl md:text-5xl font-serif text-[var(--color-text-main)] leading-tight">
            흐릿한 기억을 <br /> 선명한 감동으로
          </h2>
          <div className="mt-8 h-1 w-20 bg-[var(--color-accent)] mx-auto rounded-full" />
          <p className="mt-8 text-lg text-gray-500 max-w-2xl mx-auto leading-relaxed font-sans">
            초음파 사진 속 작고 흐릿한 형체, <br />
            매일 밤 상상하던 우리 아기의 진짜 얼굴은 어떤 모습일까요? <br />
            가장 진보된 AI 기술로 그 궁금함에 답을 드립니다.
          </p>
        </motion.div>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
          {[
            {
              title: "30초의 기적",
              desc: "기다림의 시간은 줄이고 감동의 크기는 키웠습니다.",
            },
            {
              title: "압도적 사실주의",
              desc: "단순한 합성을 넘어 태아의 특징을 정밀하게 분석합니다.",
            },
            {
              title: "영원한 기록",
              desc: "우리 아기의 첫 미소를 고해상도로 평생 소장하세요.",
            },
          ].map((feature, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.2, duration: 0.6 }}
              className="p-8 rounded-2xl bg-[var(--color-bg-main)] border border-slate-100 hover:shadow-lg transition-shadow"
            >
              <h3 className="text-xl font-bold text-[var(--color-text-main)] mb-3">
                {feature.title}
              </h3>
              <p className="text-gray-500 leading-relaxed">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
