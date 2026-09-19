// Centralized Mock Data & Schema for Prashasak AI Interview Simulator

export const interviewers = [
  {
    id: "v-k-sharma",
    name: "Shri V. K. Sharma (Retd. IAS)",
    role: "Former Union Secretary & UPSC Board Chairman",
    status: "Online",
    image: "https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&q=80&w=1200",
    initialSpeech: "Let's have a meaningful discussion. Take your time to think and answer."
  },
  {
    id: "anita-desai",
    name: "Dr. Anita Desai",
    role: "Ex-UPSC Board Member & Public Policy Chair",
    status: "Online",
    image: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&q=80&w=1200",
    initialSpeech: "Welcome. We look forward to understanding your administrative perspective."
  },
  {
    id: "r-k-hegde",
    name: "Prof. R. K. Hegde",
    role: "Governance & Ethics Expert",
    status: "Online",
    image: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&q=80&w=1200",
    initialSpeech: "Stay calm and composed. Focus on clarity and balanced reasoning."
  }
];

export const interviewSession = {
  totalQuestions: 10,
  currentQuestionIndex: 3,
  timeRemainingSeconds: 900, // 15:00
  overallProgressPercentage: 30,
  quote: "“Great administrators are great listeners first.” — S. Radhakrishnan"
};

export const questionFlowList = [
  { step: 1, text: "Tell me about yourself.", status: "completed", type: "MAIN" },
  { step: 2, text: "Why do you want to join civil services?", status: "completed", type: "MAIN" },
  { step: 3, text: "Current Question", status: "active", type: "MAIN" },
  { step: 4, text: "Follow-up Question", status: "upcoming", type: "FOLLOW_UP" },
  { step: 5, text: "Counter Question", status: "upcoming", type: "COUNTER" },
  { step: 6, text: "Ethics Scenario", status: "upcoming", type: "ETHICAL" },
  { step: 7, text: "International Relations", status: "upcoming", type: "MAIN" },
  { step: 8, text: "DAF Profile Deep-Dive", status: "upcoming", type: "DAF" },
  { step: 9, text: "Administrative Decision Making", status: "upcoming", type: "ADMINISTRATIVE" },
  { step: 10, text: "Concluding Remarks", status: "upcoming", type: "CONCLUSION" },
];

export const currentQuestionData = {
  id: 3,
  type: "MAIN QUESTION",
  badgeColor: "bg-[#0B1628] text-white",
  question: "What are your views on Artificial Intelligence in Public Administration?",
  promptText: "You may take your time to think and answer. Try to be clear, balanced and provide relevant examples.",
  source: "CURRENT AFFAIRS",
  topic: "AI Governance",
  categories: ["Technology", "Governance", "Public Policy"],
  difficulty: "Moderate",
  difficultyColor: "text-amber-600 bg-amber-50 border-amber-200",
  typeLabel: "Main Question",
  speechAudioUrl: "https://actions.google.com/sounds/v1/ambiences/office_quiet.ogg"
};

export const mockFeedback = {
  badge: "Good Start",
  badgeColor: "bg-emerald-100 text-emerald-800 border-emerald-300",
  score: "78%",
  summary: "Your answer was relevant and structured, but you could strengthen it with a specific governance example.",
  strengths: [
    "Clear structure and articulate expression",
    "Balanced view on technology adoption"
  ],
  improvementArea: "Include real-world Indian schemes like IndiaAI Mission or Digital Public Infrastructure (DPI) to ground your answer.",
  followUpQuestion: "You mentioned data privacy risks. How would you as a District Collector balance AI deployment with citizen privacy rights?"
};

export const answerTips = [
  "Be structured in your response",
  "Use real-world examples",
  "Show balance and critical thinking",
  "Connect with India's context",
  "Stay calm and take your time"
];
