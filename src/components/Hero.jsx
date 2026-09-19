import React from 'react';
import { motion } from 'framer-motion';
import HeroBackground from './HeroBackground';
import HeroBadge from './HeroBadge';
import HeroHeading from './HeroHeading';
import HeroCTA from './HeroCTA';
import AspirantStack from './AspirantStack';
import HeroPrinciples from './HeroPrinciples';
import DynamicHeroMessage from './DynamicHeroMessage';

export default function Hero() {
  return (
    <section className="relative min-h-[620px] lg:min-h-[680px] flex flex-col justify-between overflow-hidden px-4 lg:px-12 pt-6 pb-20 bg-[#FBF9F5]">
      
      {/* ---------------------------------------------------- */}
      {/* 1. CINEMATIC BACKGROUND LAYER (IMAGE 3 BACKDROP)     */}
      {/* ---------------------------------------------------- */}
      <HeroBackground />

      {/* ---------------------------------------------------- */}
      {/* 2. MAIN HERO CONTENT GRID (HTML INTERACTIVE LAYER)   */}
      {/* ---------------------------------------------------- */}
      <div className="max-w-7xl mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-8 items-center z-10 relative pt-2">

        {/* LEFT COLUMN: BADGE, MARATHI HEADING, CTAS, AVATARS, PRINCIPLES */}
        <div className="lg:col-span-7 flex flex-col justify-center space-y-5">
          
          {/* AI Badge */}
          <HeroBadge />

          {/* Marathi Heading matching Image 2 typography */}
          <HeroHeading />

          {/* Subheading Tagline & Description */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.35, ease: [0.16, 1, 0.3, 1] }}
            className="space-y-2 max-w-lg"
          >
            <h2 className="text-base sm:text-lg font-bold text-[#1E293B] tracking-tight">
              Smart Practice. Deeper Thinking. A Stronger You.
            </h2>
            <p className="text-xs sm:text-sm text-[#475569] leading-relaxed font-normal">
              <strong className="font-semibold text-[#0F172A]">प्रशासक AI</strong> helps you prepare for the UPSC interview with AI-powered question generation, personalized feedback, and real-world perspectives.
            </p>
          </motion.div>

          {/* CTAs */}
          <HeroCTA />

          {/* Aspirant Avatars */}
          <AspirantStack />

          {/* 4 Hero Principles (Learn Deeper, Think Broader, Answer Better, Serve Greater) */}
          <HeroPrinciples />

        </div>

        {/* RIGHT COLUMN: SPACER FOR BACKGROUND LION CAPITAL & BOTTOM-RIGHT DYNAMIC CARD */}
        <div className="lg:col-span-5 flex flex-col justify-end items-end min-h-[220px] lg:min-h-[460px] relative">
          {/* Dynamic "तुमच्या स्वप्नातील भारतासाठी !" Card placed at bottom right of Hero */}
          <div className="w-full mt-auto pt-6 lg:pt-0">
            <DynamicHeroMessage />
          </div>
        </div>

      </div>

    </section>
  );
}
