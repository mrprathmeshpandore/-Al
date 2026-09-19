import React from 'react';
import { motion } from 'framer-motion';

export default function ProfileCompletionCard({ percentage }) {
  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-2xs space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-bold text-[#0B1628] font-sans">
          Profile Completion
        </h4>
        <span className="text-sm font-extrabold text-[#0B1628]">
          {percentage}%
        </span>
      </div>

      <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden p-0.5">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="h-full bg-gradient-to-r from-amber-500 to-orange-600 rounded-full"
        />
      </div>
    </div>
  );
}
