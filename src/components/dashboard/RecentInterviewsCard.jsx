import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Globe, Scale, ArrowRight } from 'lucide-react';
import { recentInterviews } from '../../data/dashboardData';

const iconMap = {
  shield: Shield,
  globe: Globe,
  scale: Scale
};

export default function RecentInterviewsCard() {
  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-2xs space-y-4">
      
      {/* HEADER */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-[#0B1628] tracking-tight">
          Recent Interviews
        </h3>
        <button className="text-xs font-semibold text-slate-500 hover:text-[#0B1628] flex items-center gap-1 transition-colors">
          <span>View All</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* ROWS LIST */}
      <div className="space-y-3">
        {recentInterviews.map((item, idx) => {
          const IconComp = iconMap[item.icon] || Shield;

          return (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: idx * 0.08 }}
              className="flex items-center justify-between p-3.5 rounded-xl border border-slate-100 hover:border-slate-200/80 hover:bg-slate-50/60 transition-all duration-200 group"
            >
              {/* TOPIC & DATE */}
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg bg-slate-100 border border-slate-200/60 text-[#0B1628] flex items-center justify-center group-hover:bg-[#0B1628] group-hover:text-white transition-colors">
                  <IconComp className="w-4.5 h-4.5" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-[#0B1628] group-hover:text-amber-600 transition-colors">
                    {item.topic}
                  </h4>
                  <p className="text-[11px] font-medium text-slate-400">
                    {item.date}
                  </p>
                </div>
              </div>

              {/* SCORE & VIEW REPORT */}
              <div className="flex items-center gap-4">
                <div className={`px-2.5 py-1 rounded-full text-xs font-bold border ${item.statusColor}`}>
                  {item.score}%
                </div>

                <button className="text-xs font-semibold text-slate-600 hover:text-[#0B1628] hidden sm:flex items-center gap-1 transition-colors">
                  <span>View Report</span>
                  <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                </button>
              </div>
            </motion.div>
          );
        })}
      </div>

    </div>
  );
}
