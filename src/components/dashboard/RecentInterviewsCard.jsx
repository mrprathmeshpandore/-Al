import React from 'react';
import { motion } from 'framer-motion';
import { Shield, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function RecentInterviewsCard({ recentInterviews }) {
  const navigate = useNavigate();

  const items = (recentInterviews && recentInterviews.length > 0) ? recentInterviews : [];

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-2xs space-y-4">
      {/* HEADER */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-[#0B1628] tracking-tight">
          Recent Interviews
        </h3>
        <button
          onClick={() => navigate('/progress')}
          className="text-xs font-semibold text-slate-500 hover:text-[#0B1628] flex items-center gap-1 transition-colors cursor-pointer"
        >
          <span>View All</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* ROWS LIST */}
      <div className="space-y-3">
        {items.length > 0 ? (
          items.map((item, idx) => {
            const dateStr = item.started_at ? new Date(item.started_at).toLocaleDateString() : 'Recent';
            const scoreVal = item.average_score != null ? `${item.average_score}/10` : 'Pending';

            return (
              <motion.div
                key={item.session_id || idx}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: idx * 0.08 }}
                onClick={() => navigate('/interview')}
                className="flex items-center justify-between p-3.5 rounded-xl border border-slate-100 hover:border-slate-200/80 hover:bg-slate-50/60 transition-all duration-200 group cursor-pointer"
              >
                {/* TOPIC & DATE */}
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-lg bg-slate-100 border border-slate-200/60 text-[#0B1628] flex items-center justify-center group-hover:bg-[#0B1628] group-hover:text-white transition-colors">
                    <Shield className="w-4.5 h-4.5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-[#0B1628] group-hover:text-amber-600 transition-colors">
                      {item.interview_type ? item.interview_type.replace('_', ' ') : 'UPSC Mock Interview'}
                    </h4>
                    <p className="text-[11px] font-medium text-slate-400">
                      {dateStr} · {item.answered_questions || 0} Questions
                    </p>
                  </div>
                </div>

                {/* SCORE & VIEW REPORT */}
                <div className="flex items-center gap-4">
                  <div className="px-2.5 py-1 rounded-full text-xs font-bold border bg-amber-50 border-amber-200 text-amber-800">
                    {scoreVal}
                  </div>
                </div>
              </motion.div>
            );
          })
        ) : (
          <div className="p-4 text-center border border-dashed border-slate-200 rounded-xl text-xs text-slate-500 font-medium">
            No completed mock interviews yet. Start your first session to see evaluation results!
          </div>
        )}
      </div>
    </div>
  );
}
