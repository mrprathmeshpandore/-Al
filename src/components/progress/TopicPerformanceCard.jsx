import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ChevronDown, Landmark, Scale, BookOpen, TrendingUp, Globe } from 'lucide-react';
import { topicPerformance } from '../../data/progressData';

const iconMap = {
  landmark: Landmark,
  scale: Scale,
  bookOpen: BookOpen,
  trendingUp: TrendingUp,
  globe: Globe
};

export default function TopicPerformanceCard() {
  const navigate = useNavigate();
  const [selectedFilter, setSelectedFilter] = useState('All Topics');
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const filterOptions = ['All Topics', 'GS I', 'GS II', 'GS III', 'GS IV', 'Current Affairs', 'DAF'];

  const handleTopicClick = (topicId) => {
    navigate(`/question-bank?topic=${topicId}`);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="bg-white rounded-2xl p-6 border border-amber-950/5 shadow-sm flex flex-col justify-between"
    >
      {/* Header & Dropdown */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-serif font-bold text-slate-900 text-lg">Topic Performance</h3>
          <p className="text-xs text-slate-500 font-sans">Proficiency levels across subject areas</p>
        </div>

        <div className="relative">
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-medium text-slate-700 bg-slate-50/50 hover:bg-slate-100 transition-colors"
          >
            {selectedFilter}
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {dropdownOpen && (
            <div className="absolute right-0 mt-1 w-36 bg-white border border-slate-200 rounded-xl shadow-lg py-1 z-20">
              {filterOptions.map((option) => (
                <button
                  key={option}
                  onClick={() => {
                    setSelectedFilter(option);
                    setDropdownOpen(false);
                  }}
                  className={`w-full text-left px-3 py-1.5 text-xs ${
                    selectedFilter === option
                      ? 'bg-amber-50 text-amber-900 font-semibold'
                      : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Topic Rows */}
      <div className="space-y-3.5 my-auto">
        {topicPerformance.map((topic, index) => {
          const IconComponent = iconMap[topic.icon] || Landmark;
          return (
            <div
              key={topic.id}
              onClick={() => handleTopicClick(topic.id)}
              className="group flex items-center justify-between gap-3 p-2 rounded-xl hover:bg-slate-50 transition-colors cursor-pointer"
            >
              <div className="flex items-center gap-2.5 min-w-[150px]">
                <div className="p-1.5 rounded-lg bg-slate-100 text-slate-600 group-hover:bg-amber-100 group-hover:text-amber-800 transition-colors">
                  <IconComponent className="w-4 h-4" />
                </div>
                <span className="text-xs font-semibold text-slate-800 group-hover:text-amber-900 transition-colors">
                  {topic.label}
                </span>
              </div>

              <div className="flex-1 flex items-center gap-3">
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    whileInView={{ width: `${topic.score}%` }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: index * 0.1, ease: 'easeOut' }}
                    className={`h-full ${topic.color} rounded-full`}
                  />
                </div>
                <span className="text-xs font-bold text-slate-900 w-8 text-right font-sans">
                  {topic.score}%
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}
