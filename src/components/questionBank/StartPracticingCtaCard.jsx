import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Target } from 'lucide-react';

export default function StartPracticingCtaCard() {
  const navigate = useNavigate();

  return (
    <div className="bg-gradient-to-br from-amber-500/10 via-amber-100/30 to-slate-100/80 rounded-2xl p-5 border border-amber-200/60 shadow-2xs space-y-3 relative overflow-hidden">
      
      <div className="flex items-center gap-2">
        <Target className="w-5 h-5 text-amber-600 shrink-0" />
        <h3 className="text-sm font-bold text-[#0B1628]">Start Practicing Today</h3>
      </div>

      <p className="text-xs font-semibold text-slate-600 leading-relaxed">
        Turn questions into confident answers. Practice real UPSC mock rounds with immediate AI evaluation.
      </p>

      <button
        onClick={() => navigate('/interview')}
        className="w-full bg-[#0B1628] hover:bg-[#152744] text-white py-2.5 px-4 rounded-xl text-xs font-bold flex items-center justify-center gap-2 shadow-md transition-all cursor-pointer"
      >
        <span>Start AI Interview</span>
        <ArrowRight className="w-4 h-4 text-amber-400" />
      </button>

      {/* PARLIAMENT DOME SILHOUETTE */}
      <div className="absolute right-0 bottom-0 opacity-10 text-5xl select-none font-serif text-slate-800 pointer-events-none">
        🏛️
      </div>

    </div>
  );
}
