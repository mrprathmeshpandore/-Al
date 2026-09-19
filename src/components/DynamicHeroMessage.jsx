import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, Quote } from 'lucide-react';

export default function DynamicHeroMessage() {
  const heroMessages = [
    "तुमच्या स्वप्नातील भारतासाठी !",
    "तुमच्या ध्येयातील यशासाठी !",
    "तुमच्या प्रशासकीय प्रवासासाठी !",
    "समर्थ भारताच्या उभारणीसाठी !",
  ];

  const [currentIndex, setCurrentIndex] = useState(0);

  // Auto switch message every 4.5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => (prevIndex + 1) % heroMessages.length);
    }, 4500);

    return () => clearInterval(interval);
  }, [heroMessages.length]);

  const handleNextMessage = () => {
    setCurrentIndex((prevIndex) => (prevIndex + 1) % heroMessages.length);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.7, delay: 0.7, ease: [0.16, 1, 0.3, 1] }}
      className="bg-white/80 backdrop-blur-md border border-white/80 shadow-xl shadow-slate-900/5 rounded-2xl p-4 sm:p-5 flex items-center justify-between gap-4 w-full max-w-sm sm:max-w-md ml-auto group transition-all duration-300 hover:shadow-2xl hover:bg-white/90"
    >
      <div className="flex items-center gap-3.5 flex-1 min-w-0">
        {/* Double Quote Icon */}
        <div className="shrink-0 w-8 h-8 rounded-xl bg-amber-500/10 text-[#D97706] flex items-center justify-center">
          <Quote className="w-4 h-4 fill-current rotate-180" />
        </div>

        {/* Animated Message Text */}
        <div className="relative flex-1 min-h-[44px] flex items-center overflow-hidden">
          <AnimatePresence mode="wait">
            <motion.p
              key={currentIndex}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
              className="font-marathi text-base sm:text-lg font-bold text-[#0B1628] leading-tight select-none"
            >
              {heroMessages[currentIndex]}
            </motion.p>
          </AnimatePresence>
        </div>
      </div>

      {/* Interactive Arrow Button */}
      <motion.button
        whileHover={{ scale: 1.08, x: 2 }}
        whileTap={{ scale: 0.92 }}
        onClick={handleNextMessage}
        className="w-10 h-10 rounded-full bg-white shadow-md border border-slate-200/80 text-[#0B1628] hover:text-[#E86A24] flex items-center justify-center shrink-0 transition-colors cursor-pointer"
        aria-label="Next Message"
      >
        <ArrowRight className="w-4 h-4" />
      </motion.button>
    </motion.div>
  );
}
