import React from 'react';
import { motion } from 'framer-motion';

export default function FooterBanner() {
  return (
    <motion.footer
      initial={{ opacity: 0, y: 30 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
      className="max-w-7xl mx-auto px-4 lg:px-12 pt-8 pb-16 z-10 relative"
    >
      <div className="flex flex-col md:flex-row items-center justify-between gap-6 border-t border-slate-200/60 pt-8">
        
        {/* LEFT: LOTUS CIVIC MOTIF & MARATHI QUOTE */}
        <div className="flex items-center gap-4">
          {/* Decorative Lotus Outline Icon */}
          <div className="w-12 h-12 rounded-full bg-amber-50 border border-amber-200/70 flex items-center justify-center text-[#E86A24] shrink-0 shadow-xs">
            <svg className="w-7 h-7 stroke-current fill-none stroke-[1.5]" viewBox="0 0 24 24">
              {/* Lotus Flower Civic Motif */}
              <path d="M12 4C10 7 7 11 4 14C7 16 12 17 12 17C12 17 17 16 20 14C17 11 14 7 12 4Z" />
              <path d="M12 8C11 11 9 14 6 16C9 18 12 19 12 19C12 19 15 18 18 16C15 14 13 11 12 8Z" />
              <path d="M12 17V21" />
              <path d="M8 21H16" />
            </svg>
          </div>

          <div>
            <h3 className="font-marathi text-lg sm:text-xl font-black text-[#0F172A] tracking-tight">
              “ सक्षम प्रशासन, समृद्ध भारत. ”
            </h3>
            <p className="text-[10px] font-bold text-[#64748B] uppercase tracking-widest mt-0.5">
              FROM ASPIRATION TO ACTION
            </p>
          </div>
        </div>

        {/* RIGHT: TRICOLOR RIBBON FLOURISH & SLOGAN */}
        <div className="flex items-center gap-3 bg-white px-5 py-2.5 rounded-full border border-slate-200/80 shadow-xs">
          <div className="w-8 h-2 rounded-full bg-gradient-to-r from-[#FF9933] via-slate-200 to-[#138808] shrink-0" />
          <span className="text-xs font-bold text-[#0F172A] tracking-tight">
            A Stronger India <span className="font-medium text-[#64748B]">Begins With You</span>
          </span>
        </div>

      </div>
    </motion.footer>
  );
}
