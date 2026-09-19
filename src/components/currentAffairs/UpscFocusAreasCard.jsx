import React from 'react';
import { Target, ArrowRight } from 'lucide-react';
import { upscFocusAreas } from '../../data/currentAffairsData';

export default function UpscFocusAreasCard({ onSelectPaper }) {
  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-2xs space-y-4">
      
      {/* HEADER */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <Target className="w-4 h-4 text-amber-600 shrink-0" />
          <h3 className="text-sm font-bold text-[#0B1628]">UPSC Focus Areas</h3>
        </div>
        <button className="text-xs font-semibold text-slate-500 hover:text-[#0B1628] flex items-center gap-1">
          <span>See Syllabus</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* GS PAPERS PILLS GRID */}
      <div className="flex flex-wrap items-center gap-2">
        {upscFocusAreas.map((area, idx) => (
          <button
            key={idx}
            onClick={() => onSelectPaper && onSelectPaper(area.paper)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-50 hover:bg-slate-100 border border-slate-200/70 transition-all text-xs cursor-pointer group"
          >
            <span className={`text-[10px] font-extrabold px-1.5 py-0.5 rounded border ${area.color}`}>
              {area.paper}
            </span>
            <span className="font-semibold text-slate-700 group-hover:text-[#0B1628]">
              {area.label}
            </span>
          </button>
        ))}
      </div>

    </div>
  );
}
