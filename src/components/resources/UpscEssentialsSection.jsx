import React from 'react';
import { motion } from 'framer-motion';
import { Bookmark, ArrowRight, FileText, CheckCircle2, Shield } from 'lucide-react';

export default function UpscEssentialsSection({ onOpenResource, onToggleBookmark, savedIds = [], resources = [], isLoading }) {
  // If resources are passed from parent, use them; otherwise fallback to empty list
  const displayItems = resources.length > 0 ? resources.slice(0, 4) : [];

  if (isLoading) {
    return (
      <div className="space-y-4">
        <h2 className="font-serif font-bold text-slate-900 text-lg">UPSC Essentials</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((n) => (
            <div key={n} className="bg-white rounded-2xl p-4 border border-slate-100 animate-pulse h-44 space-y-3">
              <div className="w-8 h-8 rounded-xl bg-slate-100" />
              <div className="h-4 bg-slate-100 rounded w-3/4" />
              <div className="h-3 bg-slate-100 rounded w-full" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (displayItems.length === 0) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-serif font-bold text-slate-900 text-lg">UPSC Essentials</h2>
            <p className="text-xs text-slate-500 font-sans">Start with the most important official resources.</p>
          </div>
        </div>
        <div className="p-6 bg-white rounded-2xl border border-amber-950/5 text-center text-slate-500 text-xs font-sans">
          No official essential resources found for this filter.
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-serif font-bold text-slate-900 text-lg">UPSC Essentials</h2>
          <p className="text-xs text-slate-500 font-sans">Start with the most important built-in official resources.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {displayItems.map((res, index) => {
          const isBookmarked = savedIds.includes(res.id);
          return (
            <motion.div
              key={res.id}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.08 }}
              className="bg-white rounded-2xl p-4 border border-amber-950/5 shadow-2xs hover:shadow-md transition-all flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-9 h-9 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center font-bold text-xs group-hover:bg-amber-100 transition-colors">
                    <FileText className="w-4 h-4" />
                  </div>
                  <button
                    onClick={() => onToggleBookmark(res.id)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-amber-600 hover:bg-amber-50 transition-colors cursor-pointer"
                  >
                    <Bookmark className={`w-4 h-4 ${isBookmarked ? 'fill-amber-500 text-amber-500' : ''}`} />
                  </button>
                </div>

                <h3 className="font-serif font-bold text-slate-900 text-sm mb-1 group-hover:text-amber-900 transition-colors line-clamp-2">
                  {res.title}
                </h3>
                <p className="text-xs text-slate-500 font-sans line-clamp-2 leading-relaxed mb-3">
                  {res.description}
                </p>

                <div className="flex items-center gap-1.5 mb-4">
                  <span className="px-2 py-0.5 rounded-md bg-amber-50 text-[10px] font-semibold text-amber-800 border border-amber-200/60">
                    {res.subject || res.category}
                  </span>
                  <span className="px-2 py-0.5 rounded-md bg-slate-100 text-[10px] font-semibold text-slate-600">
                    {res.resource_type ? res.resource_type.toUpperCase() : 'PDF'}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-slate-100">
                <button
                  onClick={() => onOpenResource(res)}
                  className="flex items-center gap-1 text-xs font-bold text-slate-800 hover:text-amber-700 transition-colors cursor-pointer"
                >
                  <span>Open</span>
                  <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
                </button>
                {res.is_official && (
                  <span className="flex items-center gap-1 text-[10px] text-emerald-600 font-medium">
                    <CheckCircle2 className="w-3 h-3" /> Official
                  </span>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
