import React from 'react';
import { motion } from 'framer-motion';

export default function ProgressInsightCard() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.5 }}
      className="relative overflow-hidden rounded-2xl p-6 border border-amber-900/10 bg-gradient-to-br from-amber-50/80 via-white to-amber-100/40 shadow-sm flex flex-col justify-center min-h-[160px]"
    >
      {/* Decorative background overlay */}
      <div className="absolute right-0 bottom-0 opacity-10 pointer-events-none transform translate-x-4 translate-y-4">
        <svg width="180" height="120" viewBox="0 0 180 120" fill="currentColor" className="text-amber-900">
          <path d="M0 120 L40 60 L80 90 L140 20 L180 120 Z" />
        </svg>
      </div>

      <div className="relative z-10 space-y-2 max-w-[85%]">
        <div className="w-8 h-0.5 bg-amber-500 rounded-full" />
        <p className="font-serif italic font-bold text-slate-800 text-base leading-snug">
          “Small steps every day lead to big results.”
        </p>
        <p className="text-[11px] font-sans font-medium text-amber-900/70 tracking-wide uppercase">
          Prashasak AI Preparation Philosophy
        </p>
      </div>
    </motion.div>
  );
}
