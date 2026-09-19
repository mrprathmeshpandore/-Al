import React from 'react';
import { motion } from 'framer-motion';

export default function SatyamevGlow() {
  return (
    <div className="absolute inset-0 pointer-events-none z-0 overflow-hidden">
      {/* Primary Warm Golden Glow Radial Layer */}
      <motion.div
        className="absolute top-[68%] left-[64%] -translate-x-1/2 -translate-y-1/2 w-[340px] h-[340px] rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(251, 191, 36, 0.45) 0%, rgba(245, 158, 11, 0.25) 45%, rgba(217, 119, 6, 0.05) 75%, transparent 100%)',
          filter: 'blur(35px)',
        }}
        initial={{ opacity: 0.15, scale: 0.9 }}
        animate={{
          opacity: [0.15, 0.45, 0.15],
          scale: [0.9, 1.08, 0.9],
        }}
        transition={{
          duration: 5.5,
          ease: "easeInOut",
          repeat: Infinity,
        }}
      />

      {/* Secondary Soft Ambient Sunlight Diffusion behind Lion Top */}
      <motion.div
        className="absolute top-[35%] left-[68%] -translate-x-1/2 -translate-y-1/2 w-[420px] h-[420px] rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(254, 240, 138, 0.35) 0%, rgba(253, 224, 71, 0.15) 50%, transparent 80%)',
          filter: 'blur(50px)',
        }}
        initial={{ opacity: 0.2, scale: 0.95 }}
        animate={{
          opacity: [0.2, 0.4, 0.2],
          scale: [0.95, 1.05, 0.95],
        }}
        transition={{
          duration: 7,
          ease: "easeInOut",
          repeat: Infinity,
          delay: 1,
        }}
      />
    </div>
  );
}
