import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';
import { heroBadgeVariant } from '../utils/animations';

export default function HeroBadge() {
  return (
    <motion.div
      variants={heroBadgeVariant}
      initial="hidden"
      animate="visible"
      className="inline-flex items-center gap-2 bg-[#FAF4EA]/95 backdrop-blur-xs border border-[#E9DFCE] px-3.5 py-1.5 rounded-full w-fit shadow-xs"
    >
      <div className="w-4 h-4 rounded-full bg-[#E86A24]/10 text-[#E86A24] flex items-center justify-center">
        <Sparkles className="w-2.5 h-2.5" />
      </div>
      <span className="text-xs font-semibold text-[#0B1628] tracking-wide">
        AI-Powered UPSC Interview Preparation
      </span>
    </motion.div>
  );
}
