import React from 'react';
import { motion } from 'framer-motion';
import { Layers, FileCheck, Star, Flame, ChevronDown } from 'lucide-react';
import { dashboardStats } from '../../data/dashboardData';

const statIcons = {
  layers: { icon: Layers, bg: 'bg-blue-50 text-blue-600 border-blue-100' },
  fileCheck: { icon: FileCheck, bg: 'bg-indigo-50 text-indigo-600 border-indigo-100' },
  star: { icon: Star, bg: 'bg-amber-50 text-amber-600 border-amber-100' },
  flame: { icon: Flame, bg: 'bg-orange-50 text-orange-600 border-orange-100' },
};

export default function ProgressStatCard() {
  const statsList = [
    { key: 'questionsPracticed', ...dashboardStats.questionsPracticed },
    { key: 'interviewsCompleted', ...dashboardStats.interviewsCompleted },
    { key: 'averageScore', ...dashboardStats.averageScore },
    { key: 'dayStreak', ...dashboardStats.dayStreak },
  ];

  return (
    <div className="space-y-4">
      
      {/* SECTION HEADER */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-[#0B1628] tracking-tight">
          Your Progress
        </h3>
        <div className="relative">
          <button className="text-xs font-semibold text-slate-600 bg-white border border-slate-200/80 px-3 py-1.5 rounded-lg flex items-center gap-1.5 shadow-2xs hover:border-slate-300 transition-all">
            <span>This Month</span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>
        </div>
      </div>

      {/* 4 STATS GRID */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statsList.map((stat, idx) => {
          const style = statIcons[stat.icon] || statIcons.layers;
          const IconComp = style.icon;

          return (
            <motion.div
              key={stat.key}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.35, delay: idx * 0.06 }}
              className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200/80 shadow-2xs hover:shadow-sm transition-all duration-200 flex flex-col justify-between"
            >
              <div className="flex items-center justify-between">
                <div className={`w-10 h-10 rounded-xl ${style.bg} border flex items-center justify-center`}>
                  <IconComp className="w-5 h-5" />
                </div>
                {stat.trend && (
                  <span className="text-[11px] font-bold text-emerald-600 bg-emerald-50 border border-emerald-200/60 px-2 py-0.5 rounded-full flex items-center gap-0.5">
                    {stat.trend}
                  </span>
                )}
                {stat.badge && (
                  <span className="text-[10px] font-bold text-orange-700 bg-orange-50 border border-orange-200/60 px-2 py-0.5 rounded-full">
                    {stat.badge}
                  </span>
                )}
              </div>

              <div className="mt-4">
                <div className="text-2xl sm:text-3xl font-extrabold text-[#0B1628] tracking-tight">
                  {typeof stat.value === 'number' && stat.value < 10 ? `0${stat.value}` : stat.value}
                </div>
                <p className="text-xs font-medium text-slate-500 mt-0.5">
                  {stat.label}
                </p>
              </div>
            </motion.div>
          );
        })}
      </div>

    </div>
  );
}
