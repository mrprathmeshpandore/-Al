import React from 'react';
import { motion } from 'framer-motion';
import { Newspaper, BookOpen, UserCheck, ArrowRight } from 'lucide-react';
import { todayPractice } from '../../data/dashboardData';

const iconComponents = {
  newspaper: Newspaper,
  bookOpen: BookOpen,
  userCheck: UserCheck
};

export default function PracticeCard() {
  return (
    <div className="space-y-4">
      
      {/* SECTION HEADER */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-[#0B1628] tracking-tight">
          Today's Practice
        </h3>
        <button className="text-xs font-semibold text-slate-500 hover:text-[#0B1628] flex items-center gap-1 transition-colors">
          <span>View All</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* 3 CARDS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {todayPractice.map((card, idx) => {
          const Icon = iconComponents[card.icon] || BookOpen;

          return (
            <motion.div
              key={card.id}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: idx * 0.08 }}
              whileHover={{ y: -3 }}
              className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs hover:shadow-md transition-all duration-200 flex flex-col justify-between group cursor-pointer"
            >
              <div className="space-y-3">
                {/* ICON CONTAINER & CATEGORY */}
                <div className="flex items-center justify-between">
                  <div className={`w-11 h-11 rounded-xl ${card.bgColor} ${card.textColor} border ${card.borderColor} flex items-center justify-center transition-transform group-hover:scale-105`}>
                    <Icon className="w-5.5 h-5.5" />
                  </div>
                  <span className="text-[11px] font-semibold text-slate-400 group-hover:text-slate-600 transition-colors">
                    {card.category}
                  </span>
                </div>

                {/* TITLE & DESCRIPTION */}
                <div>
                  <h4 className="text-base font-bold text-[#0B1628] group-hover:text-amber-600 transition-colors">
                    {card.title}
                  </h4>
                  <p className="text-xs text-slate-500 font-medium leading-relaxed mt-1">
                    {card.description}
                  </p>
                </div>
              </div>

              {/* ACTION BUTTON / LINK */}
              <div className="pt-4 mt-2 border-t border-slate-100 flex items-center text-xs font-bold text-[#0B1628] group-hover:text-amber-600 transition-colors">
                <span>{card.buttonText}</span>
              </div>
            </motion.div>
          );
        })}
      </div>

    </div>
  );
}
