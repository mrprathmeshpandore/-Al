import React from 'react';
import { motion } from 'framer-motion';

export default function HeroHeading() {
  return (
    <div className="space-y-1">
      <motion.h1
        initial={{ opacity: 0, y: 25 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
        className="font-marathi text-4xl sm:text-5xl lg:text-[58px] font-black text-[#0B1628] leading-[1.12] tracking-tight"
      >
        प्रश्नांची नाही,
      </motion.h1>

      <motion.h1
        initial={{ opacity: 0, y: 25 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.28, ease: [0.16, 1, 0.3, 1] }}
        className="font-marathi text-4xl sm:text-5xl lg:text-[58px] font-black leading-[1.12] tracking-tight"
      >
        <span className="text-[#D97706]">विचारांची</span>{' '}
        <span className="text-[#0B1628]">तयारी.</span>
      </motion.h1>
    </div>
  );
}
