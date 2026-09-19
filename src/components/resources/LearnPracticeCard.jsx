import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Upload } from 'lucide-react';

export default function LearnPracticeCard() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="bg-white rounded-2xl p-5 border border-amber-950/5 shadow-2xs flex flex-col justify-between"
    >
      <div>
        <div className="flex items-center gap-2 mb-2">
          <div className="p-1.5 rounded-lg bg-amber-50 text-amber-600">
            <Sparkles className="w-4 h-4" />
          </div>
          <h3 className="font-serif font-bold text-slate-900 text-base">Learn → Practice</h3>
        </div>

        <p className="text-xs text-slate-600 font-sans leading-relaxed mb-4">
          Found something important? Turn your study material into interview practice.
        </p>

        {/* Upload dropzone mockup */}
        <div className="border-2 border-dashed border-slate-200 rounded-xl p-4 text-center bg-slate-50/50 hover:bg-slate-50 transition-colors cursor-pointer mb-3 group">
          <div className="w-8 h-8 rounded-full bg-white shadow-2xs text-blue-600 flex items-center justify-center mx-auto mb-1.5 group-hover:scale-105 transition-transform">
            <Upload className="w-4 h-4" />
          </div>
          <span className="text-xs font-bold text-slate-700 block">Upload a PDF</span>
          <span className="text-[10px] text-slate-400 font-medium">(Coming Soon)</span>
        </div>
      </div>

      <p className="text-[11px] text-slate-400 italic text-center font-sans leading-snug">
        Get summaries, key points, UPSC relevance, and potential interview questions using AI.
      </p>
    </motion.div>
  );
}
