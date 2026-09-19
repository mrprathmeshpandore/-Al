import React from 'react';
import { useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import InterviewHeroCard from '../components/dashboard/InterviewHeroCard';
import PracticeCard from '../components/dashboard/PracticeCard';
import ProgressStatCard from '../components/dashboard/ProgressStatCard';
import PerformanceCard from '../components/dashboard/PerformanceCard';
import RecentInterviewsCard from '../components/dashboard/RecentInterviewsCard';
import CurrentAffairsCard from '../components/dashboard/CurrentAffairsCard';

export default function DashboardPage() {
  const location = useLocation();
  const currentTab = new URLSearchParams(location.search).get('tab') || 'dashboard';

  return (
    <DashboardLayout>
      <div className="space-y-8">
        
        {/* TAB 1: MAIN DASHBOARD OVERVIEW */}
        {currentTab === 'dashboard' && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4 }}
            className="space-y-8"
          >
            {/* PRIMARY AI INTERVIEW HERO BANNER */}
            <InterviewHeroCard 
              onStartInterview={() => alert("Launching AI Interview Session...")} 
            />

            {/* DASHBOARD GRID LAYOUT */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
              
              {/* LEFT MAIN COLUMN (8 cols on desktop) */}
              <div className="lg:col-span-8 space-y-8">
                {/* TODAY'S PRACTICE MODULES */}
                <PracticeCard />

                {/* YOUR PROGRESS STATISTICS */}
                <ProgressStatCard />

                {/* INTERVIEW PERFORMANCE ANALYTICS */}
                <PerformanceCard />

                {/* RECENT INTERVIEWS */}
                <RecentInterviewsCard />
              </div>

              {/* RIGHT COLUMN (4 cols on desktop) */}
              <div className="lg:col-span-4 space-y-8">
                {/* TODAY'S CURRENT AFFAIRS */}
                <CurrentAffairsCard />
              </div>

            </div>
          </motion.div>
        )}

        {/* TAB 2: AI INTERVIEW TAB PLACEHOLDER */}
        {currentTab === 'interview' && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <InterviewHeroCard onStartInterview={() => alert("Launching AI Interview...")} />
            <RecentInterviewsCard />
          </motion.div>
        )}

        {/* TAB 3: QUESTION BANK TAB PLACEHOLDER */}
        {currentTab === 'question-bank' && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="bg-white rounded-2xl p-8 border border-slate-200/80 shadow-2xs">
              <h2 className="text-xl font-bold text-[#0B1628] mb-2">Question Bank</h2>
              <p className="text-slate-600 text-sm mb-6">Explore thousands of curated UPSC interview questions categorized by GS subjects, optional papers, and DAF parameters.</p>
              <PracticeCard />
            </div>
          </motion.div>
        )}

        {/* TAB 4: CURRENT AFFAIRS TAB PLACEHOLDER */}
        {currentTab === 'current-affairs' && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 lg:grid-cols-12 gap-8"
          >
            <div className="lg:col-span-8">
              <CurrentAffairsCard />
            </div>
            <div className="lg:col-span-4">
              <PracticeCard />
            </div>
          </motion.div>
        )}

        {/* OTHER PLACEHOLDER TABS */}
        {['resources', 'progress', 'settings', 'profile'].includes(currentTab) && (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl p-8 border border-slate-200/80 shadow-2xs text-center space-y-3"
          >
            <div className="w-12 h-12 rounded-full bg-amber-500/10 text-amber-600 flex items-center justify-center mx-auto text-xl font-bold">
              🏛️
            </div>
            <h2 className="text-xl font-bold text-[#0B1628] capitalize">{currentTab.replace('-', ' ')} Workspace</h2>
            <p className="text-slate-500 text-sm max-w-md mx-auto">This module is part of your Prashasak AI suite. You can navigate back to your main preparation dashboard anytime.</p>
            <a 
              href="/dashboard" 
              className="inline-block mt-4 bg-[#0B1628] text-white px-5 py-2.5 rounded-full text-xs font-bold hover:bg-[#152744] transition-colors"
            >
              Back to Dashboard
            </a>
          </motion.div>
        )}

      </div>
    </DashboardLayout>
  );
}
