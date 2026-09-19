// Centralized Dataset for Prashasak AI Current Affairs Module

export const caCategories = [
  { id: "all", label: "All Topics", icon: "layoutGrid" },
  { id: "national", label: "National", icon: "building" },
  { id: "international", label: "International", icon: "globe" },
  { id: "economy", label: "Economy", icon: "trendingUp" },
  { id: "governance", label: "Governance", icon: "landmark" },
  { id: "environment", label: "Environment", icon: "leaf" },
  { id: "science-tech", label: "Science & Tech", icon: "cpu" },
  { id: "social-issues", label: "Social Issues", icon: "users" },
];

export const featuredAffair = {
  id: "ai-mission-2026",
  badge: "FEATURED",
  date: "19 Sep 2026",
  title: "India's AI Mission: Building an AI-Ready Nation",
  summary: "India's AI Mission aims to strengthen the country's AI ecosystem through computing infrastructure, research, skilling, and responsible AI development.",
  tags: ["Technology", "Governance", "Public Policy"],
  category: "science-tech",
  primaryCtaText: "Practice Interview Questions →",
  image: "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&q=80&w=1200",
  quote: "“Technology for People, Progress and Possibilities.”",
  whyItMatters: "Artificial Intelligence is shifting from an experimental tool to a core component of national sovereignty and digital governance in India.",
  shortContext: "The Cabinet approved the IndiaAI Mission with a multi-crore allocation to establish GPU computing infrastructure, AI innovation hubs, and regulatory frameworks for ethical AI.",
  keyPoints: [
    "Establishment of 10,000+ GPU computing capacity under public-private partnerships.",
    "Launch of IndiaAI Innovation Centre for indigenous Large Multimodal Models (LMMs).",
    "Dataset Platform to democratize non-personal data access for Indian startups.",
    "Responsible AI guidelines prioritizing safety, bias reduction, and privacy."
  ],
  importantFacts: [
    "Allocation: ₹10,372 Crore over 5 years.",
    "Nodal Ministry: Ministry of Electronics and Information Technology (MeitY).",
    "Focus Areas: Agriculture, Healthcare, Vernacular Education, Smart Governance."
  ],
  challenges: [
    "High capital expenditure for advanced GPU hardware imports.",
    "Data privacy risks and algorithmic bias in vernacular language processing.",
    "Talent shortage in deep-tech AI research within domestic academia."
  ],
  governmentResponse: "Targeted skilling initiatives under FutureSkills Prime and AI Fellowship grants for PhD scholars.",
  upscRelevance: [
    { paper: "GS II", topic: "Governance, Transparency and Technology in Public Service" },
    { paper: "GS III", topic: "Science & Technology - Developments and Applications" },
    { paper: "GS IV", topic: "Ethics in Technology & Artificial Intelligence" }
  ],
  potentialQuestions: [
    {
      type: "MAIN QUESTION",
      text: "How can India leverage its IndiaAI Mission to bridge the digital divide in rural healthcare and agriculture?"
    },
    {
      type: "PRACTICE-WORTHY FOLLOW-UP",
      text: "What ethical safeguards should a District Magistrate enforce when implementing automated AI decision systems for beneficiary selection?"
    },
    {
      type: "POSSIBLE COUNTER QUESTION",
      text: "Critics argue that AI deployment might cause job displacement in administrative entry roles. What is your balanced perspective?"
    }
  ]
};

export const todayHighlights = [
  {
    id: "ca-highlight-1",
    step: 1,
    title: "India's AI Mission",
    category: "Technology",
    subcategory: "Governance",
    targetId: "ai-mission-2026"
  },
  {
    id: "ca-highlight-2",
    step: 2,
    title: "India–EU Trade Relations",
    category: "International Relations",
    subcategory: "Economy",
    targetId: "india-eu-trade"
  },
  {
    id: "ca-highlight-3",
    step: 3,
    title: "Climate Policy & Green Development",
    category: "Environment",
    subcategory: "Sustainability",
    targetId: "climate-policy"
  },
  {
    id: "ca-highlight-4",
    step: 4,
    title: "Digital Public Infrastructure",
    category: "Governance",
    subcategory: "Innovation",
    targetId: "dpi-global-model"
  }
];

export const currentAffairsList = [
  {
    id: "chandrayaan-4",
    title: "Chandrayaan-4: India's Next Lunar Mission",
    date: "19 Sep 2026",
    category: "science-tech",
    categoryLabel: "Science & Tech",
    subcategory: "Space",
    image: "https://images.unsplash.com/photo-1614728894747-a83421e2b9c9?auto=format&fit=crop&q=80&w=800",
    summary: "ISRO outlines Chandrayaan-4 sample return mission architecture, demonstrating advanced robotic docking and lunar orbit ascent technology.",
    isBookmarked: false,
    upscRelevance: [{ paper: "GS III", topic: "Indigenization of Technology & Space Achievements" }],
    potentialQuestions: [
      { type: "MAIN QUESTION", text: "Analyze the strategic significance of Chandrayaan-4 sample-return capability for India's space diplomacy and planetary research." }
    ]
  },
  {
    id: "india-eu-trade",
    title: "India–EU Trade Relations: A New Chapter",
    date: "18 Sep 2026",
    category: "international",
    categoryLabel: "International",
    subcategory: "Economy",
    image: "https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&q=80&w=800",
    summary: "Comprehensive Economic Partnership discussions accelerate with focus on Carbon Border Adjustment Mechanism (CBAM) negotiations and supply chain resilience.",
    isBookmarked: true,
    upscRelevance: [{ paper: "GS II", topic: "Bilateral Agreements Involving India's Interests" }],
    potentialQuestions: [
      { type: "MAIN QUESTION", text: "How should India safeguard its export competitiveness against EU's Carbon Border Tax while promoting sustainable trade?" }
    ]
  },
  {
    id: "climate-policy",
    title: "Climate Policy & Green Development",
    date: "18 Sep 2026",
    category: "environment",
    categoryLabel: "Environment",
    subcategory: "Sustainability",
    image: "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&q=80&w=800",
    summary: "National Green Hydrogen Mission achieves key milestone with indigenous electrolyzer deployment and green steel pilot projects.",
    isBookmarked: false,
    upscRelevance: [{ paper: "GS III", topic: "Environmental Conservation & Renewable Energy" }],
    potentialQuestions: [
      { type: "MAIN QUESTION", text: "Examine the role of Green Hydrogen in decarbonizing India's hard-to-abate industrial sectors." }
    ]
  },
  {
    id: "ucc-debate",
    title: "Uniform Civil Code: Debate and Implications",
    date: "17 Sep 2026",
    category: "governance",
    categoryLabel: "Governance",
    subcategory: "Social Issues",
    image: "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&q=80&w=800",
    summary: "Law Commission synthesizes state-level implementations, examining Article 44 Directive Principles against Article 25 freedom of religion guarantees.",
    isBookmarked: false,
    upscRelevance: [{ paper: "GS II", topic: "Indian Constitution - Features, Significant Provisions" }],
    potentialQuestions: [
      { type: "MAIN QUESTION", text: "Discuss how a Uniform Civil Code can balance gender justice with cultural pluralism under the Indian Constitution." }
    ]
  },
  {
    id: "dpi-global-model",
    title: "Digital Public Infrastructure: India's Global Model",
    date: "17 Sep 2026",
    category: "science-tech",
    categoryLabel: "Technology",
    subcategory: "Governance",
    image: "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&q=80&w=800",
    summary: "India Stack expansion across Global South nations highlights open API standards for financial inclusion, digital identity, and health data.",
    isBookmarked: false,
    upscRelevance: [{ paper: "GS II", topic: "E-Governance - Applications, Models and Successes" }],
    potentialQuestions: [
      { type: "MAIN QUESTION", text: "Why is Digital Public Infrastructure considered India's most effective instrument of soft power in international development?" }
    ]
  },
  {
    id: "global-south-leadership",
    title: "Global South and India's Leadership Role",
    date: "16 Sep 2026",
    category: "international",
    categoryLabel: "International",
    subcategory: "Foreign Policy",
    image: "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?auto=format&fit=crop&q=80&w=800",
    summary: "Voice of Global South Summit addresses debt distress, food security, and reformed multilateralism at global governance forums.",
    isBookmarked: true,
    upscRelevance: [{ paper: "GS II", topic: "Important International Institutions & Groupings" }],
    potentialQuestions: [
      { type: "MAIN QUESTION", text: "How does India position itself as a consensus builder between the Global North and Global South?" }
    ]
  }
];

export const upscFocusAreas = [
  { paper: "GS I", label: "Society", color: "bg-amber-100 text-amber-800 border-amber-300" },
  { paper: "GS II", label: "Governance", color: "bg-sky-100 text-sky-800 border-sky-300" },
  { paper: "GS III", label: "Economy", color: "bg-emerald-100 text-emerald-800 border-emerald-300" },
  { paper: "GS III", label: "Science & Tech", color: "bg-indigo-100 text-indigo-800 border-indigo-300" },
  { paper: "GS IV", label: "Ethics", color: "bg-orange-100 text-orange-800 border-orange-300" },
];
