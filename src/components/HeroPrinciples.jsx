import React from 'react';
import { motion } from 'framer-motion';
import { BookOpen, Lightbulb, Target, BarChart2 } from 'lucide-react';

export default function HeroPrinciples() {
  const heroPrinciples = [
    { icon: BookOpen, title: 'Learn', subtitle: 'Deeper' },
    { icon: Lightbulb, title: 'Think', subtitle: 'Broader' },
    { icon: Target, title: 'Answer', subtitle: 'Better' },
    { icon: BarChart2, title: 'Serve', subtitle: 'Greater' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, delay: 0.65, ease: [0.16, 1, 0.3, 1] }}
      className="w-full pt-4 z-10"
    >
      <div className="flex flex-wrap items-center justify-start gap-4 sm:gap-6 lg:gap-8">
        {heroPrinciples.map((item, index) => {
          const Icon = item.icon;
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.92, y: 15 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              transition={{
                duration: 0.5,
                delay: 0.7 + index * 0.08,
                ease: [0.16, 1, 0.3, 1],
              }}
              whileHover={{ y: -3, scale: 1.04 }}
              className="flex items-center gap-3 p-2 rounded-2xl bg-white/70 backdrop-blur-xs border border-white/80 hover:bg-white transition-all cursor-pointer shadow-xs group"
            >
              <div className="w-10 h-10 rounded-full bg-white border border-slate-200 flex items-center justify-center text-[#0B1628] shadow-xs group-hover:border-amber-400 group-hover:shadow-md transition-all shrink-0">
                <Icon className="w-4.5 h-4.5 text-[#0B1628] group-hover:scale-1.1 transition-transform" />
              </div>
              <div className="flex flex-col pr-1">
                <span className="text-xs font-bold text-[#0F172A] leading-tight">
                  {item.title}
                </span>
                <span className="text-[11px] font-medium text-[#64748B] leading-tight">
                  {item.subtitle}
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}
