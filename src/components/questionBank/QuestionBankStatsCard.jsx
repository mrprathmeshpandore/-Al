import React from 'react';
import { Award, CheckCircle, Bookmark, BarChart3 } from 'lucide-react';
import { questionBankStats } from '../../data/questionBankData';

export default function QuestionBankStatsCard({ stats = questionBankStats }) {
  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-2xs space-y-4">
      <h3 className="text-sm font-bold text-[#0B1628]">
        Question Bank Stats
      </h3>

      <div className="grid grid-cols-2 gap-3">
        
        {/* TOTAL QUESTIONS */}
        <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-200/60 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-amber-500 text-white flex items-center justify-center shrink-0 shadow-2xs">
            <Award className="w-4 h-4" />
          </div>
          <div>
            <div className="text-lg font-extrabold text-[#0B1628] leading-none">
              {stats.totalQuestions}
            </div>
            <span className="text-[10px] font-semibold text-slate-500 mt-0.5 block">
              Total Questions
            </span>
          </div>
        </div>

        {/* PRACTICED */}
        <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-200/60 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center shrink-0 shadow-2xs">
            <CheckCircle className="w-4 h-4" />
          </div>
          <div>
            <div className="text-lg font-extrabold text-[#0B1628] leading-none">
              {stats.practicedCount}
            </div>
            <span className="text-[10px] font-semibold text-slate-500 mt-0.5 block">
              Practiced
            </span>
          </div>
        </div>

        {/* SAVED */}
        <div className="p-3.5 rounded-xl bg-blue-500/10 border border-blue-200/60 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center shrink-0 shadow-2xs">
            <Bookmark className="w-4 h-4" />
          </div>
          <div>
            <div className="text-lg font-extrabold text-[#0B1628] leading-none">
              {stats.savedCount}
            </div>
            <span className="text-[10px] font-semibold text-slate-500 mt-0.5 block">
              Saved
            </span>
          </div>
        </div>

        {/* AVG SCORE */}
        <div className="p-3.5 rounded-xl bg-purple-500/10 border border-purple-200/60 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-purple-600 text-white flex items-center justify-center shrink-0 shadow-2xs">
            <BarChart3 className="w-4 h-4" />
          </div>
          <div>
            <div className="text-lg font-extrabold text-[#0B1628] leading-none">
              {stats.averageScore}
            </div>
            <span className="text-[10px] font-semibold text-slate-500 mt-0.5 block">
              Avg. Score
            </span>
          </div>
        </div>

      </div>
    </div>
  );
}
