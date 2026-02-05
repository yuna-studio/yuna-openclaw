"use client";

import { motion } from "framer-motion";
import { CreditCard, Check } from "lucide-react";

export default function PricingSection({ onPay }: { onPay: () => void }) {
  return (
    <section className="py-24 px-4 bg-white border-t border-slate-100">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-4xl font-serif text-[var(--color-text-main)] mb-12">
          단 한 번의 선택으로 마주하는 <br /> 잊지 못할 첫 만남
        </h2>
        
        <div className="max-w-md mx-auto p-8 rounded-3xl border-2 border-[var(--color-accent)] bg-slate-50 relative shadow-2xl">
          <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-[var(--color-accent)] text-white px-4 py-1 rounded-full text-sm font-bold">
            BEST VALUE
          </div>
          
          <p className="text-gray-500 mb-2">프리미엄 AI 실사화 패키지</p>
          <div className="flex items-end justify-center gap-1 mb-8">
            <span className="text-5xl font-bold text-[var(--color-text-main)]">5,900</span>
            <span className="text-xl text-gray-500 mb-1">원</span>
          </div>

          <ul className="text-left space-y-4 mb-10">
            {[
              "초정밀 실사 이미지 3종 (정면, 미소, 수면)",
              "평생 소장 가능한 고해상도 이미지",
              "인스타그램 맞춤형 공유 카드 제공",
              "개인정보 100% 암호화 및 자동 파기",
            ].map((text, i) => (
              <li key={i} className="flex items-start gap-3 text-sm text-gray-600">
                <Check className="w-5 h-5 text-[var(--color-success)] shrink-0" />
                {text}
              </li>
            ))}
          </ul>

          <button 
            onClick={onPay}
            className="w-full py-5 bg-[var(--color-primary)] text-white rounded-2xl font-bold text-xl flex items-center justify-center gap-3 hover:scale-[1.02] transition-transform shadow-lg active:scale-95"
          >
            <CreditCard className="w-6 h-6" />
            지금 바로 시작하기
          </button>

          <div className="mt-8 pt-8 border-t border-slate-200">
            <p className="text-sm font-bold text-gray-500 mb-4">카드 결제가 어려우신가요?</p>
            <div className="bg-white border border-slate-200 rounded-2xl p-4 text-left">
              <p className="text-xs text-gray-400 mb-2 font-semibold">무통장 입금 안내 (Concierge)</p>
              <div className="flex justify-between items-center">
                <span className="text-sm font-bold text-slate-700">기업은행</span>
                <span className="text-sm font-mono text-[var(--color-primary)]">568-023070-01-017</span>
              </div>
              <div className="flex justify-between items-center mt-1">
                <span className="text-xs text-gray-500">예금주: 공경환</span>
                <span className="text-xs font-bold text-gray-500">입금액: 5,900원</span>
              </div>
              <p className="mt-3 text-[10px] text-gray-400 leading-relaxed">
                * 입금 확인 후 10분 이내로 티켓이 자동 지급됩니다. <br />
                * 입금자명은 반드시 로그인한 성함과 동일하게 입력해주세요.
              </p>
            </div>
          </div>
          
          <p className="mt-6 text-xs text-gray-400">
            * 결제 즉시 AI 분석이 시작되며, 결과 확인 후에는 환불이 불가합니다.
          </p>
        </div>
      </div>
    </section>
  );
}
