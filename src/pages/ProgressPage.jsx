import React from 'react';
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

export default function ProgressPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6 pb-12">
        {/* Page Header */}
        <ProgressHeader />

        {/* Top 4 Statistic Cards */}
        <ProgressTopStats />

        {/* Analytics Row 1: Performance Over Time | Skill Analysis | Topic Performance */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <PerformanceChartCard />
          <SkillAnalysisCard />
          <TopicPerformanceCard />
        </div>

        {/* Analytics Row 2: Focus Areas | AI Recommendation | Practice Activity */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <FocusAreasCard />
          <AiRecommendationCard />
          <PracticeActivityCard />
        </div>

        {/* Analytics Row 3: Achievements | Recent Activity | Performance Insight */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <AchievementsCard />
          <RecentActivityCard />
          <ProgressInsightCard />
        </div>
      </div>
    </DashboardLayout>
  );
}
