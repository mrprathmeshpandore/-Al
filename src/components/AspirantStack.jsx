import React from 'react';
import { motion } from 'framer-motion';

export default function AspirantStack() {
  const avatars = [
    '/avatar_1.png',
    '/avatar_2.png',
    '/avatar_3.png',
    '/avatar_4.png',
    '/avatar_5.png',
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.55, ease: [0.16, 1, 0.3, 1] }}
      className="flex items-center gap-3 pt-1"
    >
      <div className="flex -space-x-2 overflow-hidden py-0.5">
        {avatars.map((src, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, scale: 0.7 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{
              duration: 0.35,
              delay: 0.6 + i * 0.07,
              ease: "backOut",
            }}
            className="inline-block h-7 w-7 rounded-full ring-2 ring-white overflow-hidden bg-slate-200 shadow-xs"
          >
            <img
              src={src}
              alt={`Aspirant ${i + 1}`}
              className="h-full w-full object-cover"
            />
          </motion.div>
        ))}
      </div>

      <div className="text-xs text-[#475569] leading-tight">
        <span className="font-bold text-[#0F172A] block sm:inline">10,000+ UPSC Aspirants </span>
        <span className="text-[#64748B]">are preparing smarter with <strong className="font-semibold text-[#0F172A]">प्रशासक AI</strong></span>
      </div>
    </motion.div>
  );
}
