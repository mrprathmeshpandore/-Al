import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check } from 'lucide-react';

export default function GoogleAuthSuccessAnimation({ onComplete }) {
  // STEPS: 
  // 1: Google G 360° Rotation (0s - 0.6s)
  // 2: Circular Ring Draw (0.6s - 1.4s)
  // 3: Checkmark Reveal (1.4s - 1.8s)
  // 4: Prashasak AI Logo Reveal (1.8s - 2.4s)
  // 5: Animated Glass Success Popup (2.4s - 3.8s)
  const [step, setStep] = useState(1);
  const [popupProgress, setPopupProgress] = useState(0);

  useEffect(() => {
    // Step 1 -> Step 2 at 600ms
    const t1 = setTimeout(() => setStep(2), 600);

    // Step 2 -> Step 3 at 1400ms
    const t2 = setTimeout(() => setStep(3), 1400);

    // Step 3 -> Step 4 at 1800ms
    const t3 = setTimeout(() => setStep(4), 1800);

    // Step 4 -> Step 5 at 2400ms
    const t4 = setTimeout(() => setStep(5), 2400);

    // Step 5 Progress fill & complete at 3800ms
    const t5 = setTimeout(() => {
      if (onComplete) onComplete();
    }, 3800);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      clearTimeout(t3);
      clearTimeout(t4);
      clearTimeout(t5);
    };
  }, [onComplete]);

  // Progress bar animation for Popup (2400ms to 3700ms)
  useEffect(() => {
    if (step === 5) {
      const interval = setInterval(() => {
        setPopupProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval);
            return 100;
          }
          return prev + 5;
        });
      }, 60);
      return () => clearInterval(interval);
    }
  }, [step]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0B1628]/70 backdrop-blur-lg select-none">
      <AnimatePresence mode="wait">
        
        {/* STEPS 1 to 4: LOGO & CHECKMARK ANIMATION CARD */}
        {step < 5 && (
          <motion.div
            key="sequence-visual"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.3 } }}
            className="relative w-80 h-80 bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl border border-slate-200/80 flex flex-col items-center justify-center p-6 overflow-hidden"
          >
            {/* Background subtle light ambient glow */}
            <div className="absolute inset-0 bg-gradient-to-tr from-amber-500/5 via-blue-500/5 to-emerald-500/5 rounded-3xl" />

            {/* STEP 1, 2, 3: GOOGLE G & RING & CHECKMARK */}
            {(step === 1 || step === 2 || step === 3) && (
              <div className="relative flex items-center justify-center w-36 h-36">
                
                {/* STEP 2 & 3: CIRCULAR RING (DRAWING ANIMATION) */}
                {(step === 2 || step === 3) && (
                  <svg className="absolute inset-0 w-full h-full -rotate-90 pointer-events-none" viewBox="0 0 100 100">
                    <circle
                      cx="50"
                      cy="50"
                      r="44"
                      className="text-slate-100"
                      strokeWidth="3"
                      stroke="currentColor"
                      fill="transparent"
                    />
                    <motion.circle
                      cx="50"
                      cy="50"
                      r="44"
                      stroke="url(#ringGradient)"
                      strokeWidth="3.5"
                      strokeLinecap="round"
                      fill="transparent"
                      initial={{ pathLength: 0 }}
                      animate={{ pathLength: 1 }}
                      transition={{ duration: 0.8, ease: "easeInOut" }}
                    />
                    <defs>
                      <linearGradient id="ringGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#4285F4" />
                        <stop offset="50%" stopColor="#34A853" />
                        <stop offset="100%" stopColor="#EA4335" />
                      </linearGradient>
                    </defs>
                  </svg>
                )}

                {/* STEP 1 & 2: OFFICIAL GOOGLE G LOGO */}
                {(step === 1 || step === 2) && (
                  <motion.div
                    key="google-g"
                    initial={{ rotate: 0, scale: 0.9 }}
                    animate={{ rotate: step === 1 ? 360 : 360, scale: [0.9, 1.05, 1.0] }}
                    transition={{ duration: 0.6, ease: "easeInOut" }}
                    className="w-16 h-16 flex items-center justify-center"
                  >
                    <svg viewBox="0 0 24 24" className="w-14 h-14">
                      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" />
                      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" />
                    </svg>
                  </motion.div>
                )}

                {/* STEP 3: CHECKMARK REVEAL */}
                {step === 3 && (
                  <motion.div
                    key="checkmark-icon"
                    initial={{ scale: 0, opacity: 0 }}
                    animate={{ scale: [0, 1.25, 1.0], opacity: 1 }}
                    transition={{ duration: 0.4, ease: [0.165, 0.84, 0.44, 1] }}
                    className="w-16 h-16 rounded-full bg-emerald-500 text-white flex items-center justify-center shadow-lg shadow-emerald-500/30"
                  >
                    <Check className="w-9 h-9 stroke-[3]" />
                  </motion.div>
                )}
              </div>
            )}

            {/* STEP 4: PRASHASAK AI BRANDING REVEAL */}
            {step === 4 && (
              <motion.div
                key="prashasak-logo"
                initial={{ opacity: 0, scale: 0.85 }}
                animate={{ opacity: 1, scale: 1.0 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
                className="flex flex-col items-center justify-center space-y-3"
              >
                <div className="w-16 h-16 rounded-2xl bg-[#0B1628] text-white flex items-center justify-center font-bold text-3xl shadow-xl border border-white/10">
                  🏛️
                </div>
                <div className="text-center">
                  <span className="font-marathi text-2xl font-extrabold text-[#0B1628]">प्रशासक</span>{' '}
                  <span className="text-[#E86A24] font-black text-2xl">AI</span>
                </div>
                <p className="text-xs font-semibold text-slate-400">Authenticating Aspirant...</p>
              </motion.div>
            )}

          </motion.div>
        )}

        {/* STEP 5: ANIMATED GLASS SUCCESS POPUP */}
        {step === 5 && (
          <motion.div
            key="success-popup"
            initial={{ opacity: 0, scale: 0.85, y: 15 }}
            animate={{ opacity: 1, scale: 1.0, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -10 }}
            transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
            className="relative w-full max-w-sm bg-white/95 backdrop-blur-2xl rounded-3xl shadow-2xl border border-slate-200/90 p-8 flex flex-col items-center justify-center text-center overflow-hidden"
          >
            {/* Top Success Badge Icon */}
            <motion.div
              initial={{ scale: 0, rotate: -30 }}
              animate={{ scale: [0, 1.2, 1.0], rotate: 0 }}
              transition={{ duration: 0.4, delay: 0.15, ease: "easeOut" }}
              className="w-16 h-16 rounded-full bg-emerald-50 border-4 border-emerald-100 text-emerald-600 flex items-center justify-center mb-4 shadow-sm"
            >
              <Check className="w-8 h-8 stroke-[3]" />
            </motion.div>

            {/* Prashasak AI Logo Header */}
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35, delay: 0.25 }}
              className="flex items-center justify-center gap-2 mb-2"
            >
              <div className="w-6 h-6 rounded-lg bg-[#0B1628] text-white flex items-center justify-center text-xs font-bold">
                🏛️
              </div>
              <span className="font-marathi text-sm font-bold text-[#0B1628]">प्रशासक</span>
              <span className="text-[#E86A24] font-black text-sm">AI</span>
            </motion.div>

            {/* Main Title */}
            <motion.h3
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35, delay: 0.3 }}
              className="text-lg font-extrabold text-[#0B1628] tracking-tight"
            >
              Authentication Successful
            </motion.h3>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35, delay: 0.35 }}
              className="text-xs font-semibold text-slate-500 mt-1"
            >
              Welcome to Prashasak AI
            </motion.p>

            {/* Thin Progress Bar at Bottom */}
            <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden mt-6">
              <motion.div
                className="h-full bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full"
                style={{ width: `${popupProgress}%` }}
                transition={{ ease: "easeInOut" }}
              />
            </div>
          </motion.div>
        )}

      </AnimatePresence>
    </div>
  );
}
