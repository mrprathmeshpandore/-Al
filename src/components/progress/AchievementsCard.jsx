import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Trophy, FileText, MessageSquare, Flame, Lock, CheckCircle2, ArrowRight } from 'lucide-react';
import { achievements } from '../../data/progressData';

const iconMap = {
  fileText: FileText,
  messageSquare: MessageSquare,
  flame: Flame,
  lock: Lock
};

export default function AchievementsCard() {
  const navigate = useNavigate();

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.4 }}
      className="bg-white rounded-2xl p-6 border border-amber-950/5 shadow-sm flex flex-col justify-between"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-amber-50 text-amber-600">
            <Trophy className="w-4 h-4" />
          </div>
          <h3 className="font-serif font-bold text-slate-900 text-base">Achievements</h3>
        </div>

        <button
          onClick={() => navigate('/progress')}
          className="flex items-center gap-1 text-xs font-semibold text-slate-500 hover:text-amber-800 transition-colors"
        >
          <span>View All</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {achievements.map((ach) => {
          const IconComponent = iconMap[ach.icon] || Trophy;
          return (
            <div
              key={ach.id}
              className={`relative flex flex-col items-center justify-between p-3.5 rounded-2xl border text-center transition-all ${
                ach.unlocked
                  ? `${ach.color} hover:scale-[1.02]`
                  : 'bg-slate-50 text-slate-400 border-slate-200/60 opacity-60'
              }`}
            >
              <div className="p-2 rounded-xl bg-white/80 shadow-2xs mb-2">
                <IconComponent className="w-5 h-5" />
              </div>

              <span className="text-[11px] font-bold leading-tight font-sans">
                {ach.title}
              </span>

              <div className="mt-2">
                {ach.unlocked ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-600 fill-emerald-100" />
                ) : (
                  <Lock className="w-3.5 h-3.5 text-slate-400" />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}
