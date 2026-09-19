import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, Calendar, BookOpen } from 'lucide-react';
import { featuredAffair } from '../../data/currentAffairsData';

export default function FeaturedCurrentAffair({ onOpenDetail }) {
  const navigate = useNavigate();

  const handlePracticeClick = (e) => {
    e.stopPropagation();
    // Navigate to /interview with topic state
    navigate('/interview', {
      state: {
        topic: featuredAffair.title,
        categories: featuredAffair.tags,
        source: "CURRENT AFFAIRS"
      }
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      onClick={() => onOpenDetail(featuredAffair)}
      className="w-full bg-white rounded-2xl border border-slate-200/80 shadow-2xs hover:shadow-md transition-all duration-300 overflow-hidden group cursor-pointer"
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 items-stretch">
        
        {/* LEFT TEXT & CTA AREA */}
        <div className="lg:col-span-7 p-6 sm:p-8 space-y-4 flex flex-col justify-between">
          
          <div className="space-y-3">
            {/* BADGES */}
            <div className="flex items-center gap-3">
              <span className="text-[10px] font-extrabold tracking-wider uppercase bg-amber-500/10 text-amber-700 border border-amber-300/60 px-2.5 py-0.5 rounded-full inline-flex items-center gap-1">
                <Sparkles className="w-3 h-3 text-amber-600" />
                <span>{featuredAffair.badge}</span>
              </span>
              <span className="text-xs font-semibold text-slate-400 flex items-center gap-1">
                <Calendar className="w-3.5 h-3.5" />
                <span>{featuredAffair.date}</span>
              </span>
            </div>

            {/* TITLE & SUMMARY */}
            <h2 className="text-xl sm:text-2xl font-extrabold text-[#0B1628] group-hover:text-amber-600 transition-colors tracking-tight leading-tight">
              {featuredAffair.title}
            </h2>

            <p className="text-xs sm:text-sm font-medium text-slate-600 leading-relaxed">
              {featuredAffair.summary}
            </p>
          </div>

          {/* TAGS & PRIMARY CTA */}
          <div className="pt-2 space-y-4">
            <div className="flex flex-wrap items-center gap-2">
              {featuredAffair.tags.map((tag) => (
                <span key={tag} className="text-[11px] font-semibold text-slate-600 bg-slate-100 border border-slate-200/60 px-2.5 py-1 rounded-lg">
                  {tag}
                </span>
              ))}
            </div>

            <div>
              <button
                type="button"
                onClick={handlePracticeClick}
                className="bg-[#0B1628] hover:bg-[#152744] text-white px-5 py-2.5 rounded-full text-xs font-bold inline-flex items-center gap-2 shadow-md transition-all cursor-pointer"
              >
                <span>{featuredAffair.primaryCtaText}</span>
                <ArrowRight className="w-4 h-4 text-amber-400" />
              </button>
            </div>
          </div>

        </div>

        {/* RIGHT EDITORIAL ARTWORK VISUAL */}
        <div className="lg:col-span-5 relative min-h-[220px] lg:min-h-[280px] bg-gradient-to-br from-amber-500/10 via-slate-900 to-[#0B1628] overflow-hidden flex items-center justify-center p-6">
          
          {/* BACKGROUND ARTWORK */}
          <img 
            src={featuredAffair.image}
            alt={featuredAffair.title}
            className="absolute inset-0 w-full h-full object-cover opacity-60 group-hover:scale-105 transition-transform duration-700"
          />

          <div className="absolute inset-0 bg-gradient-to-t from-[#0B1628] via-[#0B1628]/40 to-transparent" />

          {/* GRAPHIC OVERLAY EMBLEM */}
          <div className="relative z-10 text-center text-white space-y-2 max-w-xs">
            <div className="w-14 h-14 rounded-2xl bg-white/10 backdrop-blur-md border border-white/20 mx-auto flex items-center justify-center text-amber-400 text-2xl font-bold shadow-lg">
              🏛️
            </div>
            <div className="text-xs font-black uppercase tracking-widest text-amber-300">
              VIKSIT BHARAT THROUGH AI
            </div>
          </div>

          {/* QUOTE OVERLAY BADGE */}
          <div className="absolute bottom-4 right-4 z-10 bg-white/90 backdrop-blur-md p-2.5 rounded-xl border border-slate-200 shadow-md text-right max-w-[200px] hidden sm:block">
            <p className="text-[10.5px] font-semibold italic text-slate-800 leading-snug font-serif">
              {featuredAffair.quote}
            </p>
          </div>

        </div>

      </div>
    </motion.div>
  );
}
