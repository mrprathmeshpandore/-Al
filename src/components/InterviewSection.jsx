import React from 'react';
import { motion } from 'framer-motion';
import { Play, UserCheck, Newspaper, MessageSquareCode, TrendingUp, ArrowRight } from 'lucide-react';
import { iconInteractiveHover } from '../utils/animations';

export default function InterviewSection() {
  const featureList = [
    {
      icon: UserCheck,
      iconBg: 'bg-blue-600',
      title: 'Profile Based Questions',
      description: 'Personalized questions from your DAF',
    },
    {
      icon: Newspaper,
      iconBg: 'bg-[#B45309]',
      title: 'Current Affairs Integration',
      description: 'Latest news, deeper insights, relevant questions',
    },
    {
      icon: MessageSquareCode,
      iconBg: 'bg-blue-600',
      title: 'AI Feedback & Evaluation',
      description: 'Improve your answers with detailed feedback',
    },
    {
      icon: TrendingUp,
      iconBg: 'bg-teal-600',
      title: 'Performance Analytics',
      description: 'Track progress and identify weak areas',
    },
  ];

  return (
    <section className="max-w-7xl mx-auto px-4 lg:px-12 py-12 z-10 relative">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
        
        {/* LEFT COLUMN: LARGE VIDEO INTERVIEW CARD (Slides in X: -60 -> 0) */}
        <motion.div
          initial={{ opacity: 0, x: -60 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
          className="lg:col-span-5 relative group"
        >
          <div className="relative rounded-3xl overflow-hidden shadow-2xl border border-slate-200/80 bg-slate-900 aspect-[4/3] sm:aspect-[16/11]">
            <img
              src="/ias_interview.png"
              alt="AI Interview Simulation Panelist - प्रशासक AI"
              className="w-full h-full object-cover object-center group-hover:scale-1.03 transition-transform duration-700"
              onError={(e) => {
                e.target.src = '/reference_original.jpg';
              }}
            />
            
            {/* Dark Gradient Overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent pointer-events-none" />

            {/* Center Pulsing Play Button Overlay */}
            <div className="absolute inset-0 flex items-center justify-center">
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                className="relative w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-white/20 backdrop-blur-md border border-white/40 text-white flex items-center justify-center shadow-2xl group-hover:bg-white/30 transition-all cursor-pointer"
              >
                {/* Ripple ring */}
                <span className="absolute inset-0 rounded-full bg-white/30 animate-ping opacity-40 pointer-events-none" />
                <div className="w-12 h-12 rounded-full bg-white text-[#0B1628] flex items-center justify-center shadow-lg ml-0.5">
                  <Play className="w-6 h-6 fill-current" />
                </div>
              </motion.button>
            </div>

            {/* Bottom Floating Tag overlay */}
            <div className="absolute bottom-4 left-4 right-4 bg-black/40 backdrop-blur-md border border-white/10 p-4 rounded-2xl text-white">
              <h4 className="text-sm font-bold tracking-tight">
                AI Interview Simulation
              </h4>
              <p className="text-xs text-slate-300 mt-0.5 leading-snug">
                Experience a realistic UPSC interview with our advanced AI panel.
              </p>
            </div>

          </div>
        </motion.div>

        {/* RIGHT COLUMN: SECTION HEADER & 4 FEATURE GRID CARDS */}
        <div className="lg:col-span-7 flex flex-col justify-center space-y-6">
          
          {/* Header & View All Link */}
          <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 border-b border-slate-200/60 pb-4">
            <div>
              <span className="text-xs font-bold tracking-wider text-[#E86A24] uppercase flex items-center gap-1">
                <span className="h-0.5 w-4 bg-[#E86A24] rounded-full inline-block" /> FEATURES
              </span>
              <h2 className="text-2xl sm:text-3xl font-extrabold text-[#0F172A] mt-1 tracking-tight">
                Everything You Need<br />For Your UPSC Interview
              </h2>
            </div>

            <motion.a
              whileHover={{ x: 3 }}
              href="#all-features"
              className="text-xs font-bold text-[#0B1628] hover:text-[#E86A24] flex items-center gap-1 transition-colors self-start sm:self-end"
            >
              <span>View All Features</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </motion.a>
          </div>

          {/* 4 Feature Cards Grid */}
          <motion.div
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            variants={{
              hidden: {},
              visible: {
                transition: {
                  staggerChildren: 0.1,
                  delayChildren: 0.15,
                },
              },
            }}
            className="grid grid-cols-1 sm:grid-cols-2 gap-4"
          >
            {featureList.map((feat, index) => {
              const Icon = feat.icon;
              return (
                <motion.div
                  key={index}
                  variants={{
                    hidden: { opacity: 0, y: 30 },
                    visible: {
                      opacity: 1,
                      y: 0,
                      transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] },
                    },
                  }}
                  whileHover={{ y: -4, transition: { duration: 0.2 } }}
                  className="bg-white rounded-2xl p-5 border border-slate-200/80 card-shadow flex flex-col justify-between group cursor-pointer"
                >
                  <div className="space-y-3">
                    {/* Feature Icon with max 3 deg hover rotation */}
                    <motion.div
                      variants={iconInteractiveHover}
                      initial="rest"
                      whileHover="hover"
                      className={`w-11 h-11 rounded-full ${feat.iconBg} text-white flex items-center justify-center shadow-md shadow-slate-900/10`}
                    >
                      <Icon className="w-5 h-5" />
                    </motion.div>

                    <div>
                      <h3 className="text-sm font-bold text-[#0F172A] group-hover:text-[#E86A24] transition-colors">
                        {feat.title}
                      </h3>
                      <p className="text-xs text-[#64748B] mt-1 leading-relaxed">
                        {feat.description}
                      </p>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </motion.div>

        </div>

      </div>
    </section>
  );
}
