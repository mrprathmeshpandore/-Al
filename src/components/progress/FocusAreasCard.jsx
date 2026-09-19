import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Target, ArrowRight, TrendingUp, HelpCircle, Scale } from 'lucide-react';
import { focusAreas } from '../../data/progressData';

export default function FocusAreasCard() {
  const navigate = useNavigate();

  const handlePracticeWeakAreas = () => {
    navigate(`/question-bank?focus=${focusAreas.targetFilter}`);
  };

  const handleTagClick = (category) => {
    navigate(`/question-bank?focus=${category}`);
  };

  const getTagIcon = (category) => {
    if (category === 'economy') return <TrendingUp className="w-3.5 h-3.5" />;
    if (category === 'ethics') return <Scale className="w-3.5 h-3.5" />;
    return <HelpCircle className="w-3.5 h-3.5" />;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.25 }}
      className="bg-white rounded-2xl p-6 border border-amber-950/5 shadow-sm flex flex-col justify-between"
    >
      <div>
        <div className="flex items-center gap-2 mb-2">
          <div className="p-1.5 rounded-lg bg-rose-50 text-rose-600">
            <Target className="w-4 h-4" />
          </div>
          <h3 className="font-serif font-bold text-slate-900 text-base">{focusAreas.title}</h3>
        </div>
        <p className="text-xs text-slate-500 font-sans mb-4">
          {focusAreas.description}
        </p>

        <div className="flex flex-wrap gap-2 mb-6">
          {focusAreas.tags.map((tag) => (
            <button
              key={tag.label}
              onClick={() => handleTagClick(tag.category)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-semibold transition-all hover:scale-[1.02] cursor-pointer ${tag.color}`}
            >
              {getTagIcon(tag.category)}
              {tag.label}
            </button>
          ))}
        </div>
      </div>

      <button
        onClick={handlePracticeWeakAreas}
        className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-[#0b1628] hover:bg-[#132238] text-white text-xs font-semibold shadow-sm transition-all group"
      >
        <span>{focusAreas.ctaText}</span>
        <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
      </button>
    </motion.div>
  );
}
