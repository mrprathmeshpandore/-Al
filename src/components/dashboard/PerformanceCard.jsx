import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Quote } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function PerformanceCard({ skillData }) {
  const navigate = useNavigate();

  const categories = skillData ? [
    { label: 'Content', score: skillData.content?.average_score != null ? Math.round(skillData.content.average_score * 10) : 0, color: 'bg-emerald-600' },
    { label: 'Clarity', score: skillData.clarity?.average_score != null ? Math.round(skillData.clarity.average_score * 10) : 0, color: 'bg-blue-600' },
    { label: 'Depth', score: skillData.depth?.average_score != null ? Math.round(skillData.depth.average_score * 10) : 0, color: 'bg-indigo-600' },
    { label: 'Reasoning', score: skillData.reasoning?.average_score != null ? Math.round(skillData.reasoning.average_score * 10) : 0, color: 'bg-amber-600' },
    { label: 'Balance', score: skillData.balance?.average_score != null ? Math.round(skillData.balance.average_score * 10) : 0, color: 'bg-rose-600' },
    { label: 'Communication', score: skillData.communication?.average_score != null ? Math.round(skillData.communication.average_score * 10) : 0, color: 'bg-purple-600' },
  ] : [
    { label: 'Content', score: 0, color: 'bg-[#0B1628]' },
    { label: 'Clarity', score: 0, color: 'bg-[#0B1628]' },
    { label: 'Depth', score: 0, color: 'bg-[#0B1628]' },
    { label: 'Reasoning', score: 0, color: 'bg-[#0B1628]' },
  ];

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-2xs space-y-5">
      {/* HEADER */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-[#0B1628] tracking-tight">
          6-Dimensional Skill Proficiency
        </h3>
        <button
          onClick={() => navigate('/progress')}
          className="text-xs font-semibold text-slate-500 hover:text-[#0B1628] flex items-center gap-1 transition-colors cursor-pointer"
        >
          <span>View Progress Report</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* BODY GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
        {/* PROGRESS BARS AREA */}
        <div className="lg:col-span-8 space-y-3">
          {categories.map((cat, idx) => (
            <div key={cat.label} className="space-y-1">
              <div className="flex items-center justify-between text-xs font-semibold">
                <span className="text-slate-700">{cat.label}</span>
                <span className="text-[#0B1628] font-bold">{cat.score > 0 ? `${cat.score}%` : 'No data'}</span>
              </div>
              
              <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden p-0.5">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${cat.score}%` }}
                  transition={{ duration: 0.8, delay: idx * 0.08, ease: "easeOut" }}
                  className={`h-full rounded-full ${cat.color}`}
                />
              </div>
            </div>
          ))}
        </div>

        {/* QUOTE CARD AREA */}
        <div className="lg:col-span-4 h-full flex flex-col justify-center">
          <div className="p-5 rounded-xl bg-amber-500/5 border border-amber-200/60 relative overflow-hidden flex flex-col justify-between space-y-3 h-full min-h-[160px]">
            <Quote className="w-6 h-6 text-amber-500 opacity-60" />
            <p className="text-sm font-semibold text-slate-700 italic leading-relaxed">
              “Consistent structured evaluation elevates analytical depth and administrative poise.”
            </p>
            <div className="w-8 h-1 bg-amber-500 rounded-full" />
          </div>
        </div>
      </div>
    </div>
  );
}
