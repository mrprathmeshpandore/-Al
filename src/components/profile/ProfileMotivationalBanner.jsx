import React from 'react';
import { motion } from 'framer-motion';

export default function ProfileMotivationalBanner() {
  return (
    <div className="w-full bg-gradient-to-r from-amber-500/10 via-amber-100/30 to-slate-100/80 rounded-2xl p-6 border border-amber-200/60 shadow-2xs relative overflow-hidden flex flex-col md:flex-row items-center justify-between gap-6">
      
      {/* QUOTE SECTION */}
      <div className="flex items-center gap-4 z-10">
        <span className="text-3xl text-amber-600 font-serif font-bold opacity-80">
          “
        </span>
        <div className="space-y-1">
          <p className="text-sm sm:text-base font-bold italic text-slate-800 leading-snug font-serif">
            The more you know about yourself, the better questions you can answer.
          </p>
          <div className="w-12 h-1 bg-amber-500 rounded-full" />
        </div>
      </div>

      {/* RIGHT ARTWORK SILHOUETTE & SLOGAN */}
      <div className="flex items-center gap-6 z-10 shrink-0">
        <div className="text-right leading-tight">
          <span className="text-[10px] font-black text-slate-500 tracking-wider block uppercase">
            BETTER CITIZENS
          </span>
          <span className="text-[12px] font-black text-amber-700 tracking-tight block uppercase">
            STRONGER INDIA
          </span>
        </div>

        {/* PARLIAMENT DOME MINIMAL ILLUSTRATION */}
        <div className="w-16 h-16 relative opacity-75">
          <svg viewBox="0 0 100 100" fill="none" className="w-full h-full">
            <path d="M 20 80 L 80 80 M 30 80 L 30 60 C 30 40, 70 40, 70 60 L 70 80" stroke="#0B1628" strokeWidth="3" />
            <circle cx="50" cy="30" r="4" fill="#E86A24" />
          </svg>
        </div>
      </div>

    </div>
  );
}
