import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Clock, CheckCircle2, Landmark, Bookmark, FileText, ArrowRight } from 'lucide-react';
import { recentActivity } from '../../data/progressData';

const iconMap = {
  checkCircle: CheckCircle2,
  landmark: Landmark,
  bookmark: Bookmark,
  fileText: FileText
};

export default function RecentActivityCard() {
  const navigate = useNavigate();

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.45 }}
      className="bg-white rounded-2xl p-6 border border-amber-950/5 shadow-sm flex flex-col justify-between"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-blue-50 text-blue-600">
            <Clock className="w-4 h-4" />
          </div>
          <h3 className="font-serif font-bold text-slate-900 text-base">Recent Activity</h3>
        </div>

        <button
          onClick={() => navigate('/progress')}
          className="flex items-center gap-1 text-xs font-semibold text-slate-500 hover:text-amber-800 transition-colors"
        >
          <span>View All</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="space-y-3">
        {recentActivity.map((activity) => {
          const IconComponent = iconMap[activity.icon] || CheckCircle2;
          return (
            <div
              key={activity.id}
              className="flex items-center justify-between p-2 rounded-xl hover:bg-slate-50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-xl ${activity.iconColor}`}>
                  <IconComponent className="w-4 h-4" />
                </div>
                <span className="text-xs font-semibold text-slate-800 font-sans">
                  {activity.text}
                </span>
              </div>

              <span className="text-[11px] text-slate-400 font-medium font-sans">
                {activity.timestamp}
              </span>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}
