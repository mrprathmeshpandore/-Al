import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, Play } from 'lucide-react';
import { buttonTapHover } from '../utils/animations';

export default function HeroCTA() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.45, ease: [0.16, 1, 0.3, 1] }}
      className="flex flex-wrap items-center gap-4 pt-1"
    >
      {/* Primary CTA: Start AI Interview */}
      <Link to="/dashboard">
        <motion.button
          variants={buttonTapHover}
          initial="rest"
          whileHover="hover"
          whileTap="tap"
          className="bg-[#0B1628] hover:bg-[#152744] text-white px-6 py-3.5 rounded-full font-semibold text-sm flex items-center gap-2.5 shadow-md shadow-slate-900/15 transition-all duration-200 cursor-pointer"
        >
          <span>Start AI Interview</span>
          <ArrowRight className="w-4 h-4" />
        </motion.button>
      </Link>

      {/* Secondary CTA: Watch Demo */}
      <motion.button
        variants={buttonTapHover}
        initial="rest"
        whileHover="hover"
        whileTap="tap"
        className="bg-white/95 hover:bg-white text-[#0F172A] border border-[#CBD5E1] px-6 py-3.5 rounded-full font-semibold text-sm flex items-center gap-2.5 shadow-xs transition-all duration-200 cursor-pointer"
      >
        <div className="w-4 h-4 rounded-full bg-slate-100 flex items-center justify-center text-[#0F172A]">
          <Play className="w-2.5 h-2.5 fill-current ml-0.5" />
        </div>
        <span>Watch Demo</span>
      </motion.button>
    </motion.div>
  );
}
