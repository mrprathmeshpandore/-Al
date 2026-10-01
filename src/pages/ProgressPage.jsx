import React, { useState, useEffect } from 'react';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import ProgressHeader from '../components/progress/ProgressHeader';
import ProgressTopStats from '../components/progress/ProgressTopStats';
import PerformanceChartCard from '../components/progress/PerformanceChartCard';
import SkillAnalysisCard from '../components/progress/SkillAnalysisCard';
import TopicPerformanceCard from '../components/progress/TopicPerformanceCard';
import FocusAreasCard from '../components/progress/FocusAreasCard';
import AiRecommendationCard from '../components/progress/AiRecommendationCard';
import PracticeActivityCard from '../components/progress/PracticeActivityCard';
import AchievementsCard from '../components/progress/AchievementsCard';
import RecentActivityCard from '../components/progress/RecentActivityCard';
import ProgressInsightCard from '../components/progress/ProgressInsightCard';
import { analyticsApi } from '../services/analyticsApi';

export default function ProgressPage() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadAnalytics() {
      try {
        setLoading(true);
        const data = await analyticsApi.getAnalyticsDashboard();
        setDashboard(data);
      } catch (err) {
        setError(err.message || 'Failed to load analytics');
      } finally {
        setLoading(false);
      }
    }
    loadAnalytics();
  }, []);

  const topStats = dashboard ? {
    questionsPracticed: {
      value: dashboard.overview.total_questions_practiced,
      label: 'Questions Practiced',
      icon: 'messageSquare',
      trend: `${dashboard.overview.total_answers} Total Answers`,
    },
    interviewsCompleted: {
      value: dashboard.overview.total_interviews_completed,
      label: 'Interviews Completed',
      icon: 'users',
      trend: `${dashboard.overview.total_interviews_started} Started`,
    },
    averageScore: {
      value: dashboard.overview.average_score != null ? `${dashboard.overview.average_score}/10` : '—',
      label: 'Average Score',
      icon: 'barChart',
      trend: dashboard.overview.total_evaluated_answers > 0 ? `${dashboard.overview.total_evaluated_answers} Evaluated` : 'No evaluations yet',
    },
    dayStreak: {
      value: `${dashboard.overview.current_streak} Days`,
      label: 'Day Streak',
      icon: 'flame',
      badge: `Best: ${dashboard.overview.longest_streak} Days`,
    }
  } : undefined;

  return (
    <DashboardLayout>
      <div className="space-y-6 pb-12">
        {/* Page Header */}
        <ProgressHeader />

        {loading ? (
          <div className="p-12 text-center text-slate-500 font-semibold bg-white rounded-2xl border border-slate-200">
            <div className="w-10 h-10 border-4 border-amber-500/20 border-t-amber-600 rounded-full animate-spin mx-auto mb-3" />
            <p className="text-xs">Loading Candidate Analytics Engine...</p>
          </div>
        ) : error ? (
          <div className="p-8 text-center text-rose-600 font-semibold bg-rose-50 border border-rose-200 rounded-2xl text-xs">
            {error}
          </div>
        ) : (
          <>
            {/* Top 4 Statistic Cards */}
            <ProgressTopStats stats={topStats} />

            {/* Analytics Row 1: Performance Over Time | Skill Analysis | Topic Performance */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <PerformanceChartCard trendPoints={dashboard?.recent_trend} />
              <SkillAnalysisCard skillData={dashboard?.skills} />
              <TopicPerformanceCard topicsData={dashboard?.topics} />
            </div>

            {/* Analytics Row 2: Focus Areas | AI Recommendation | Practice Activity */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <FocusAreasCard weakAreas={dashboard?.weak_areas} />
              <AiRecommendationCard adaptiveData={dashboard?.adaptive} />
              <PracticeActivityCard activityData={dashboard?.recent_activity} />
            </div>

            {/* Analytics Row 3: Achievements | Recent Activity | Performance Insight */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <AchievementsCard overview={dashboard?.overview} />
              <RecentActivityCard recentInterviews={dashboard?.recent_interviews} />
              <ProgressInsightCard strongAreas={dashboard?.strong_areas} />
            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
