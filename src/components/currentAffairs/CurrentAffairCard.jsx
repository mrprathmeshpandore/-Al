import React from 'react';
import { motion } from 'framer-motion';
import { Bookmark, ChevronRight, Calendar } from 'lucide-react';

export default function CurrentAffairCard({ item, onOpenDetail, onToggleBookmark }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -3 }}
      onClick={() => onOpenDetail(item)}
      className="bg-white rounded-2xl border border-slate-200/80 shadow-2xs hover:shadow-md transition-all duration-200 flex flex-col justify-between overflow-hidden group cursor-pointer relative"
    >
      {/* THUMBNAIL IMAGE & BOOKMARK OVERLAY */}
      <div className="relative h-40 w-full bg-slate-900 overflow-hidden">
        <img
          src={item.image}
          alt={item.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          onError={(e) => {
            e.target.src = "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&q=80&w=600";
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent pointer-events-none" />

        {/* BOOKMARK BUTTON OVERLAY */}
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onToggleBookmark(item.id);
          }}
          className={`absolute top-3 right-3 p-2 rounded-full backdrop-blur-md border transition-all cursor-pointer ${
            item.isBookmarked 
              ? 'bg-amber-500 text-white border-amber-400 shadow-md' 
              : 'bg-white/80 text-slate-700 hover:text-[#0B1628] border-white/60 hover:bg-white'
          }`}
          aria-label="Bookmark Current Affair"
        >
          <Bookmark className={`w-3.5 h-3.5 ${item.isBookmarked ? 'fill-current' : ''}`} />
        </button>
      </div>

      {/* CARD BODY CONTENT */}
      <div className="p-5 flex-1 flex flex-col justify-between space-y-3">
        <div className="space-y-1.5">
          <span className="text-[11px] font-semibold text-slate-400 flex items-center gap-1">
            <Calendar className="w-3 h-3 text-slate-400" />
            <span>{item.date}</span>
          </span>

          <h3 className="text-sm font-bold text-[#0B1628] group-hover:text-amber-600 transition-colors line-clamp-2 leading-snug">
            {item.title}
          </h3>
        </div>

        {/* FOOTER: TAGS & ARROW LINK */}
        <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-[10.5px] font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded">
              {item.categoryLabel}
            </span>
            <span className="text-[10.5px] font-medium text-slate-400">
              · {item.subcategory}
            </span>
          </div>

          <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-[#0B1628] group-hover:translate-x-1 transition-all shrink-0 ml-1" />
        </div>
      </div>

    </motion.div>
  );
}
