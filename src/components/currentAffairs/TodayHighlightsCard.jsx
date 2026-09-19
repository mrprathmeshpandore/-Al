import React from 'react';
import { Calendar, ArrowRight } from 'lucide-react';
import { todayHighlights } from '../../data/currentAffairsData';

export default function TodayHighlightsCard({ onSelectHighlight }) {
  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-2xs space-y-4">
      
      {/* HEADER */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-amber-600 shrink-0" />
          <div>
            <h3 className="text-sm font-bold text-[#0B1628]">Today's Highlights</h3>
            <p className="text-[10.5px] font-medium text-slate-400">Friday, 19 Sep 2026</p>
          </div>
        </div>
        <button className="text-xs font-semibold text-slate-500 hover:text-[#0B1628] flex items-center gap-1">
          <span>View All</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* 4 HIGHLIGHTED ITEMS */}
      <div className="space-y-3">
        {todayHighlights.map((item) => (
          <div
            key={item.id}
            onClick={() => onSelectHighlight(item.targetId)}
            className="flex items-center gap-3 p-2.5 rounded-xl border border-slate-100 hover:border-amber-200/80 hover:bg-amber-500/5 transition-all duration-200 cursor-pointer group"
          >
            <div className="w-7 h-7 rounded-full bg-slate-100 border border-slate-200 text-slate-700 font-extrabold text-xs flex items-center justify-center shrink-0 group-hover:bg-[#0B1628] group-hover:text-amber-400 transition-colors">
              {item.step}
            </div>

            <div className="min-w-0 flex-1">
              <h4 className="text-xs font-bold text-[#0B1628] group-hover:text-amber-600 transition-colors truncate">
                {item.title}
              </h4>
              <p className="text-[10.5px] font-medium text-slate-400 truncate">
                {item.category} · <span className="text-slate-500">{item.subcategory}</span>
              </p>
            </div>
          </div>
        ))}
      </div>

    </div>
  );
}
