import React from 'react';
import { motion } from 'framer-motion';
import { Calendar, ChevronLeft, ChevronRight } from 'lucide-react';
import { practiceActivity } from '../../data/progressData';

export default function PracticeActivityCard() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.35 }}
      className="bg-white rounded-2xl p-6 border border-amber-950/5 shadow-sm flex flex-col justify-between"
    >
      <div>
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-emerald-50 text-emerald-600">
              <Calendar className="w-4 h-4" />
            </div>
            <h3 className="font-serif font-bold text-slate-900 text-base">Practice Activity</h3>
          </div>

          <div className="flex items-center gap-1.5 text-xs text-slate-600 font-medium">
            <span>{practiceActivity.month}</span>
            <div className="flex items-center gap-0.5 ml-1 text-slate-400">
              <button className="p-0.5 hover:text-slate-700 transition-colors">
                <ChevronLeft className="w-3.5 h-3.5" />
              </button>
              <button className="p-0.5 hover:text-slate-700 transition-colors">
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>

        {/* Days & Activity Dots */}
        <div className="grid grid-cols-7 gap-1 text-center my-4">
          {practiceActivity.days.map((item) => (
            <div key={item.day} className="flex flex-col items-center gap-2">
              <span className="text-[11px] font-medium text-slate-500 font-sans">{item.day}</span>
              <div className="h-6 flex items-center justify-center">
                {item.status === 'practiced' && (
                  <span className="w-3 h-3 rounded-full bg-emerald-500 shadow-sm" />
                )}
                {item.status === 'no-practice' && (
                  <span className="w-3 h-3 rounded-full bg-slate-100" />
                )}
                {item.status === 'today' && (
                  <span className="w-3 h-3 rounded-full bg-emerald-500 ring-4 ring-emerald-100" />
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center justify-around pt-3 border-t border-slate-100 text-[11px] text-slate-600 font-medium">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
          <span>Practiced</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-slate-200" />
          <span>No Practice</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 ring-2 ring-emerald-200" />
          <span>Today</span>
        </div>
      </div>
    </motion.div>
  );
}
