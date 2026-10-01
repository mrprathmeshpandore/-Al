import React from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, UserCheck, Scale, Target, Layout, ArrowRight } from 'lucide-react';

const iconMap = {
  messageSquare: MessageSquare,
  userCheck: UserCheck,
  scale: Scale,
  target: Target,
  layout: Layout
};

export default function InterviewResourcesSection({ onOpenResource, resources = [], isLoading }) {
  // Filter interview-related resources from backend list
  const interviewItems = resources.filter(
    (res) =>
      res.category?.toLowerCase().includes('interview') ||
      res.category?.toLowerCase().includes('daf') ||
      res.subject?.toLowerCase().includes('interview') ||
      res.subject?.toLowerCase().includes('daf')
  );

  const displayItems = interviewItems.length > 0 ? interviewItems.slice(0, 5) : [];

  if (isLoading) {
    return (
      <div className="space-y-4">
        <h2 className="font-serif font-bold text-slate-900 text-lg">Interview Resources</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {[1, 2, 3, 4, 5].map((n) => (
            <div key={n} className="bg-white rounded-2xl p-4 border border-slate-100 animate-pulse h-36 space-y-2">
              <div className="w-8 h-8 rounded-xl bg-slate-100" />
              <div className="h-3.5 bg-slate-100 rounded w-3/4" />
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
            <h2 className="font-serif font-bold text-slate-900 text-lg">Interview Resources</h2>
            <p className="text-xs text-slate-500 font-sans">Prepare specifically for your UPSC interview.</p>
          </div>
        </div>
        <div className="p-6 bg-white rounded-2xl border border-amber-950/5 text-center text-slate-500 text-xs font-sans">
          No interview resources found for this filter.
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-serif font-bold text-slate-900 text-lg">Interview Resources</h2>
          <p className="text-xs text-slate-500 font-sans">Prepare specifically for your UPSC interview.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {displayItems.map((item, index) => {
          return (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className="bg-white rounded-2xl p-4 border border-amber-950/5 shadow-2xs hover:shadow-md transition-all flex flex-col justify-between group"
            >
              <div>
                <div className="w-8 h-8 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-xs mb-3 group-hover:bg-blue-100 transition-colors">
                  <MessageSquare className="w-4 h-4" />
                </div>

                <h3 className="font-serif font-bold text-slate-900 text-xs mb-1.5 group-hover:text-blue-900 transition-colors line-clamp-2">
                  {item.title}
                </h3>
                <p className="text-[11px] text-slate-500 font-sans line-clamp-3 leading-relaxed mb-3">
                  {item.description}
                </p>
              </div>

              <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                <button
                  onClick={() => onOpenResource(item)}
                  className="flex items-center gap-1 text-xs font-bold text-blue-700 hover:text-blue-900 transition-colors cursor-pointer"
                >
                  <span>Open</span>
                  <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
                </button>
                <span className="text-[10px] text-slate-400 font-mono">
                  {item.resource_type ? item.resource_type.toUpperCase() : 'PDF'}
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
