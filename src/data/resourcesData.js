// Centralized Mock Dataset for Prashasak AI Resources Module

export const resourceCategories = [
  { id: "all", label: "All" },
  { id: "syllabus", label: "Syllabus" },
  { id: "pyqs", label: "PYQs" },
  { id: "study-material", label: "Study Material" },
  { id: "interview", label: "Interview" },
  { id: "daf", label: "DAF" },
  { id: "notes", label: "Notes" },
  { id: "guides", label: "Guides" },
  { id: "videos", label: "Videos" },
  { id: "articles", label: "Articles" }
];

export const upscEssentials = [
  {
    id: "ess-1",
    title: "UPSC Syllabus",
    description: "Complete UPSC Civil Services Examination syllabus covering Prelims, Mains & Interview.",
    tags: ["PDF", "Official"],
    category: "syllabus",
    type: "PDF",
    fileSize: "1.8 MB",
    isOfficial: true,
    isSaved: false,
    subject: "Governance",
    whyItMatters: "Provides the foundational roadmap for all stages of UPSC examination and interview expectation mapping.",
    keyTopics: ["Prelims GS-1 & CSAT", "Mains GS-I to IV", "Optional Subjects", "Personality Test Standards"],
    url: "#"
  },
  {
    id: "ess-2",
    title: "Previous Year Questions",
    description: "Last 10 years UPSC Prelims, Mains and Interview questions with trend analysis.",
    tags: ["PDF", "Official"],
    category: "pyqs",
    type: "PDF",
    fileSize: "8.4 MB",
    isOfficial: true,
    isSaved: true,
    subject: "All Subjects",
    whyItMatters: "Essential for identifying repeating themes, examiner mindset, and high-frequency topics.",
    keyTopics: ["Topic-wise PYQs", "Mains Answer Key Trends", "Interview Board Questions", "Difficulty Rating"],
    url: "#"
  },
  {
    id: "ess-3",
    title: "Interview Guidelines",
    description: "Official UPSC interview guidelines, evaluation criteria and board preparation guidance.",
    tags: ["PDF", "Official"],
    category: "interview",
    type: "PDF",
    fileSize: "2.2 MB",
    isOfficial: true,
    isSaved: false,
    subject: "Interview Prep",
    whyItMatters: "Outlines the 275-mark personality test parameters: mental alertness, critical powers of assimilation, clear exposition, and balance of judgement.",
    keyTopics: ["Assessment Criteria", "Body Language & Etiquette", "Board Formats", "Current Issue Framing"],
    url: "#"
  },
  {
    id: "ess-4",
    title: "DAF Guidelines",
    description: "How to fill DAF, important areas, and preparation strategy based on your profile.",
    tags: ["PDF", "Guide"],
    category: "daf",
    type: "PDF",
    fileSize: "3.1 MB",
    isOfficial: false,
    isSaved: false,
    subject: "DAF Profile",
    whyItMatters: "70%+ of interview questions stem directly from DAF details (hobbies, home state, educational background).",
    keyTopics: ["Service Preference Strategy", "Hobby Keywords", "Cadre Preference", "District/State Nuances"],
    url: "#"
  }
];

export const subjects = [
  { id: "polity", name: "Polity", slug: "polity", count: 42, icon: "landmark", color: "bg-rose-50 text-rose-600 border-rose-200" },
  { id: "economy", name: "Economy", slug: "economy", count: 38, icon: "trendingUp", color: "bg-amber-50 text-amber-600 border-amber-200" },
  { id: "history", name: "History", slug: "history", count: 28, icon: "bookOpen", color: "bg-red-50 text-red-600 border-red-200" },
  { id: "geography", name: "Geography", slug: "geography", count: 26, icon: "globe", color: "bg-emerald-50 text-emerald-600 border-emerald-200" },
  { id: "environment", name: "Environment", slug: "environment", count: 32, icon: "leaf", color: "bg-green-50 text-green-600 border-green-200" },
  { id: "ethics", name: "Ethics", slug: "ethics", count: 24, icon: "scale", color: "bg-blue-50 text-blue-600 border-blue-200" },
  { id: "governance", name: "Governance", slug: "governance", count: 30, icon: "shield", color: "bg-indigo-50 text-indigo-600 border-indigo-200" },
  { id: "science-technology", name: "Science & Tech", slug: "science-technology", count: 22, icon: "flask", color: "bg-purple-50 text-purple-600 border-purple-200" },
  { id: "international-relations", name: "International Relations", slug: "international-relations", count: 27, icon: "network", color: "bg-sky-50 text-sky-600 border-sky-200" },
  { id: "society", name: "Society", slug: "society", count: 18, icon: "users", color: "bg-pink-50 text-pink-600 border-pink-200" }
];

export const interviewResources = [
  {
    id: "int-res-1",
    title: "Frequently Asked Questions",
    description: "100+ commonly asked UPSC interview questions categorized by board member styles.",
    icon: "messageSquare",
    category: "interview",
    type: "Guide",
    fileSize: "1.4 MB",
    whyItMatters: "Helps aspirants build structured answers for predictable introductory and thematic questions.",
    keyTopics: ["Why Civil Services?", "Strengths & Weaknesses", "State Administration", "Recent National Debates"]
  },
  {
    id: "int-res-2",
    title: "DAF Based Preparation",
    description: "Subject-wise DAF questions and targeted interview preparation approach.",
    icon: "userCheck",
    category: "daf",
    type: "Framework",
    fileSize: "2.5 MB",
    whyItMatters: "Ensures comprehensive coverage of every phrase mentioned in your Detailed Application Form.",
    keyTopics: ["Name & Meaning Context", "College / Degree Applications", "Hobby Deep-Dives", "Home District Issues"]
  },
  {
    id: "int-res-3",
    title: "Ethics & Situational Questions",
    description: "Real-life scenarios and ethical dilemmas tested by UPSC interview boards.",
    icon: "scale",
    category: "ethics",
    type: "Case Studies",
    fileSize: "3.2 MB",
    whyItMatters: "Prepares you to respond with administrative integrity, constitutional morality, and balanced judgment.",
    keyTopics: ["Conflict of Interest", "Public Order vs Rights", "Whistleblowing Scenarios", "Disaster Response Choice"]
  },
  {
    id: "int-res-4",
    title: "Interview Strategy",
    description: "Structure, tips and practical interview preparation proven strategies.",
    icon: "target",
    category: "interview",
    type: "Guide",
    fileSize: "1.1 MB",
    whyItMatters: "Master non-verbal communication, managing tough questions gracefully, and staying composed.",
    keyTopics: ["Handling I Don't Know", "Voice Modulation", "Stress Interview Handling", "Board Neutrality"]
  },
  {
    id: "int-res-5",
    title: "Answer Frameworks",
    description: "Learn how to structure clear, multidimensional, and effective oral answers.",
    icon: "layout",
    category: "guides",
    type: "Template",
    fileSize: "950 KB",
    whyItMatters: "Provides 3-tier structure (Context -> Pros/Cons -> Balanced Conclusion) for any open-ended question.",
    keyTopics: ["PESTEL Analysis Method", "Constitutional Alignment", "Data-Backed Statements", "Concise Delivery"]
  }
];

export const savedResourcesList = [
  {
    id: "sav-1",
    title: "Ethics Case Studies PDF",
    type: "PDF",
    info: "PDF • 2.4 MB",
    isSaved: true,
    subject: "Ethics"
  },
  {
    id: "sav-2",
    title: "India's Foreign Policy Notes",
    type: "PDF",
    info: "PDF • 3.1 MB",
    isSaved: true,
    subject: "International Relations"
  },
  {
    id: "sav-3",
    title: "UPSC Interview Experiences",
    type: "Article",
    info: "Article • 5 min read",
    isSaved: true,
    subject: "Interview Prep"
  },
  {
    id: "sav-4",
    title: "Economic Survey 2024",
    type: "PDF",
    info: "PDF • 4.8 MB",
    isSaved: true,
    subject: "Economy"
  }
];

export const mockDetailedResources = [
  {
    id: "res-polity-1",
    title: "Indian Constitution & Federal Framework",
    subject: "Polity",
    category: "study-material",
    type: "PDF",
    fileSize: "4.2 MB",
    duration: "20 min read",
    source: "Official Governance Committee",
    date: "Sep 2026",
    description: "Comprehensive notes on Centre-State legislative, administrative, and financial relations with recent Supreme Court judgments.",
    whyItMatters: "Federalism is a core UPSC Mains and Interview topic frequently tested with current constitutional debates.",
    keyTopics: ["Article 356 & Governor's Role", "GST Council Dynamics", "Inter-State Water Disputes", "Seventh Schedule Reforms"],
    isSaved: false
  },
  {
    id: "res-economy-1",
    title: "Fiscal Deficit & Macroeconomic Stability",
    subject: "Economy",
    category: "notes",
    type: "Notes",
    fileSize: "2.1 MB",
    duration: "15 min read",
    source: "Ministry of Finance Brief",
    date: "Aug 2026",
    description: "Analysis of India's fiscal consolidation roadmap, debt-to-GDP ratio, and capital expenditure impact on economic growth.",
    whyItMatters: "Crucial for understanding macroeconomic management questions during personality tests.",
    keyTopics: ["FRBM Target Rules", "Capex Multiplier Effect", "Inflation Targeting Framework", "Off-Budget Borrowings"],
    isSaved: true
  },
  {
    id: "res-ethics-1",
    title: "Probity in Governance & Anti-Corruption",
    subject: "Ethics",
    category: "guides",
    type: "Guide",
    fileSize: "1.9 MB",
    duration: "18 min read",
    source: "Administrative Reforms Commission",
    date: "Jul 2026",
    description: "Operationalizing ethical standards, Lokpal mechanisms, and citizen charter implementations in civil services.",
    whyItMatters: "Directly addresses GS IV ethics paper and interview board evaluation of personal integrity.",
    keyTopics: ["2nd ARC 4th Report", "Whistleblower Protection", "Code of Conduct vs Ethics", "Transparency Tools"],
    isSaved: false
  }
];
