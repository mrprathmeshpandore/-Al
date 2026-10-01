import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  Landmark, 
  TrendingUp, 
  BookOpen, 
  Globe, 
  Leaf, 
  Scale, 
  Shield, 
  FlaskConical, 
  Network, 
  Users, 
  ChevronRight, 
  ArrowRight 
} from 'lucide-react';

const iconMap = {
  polity: Landmark,
  governance: Shield,
  economy: TrendingUp,
  history: BookOpen,
  geography: Globe,
  environment: Leaf,
  ethics: Scale,
  'science & tech': FlaskConical,
  'science & technology': FlaskConical,
  'international relations': Network,
  society: Users
};

const defaultSubjectList = [
  { name: "Polity", slug: "polity", icon: "polity", color: "bg-rose-50 text-rose-600 border-rose-200" },
  { name: "Governance", slug: "governance", icon: "governance", color: "bg-indigo-50 text-indigo-600 border-indigo-200" },
  { name: "Economy", slug: "economy", icon: "economy", color: "bg-amber-50 text-amber-600 border-amber-200" },
  { name: "History", slug: "history", icon: "history", color: "bg-red-50 text-red-600 border-red-200" },
  { name: "Geography", slug: "geography", icon: "geography", color: "bg-emerald-50 text-emerald-600 border-emerald-200" },
  { name: "Environment", slug: "environment", icon: "environment", color: "bg-green-50 text-green-600 border-green-200" },
  { name: "Ethics", slug: "ethics", icon: "ethics", color: "bg-blue-50 text-blue-600 border-blue-200" },
  { name: "Science & Tech", slug: "science-technology", icon: "science & tech", color: "bg-purple-50 text-purple-600 border-purple-200" },
  { name: "International Relations", slug: "international-relations", icon: "international relations", color: "bg-sky-50 text-sky-600 border-sky-200" },
  { name: "Society", slug: "society", icon: "society", color: "bg-pink-50 text-pink-600 border-pink-200" }
];

export default function StudyMaterialSection({ subjectCounts = [] }) {
  const navigate = useNavigate();

  // Map backend subject counts to subjects list
  const countMap = {};
  if (Array.isArray(subjectCounts)) {
    subjectCounts.forEach((sc) => {
      if (sc.subject) {
        countMap[sc.subject.toLowerCase()] = sc.resource_count;
      }
    });
  }

  const subjectsToDisplay = defaultSubjectList.map((sub) => {
    // Find matching count from backend countMap
    const backendCount = countMap[sub.name.toLowerCase()] ?? countMap[sub.slug.toLowerCase()] ?? 0;
    return {
      ...sub,
      count: backendCount
    };
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-serif font-bold text-slate-900 text-lg">Study Material</h2>
          <p className="text-xs text-slate-500 font-sans">Explore subject-wise resources with real database counts.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {subjectsToDisplay.map((sub, index) => {
          const IconComponent = iconMap[sub.icon] || Landmark;
          return (
            <motion.div
              key={sub.slug}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              onClick={() => navigate(`/resources/${sub.slug}`)}
              className="bg-white rounded-2xl p-3.5 border border-amber-950/5 shadow-2xs hover:shadow-md transition-all flex items-center justify-between cursor-pointer group hover:border-amber-200"
            >
              <div className="flex items-center gap-3 min-w-0">
                <div className={`p-2 rounded-xl ${sub.color} transition-transform group-hover:scale-105 shrink-0`}>
                  <IconComponent className="w-4 h-4" />
                </div>
                <div className="truncate">
                  <h3 className="font-serif font-bold text-slate-900 text-xs group-hover:text-amber-900 transition-colors truncate">
                    {sub.name}
                  </h3>
                  <span className="text-[10.5px] text-slate-400 font-medium font-sans">
                    {sub.count} {sub.count === 1 ? 'resource' : 'resources'}
                  </span>
                </div>
              </div>

              <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-amber-700 group-hover:translate-x-0.5 transition-all shrink-0" />
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
