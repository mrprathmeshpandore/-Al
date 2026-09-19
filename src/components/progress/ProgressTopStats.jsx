import React from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, Users, BarChart3, Flame } from 'lucide-react';
import { progressStats } from '../../data/progressData';

const statStyleMap = {
  messageSquare: { icon: MessageSquare, bg: 'bg-blue-50 text-blue-600 border-blue-100' },
  users: { icon: Users, bg: 'bg-emerald-50 text-emerald-600 border-emerald-100' },
  barChart: { icon: BarChart3, bg: 'bg-amber-50 text-amber-600 border-amber-100' },
  flame: { icon: Flame, bg: 'bg-orange-50 text-orange-600 border-orange-100' },
};

export default function ProgressTopStats({ stats = progressStats }) {
  const list = [
    { key: 'questionsPracticed', ...stats.questionsPracticed },
    { key: 'interviewsCompleted', ...stats.interviewsCompleted },
    { key: 'averageScore', ...stats.averageScore },
    { key: 'dayStreak', ...stats.dayStreak },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {list.map((item, idx) => {
        const style = statStyleMap[item.icon] || statStyleMap.messageSquare;
        const IconComp = style.icon;

        return (
          <motion.div
            key={item.key}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, delay: idx * 0.06 }}
            className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-2xs hover:shadow-xs transition-all flex flex-col justify-between"
          >
            <div className="flex items-center justify-between">
              <div className={`w-10 h-10 rounded-xl ${style.bg} border flex items-center justify-center`}>
                <IconComp className="w-5 h-5" />
              </div>
            </div>

            <div className="mt-4 space-y-1">
              <div className="text-2xl sm:text-3xl font-extrabold text-[#0B1628] tracking-tight">
                {typeof item.value === 'number' && item.value < 10 ? `0${item.value}` : item.value}
              </div>
              <p className="text-xs font-semibold text-slate-500">
                {item.label}
              </p>
              
              {item.trend && (
                <span className="text-[11px] font-bold text-emerald-600 block pt-0.5">
                  {item.trend}
                </span>
              )}

              {item.badge && (
                <span className="text-[11px] font-bold text-orange-600 block pt-0.5">
                  {item.badge}
                </span>
              )}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
