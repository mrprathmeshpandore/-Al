import React from 'react';
import { motion } from 'framer-motion';

export default function AshokaEmblemIllustration() {
  return (
    <div className="relative w-full h-full min-h-[220px] flex items-center justify-center overflow-hidden rounded-r-2xl pointer-events-none select-none">
      {/* Background Soft Sky & Tricolor Gradient Glow */}
      <div className="absolute inset-0 bg-gradient-to-br from-amber-500/10 via-amber-100/20 to-emerald-500/10 opacity-70" />

      {/* Flag Color Light Sweeps */}
      <div className="absolute top-0 right-0 w-72 h-72 bg-gradient-to-bl from-amber-400/20 via-orange-300/10 to-transparent rounded-full blur-2xl -translate-y-12 translate-x-12" />
      <div className="absolute bottom-0 right-12 w-64 h-64 bg-gradient-to-tl from-emerald-500/15 via-teal-300/10 to-transparent rounded-full blur-2xl translate-y-12" />

      {/* Decorative Quote Banner Pill */}
      <motion.div 
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="absolute top-4 right-6 bg-white/90 backdrop-blur-md px-3.5 py-1.5 rounded-full border border-slate-200/80 shadow-xs flex items-center gap-2 text-[11px] font-medium text-slate-700 z-10"
      >
        <span className="text-amber-600 font-bold">🚀</span>
        <span>"A small step every day leads to a big change."</span>
      </motion.div>

      {/* Secondary Motto Text Overlay */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.5 }}
        className="absolute bottom-6 left-6 text-center lg:text-left z-10 max-w-[200px]"
      >
        <div className="text-[20px] font-extrabold tracking-tight text-[#0B1628] leading-tight opacity-90 font-serif italic">
          Better Citizens,
        </div>
        <div className="text-[22px] font-black text-amber-600 tracking-tight font-serif italic -mt-1">
          Stronger India
        </div>
      </motion.div>

      {/* SVG Artwork: Ashoka Lion Capital + Pillar + India Gate Motif */}
      <svg 
        viewBox="0 0 400 300" 
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
        className="w-full h-full max-h-[250px] object-contain drop-shadow-md z-0 opacity-90 transition-transform duration-700 hover:scale-105"
      >
        <defs>
          <linearGradient id="goldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#D97706" />
            <stop offset="50%" stopColor="#F59E0B" />
            <stop offset="100%" stopColor="#B45309" />
          </linearGradient>

          <linearGradient id="flagGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#FF9933" stopOpacity="0.85" />
            <stop offset="50%" stopColor="#FFFFFF" stopOpacity="0.95" />
            <stop offset="100%" stopColor="#138808" stopOpacity="0.85" />
          </linearGradient>

          <radialGradient id="sunGlow" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#FEF3C7" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#FEF3C7" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* Sun Glow Behind Statue */}
        <circle cx="280" cy="120" r="90" fill="url(#sunGlow)" />

        {/* Ashoka Chakra Wheel Lines */}
        <g opacity="0.2" transform="translate(280, 110)">
          <circle cx="0" cy="0" r="60" stroke="#0B1628" strokeWidth="2" strokeDasharray="3 3" />
          {Array.from({ length: 24 }).map((_, i) => (
            <line
              key={i}
              x1="0"
              y1="0"
              x2={60 * Math.cos((i * 15 * Math.PI) / 180)}
              y2={60 * Math.sin((i * 15 * Math.PI) / 180)}
              stroke="#0B1628"
              strokeWidth="1"
            />
          ))}
        </g>

        {/* Indian Flag Ribbon Detail */}
        <path
          d="M 180 230 C 220 210, 260 250, 310 215 C 340 195, 370 220, 390 200 L 390 240 C 370 260, 340 235, 310 255 C 260 290, 220 250, 180 270 Z"
          fill="url(#flagGradient)"
          opacity="0.75"
        />

        {/* Lion Capital Pillar Base & Capital (Simplified High-Style Vector) */}
        <g transform="translate(270, 70) scale(0.85)">
          {/* Abacus Base */}
          <rect x="-35" y="110" width="70" height="12" rx="3" fill="#B45309" />
          <rect x="-42" y="122" width="84" height="16" rx="4" fill="#92400E" />
          
          {/* Bell Shaped Lotus Base */}
          <path d="M-30 138 C-25 155, 25 155, 30 138 Z" fill="url(#goldGradient)" />
          <path d="M-38 155 L38 155 L45 220 L-45 220 Z" fill="#78350F" />

          {/* Abacus Animals Silhouette */}
          <circle cx="-18" cy="116" r="4" fill="#FEF3C7" />
          <circle cx="18" cy="116" r="4" fill="#FEF3C7" />

          {/* Lions Back-to-Back Heads */}
          <path
            d="M-28 70 C-35 50, -25 30, -10 25 C-5 15, 5 15, 10 25 C25 30, 35 50, 28 70 C32 80, 25 105, 0 108 C-25 105, -32 80, -28 70 Z"
            fill="url(#goldGradient)"
          />
          
          {/* Lion Mane Detailing */}
          <path d="M-22 45 C-15 35, -10 55, 0 40 C10 55, 15 35, 22 45 C18 65, 0 80, -22 45 Z" fill="#92400E" opacity="0.6" />
          <path d="M-12 28 C-8 20, 8 20, 12 28 C10 38, -10 38, -12 28 Z" fill="#78350F" />
          
          {/* Crown/Chakra Silhouette */}
          <circle cx="0" cy="15" r="7" fill="#F59E0B" stroke="#78350F" strokeWidth="2" />
        </g>

        {/* Classical Governance Architecture / Pillars in background */}
        <g stroke="#0B1628" strokeWidth="1.2" strokeOpacity="0.25" fill="none">
          <path d="M 50 250 L 50 180 L 140 180 L 140 250" />
          <path d="M 60 180 L 60 250 M 80 180 L 80 250 M 100 180 L 100 250 M 120 180 L 120 250 M 130 180 L 130 250" />
          <path d="M 45 180 L 145 180 L 95 150 Z" fill="#0B1628" fillOpacity="0.05" />
        </g>

      </svg>
    </div>
  );
}
