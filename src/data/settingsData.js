// Centralized Mock Settings Data & Configuration

export const defaultSettings = {
  interview: {
    answerMode: "Voice",
    difficulty: "Medium",
    duration: "15 minutes",
    followUpQuestions: true
  },
  notifications: {
    dailyPractice: true,
    currentAffairs: true,
    interviewUpdates: true,
    email: false
  },
  appearance: {
    theme: "Light",
    language: "English",
    fontSize: "Medium",
    reducedMotion: false
  }
};

export const interviewOptions = {
  answerModes: ["Voice", "Text"],
  difficulties: ["Easy", "Medium", "Hard"],
  durations: ["5 minutes", "10 minutes", "15 minutes", "20 minutes"]
};

export const appearanceOptions = {
  themes: ["Light", "Dim", "Dark"],
  languages: ["English", "Marathi"],
  fontSizes: ["Small", "Medium", "Large"]
};

export const privacyLinks = [
  { id: "your-data", title: "Your Data", description: "View and manage your data", icon: "clipboardList" },
  { id: "saved-questions", title: "Saved Questions", description: "Manage your saved questions", icon: "bookmark", path: "/question-bank" },
  { id: "download-data", title: "Download My Data", description: "Export your data", icon: "download" },
  { id: "privacy-policy", title: "Privacy Policy", description: "Read our privacy policy", icon: "fileText" },
  { id: "terms-of-service", title: "Terms of Service", description: "Read our terms of service", icon: "shieldCheck" }
];
