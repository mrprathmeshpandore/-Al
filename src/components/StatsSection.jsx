import React, { useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { Users, FileText, Cpu, BarChart3, Quote } from 'lucide-react';
import { useCountUp } from '../hooks/useCountUp';

function StatCard({ stat, index }) {
  const cardRef = useRef(null);
  const isInView = useInView(cardRef, { once: true, margin: "-50px" });

  const countValue = useCountUp(stat.targetNumber || 0, isInView, 1600);
  const animatedCount = stat.targetNumber ? countValue : null;

  return (
    <motion.div
      ref={cardRef}
      initial={{ opacity: 0, y: 35, scale: 0.97 }}
      whileInView={{ opacity: 1, y: 0, scale: 1 }}
      viewport={{ once: true }}
      transition={{
        duration: 0.6,
        delay: index * 0.08,
        ease: [0.16, 1, 0.3, 1],
      }}
      whileHover={{ y: -5, transition: { duration: 0.2 } }}
      className="bg-white/95 backdrop-blur-md rounded-2xl p-4 sm:p-5 border border-slate-200/80 card-shadow flex flex-col justify-between relative overflow-hidden group cursor-pointer"
    >
      <div className="flex items-center gap-3.5">
        {/* Icon Circle */}
        <motion.div
          whileHover={{ scale: 1.08 }}
          className={`w-11 h-11 rounded-2xl flex items-center justify-center shrink-0 ${stat.iconBg} ${stat.iconColor} shadow-xs group-hover:shadow-md transition-all`}
        >
          <stat.icon className="w-5.5 h-5.5" />
        </motion.div>

        {/* Number & Label */}
        <div>
          <h3 className="text-xl sm:text-2xl font-black text-[#0F172A] tracking-tight">
            {stat.targetNumber ? `${animatedCount}${stat.suffix}` : stat.title}
          </h3>
          <p className="text-xs font-bold text-[#1E293B]">
            {stat.subtitle}
          </p>
        </div>
      </div>

      <p className="text-[11.5px] font-normal text-[#64748B] mt-3 leading-snug">
        {stat.description}
      </p>

      {/* Border Highlight on Hover */}
      <div className="absolute inset-0 border-2 border-transparent group-hover:border-amber-400/40 rounded-2xl pointer-events-none transition-colors" />
    </motion.div>
  );
}

export default function StatsSection() {
  const statsData = [
    {
      icon: Users,
      iconBg: 'bg-blue-50',
      iconColor: 'text-blue-600',
      targetNumber: 10,
      suffix: 'K+',
      title: '10K+',
      subtitle: 'Aspirants',
      description: 'Building their interview skills',
    },
    {
      icon: FileText,
      iconBg: 'bg-emerald-50',
      iconColor: 'text-emerald-600',
      targetNumber: 50,
      suffix: 'K+',
      title: '50K+',
      subtitle: 'Questions',
      description: 'Covering all key topics',
    },
    {
      icon: Cpu,
      iconBg: 'bg-purple-50',
      iconColor: 'text-purple-600',
      targetNumber: null,
      suffix: '',
      title: 'AI',
      subtitle: 'Personalized',
      description: 'Practice based on your profile',
    },
    {
      icon: BarChart3,
      iconBg: 'bg-orange-50',
      iconColor: 'text-orange-600',
      targetNumber: 95,
      suffix: '%',
      title: '95%',
      subtitle: 'Satisfaction',
      description: 'From our learners',
    },
  ];

  return (
    <section className="max-w-7xl mx-auto px-4 lg:px-12 pb-8 -mt-12 sm:-mt-16 lg:-mt-20 z-20 relative">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-12 gap-4 sm:gap-5 items-stretch">
        
        {/* 4 Stat Cards */}
        <div className="lg:col-span-9 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {statsData.map((stat, i) => (
            <StatCard key={i} stat={stat} index={i} />
          ))}
        </div>

        {/* 5th Card: UPSC Discipline Quote */}
        <motion.div
          initial={{ opacity: 0, y: 35, scale: 0.97 }}
          whileInView={{ opacity: 1, y: 0, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.4 }}
          whileHover={{ y: -5 }}
          className="lg:col-span-3 bg-gradient-to-br from-white via-slate-50 to-amber-50/40 rounded-2xl p-5 border border-slate-200/80 card-shadow relative overflow-hidden flex flex-col justify-between group"
        >
          {/* Subtle Parliament Dome Silhouette Backdrop */}
          <div className="absolute right-0 bottom-0 opacity-10 pointer-events-none">
            <svg className="w-36 h-36 fill-slate-900" viewBox="0 0 100 100">
              <path d="M 50 10 Q 75 30 80 50 L 90 90 L 10 90 L 20 50 Q 25 30 50 10 Z" />
            </svg>
          </div>

          <div className="relative z-10">
            <Quote className="w-5 h-5 text-amber-600 rotate-180 mb-2" />
            <p className="text-xs font-bold text-[#0F172A] italic leading-relaxed">
              “Discipline today for a better tomorrow.”
            </p>
          </div>

          <p className="text-[11px] font-semibold text-[#64748B] mt-3 relative z-10">
            – UPSC
          </p>
        </motion.div>

      </div>
    </section>
  );
}
