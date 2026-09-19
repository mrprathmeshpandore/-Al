// Centralized Mock Dataset for Prashasak AI Question Bank Module

export const questionBankStats = {
  totalQuestions: 248,
  practicedCount: 12,
  savedCount: 28,
  averageScore: "65%"
};

export const qbCategories = [
  { id: "all", label: "All" },
  { id: "polity", label: "Polity" },
  { id: "economy", label: "Economy" },
  { id: "governance", label: "Governance" },
  { id: "international-relations", label: "International Relations" },
  { id: "science-tech", label: "Science & Tech" },
  { id: "environment", label: "Environment" },
  { id: "ethics", label: "Ethics" },
  { id: "social-issues", label: "Social Issues" },
  { id: "current-affairs", label: "Current Affairs" },
  { id: "daf-based", label: "DAF Based" },
  { id: "society", label: "Society" },
  { id: "security", label: "Security" },
  { id: "history", label: "History" },
  { id: "geography", label: "Geography" }
];

export const qbDifficulties = [
  { id: "all", label: "All" },
  { id: "easy", label: "Easy", color: "bg-emerald-50 text-emerald-700 border-emerald-200" },
  { id: "moderate", label: "Moderate", color: "bg-amber-50 text-amber-700 border-amber-200" },
  { id: "hard", label: "Hard", color: "bg-rose-50 text-rose-700 border-rose-200" }
];

export const qbTypes = [
  { id: "all", label: "All" },
  { id: "main", label: "Main Question" },
  { id: "follow-up", label: "Follow-up" },
  { id: "counter", label: "Counter" },
  { id: "ethical", label: "Ethical" },
  { id: "scenario", label: "Scenario Based" }
];

export const popularTopics = [
  { id: "pt-1", step: 1, title: "AI & Governance", count: "24 questions", category: "governance" },
  { id: "pt-2", step: 2, title: "Ethics in Public Life", count: "18 questions", category: "ethics" },
  { id: "pt-3", step: 3, title: "India's Foreign Policy", count: "16 questions", category: "international-relations" },
  { id: "pt-4", step: 4, title: "Climate Change", count: "15 questions", category: "environment" },
  { id: "pt-5", step: 5, title: "DAF Based Questions", count: "14 questions", category: "daf-based" }
];

export const questionsList = [
  {
    id: "qb-1",
    question: "How can AI improve public service delivery while protecting citizens' rights?",
    type: "Current Affairs",
    typeBadgeColor: "bg-sky-100 text-sky-800 border-sky-300",
    difficulty: "Moderate",
    difficultyBadgeColor: "bg-amber-100 text-amber-800 border-amber-300",
    category: "governance",
    qType: "main",
    date: "19 Sep 2026",
    description: "Explore the role of AI in governance, its benefits, challenges, and the way forward for India.",
    tags: ["Technology", "Governance", "Public Policy"],
    image: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&q=80&w=600",
    isBookmarked: true,
    isPracticed: true,
    whyItMatters: "Automation in welfare delivery reduces leakages, but algorithmic decision-making requires constitutional privacy safeguards.",
    upscRelevance: "GS Paper II: E-Governance, Applications, and Rights Issues under Article 21.",
    keyAreas: [
      "Digital inclusion and vernacular accessibility",
      "Algorithmic accountability and bias mitigation",
      "Data protection under DPDP Act 2023"
    ],
    relatedCurrentAffairs: "IndiaAI Mission & Digital Public Infrastructure (DPI)",
    potentialFollowUp: "What specific framework would you establish in a district to audit automated beneficiary exclusion?",
    potentialCounterQuestion: "If an automated algorithm wrongfully denies rations to an elderly citizen due to biometric error, who bears criminal accountability?"
  },
  {
    id: "qb-2",
    question: "Why did you choose your field of education, and how has it shaped your interest in civil services?",
    type: "DAF Based",
    typeBadgeColor: "bg-blue-100 text-blue-800 border-blue-300",
    difficulty: "Moderate",
    difficultyBadgeColor: "bg-amber-100 text-amber-800 border-amber-300",
    category: "daf-based",
    qType: "main",
    date: "18 Sep 2026",
    description: "A personal question to understand your background, motivation, and administrative perspective.",
    tags: ["Education", "Personal Background", "Motivation"],
    image: "https://images.unsplash.com/photo-1523240795612-9a054b0db644?auto=format&fit=crop&q=80&w=600",
    isBookmarked: true,
    isPracticed: false,
    whyItMatters: "Interview boards assess your self-awareness, sincerity, and how effectively you apply academic training to public administration.",
    upscRelevance: "DAF Profile Evaluation & Personality Test Core Parameters.",
    keyAreas: [
      "Connecting core academic subjects to administrative problem-solving",
      "Demonstrating consistent career progression and clarity of intent",
      "Avoiding superficial justifications"
    ],
    relatedCurrentAffairs: "National Education Policy 2020 & Multidisciplinary Skill Adoption",
    potentialFollowUp: "Given your engineering background, wouldn't you serve the nation better by joining a private R&D lab rather than general administration?",
    potentialCounterQuestion: "Isn't it true that many candidates choose civil services for social status rather than academic utilization?"
  },
  {
    id: "qb-3",
    question: "What are the key challenges in India–EU relations, and how can they be strengthened?",
    type: "International Relations",
    typeBadgeColor: "bg-indigo-100 text-indigo-800 border-indigo-300",
    difficulty: "Hard",
    difficultyBadgeColor: "bg-rose-100 text-rose-800 border-rose-300",
    category: "international-relations",
    qType: "main",
    date: "17 Sep 2026",
    description: "Discuss the current state of India–EU ties, major trade issues, and future strategic opportunities.",
    tags: ["International Relations", "Economy", "Strategic Policy"],
    image: "https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&q=80&w=600",
    isBookmarked: false,
    isPracticed: true,
    whyItMatters: "The European Union is India's largest trading partner; navigating CBAM carbon tariffs and supply chain realignment is critical.",
    upscRelevance: "GS Paper II: Bilateral, Regional Groupings and Agreements involving India.",
    keyAreas: [
      "Carbon Border Adjustment Mechanism (CBAM) impact on Indian steel and aluminum",
      "Free Trade Agreement (FTA) negotiations and intellectual property differences",
      "India-EU Trade & Technology Council (TTC) cooperation"
    ],
    relatedCurrentAffairs: "India-EU Summit & Global South Energy Diplomacy",
    potentialFollowUp: "How should India counter unilateral environmental tariffs imposed by developed trade blocs?",
    potentialCounterQuestion: "If EU insists on stringent labor standard clauses in the FTA, should India compromise to secure market access?"
  },
  {
    id: "qb-4",
    question: "What would you do if you are asked to follow an unjust order by a superior?",
    type: "Ethics",
    typeBadgeColor: "bg-purple-100 text-purple-800 border-purple-300",
    difficulty: "Easy",
    difficultyBadgeColor: "bg-emerald-100 text-emerald-800 border-emerald-300",
    category: "ethics",
    qType: "ethical",
    date: "16 Sep 2026",
    description: "Evaluate your ethical decision-making, administrative integrity, and constitutional duty.",
    tags: ["Ethics", "Probity", "Administrative Conduct"],
    image: "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&q=80&w=600",
    isBookmarked: false,
    isPracticed: false,
    whyItMatters: "Tests civil service neutrality, rule of law adherence, and courage of conviction when faced with hierarchical pressure.",
    upscRelevance: "GS Paper IV: Ethics and Human Interface, Conduct Rules, and Morality in Administration.",
    keyAreas: [
      "Distinction between legally illegal orders vs morally ambiguous instructions",
      "Written record-keeping and formal administrative representation",
      "Constitutional allegiance over personal compliance"
    ],
    relatedCurrentAffairs: "Central Civil Services (Conduct) Rules Enforcement",
    potentialFollowUp: "What if refusing the verbal order results in your immediate transfer to a remote posting?",
    potentialCounterQuestion: "Is absolute obedience to superiors necessary to maintain administrative discipline during emergency situations?"
  },
  {
    id: "qb-5",
    question: "How can India achieve its Net-Zero 2070 target while maintaining 7%+ economic growth?",
    type: "Environment",
    typeBadgeColor: "bg-emerald-100 text-emerald-800 border-emerald-300",
    difficulty: "Moderate",
    difficultyBadgeColor: "bg-amber-100 text-amber-800 border-amber-300",
    category: "environment",
    qType: "main",
    date: "15 Sep 2026",
    description: "Examine the balance between green energy transition, industrialization, and energy security.",
    tags: ["Environment", "Renewable Energy", "Economy"],
    image: "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&q=80&w=600",
    isBookmarked: true,
    isPracticed: false,
    whyItMatters: "Energy transition requires massive climate finance while ensuring affordable electricity for manufacturing and poverty alleviation.",
    upscRelevance: "GS Paper III: Conservation, Environmental Pollution & Economic Growth.",
    keyAreas: [
      "National Green Hydrogen Mission & solar capacity expansion",
      "Coal phase-down trajectory vs energy grid stability",
      "Climate finance mobilization from multilateral development banks"
    ],
    relatedCurrentAffairs: "COP Climate Summit & Panchamrit Targets",
    potentialFollowUp: "Should India accept binding emission caps if climate technology transfer is delayed by developed nations?",
    potentialCounterQuestion: "Isn't rapid industrial expansion fundamentally contradictory to strict forest conservation laws?"
  },
  {
    id: "qb-6",
    question: "As a District Magistrate, how would you resolve communal tension triggered by a social media rumor?",
    type: "Scenario Based",
    typeBadgeColor: "bg-orange-100 text-orange-800 border-orange-300",
    difficulty: "Hard",
    difficultyBadgeColor: "bg-rose-100 text-rose-800 border-rose-300",
    category: "governance",
    qType: "scenario",
    date: "14 Sep 2026",
    description: "A real-time law and order scenario testing rapid response, community outreach, and cyber regulation.",
    tags: ["Law & Order", "Crisis Management", "Cyber Regulation"],
    image: "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?auto=format&fit=crop&q=80&w=600",
    isBookmarked: false,
    isPracticed: true,
    whyItMatters: "Misinformation spreads instantly; administrators must combine Section 144/internet suspensions with proactive peace committee dialogue.",
    upscRelevance: "GS Paper II & GS Paper IV: Internal Security & Practical Ethics in Crisis Management.",
    keyAreas: [
      "Immediate deployment of police forces and digital rumor debunking",
      "Engagement of trusted community elders and Peace Committees",
      "Proportionality in shutting down internet vs protecting public peace"
    ],
    relatedCurrentAffairs: "Cyber Crime Helpline & Fact-Check Unit Regulations",
    potentialFollowUp: "How will you prevent the shutdown of internet services from crippling local UPI payments and emergency medical services?",
    potentialCounterQuestion: "If local political leaders demand the release of accused rumor-mongers, how will you handle political pressure?"
  }
];
