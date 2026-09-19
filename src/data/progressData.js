// Centralized Mock Dataset for Prashasak AI Progress & Analytics Module

export const progressStats = {
  questionsPracticed: {
    value: 42,
    label: "Questions Practiced",
    trend: "↑ 12% from last month",
    trendPositive: true,
    icon: "messageSquare"
  },
  interviewsCompleted: {
    value: 6,
    label: "Interviews Completed",
    trend: "↑ 50% from last month",
    trendPositive: true,
    icon: "users"
  },
  averageScore: {
    value: "78%",
    label: "Average Score",
    trend: "↑ 8% from last month",
    trendPositive: true,
    icon: "barChart"
  },
  dayStreak: {
    value: 5,
    label: "Day Streak",
    badge: "🔥 Keep it going!",
    icon: "flame"
  }
};

export const performanceData = {
  selectedTimeframe: "Last 6 Weeks",
  timeframeOptions: ["Last 7 Days", "Last 4 Weeks", "Last 6 Weeks", "Last 3 Months"],
  points: [
    { label: "Week 1", score: 52 },
    { label: "Week 2", score: 61 },
    { label: "Week 3", score: 68 },
    { label: "Week 4", score: 71 },
    { label: "Week 5", score: 75 },
    { label: "Week 6", score: 78 }
  ]
};

export const skillMetrics = [
  { label: "Content", score: 82, color: "bg-blue-600" },
  { label: "Clarity", score: 74, color: "bg-blue-600" },
  { label: "Depth", score: 68, color: "bg-blue-600" },
  { label: "Reasoning", score: 81, color: "bg-blue-600" },
  { label: "Communication", score: 88, color: "bg-blue-600" }
];

export const topicPerformance = [
  { id: "governance", label: "Governance", score: 84, color: "bg-emerald-500", icon: "landmark" },
  { id: "ethics", label: "Ethics", score: 79, color: "bg-blue-500", icon: "scale" },
  { id: "polity", label: "Polity", score: 81, color: "bg-amber-500", icon: "bookOpen" },
  { id: "economy", label: "Economy", score: 68, color: "bg-rose-500", icon: "trendingUp" },
  { id: "international-relations", label: "International Relations", score: 76, color: "bg-purple-500", icon: "globe" }
];

export const focusAreas = {
  title: "Focus Areas",
  description: "Based on your recent interviews, you may benefit from practicing:",
  tags: [
    { label: "Economy", category: "economy", color: "bg-rose-50 text-rose-700 border-rose-200" },
    { label: "Analytical Questions", category: "governance", color: "bg-sky-50 text-sky-700 border-sky-200" },
    { label: "Ethics Case Studies", category: "ethics", color: "bg-amber-50 text-amber-700 border-amber-200" }
  ],
  ctaText: "Practice Weak Areas →",
  targetFilter: "economy"
};

export const aiRecommendation = {
  title: "Your Next Best Practice",
  recommendationText: "“Practice 5 Economy + Governance questions and focus on adding specific examples to your answers.”",
  ctaText: "Start Recommended Practice →",
  targetRoute: "/interview"
};

export const practiceActivity = {
  month: "September 2026",
  days: [
    { day: "Mon", status: "practiced" },
    { day: "Tue", status: "practiced" },
    { day: "Wed", status: "no-practice" },
    { day: "Thu", status: "practiced" },
    { day: "Fri", status: "today" },
    { day: "Sat", status: "no-practice" },
    { day: "Sun", status: "no-practice" }
  ]
};

export const achievements = [
  {
    id: "ach-1",
    title: "First Interview Completed",
    icon: "fileText",
    unlocked: true,
    color: "bg-emerald-50 text-emerald-600 border-emerald-200"
  },
  {
    id: "ach-2",
    title: "10 Questions Practiced",
    icon: "messageSquare",
    unlocked: true,
    color: "bg-blue-50 text-blue-600 border-blue-200"
  },
  {
    id: "ach-3",
    title: "5 Day Streak",
    icon: "flame",
    unlocked: true,
    color: "bg-orange-50 text-orange-600 border-orange-200"
  },
  {
    id: "ach-4",
    title: "10 Interviews Completed",
    icon: "lock",
    unlocked: false,
    color: "bg-slate-100 text-slate-400 border-slate-200"
  }
];

export const recentActivity = [
  {
    id: "act-1",
    text: "Practiced a Governance question",
    timestamp: "2 hours ago",
    icon: "checkCircle",
    iconColor: "text-emerald-600 bg-emerald-50"
  },
  {
    id: "act-2",
    text: "Completed AI Interview #6",
    timestamp: "1 day ago",
    icon: "landmark",
    iconColor: "text-amber-600 bg-amber-50"
  },
  {
    id: "act-3",
    text: "Saved a Current Affairs question",
    timestamp: "2 days ago",
    icon: "bookmark",
    iconColor: "text-blue-600 bg-blue-50"
  },
  {
    id: "act-4",
    text: "Practiced an Ethics question",
    timestamp: "3 days ago",
    icon: "fileText",
    iconColor: "text-purple-600 bg-purple-50"
  }
];
