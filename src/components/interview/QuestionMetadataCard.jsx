import React from 'react';
import { Landmark, BarChart2, FileText } from 'lucide-react';
import { currentQuestionData } from '../../data/interviewData';

export default function QuestionMetadataCard({ metadata = currentQuestionData }) {
  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-2xs space-y-4">
      
      {/* TOPIC HEADER */}
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-600 border border-blue-200/60 flex items-center justify-center shrink-0">
          <Landmark className="w-5 h-5" />
        </div>
        <div className="space-y-0.5 min-w-0">
          <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
            Current Topic
          </span>
          <h3 className="text-base font-bold text-[#0B1628] truncate">
            {metadata.topic}
          </h3>
          <p className="text-[11px] font-semibold text-slate-500 truncate">
            {metadata.categories.join(' · ')}
          </p>
        </div>
      </div>

      {/* METADATA BADGES GRID */}
      <div className="grid grid-cols-2 gap-3 pt-1 border-t border-slate-100">
        
        {/* DIFFICULTY */}
        <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 flex items-center gap-2">
          <BarChart2 className="w-4 h-4 text-amber-600 shrink-0" />
          <div className="flex flex-col">
            <span className="text-[10px] font-semibold text-slate-400 leading-tight">Difficulty</span>
            <span className="text-xs font-bold text-slate-800 leading-tight">{metadata.difficulty}</span>
          </div>
        </div>

        {/* TYPE */}
        <div className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 flex items-center gap-2">
          <FileText className="w-4 h-4 text-blue-600 shrink-0" />
          <div className="flex flex-col">
            <span className="text-[10px] font-semibold text-slate-400 leading-tight">Type</span>
            <span className="text-xs font-bold text-slate-800 leading-tight">{metadata.typeLabel}</span>
          </div>
        </div>

      </div>

    </div>
  );
}
