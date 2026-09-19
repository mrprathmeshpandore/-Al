// Centralized Mock Data for Prashasak AI Dashboard
// This architecture ensures seamless integration when connecting to backend APIs later.

export const userProfile = {
  name: "Pratham",
  role: "UPSC Aspirant",
  avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=250",
  greetingTime: "Good Morning",
  subtitle: "Ready to challenge your thinking today?"
};

export const dashboardStats = {
  questionsPracticed: {
    value: 42,
    label: "Questions Practiced",
    trend: "+12%",
    trendPositive: true,
    icon: "layers"
  },
  interviewsCompleted: {
    value: 6,
    label: "Interviews Completed",
    trend: "+20%",
    trendPositive: true,
    icon: "fileCheck"
  },
  averageScore: {
    value: "78%",
    label: "Average Score",
    trend: "+8%",
    trendPositive: true,
    icon: "star"
  },
  dayStreak: {
    value: 5,
    label: "Day Streak",
    badge: "🔥 Keep it up!",
    icon: "flame"
  }
};

export const todayPractice = [
  {
    id: "ca-practice",
    title: "Current Affairs",
    description: "Practice questions from today's important issues.",
    buttonText: "Practice Now →",
    category: "Current Affairs",
    color: "saffron",
    bgColor: "bg-amber-500/10",
    textColor: "text-amber-600",
    borderColor: "border-amber-200",
    icon: "newspaper"
  },
  {
    id: "qb-practice",
    title: "Question Bank",
    description: "Explore topic-wise UPSC interview questions.",
    buttonText: "Explore →",
    category: "Question Bank",
    color: "navy",
    bgColor: "bg-slate-900/10",
    textColor: "text-[#0B1628]",
    borderColor: "border-slate-200",
    icon: "bookOpen"
  },
  {
    id: "daf-practice",
    title: "DAF Practice",
    description: "Practice questions based on your profile.",
    buttonText: "Start Practice →",
    category: "DAF Profile",
    color: "emerald",
    bgColor: "bg-emerald-500/10",
    textColor: "text-emerald-600",
    borderColor: "border-emerald-200",
    icon: "userCheck"
  }
];

export const performanceMetrics = {
  title: "Your Interview Performance",
  viewReportText: "View Detailed Report →",
  categories: [
    { label: "Content", score: 82, color: "bg-[#0B1628]" },
    { label: "Clarity", score: 74, color: "bg-[#0B1628]" },
    { label: "Depth", score: 68, color: "bg-amber-600" },
    { label: "Reasoning", score: 81, color: "bg-[#0B1628]" },
    { label: "Communication", score: 88, color: "bg-emerald-600" }
  ],
  quote: "“The more you reflect, the better you respond.”"
};

export const recentInterviews = [
  {
    id: "int-1",
    topic: "AI Governance",
    date: "Today",
    score: 78,
    statusColor: "bg-emerald-100 text-emerald-700 border-emerald-200",
    icon: "shield"
  },
  {
    id: "int-2",
    topic: "International Relations",
    date: "Yesterday",
    score: 82,
    statusColor: "bg-emerald-100 text-emerald-700 border-emerald-200",
    icon: "globe"
  },
  {
    id: "int-3",
    topic: "Ethics & Administration",
    date: "2 Days Ago",
    score: 74,
    statusColor: "bg-amber-100 text-amber-700 border-amber-200",
    icon: "scale"
  }
];

export const currentAffairs = [
  {
    id: "ca-1",
    title: "India's AI Mission & Governance",
    category: "Technology",
    date: "Today",
    imageUrl: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&q=80&w=200",
    icon: "cpu"
  },
  {
    id: "ca-2",
    title: "India–EU Trade Relations",
    category: "International Relations",
    date: "Today",
    imageUrl: "https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&q=80&w=200",
    icon: "globe2"
  },
  {
    id: "ca-3",
    title: "Climate Policy & Green Development",
    category: "Environment",
    date: "Today",
    imageUrl: "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&q=80&w=200",
    icon: "leaf"
  },
  {
    id: "ca-4",
    title: "Digital Public Infrastructure",
    category: "Governance",
    date: "Today",
    imageUrl: "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&q=80&w=200",
    icon: "landmark"
  }
];

export const sidebarNavigation = [
  { id: "dashboard", label: "Dashboard", path: "/dashboard", icon: "layoutDashboard", active: true },
  { id: "ai-interview", label: "AI Interview", path: "/interview", icon: "mic", active: false },
  { id: "question-bank", label: "Question Bank", path: "/question-bank", icon: "bookOpen", active: false },
  { id: "current-affairs", label: "Current Affairs", path: "/current-affairs", icon: "newspaper", active: false },
  { id: "resources", label: "Resources", path: "/resources", icon: "folder", active: false },
];

export const sidebarSecondaryNav = [
  { id: "progress", label: "My Progress", path: "/progress", icon: "barChart3" },
  { id: "settings", label: "Settings", path: "/dashboard?tab=settings", icon: "settings" },
];
