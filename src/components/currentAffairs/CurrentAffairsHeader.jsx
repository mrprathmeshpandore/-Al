import React from 'react';
import { motion } from 'framer-motion';

export default function CurrentAffairsHeader() {
  return (
    <div className="w-full bg-gradient-to-r from-white via-[#FAF7F2] to-amber-500/10 rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-2xs relative overflow-hidden flex flex-col lg:flex-row items-center justify-between gap-6">
      
      {/* LEFT CONTENT */}
      <div className="space-y-2 max-w-xl z-10">
        <span className="text-[11px] font-bold tracking-widest text-amber-600 uppercase bg-amber-500/10 border border-amber-300/40 px-3 py-1 rounded-full inline-block">
          CURRENT AFFAIRS
        </span>
        
        <h1 className="text-2xl sm:text-3xl font-extrabold text-[#0B1628] tracking-tight leading-tight font-sans">
          Stay updated. Think deeper. Answer better.
        </h1>
        
        <p className="text-xs sm:text-sm font-medium text-slate-600 leading-relaxed">
          Explore important issues, understand their context, and practice interview questions for a stronger preparation.
        </p>
      </div>

      {/* RIGHT GRAPHIC ARTWORK (India Gate Architecture & Quote) */}
      <div className="relative flex items-center gap-4 z-10 shrink-0">
        
        {/* QUOTE BADGE CARD */}
        <div className="bg-white/90 backdrop-blur-xs border border-slate-200/80 px-4 py-2.5 rounded-2xl shadow-2xs text-right hidden md:block">
          <p className="text-xs font-semibold italic text-slate-700 font-serif">
            "A more aware you, for a stronger India."
          </p>
        </div>

        {/* INDIA GATE ARCHITECTURE SILHOUETTE */}
        <div className="w-24 h-24 sm:w-28 sm:h-28 relative opacity-85">
          <svg viewBox="0 0 100 100" fill="none" className="w-full h-full drop-shadow-xs">
            <circle cx="50" cy="50" r="42" fill="#FEF3C7" opacity="0.6" />
            
            {/* India Gate Silhouette */}
            <path d="M 20 85 L 80 85 M 25 85 L 25 35 L 75 35 L 75 85 M 35 35 L 35 25 L 65 25 L 65 35" stroke="#0B1628" strokeWidth="2.5" strokeLinecap="round" />
            <path d="M 40 85 L 40 50 C 40 42, 60 42, 60 50 L 60 85" stroke="#0B1628" strokeWidth="2" />
            <path d="M 30 25 L 70 25 L 50 15 Z" fill="#E86A24" fillOpacity="0.7" />
          </svg>
        </div>

      </div>

    </div>
  );
}
