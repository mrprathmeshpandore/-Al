// Centralized Mock Data & Schema for Prashasak AI DAF Profile

export const initialProfileData = {
  personal: {
    fullName: "Pratham Pandore",
    dob: "2004-04-25",
    homeState: "Maharashtra",
    district: "Pune",
    currentCity: "Pune",
    gender: "Male",
    photoUrl: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=250"
  },
  education: {
    degree: "B.Tech Computer Science",
    university: "Savitribai Phule Pune University",
    specialization: "Artificial Intelligence & Data Systems",
    postGraduation: "",
    otherQualifications: ""
  },
  upscJourney: {
    attemptCount: "1",
    optionalSubject: "Public Administration",
    hasPreviousInterview: "No",
    preparationStage: "Interview Preparation"
  },
  interests: {
    hobbies: "Photography, Classical Music",
    sports: "Badminton",
    readingBooks: "Indian History, Public Policy",
    areasOfInterest: "Digital Governance, Rural Development",
    communityActivities: "NSS Volunteer"
  },
  perspective: {
    whyCivilServices: "To contribute to grassroot policy implementation and public service at scale.",
    keyFocusAreas: "Digital Public Infrastructure, Education reform",
    boardNotes: "Passionate about leveraging technology for administrative efficiency."
  }
};

export const profileSteps = [
  { id: 1, key: 'personal', title: 'Personal', subtitle: 'About You' },
  { id: 2, key: 'education', title: 'Education', subtitle: 'Your Academics' },
  { id: 3, key: 'upscJourney', title: 'UPSC Journey', subtitle: 'Your Preparation' },
  { id: 4, key: 'interests', title: 'Interests', subtitle: 'Beyond Academics' },
  { id: 5, key: 'perspective', title: 'Perspective', subtitle: 'Your Thoughts' },
];

export const indianStates = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
  "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
  "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
  "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
  "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
  "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi (NCT)"
];

export const maharashtraDistricts = [
  "Ahmednagar", "Akola", "Amravati", "Chhatrapati Sambhajinagar", "Beed",
  "Bhandara", "Buldhana", "Chandrapur", "Dhule", "Gadchiroli",
  "Gondia", "Hingoli", "Jalgaon", "Jalna", "Kolhapur",
  "Latur", "Mumbai City", "Mumbai Suburban", "Nagpur", "Nanded",
  "Nandurbar", "Nashik", "Dharashiv", "Palghar", "Parbhani",
  "Pune", "Raigad", "Ratnagiri", "Sangli", "Satara",
  "Sindhudurg", "Solapur", "Thane", "Wardha", "Washim", "Yavatmal"
];

export const optionalSubjects = [
  "Public Administration", "Political Science & International Relations",
  "Sociology", "Geography", "History", "Economics", "Philosophy",
  "Psychology", "Law", "Anthropology", "Management", "Commerce & Accountancy",
  "Agriculture", "Animal Husbandry & Veterinary Science", "Botany", "Chemistry",
  "Civil Engineering", "Electrical Engineering", "Mechanical Engineering",
  "Geology", "Mathematics", "Medical Science", "Physics", "Statistics", "Zoology",
  "Literature of Marathi", "Literature of Hindi", "Literature of English", "Literature of Tamil"
];

export const prepStages = [
  "Beginner",
  "Prelims Preparation",
  "Mains Preparation",
  "Interview Preparation"
];
