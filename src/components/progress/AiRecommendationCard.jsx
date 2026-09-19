import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Lightbulb, ArrowRight } from 'lucide-react';
import { aiRecommendation } from '../../data/progressData';

export default function AiRecommendationCard() {
  const navigate = useNavigate();

  const handleStartPractice = () => {
    navigate(aiRecommendation.targetRoute);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.3 }}
      className="bg-white rounded-2xl p-6 border border-amber-950/5 shadow-sm flex flex-col justify-between"
    >
      <div>
        <div className="flex items-center gap-2 mb-2">
          <div className="p-1.5 rounded-lg bg-amber-50 text-amber-600">
            <Lightbulb className="w-4 h-4" />
          </div>
          <h3 className="font-serif font-bold text-slate-900 text-base">AI Recommendation</h3>
        </div>

        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 font-sans">
          {aiRecommendation.title}
        </h4>

        <p className="text-xs text-slate-600 italic bg-amber-50/50 p-3 rounded-xl border border-amber-100/60 leading-relaxed font-sans mb-4">
          {aiRecommendation.recommendationText}
        </p>
      </div>

      <button
        onClick={handleStartPractice}
        className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-semibold border border-blue-200/80 transition-all group"
      >
        <span>{aiRecommendation.ctaText}</span>
        <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
      </button>
    </motion.div>
  );
}
