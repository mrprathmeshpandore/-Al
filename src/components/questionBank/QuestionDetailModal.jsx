import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  Bookmark, 
  ArrowRight, 
  HelpCircle, 
  Sparkles, 
  CheckCircle2, 
  GitPullRequest,
  BookOpen
} from 'lucide-react';

export default function QuestionDetailModal({ item, onClose, onToggleBookmark }) {
  const navigate = useNavigate();

  if (!item) return null;

  const handleStartPractice = () => {
    onClose();
    navigate('/interview', {
      state: {
        questionId: item.id,
        question: item.question,
        topic: item.tags?.[0] || item.category,
        categories: item.tags || [item.type],
        source: "QUESTION BANK"
      }
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs overflow-y-auto">
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 15 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 15 }}
        className="bg-white rounded-2xl max-w-2xl w-full border border-slate-200 shadow-2xl overflow-hidden my-8 max-h-[90vh] flex flex-col font-sans"
      >
        
        {/* MODAL HEADER */}
        <div className="p-6 bg-[#0B1628] text-white flex items-start justify-between gap-4 shrink-0">
          <div className="space-y-2 max-w-xl">
            <span className="text-[10px] font-extrabold tracking-wider uppercase bg-amber-500/20 text-amber-300 border border-amber-400/40 px-2.5 py-0.5 rounded-full inline-block">
              POTENTIAL INTERVIEW QUESTION
            </span>
            <h2 className="text-lg sm:text-xl font-extrabold leading-tight">
              "{item.question}"
            </h2>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => onToggleBookmark(item.id)}
              className={`p-2 rounded-full border transition-all cursor-pointer ${
                item.isBookmarked 
                  ? 'bg-amber-500 text-white border-amber-400' 
                  : 'bg-white/10 text-white border-white/20 hover:bg-white/20'
              }`}
              aria-label="Bookmark Question"
            >
              <Bookmark className={`w-4 h-4 ${item.isBookmarked ? 'fill-current' : ''}`} />
            </button>

            <button
              onClick={onClose}
              className="p-2 rounded-full bg-white/10 hover:bg-white/20 text-white border border-white/20 transition-all cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* MODAL BODY CONTENT */}
        <div className="p-6 sm:p-8 overflow-y-auto space-y-6 flex-1 text-slate-700">
          
          {/* WHY THIS QUESTION MATTERS */}
          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-200/60 space-y-1">
            <h4 className="text-xs font-bold text-amber-800 uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-amber-600" />
              <span>Why This Question Matters</span>
            </h4>
            <p className="text-xs font-semibold text-slate-800 leading-relaxed">
              {item.whyItMatters || item.description}
            </p>
          </div>

          {/* UPSC RELEVANCE */}
          <div className="space-y-1.5">
            <h3 className="text-xs font-bold text-[#0B1628] uppercase tracking-wider">UPSC Relevance</h3>
            <p className="text-xs font-semibold text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-200/60">
              {item.upscRelevance}
            </p>
          </div>

          {/* KEY AREAS TO THINK ABOUT */}
          {item.keyAreas && (
            <div className="space-y-2">
              <h3 className="text-xs font-bold text-[#0B1628] uppercase tracking-wider">Key Areas To Think About</h3>
              <ul className="space-y-2 text-xs font-medium text-slate-600">
                {item.keyAreas.map((area, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                    <span>{area}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* POTENTIAL FOLLOW-UP QUESTION */}
          {item.potentialFollowUp && (
            <div className="p-3.5 rounded-xl bg-blue-500/5 border border-blue-200/60 space-y-1">
              <span className="text-[10px] font-extrabold tracking-wider text-blue-700 uppercase flex items-center gap-1">
                <GitPullRequest className="w-3.5 h-3.5 text-blue-600" />
                <span>Possible Follow-up Question</span>
              </span>
              <p className="text-xs font-bold text-[#0B1628]">
                "{item.potentialFollowUp}"
              </p>
            </div>
          )}

          {/* POTENTIAL COUNTER QUESTION */}
          {item.potentialCounterQuestion && (
            <div className="p-3.5 rounded-xl bg-rose-500/5 border border-rose-200/60 space-y-1">
              <span className="text-[10px] font-extrabold tracking-wider text-rose-700 uppercase flex items-center gap-1">
                <HelpCircle className="w-3.5 h-3.5 text-rose-600" />
                <span>Possible Counter Question</span>
              </span>
              <p className="text-xs font-bold text-[#0B1628]">
                "{item.potentialCounterQuestion}"
              </p>
            </div>
          )}

        </div>

        {/* MODAL FOOTER */}
        <div className="p-4 sm:p-6 bg-slate-50 border-t border-slate-200 flex items-center justify-between shrink-0">
          <button
            onClick={() => onToggleBookmark(item.id)}
            className="px-4 py-2 rounded-full text-xs font-bold text-slate-700 border border-slate-300 hover:bg-slate-100 cursor-pointer"
          >
            {item.isBookmarked ? 'Saved' : 'Save Question'}
          </button>

          <button
            onClick={handleStartPractice}
            className="bg-[#0B1628] hover:bg-[#152744] text-white px-6 py-2.5 rounded-full text-xs font-bold inline-flex items-center gap-2 shadow-md cursor-pointer"
          >
            <span>Start Practice →</span>
            <ArrowRight className="w-4 h-4 text-amber-400" />
          </button>
        </div>

      </motion.div>
    </div>
  );
}
