import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, HelpCircle, GitPullRequest, Award } from 'lucide-react';
import AshokaEmblemIllustration from './AshokaEmblemIllustration';

export default function InterviewHeroCard({ onStartInterview }) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="w-full bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden relative group hover:border-slate-300 transition-all duration-300"
    >
      <div className="grid grid-cols-1 lg:grid-cols-12 items-center">
        
        {/* LEFT CONTENT AREA */}
        <div className="lg:col-span-7 p-6 sm:p-8 space-y-5 z-10">
          
          {/* BADGE */}
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-300/50 text-amber-700 text-xs font-bold tracking-wide uppercase">
            <Sparkles className="w-3.5 h-3.5 fill-amber-500 text-amber-600" />
            <span>AI INTERVIEW</span>
          </div>

          {/* MAIN HEADING & DESCRIPTION */}
          <div className="space-y-2">
            <h2 className="text-2xl sm:text-3xl font-extrabold text-[#0B1628] tracking-tight leading-tight">
              Your Next Interview Awaits
            </h2>
            <p className="text-slate-600 text-sm sm:text-base leading-relaxed max-w-xl font-normal">
              Practice real UPSC interview questions with adaptive follow-ups and AI-powered evaluation.
            </p>
          </div>

          {/* CTA BUTTON */}
          <div className="pt-1">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onStartInterview}
              className="bg-[#0B1628] hover:bg-[#152744] text-white px-6 py-3 rounded-full text-sm font-semibold inline-flex items-center gap-2.5 shadow-md shadow-slate-900/15 transition-all duration-200 cursor-pointer"
            >
              <span>Start AI Interview</span>
              <ArrowRight className="w-4 h-4 text-amber-400" />
            </motion.button>
          </div>

          {/* SUPPORTING HIGHLIGHT BADGES */}
          <div className="pt-2 flex flex-wrap items-center gap-4 sm:gap-6 border-t border-slate-100 text-xs text-slate-600 font-medium">
            <div className="flex items-center gap-1.5">
              <HelpCircle className="w-4 h-4 text-amber-600" />
              <span>10 Questions</span>
            </div>
            <div className="flex items-center gap-1.5">
              <GitPullRequest className="w-4 h-4 text-blue-600" />
              <span>Adaptive Follow-ups</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Award className="w-4 h-4 text-emerald-600" />
              <span>AI Evaluation</span>
            </div>
          </div>

        </div>

        {/* RIGHT VISUAL ARTWORK AREA */}
        <div className="lg:col-span-5 h-full min-h-[200px] bg-gradient-to-br from-amber-50/50 via-slate-50 to-white relative">
          <AshokaEmblemIllustration />
        </div>

      </div>
    </motion.div>
  );
}
