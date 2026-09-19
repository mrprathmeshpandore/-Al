import React from 'react';
import { motion } from 'framer-motion';

export default function QuestionBankHeader() {
  return (
    <div className="w-full bg-gradient-to-r from-white via-[#FAF7F2] to-amber-500/10 rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-2xs relative overflow-hidden flex flex-col lg:flex-row items-center justify-between gap-6">
      
      {/* LEFT CONTENT */}
      <div className="space-y-2 max-w-xl z-10">
        <span className="text-[11px] font-bold tracking-widest text-amber-600 uppercase bg-amber-500/10 border border-amber-300/40 px-3 py-1 rounded-full inline-block">
          QUESTION BANK
        </span>
        
        <h1 className="text-2xl sm:text-3xl font-extrabold text-[#0B1628] tracking-tight leading-tight font-sans">
          Prepare smarter. Practice deeper.
        </h1>
        
        <p className="text-xs sm:text-sm font-medium text-slate-600 leading-relaxed">
          Explore a curated collection of UPSC interview questions with detailed insights, practice them, and improve your answers.
        </p>
      </div>

      {/* RIGHT GRAPHIC ARTWORK (Ashoka Pillar & Quote) */}
      <div className="relative flex items-center gap-4 z-10 shrink-0">
        
        {/* QUOTE BADGE CARD */}
        <div className="bg-white/90 backdrop-blur-xs border border-slate-200/80 px-4 py-2.5 rounded-2xl shadow-2xs text-right hidden md:block">
          <p className="text-xs font-semibold italic text-slate-700 font-serif">
            "Questions today, better answers tomorrow."
          </p>
        </div>

        {/* EMBLEM GRAPHIC */}
        <div className="w-24 h-24 sm:w-28 sm:h-28 relative opacity-85">
          <svg viewBox="0 0 100 100" fill="none" className="w-full h-full drop-shadow-xs">
            <circle cx="50" cy="50" r="42" fill="#FEF3C7" opacity="0.6" />
            
            {/* Ashoka Pillar / Books Emblem */}
            <path d="M 25 75 L 75 75 M 30 75 L 30 45 C 30 35, 70 35, 70 45 L 70 75" stroke="#0B1628" strokeWidth="2.5" />
            <path d="M 40 45 C 40 30, 60 30, 60 45" stroke="#0B1628" strokeWidth="2" fill="#E86A24" fillOpacity="0.4" />
            <path d="M 50 30 L 50 15" stroke="#0B1628" strokeWidth="2" />
            <circle cx="50" cy="15" r="3" fill="#D97706" />
          </svg>
        </div>

      </div>

    </div>
  );
}
