import React from 'react';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';
import { questionFlowList, interviewSession } from '../../data/interviewData';

export default function InterviewProgressCard() {
  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-2xs space-y-4">
      
      {/* HEADER WITH PERCENTAGE */}
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-bold text-[#0B1628]">
          Interview Progress
        </h4>
        <span className="text-sm font-extrabold text-[#0B1628]">
          {interviewSession.overallProgressPercentage}%
        </span>
      </div>

      {/* PROGRESS BAR */}
      <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden p-0.5">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${interviewSession.overallProgressPercentage}%` }}
          transition={{ duration: 0.6 }}
          className="h-full bg-gradient-to-r from-amber-500 to-emerald-600 rounded-full"
        />
      </div>

      {/* QUESTION FLOW LIST */}
      <div className="space-y-2 pt-1">
        {questionFlowList.slice(0, 6).map((item) => {
          const isCompleted = item.status === 'completed';
          const isActive = item.status === 'active';

          return (
            <div
              key={item.step}
              className={`flex items-center justify-between p-2 rounded-xl text-xs font-semibold transition-all ${
                isActive 
                  ? 'bg-[#0B1628] text-white shadow-2xs font-bold' 
                  : isCompleted 
                    ? 'text-slate-700 hover:bg-slate-50' 
                    : 'text-slate-400'
              }`}
            >
              <div className="flex items-center gap-2.5 min-w-0">
                <span className={`w-5 h-5 rounded-full flex items-center justify-center text-[11px] font-bold shrink-0 ${
                  isCompleted 
                    ? 'bg-emerald-500 text-white' 
                    : isActive 
                      ? 'bg-white text-[#0B1628]' 
                      : 'bg-slate-100 text-slate-400 border border-slate-200'
                }`}>
                  {isCompleted ? <Check className="w-3 h-3 stroke-[3]" /> : item.step}
                </span>
                <span className="truncate">{item.text}</span>
              </div>

              {isActive && (
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping shrink-0" />
              )}
            </div>
          );
        })}
      </div>

    </div>
  );
}
