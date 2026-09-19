import React from 'react';
import { motion } from 'framer-motion';

export default function SettingsBrandCard() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.15 }}
      className="relative overflow-hidden rounded-2xl p-6 border border-amber-900/10 bg-gradient-to-br from-amber-50/90 via-white to-amber-100/50 shadow-2xs flex flex-col justify-center min-h-[190px]"
    >
      {/* Decorative background overlay */}
      <div className="absolute right-0 bottom-0 opacity-15 pointer-events-none transform translate-x-3 translate-y-3">
        <svg width="180" height="130" viewBox="0 0 180 130" fill="currentColor" className="text-amber-950">
          <path d="M0 130 L40 70 L90 100 L140 30 L180 130 Z" />
        </svg>
      </div>

      <div className="relative z-10 space-y-2 max-w-[85%]">
        <span className="text-amber-700 font-serif text-3xl font-black leading-none block">“</span>
        <p className="font-serif italic font-bold text-slate-800 text-base leading-snug">
          Small changes create a big difference in your journey.
        </p>
        <span className="text-[10.5px] font-sans font-bold text-amber-800 tracking-wider uppercase block pt-1">
          — PRASHASAK AI PREPARATION
        </span>
      </div>
    </motion.div>
  );
}
