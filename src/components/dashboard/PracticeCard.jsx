import React from 'react';
import { motion } from 'framer-motion';
import { Newspaper, BookOpen, UserCheck, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const practiceModules = [
  {
    id: 'current-affairs',
    title: 'Current Affairs Intelligence',
    description: 'Practice policy-based questions derived from recent national issues.',
    category: 'Daily Module',
    buttonText: 'Practice Current Affairs →',
    icon: Newspaper,
    bgColor: 'bg-amber-50',
    textColor: 'text-amber-700',
    borderColor: 'border-amber-200',
    route: '/current-affairs',
  },
  {
    id: 'resources',
    title: 'UPSC Resources & PDF RAG',
    description: 'Study official UPSC PDFs and generate grounded practice questions.',
    category: 'Knowledge Base',
    buttonText: 'Explore Resources →',
    icon: BookOpen,
    bgColor: 'bg-blue-50',
    textColor: 'text-blue-700',
    borderColor: 'border-blue-200',
    route: '/resources',
  },
  {
    id: 'daf',
    title: 'DAF Personalization',
    description: 'Practice questions tailored to your optional subject, hobbies, and state.',
    category: 'Personalized',
    buttonText: 'Update DAF Profile →',
    icon: UserCheck,
    bgColor: 'bg-emerald-50',
    textColor: 'text-emerald-700',
    borderColor: 'border-emerald-200',
    route: '/profile',
  },
];

export default function PracticeCard() {
  const navigate = useNavigate();

  return (
    <div className="space-y-4">
      {/* SECTION HEADER */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-[#0B1628] tracking-tight">
          Today's Practice Focus
        </h3>
        <button
          onClick={() => navigate('/question-bank')}
          className="text-xs font-semibold text-slate-500 hover:text-[#0B1628] flex items-center gap-1 transition-colors cursor-pointer"
        >
          <span>Question Bank</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* 3 CARDS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {practiceModules.map((card, idx) => {
          const Icon = card.icon;

          return (
            <motion.div
              key={card.id}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: idx * 0.08 }}
              whileHover={{ y: -3 }}
              onClick={() => navigate(card.route)}
              className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs hover:shadow-md transition-all duration-200 flex flex-col justify-between group cursor-pointer"
            >
              <div className="space-y-3">
                {/* ICON CONTAINER & CATEGORY */}
                <div className="flex items-center justify-between">
                  <div className={`w-10 h-10 rounded-xl ${card.bgColor} ${card.textColor} border ${card.borderColor} flex items-center justify-center transition-transform group-hover:scale-105`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className="text-[11px] font-semibold text-slate-400 group-hover:text-slate-600 transition-colors">
                    {card.category}
                  </span>
                </div>

                {/* TITLE & DESCRIPTION */}
                <div>
                  <h4 className="text-sm font-bold text-[#0B1628] group-hover:text-amber-600 transition-colors">
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
