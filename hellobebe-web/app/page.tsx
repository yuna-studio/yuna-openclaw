"use client";

import HeroSection from "@/components/HeroSection";
import EmpathySection from "@/components/EmpathySection";
import UploadSection from "@/components/UploadSection";
import PricingSection from "@/src/presentation/components/PricingSection";
import ProcessingOverlay from "@/src/presentation/components/ProcessingOverlay";
import ResultSection from "@/src/presentation/components/ResultSection";
import { useMockFunnel } from "@/src/presentation/hooks/useMockFunnel";
import { motion } from "framer-motion";

export default function Home() {
  const { step, setStep, progress, startProcessing } = useMockFunnel();

  if (step === 'result') {
    return <ResultSection onReset={() => setStep('landing')} />;
  }

  return (
    <main className="min-h-screen relative overflow-x-hidden">
      {/* Funnel Progress Indicator for Mock Test */}
      <div className="fixed top-0 left-0 right-0 z-50 h-1 bg-slate-100">
        <div 
          className="h-full bg-[var(--color-primary)] transition-all duration-500" 
          style={{ width: step === 'landing' ? '25%' : step === 'upload' ? '50%' : '75%' }}
        />
      </div>

      {step === 'processing' && <ProcessingOverlay progress={progress} />}

      {step === 'landing' && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <HeroSection onStart={() => setStep('upload')} />
          <EmpathySection />
        </motion.div>
      )}
      
      {step === 'upload' && (
        <motion.div initial={{ opacity: 0, x: 100 }} animate={{ opacity: 1, x: 0 }}>
          <UploadSection onComplete={() => setStep('payment')} />
        </motion.div>
      )}

      {step === 'payment' && (
        <motion.div initial={{ opacity: 0, x: 100 }} animate={{ opacity: 1, x: 0 }}>
          <PricingSection onPay={startProcessing} />
        </motion.div>
      )}
      
      <footer className="py-12 bg-white text-center border-t border-slate-100">
        <p className="text-sm text-gray-400">
          © 2026 Gajae Company. All rights reserved. (Mock Test Environment)
        </p>
      </footer>
    </main>
  );
}
