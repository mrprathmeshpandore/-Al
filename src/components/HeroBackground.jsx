import React from 'react';
import { motion } from 'framer-motion';
import { useMouseParallax } from '../hooks/useMouseParallax';
import SatyamevGlow from './SatyamevGlow';

export default function HeroBackground() {
  const mousePos = useMouseParallax();

  return (
    <div className="absolute inset-0 w-full h-full pointer-events-none z-0 overflow-hidden">
      {/* 1. CINEMATIC BACKGROUND IMAGE LAYER WITH MOUSE PARALLAX */}
      <motion.div
        className="absolute inset-0 w-full h-full"
        style={{
          x: mousePos.x * 4,
          y: mousePos.y * 3,
        }}
        initial={{ opacity: 0, scale: 1.02 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1, ease: "easeOut" }}
      >
        <img
          src="/hero_background.jpg"
          alt="Prashasak AI Hero Cinematic Background"
          className="w-full h-full object-cover object-center lg:object-[65%_center] transition-all duration-700"
          onError={(e) => {
            e.target.src = '/hero_clean_canvas.jpg';
          }}
        />
      </motion.div>

      {/* 2. SATYAMEV JAYATE GOLDEN LIGHT GLOW ANIMATION */}
      <SatyamevGlow />

      {/* 3. SOFT LOCAL GRADIENT OVERLAY FOR TEXT READABILITY */}
      <div 
        className="absolute inset-0 z-1 pointer-events-none"
        style={{
          background: `linear-gradient(
            90deg,
            rgba(251, 249, 245, 0.96) 0%,
            rgba(251, 249, 245, 0.88) 32%,
            rgba(251, 249, 245, 0.45) 58%,
            rgba(251, 249, 245, 0.08) 78%,
            transparent 100%
          )`,
        }}
      />

      {/* Mobile/Tablet Fallback Soft Vignette */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#FBF9F5]/40 via-transparent to-[#FBF9F5]/90 lg:hidden pointer-events-none" />

      {/* 4. SOFT BOTTOM TRANSITION GRADIENT */}
      <div className="absolute inset-x-0 bottom-0 h-16 bg-gradient-to-t from-[#FBF9F5] via-[#FBF9F5]/60 to-transparent pointer-events-none z-2" />
    </div>
  );
}
