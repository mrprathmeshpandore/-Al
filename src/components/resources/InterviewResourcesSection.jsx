import React from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, UserCheck, Scale, Target, Layout, ArrowRight } from 'lucide-react';
import { interviewResources } from '../../data/resourcesData';

const iconMap = {
  messageSquare: MessageSquare,
  userCheck: UserCheck,
  scale: Scale,
  target: Target,
  layout: Layout
};

export default function InterviewResourcesSection({ onOpenResource }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-serif font-bold text-slate-900 text-lg">Interview Resources</h2>
          <p className="text-xs text-slate-500 font-sans">Prepare specifically for your UPSC interview.</p>
        </div>
        <button className="flex items-center gap-1 text-xs font-semibold text-slate-500 hover:text-amber-800 transition-colors">
          <span>View All</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {interviewResources.map((item, index) => {
          const IconComponent = iconMap[item.icon] || MessageSquare;
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
                  <IconComponent className="w-4 h-4" />
                </div>

                <h3 className="font-serif font-bold text-slate-900 text-xs mb-1.5 group-hover:text-blue-900 transition-colors">
                  {item.title}
                </h3>
                <p className="text-[11px] text-slate-500 font-sans line-clamp-3 leading-relaxed mb-3">
                  {item.description}
                </p>
              </div>

              <div className="pt-2 border-t border-slate-100 flex items-center justify-between">
                <button
                  onClick={() => onOpenResource(item)}
                  className="flex items-center gap-1 text-xs font-bold text-blue-700 hover:text-blue-900 transition-colors"
                >
                  <span>Open</span>
                  <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
                </button>
                <span className="text-[10px] text-slate-400 font-mono">{item.fileSize}</span>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
