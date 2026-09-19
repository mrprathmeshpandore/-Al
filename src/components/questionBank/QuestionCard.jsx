import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Bookmark, ArrowRight } from 'lucide-react';

export default function QuestionCard({ item, onOpenDetail, onToggleBookmark }) {
  const navigate = useNavigate();

  const handlePracticeClick = (e) => {
    e.stopPropagation();
    // Navigate to /interview with question state
    navigate('/interview', {
      state: {
        questionId: item.id,
        question: item.question,
        topic: item.tags?.[0] || item.category,
        categories: item.tags || [item.type],
        source: "QUESTION BANK"
      }
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      onClick={() => onOpenDetail(item)}
      className="bg-white rounded-2xl border border-slate-200/80 shadow-2xs hover:shadow-md transition-all duration-200 overflow-hidden group cursor-pointer p-4 sm:p-5 flex flex-col md:flex-row gap-5 items-stretch"
    >
      {/* LEFT THUMBNAIL IMAGE */}
      <div className="w-full md:w-44 h-36 md:h-auto rounded-xl overflow-hidden bg-slate-900 shrink-0 relative">
        <img
          src={item.image}
          alt={item.question}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          onError={(e) => {
            e.target.src = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&q=80&w=600";
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent pointer-events-none" />
      </div>

      {/* RIGHT MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col justify-between space-y-3">
        
        {/* TOP ROW: BADGES, DATE & BOOKMARK */}
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`text-[10.5px] font-extrabold uppercase px-2.5 py-0.5 rounded border ${item.typeBadgeColor || 'bg-slate-100 text-slate-700'}`}>
              {item.type}
            </span>
            <span className={`text-[10.5px] font-bold px-2.5 py-0.5 rounded border ${item.difficultyBadgeColor || 'bg-amber-100 text-amber-800'}`}>
              {item.difficulty}
            </span>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <span className="text-[11px] font-semibold text-slate-400">
              {item.date}
            </span>
            
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onToggleBookmark(item.id);
              }}
              className={`p-1.5 rounded-full border transition-all cursor-pointer ${
                item.isBookmarked 
                  ? 'bg-amber-500 text-white border-amber-400 shadow-2xs' 
                  : 'bg-slate-50 hover:bg-slate-100 text-slate-400 hover:text-[#0B1628] border-slate-200'
              }`}
              aria-label="Bookmark Question"
            >
              <Bookmark className={`w-3.5 h-3.5 ${item.isBookmarked ? 'fill-current' : ''}`} />
            </button>
          </div>
        </div>

        {/* QUESTION HEADING & DESCRIPTION */}
        <div className="space-y-1">
          <h3 className="text-sm sm:text-base font-bold text-[#0B1628] group-hover:text-amber-600 transition-colors leading-snug">
            "{item.question}"
          </h3>
          <p className="text-xs font-medium text-slate-500 leading-relaxed line-clamp-2">
            {item.description}
          </p>
        </div>

        {/* BOTTOM ROW: TAGS & PRACTICE CTA */}
        <div className="pt-2 border-t border-slate-100 flex items-center justify-between gap-3">
          <div className="flex items-center gap-1.5 flex-wrap">
            {item.tags?.map((tag) => (
              <span key={tag} className="text-[10px] font-semibold text-slate-600 bg-slate-100 border border-slate-200/60 px-2 py-0.5 rounded">
                {tag}
              </span>
            ))}
          </div>

          <button
            type="button"
            onClick={handlePracticeClick}
            className="bg-[#0B1628] hover:bg-[#152744] text-white px-4 py-1.5 rounded-full text-xs font-bold inline-flex items-center gap-1.5 shadow-2xs transition-all cursor-pointer shrink-0"
          >
            <span>Practice</span>
            <ArrowRight className="w-3.5 h-3.5 text-amber-400" />
          </button>
        </div>

      </div>
    </motion.div>
  );
}
