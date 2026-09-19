import React from 'react';
import { ArrowRight } from 'lucide-react';
import { popularTopics } from '../../data/questionBankData';

export default function PopularTopicsCard({ onSelectTopic }) {
  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-2xs space-y-4">
      
      {/* HEADER */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <h3 className="text-sm font-bold text-[#0B1628]">Popular Topics</h3>
        <button className="text-xs font-semibold text-slate-500 hover:text-[#0B1628] flex items-center gap-1">
          <span>View All</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* 5 NUMBERED ITEMS */}
      <div className="space-y-2.5">
        {popularTopics.map((topic) => (
          <div
            key={topic.id}
            onClick={() => onSelectTopic(topic.category)}
            className="flex items-center justify-between p-2.5 rounded-xl border border-slate-100 hover:border-slate-200/80 hover:bg-slate-50/70 transition-all duration-200 cursor-pointer group"
          >
            <div className="flex items-center gap-3 min-w-0">
              <span className="w-6 h-6 rounded-full bg-slate-100 border border-slate-200 text-slate-700 font-extrabold text-xs flex items-center justify-center shrink-0 group-hover:bg-[#0B1628] group-hover:text-amber-400 transition-colors">
                {topic.step}
              </span>
              <div className="min-w-0">
                <h4 className="text-xs font-bold text-[#0B1628] group-hover:text-amber-600 transition-colors truncate">
                  {topic.title}
                </h4>
                <p className="text-[10.5px] font-medium text-slate-400">
                  {topic.count}
                </p>
              </div>
            </div>
            
            <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-[#0B1628] group-hover:translate-x-0.5 transition-all shrink-0 ml-2" />
          </div>
        ))}
      </div>

    </div>
  );
}
