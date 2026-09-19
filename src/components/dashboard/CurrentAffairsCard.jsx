import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, ChevronRight, Cpu, Globe2, Leaf, Landmark } from 'lucide-react';
import { currentAffairs } from '../../data/dashboardData';

const caIconMap = {
  cpu: Cpu,
  globe2: Globe2,
  leaf: Leaf,
  landmark: Landmark
};

export default function CurrentAffairsCard() {
  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-2xs space-y-4">
      
      {/* HEADER */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-[#0B1628] tracking-tight">
          Today's Current Affairs
        </h3>
        <button className="text-xs font-semibold text-slate-500 hover:text-[#0B1628] flex items-center gap-1 transition-colors">
          <span>View All</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* ITEMS LIST */}
      <div className="space-y-3">
        {currentAffairs.map((item, idx) => {
          const IconComp = caIconMap[item.icon] || Cpu;

          return (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: idx * 0.07 }}
              className="flex items-center justify-between p-3 rounded-xl border border-slate-100 hover:border-amber-200/80 hover:bg-amber-500/5 transition-all duration-200 cursor-pointer group"
            >
              <div className="flex items-center gap-3">
                {/* THUMBNAIL WITH FALLBACK ICON */}
                <div className="relative w-11 h-11 rounded-lg overflow-hidden shrink-0 bg-slate-100 border border-slate-200/60">
                  <img 
                    src={item.imageUrl} 
                    alt={item.title} 
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                  <div className="absolute inset-0 bg-[#0B1628]/10 flex items-center justify-center text-white">
                    <IconComp className="w-5 h-5 text-[#0B1628]" />
                  </div>
                </div>

                {/* TEXT CONTENT */}
                <div>
                  <h4 className="text-xs sm:text-sm font-bold text-[#0B1628] group-hover:text-amber-600 transition-colors line-clamp-1">
                    {item.title}
                  </h4>
                  <p className="text-[11px] font-medium text-slate-400 mt-0.5">
                    {item.category} · <span className="text-slate-500">{item.date}</span>
                  </p>
                </div>
              </div>

              <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-[#0B1628] group-hover:translate-x-1 transition-all shrink-0 ml-2" />
            </motion.div>
          );
        })}
      </div>

    </div>
  );
}
