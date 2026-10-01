import React, { useState, useEffect } from 'react';
import { useLocation, Navigate, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import InterviewHeroCard from '../components/dashboard/InterviewHeroCard';
import PracticeCard from '../components/dashboard/PracticeCard';
import ProgressStatCard from '../components/dashboard/ProgressStatCard';
import PerformanceCard from '../components/dashboard/PerformanceCard';
import RecentInterviewsCard from '../components/dashboard/RecentInterviewsCard';
import CurrentAffairsCard from '../components/dashboard/CurrentAffairsCard';
import { analyticsApi } from '../services/analyticsApi';

export default function DashboardPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const currentTab = new URLSearchParams(location.search).get('tab') || 'dashboard';

  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        setLoading(true);
        const data = await analyticsApi.getAnalyticsDashboard();
        setDashboardData(data);
      } catch (err) {
        console.error('Failed to load dashboard analytics:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  // Direct redirects for tab query params to ensure actual feature pages render
  if (currentTab === 'settings') return <Navigate to="/settings" replace />;
  if (currentTab === 'progress') return <Navigate to="/progress" replace />;
  if (currentTab === 'resources') return <Navigate to="/resources" replace />;
  if (currentTab === 'profile') return <Navigate to="/profile" replace />;
  if (currentTab === 'interview') return <Navigate to="/interview" replace />;
  if (currentTab === 'question-bank') return <Navigate to="/question-bank" replace />;
  if (currentTab === 'current-affairs') return <Navigate to="/current-affairs" replace />;

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* MAIN DASHBOARD OVERVIEW */}
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.4 }}
          className="space-y-8"
        >
          {/* PRIMARY AI INTERVIEW HERO BANNER */}
          <InterviewHeroCard 
            onStartInterview={() => navigate('/interview')} 
          />

          {/* DASHBOARD GRID LAYOUT */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            
            {/* LEFT MAIN COLUMN (8 cols on desktop) */}
            <div className="lg:col-span-8 space-y-8">
              {/* TODAY'S PRACTICE MODULES */}
              <PracticeCard />

              {/* YOUR PROGRESS STATISTICS */}
              <ProgressStatCard overview={dashboardData?.overview} />

              {/* INTERVIEW PERFORMANCE ANALYTICS */}
              <PerformanceCard skillData={dashboardData?.skills} />

              {/* RECENT INTERVIEWS */}
              <RecentInterviewsCard recentInterviews={dashboardData?.recent_interviews} />
            </div>

            {/* RIGHT COLUMN (4 cols on desktop) */}
            <div className="lg:col-span-4 space-y-8">
              {/* TODAY'S CURRENT AFFAIRS */}
              <CurrentAffairsCard />
            </div>

          </div>
        </motion.div>
      </div>
    </DashboardLayout>
  );
}
