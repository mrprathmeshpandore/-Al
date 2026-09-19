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
import { subjects } from '../../data/resourcesData';

const iconMap = {
  landmark: Landmark,
  trendingUp: TrendingUp,
  bookOpen: BookOpen,
  globe: Globe,
  leaf: Leaf,
  scale: Scale,
  shield: Shield,
  flask: FlaskConical,
  network: Network,
  users: Users
};

export default function StudyMaterialSection() {
  const navigate = useNavigate();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="font-serif font-bold text-slate-900 text-lg">Study Material</h2>
          <p className="text-xs text-slate-500 font-sans">Explore subject-wise resources.</p>
        </div>
        <button className="flex items-center gap-1 text-xs font-semibold text-slate-500 hover:text-amber-800 transition-colors">
          <span>View All</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {subjects.map((sub, index) => {
          const IconComponent = iconMap[sub.icon] || Landmark;
          return (
            <motion.div
              key={sub.id}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              onClick={() => navigate(`/resources/${sub.slug}`)}
              className="bg-white rounded-2xl p-3.5 border border-amber-950/5 shadow-2xs hover:shadow-md transition-all flex items-center justify-between cursor-pointer group hover:border-amber-200"
            >
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-xl ${sub.color} transition-transform group-hover:scale-105`}>
                  <IconComponent className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-serif font-bold text-slate-900 text-xs group-hover:text-amber-900 transition-colors">
                    {sub.name}
                  </h3>
                  <span className="text-[10.5px] text-slate-400 font-medium font-sans">
                    {sub.count} resources
                  </span>
                </div>
              </div>

              <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-amber-700 group-hover:translate-x-0.5 transition-all" />
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
