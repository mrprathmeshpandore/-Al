import React from 'react';
import { motion } from 'framer-motion';

export default function ProgressHeader() {
  return (
    <div className="w-full bg-gradient-to-r from-white via-[#FAF7F2] to-amber-500/10 rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-2xs relative overflow-hidden flex flex-col lg:flex-row items-center justify-between gap-6">
      
      {/* LEFT CONTENT */}
      <div className="space-y-2 max-w-xl z-10">
        <span className="text-[11px] font-bold tracking-widest text-amber-600 uppercase bg-amber-500/10 border border-amber-300/40 px-3 py-1 rounded-full inline-block">
          PROGRESS & ANALYTICS
        </span>
        
        <h1 className="text-2xl sm:text-3xl font-extrabold text-[#0B1628] tracking-tight leading-tight font-sans">
          My Progress
        </h1>
        
        <div className="space-y-0.5">
          <p className="text-xs sm:text-sm font-semibold text-slate-700 leading-relaxed">
            Track your preparation. Understand your growth.
          </p>
          <p className="text-xs sm:text-sm font-medium text-slate-500">
            Turn your efforts into a stronger tomorrow.
          </p>
        </div>
      </div>

      {/* RIGHT GRAPHIC ARTWORK (Rashtrapati Bhavan & Ashoka Emblem) */}
      <div className="relative flex items-center gap-4 z-10 shrink-0">
        
        {/* QUOTE BADGE CARD */}
        <div className="bg-white/90 backdrop-blur-xs border border-slate-200/80 px-4 py-2.5 rounded-2xl shadow-2xs text-right hidden md:block max-w-[200px]">
          <p className="text-xs font-semibold italic text-slate-700 font-serif leading-snug">
            "Progress is the result of consistent effort."
          </p>
        </div>

        {/* RASHTRAPATI BHAVAN / EMBLEM GRAPHIC */}
        <div className="w-24 h-24 sm:w-28 sm:h-28 relative opacity-85">
          <svg viewBox="0 0 100 100" fill="none" className="w-full h-full drop-shadow-xs">
            <circle cx="50" cy="50" r="42" fill="#FEF3C7" opacity="0.6" />
            
            {/* Dome Architecture Silhouette */}
            <path d="M 15 85 L 85 85 M 20 85 L 20 65 C 20 40, 80 40, 80 65 L 80 85" stroke="#0B1628" strokeWidth="2.5" />
            <path d="M 30 65 L 30 85 M 40 60 L 40 85 M 50 55 L 50 85 M 60 60 L 60 85 M 70 65 L 70 85" stroke="#0B1628" strokeWidth="1.5" />
            <path d="M 50 40 L 50 25" stroke="#0B1628" strokeWidth="2" />
            <circle cx="50" cy="25" r="4" fill="#E86A24" />
          </svg>
        </div>

      </div>

    </div>
  );
}
