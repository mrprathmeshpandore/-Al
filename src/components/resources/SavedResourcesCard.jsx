import React from 'react';
import { motion } from 'framer-motion';
import { Bookmark, FileText, ArrowRight, BookOpen } from 'lucide-react';
import { savedResourcesList } from '../../data/resourcesData';

export default function SavedResourcesCard({ onToggleBookmark, savedIds, onOpenResource }) {
  return (
    <div className="space-y-4">
      {/* Saved Resources List Card */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.3 }}
        className="bg-white rounded-2xl p-5 border border-amber-950/5 shadow-2xs flex flex-col justify-between"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-serif font-bold text-slate-900 text-base">Saved Resources</h3>
          <button className="flex items-center gap-1 text-xs font-semibold text-slate-500 hover:text-amber-800 transition-colors">
            <span>View All</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="space-y-3">
          {savedResourcesList.map((item) => {
            const isSaved = savedIds.includes(item.id);
            return (
              <div
                key={item.id}
                className="flex items-center justify-between p-2.5 rounded-xl hover:bg-slate-50 transition-colors border border-slate-100/80 group"
              >
                <div
                  onClick={() => onOpenResource && onOpenResource(item)}
                  className="flex items-center gap-3 cursor-pointer flex-1 min-w-0"
                >
                  <div className="p-2 rounded-lg bg-amber-50 text-amber-600 group-hover:bg-amber-100 transition-colors shrink-0">
                    {item.type === 'Article' ? <BookOpen className="w-4 h-4" /> : <FileText className="w-4 h-4" />}
                  </div>
                  <div className="truncate">
                    <h4 className="text-xs font-bold text-slate-800 group-hover:text-amber-900 transition-colors truncate">
                      {item.title}
                    </h4>
                    <span className="text-[10.5px] text-slate-400 font-medium font-sans">
                      {item.info}
                    </span>
                  </div>
                </div>

                <button
                  onClick={() => onToggleBookmark(item.id)}
                  className="p-1.5 text-amber-600 hover:text-amber-800 transition-colors shrink-0"
                >
                  <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-amber-500 text-amber-500' : 'text-slate-300'}`} />
                </button>
              </div>
            );
          })}
        </div>
      </motion.div>

      {/* Inspirational Quote Card at Bottom Right */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.4 }}
        className="relative overflow-hidden rounded-2xl p-5 border border-amber-900/10 bg-gradient-to-br from-amber-50/80 via-white to-amber-100/40 shadow-2xs"
      >
        <div className="relative z-10 space-y-1">
          <span className="text-amber-700 font-serif text-2xl font-black leading-none block">“</span>
          <p className="font-serif italic font-bold text-slate-800 text-sm leading-relaxed">
            The more you learn, the better you serve.
          </p>
          <span className="text-[10px] font-sans font-semibold text-amber-900/70 tracking-wider uppercase block pt-1">
            — PRASHASAK AI MOTTO
          </span>
        </div>
      </motion.div>
    </div>
  );
}
