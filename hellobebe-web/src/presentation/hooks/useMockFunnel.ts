import { useState, useEffect } from 'react';

export type FunnelStep = 'landing' | 'upload' | 'payment' | 'processing' | 'result';

export const useMockFunnel = () => {
  const [step, setStep] = useState<FunnelStep>('landing');
  const [progress, setProgress] = useState(0);

  const startProcessing = () => {
    setStep('processing');
    let p = 0;
    const interval = setInterval(() => {
      p += Math.random() * 10;
      if (p >= 100) {
        p = 100;
        clearInterval(interval);
        setTimeout(() => setStep('result'), 500);
      }
      setProgress(p);
    }, 300);
  };

  return {
    step,
    setStep,
    progress,
    startProcessing,
  };
};
