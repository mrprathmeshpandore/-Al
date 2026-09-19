import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, 
  Calendar, 
  Sparkles, 
  ArrowRight, 
  HelpCircle, 
  FileText, 
  CheckCircle2, 
  AlertTriangle,
  Bookmark
} from 'lucide-react';

export default function CurrentAffairDetailModal({ article, onClose, onToggleBookmark }) {
  const navigate = useNavigate();

  if (!article) return null;

  const handleStartPractice = () => {
    onClose();
    navigate('/interview', {
      state: {
        topic: article.title,
        categories: [article.categoryLabel || article.category, article.subcategory],
        source: "CURRENT AFFAIRS"
      }
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs overflow-y-auto">
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 15 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 15 }}
        className="bg-white rounded-2xl max-w-3xl w-full border border-slate-200 shadow-2xl overflow-hidden my-8 max-h-[90vh] flex flex-col"
      >
        
        {/* HERO IMAGE & HEADER CLOSE BUTTON */}
        <div className="relative h-56 sm:h-64 w-full bg-slate-900 shrink-0">
          <img
            src={article.image}
            alt={article.title}
            className="w-full h-full object-cover opacity-80"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#0B1628] via-[#0B1628]/40 to-transparent" />

          {/* CLOSE & BOOKMARK BUTTONS */}
          <div className="absolute top-4 right-4 flex items-center gap-2">
            <button
              onClick={() => onToggleBookmark(article.id)}
              className={`p-2 rounded-full backdrop-blur-md border transition-all cursor-pointer ${
                article.isBookmarked 
                  ? 'bg-amber-500 text-white border-amber-400' 
                  : 'bg-white/80 text-slate-800 border-white/60 hover:bg-white'
              }`}
            >
              <Bookmark className={`w-4 h-4 ${article.isBookmarked ? 'fill-current' : ''}`} />
            </button>

            <button
              onClick={onClose}
              className="p-2 rounded-full bg-white/80 hover:bg-white text-slate-800 backdrop-blur-md border border-white/60 transition-all cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* OVERLAY TITLE & CATEGORY */}
          <div className="absolute bottom-6 left-6 right-6 text-white space-y-2">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-[10px] font-extrabold uppercase bg-amber-500 text-slate-950 px-2.5 py-0.5 rounded">
                {article.categoryLabel || article.category}
              </span>
              <span className="text-xs font-semibold text-slate-300">
                · {article.subcategory}
              </span>
              <span className="text-xs font-semibold text-slate-300 flex items-center gap-1 ml-auto">
                <Calendar className="w-3.5 h-3.5" />
                <span>{article.date}</span>
              </span>
            </div>

            <h2 className="text-xl sm:text-2xl font-extrabold tracking-tight leading-tight">
              {article.title}
            </h2>
          </div>
        </div>

        {/* MODAL BODY (SCROLLABLE) */}
        <div className="p-6 sm:p-8 overflow-y-auto space-y-6 flex-1 text-slate-700 font-sans">
          
          {/* WHY IT MATTERS */}
          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-200/60 space-y-1">
            <h4 className="text-xs font-bold text-amber-800 uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-amber-600" />
              <span>Why It Matters</span>
            </h4>
            <p className="text-xs font-semibold text-slate-800 leading-relaxed">
              {article.whyItMatters || article.summary}
            </p>
          </div>

          {/* SHORT CONTEXT */}
          <div className="space-y-2">
            <h3 className="text-sm font-bold text-[#0B1628]">Short Context</h3>
            <p className="text-xs font-medium text-slate-600 leading-relaxed">
              {article.shortContext || article.summary}
            </p>
          </div>

          {/* KEY POINTS */}
          {article.keyPoints && (
            <div className="space-y-2">
              <h3 className="text-sm font-bold text-[#0B1628]">Key Points</h3>
              <ul className="space-y-2 text-xs font-medium text-slate-600">
                {article.keyPoints.map((pt, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                    <span>{pt}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* UPSC RELEVANCE */}
          {article.upscRelevance && (
            <div className="space-y-2 pt-2 border-t border-slate-100">
              <h3 className="text-sm font-bold text-[#0B1628]">UPSC GS Paper Mapping</h3>
              <div className="flex flex-wrap gap-2">
                {article.upscRelevance.map((rel, idx) => (
                  <div key={idx} className="p-2.5 rounded-xl bg-slate-50 border border-slate-200/80 text-xs font-semibold flex items-center gap-2">
                    <span className="font-extrabold text-[#0B1628] bg-slate-200 px-2 py-0.5 rounded text-[10px]">
                      {rel.paper}
                    </span>
                    <span>{rel.topic}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* POTENTIAL INTERVIEW QUESTIONS */}
          {article.potentialQuestions && (
            <div className="space-y-3 pt-2 border-t border-slate-100">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-bold text-[#0B1628] flex items-center gap-2">
                  <HelpCircle className="w-4 h-4 text-amber-600" />
                  <span>Potential UPSC Interview Questions</span>
                </h3>
                <span className="text-[10.5px] font-semibold text-slate-400">Practice-Worthy</span>
              </div>

              <div className="space-y-2.5">
                {article.potentialQuestions.map((q, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-amber-500/5 border border-amber-200/60 space-y-1">
                    <span className="text-[10px] font-extrabold tracking-wider text-amber-700 uppercase">
                      {q.type}
                    </span>
                    <p className="text-xs font-bold text-[#0B1628] leading-snug">
                      "{q.text}"
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>

        {/* MODAL FOOTER CTA */}
        <div className="p-4 sm:p-6 bg-slate-50 border-t border-slate-200 flex items-center justify-between shrink-0">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-full text-xs font-bold text-slate-600 hover:text-slate-900 border border-slate-200 cursor-pointer"
          >
            Close
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
