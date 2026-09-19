import React from 'react';
import { motion } from 'framer-motion';

export default function ProfileHeroHeader() {
  return (
    <div className="w-full bg-gradient-to-r from-white via-[#FAF7F2] to-amber-500/10 rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-2xs relative overflow-hidden flex flex-col lg:flex-row items-center justify-between gap-6">
      
      {/* LEFT CONTENT */}
      <div className="space-y-2.5 max-w-xl z-10">
        <span className="text-[11px] font-bold tracking-widest text-amber-600 uppercase bg-amber-500/10 border border-amber-300/40 px-3 py-1 rounded-full inline-block">
          YOUR UPSC PROFILE
        </span>
        
        <h1 className="text-2xl sm:text-3xl font-extrabold text-[#0B1628] tracking-tight leading-tight font-sans">
          Help AI understand your journey.
        </h1>
        
        <p className="text-xs sm:text-sm font-medium text-slate-600 leading-relaxed">
          Fill your profile (DAF) to get personalized interview questions and a better learning experience.
        </p>
      </div>

      {/* RIGHT GRAPHIC ARTWORK (Parliament Dome & Tricolor Accent) */}
      <div className="relative flex items-center gap-4 z-10 shrink-0">
        
        {/* SLOGAN STAMP */}
        <div className="hidden sm:flex flex-col text-right leading-tight">
          <span className="text-[10px] font-extrabold text-slate-400 tracking-wider uppercase">
            SAME PEOPLE
          </span>
          <span className="text-[11px] font-black text-[#0B1628] tracking-tight uppercase">
            STRONGER
          </span>
          <span className="text-xs font-black text-amber-600 tracking-tight uppercase">
            INDIA
          </span>
        </div>

        {/* QUOTE BADGE CARD */}
        <div className="bg-white/90 backdrop-blur-xs border border-slate-200/80 px-4 py-2.5 rounded-2xl shadow-2xs text-right hidden md:block">
          <p className="text-xs font-semibold italic text-slate-700 font-serif">
            "Know yourself, to prepare better."
          </p>
        </div>

        {/* PARLIAMENT DOME SILHOUETTE */}
        <div className="w-24 h-24 sm:w-28 sm:h-28 relative opacity-85">
          <svg viewBox="0 0 100 100" fill="none" className="w-full h-full drop-shadow-xs">
            {/* Soft Glow */}
            <circle cx="50" cy="50" r="40" fill="#FEF3C7" opacity="0.6" />
            
            {/* Parliament Dome Graphic */}
            <path d="M 20 85 L 80 85 M 25 85 L 25 65 C 25 45, 75 45, 75 65 L 75 85" stroke="#0B1628" strokeWidth="2.5" strokeLinecap="round" />
            <path d="M 32 65 L 32 85 M 44 60 L 44 85 M 56 60 L 56 85 M 68 65 L 68 85" stroke="#0B1628" strokeWidth="1.5" />
            <path d="M 50 45 L 50 30" stroke="#0B1628" strokeWidth="2" />
            
            {/* Tricolor Flag Top */}
            <path d="M 50 30 C 58 26, 62 34, 70 30 L 70 40 C 62 44, 58 36, 50 40 Z" fill="url(#flagGradientProfile)" />
            
            <defs>
              <linearGradient id="flagGradientProfile" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#FF9933" />
                <stop offset="50%" stopColor="#FFFFFF" />
                <stop offset="100%" stopColor="#138808" />
              </linearGradient>
            </defs>
          </svg>
        </div>

      </div>

    </div>
  );
}
