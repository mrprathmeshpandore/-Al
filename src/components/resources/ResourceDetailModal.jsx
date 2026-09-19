import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { X, Bookmark, Download, ExternalLink, Sparkles, CheckCircle2, FileText, ArrowRight } from 'lucide-react';

export default function ResourceDetailModal({ resource, onClose, onToggleBookmark, isBookmarked }) {
  const navigate = useNavigate();

  if (!resource) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="bg-white rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-amber-950/10 shadow-2xl p-6 sm:p-8 space-y-6 relative custom-scrollbar"
        >
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-5 right-5 p-2 rounded-full bg-slate-100 text-slate-500 hover:text-slate-800 hover:bg-slate-200 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>

          {/* Header Metadata */}
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-1 rounded-lg bg-amber-50 text-amber-700 text-xs font-bold border border-amber-200">
                {resource.type || 'PDF'}
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-slate-100 text-slate-600 text-xs font-semibold">
                {resource.subject || 'UPSC General'}
              </span>
              {resource.isOfficial && (
                <span className="flex items-center gap-1 text-xs text-emerald-600 font-bold bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Official
                </span>
              )}
            </div>

            <h2 className="font-serif font-extrabold text-2xl text-[#0B1628] leading-tight">
              {resource.title}
            </h2>

            <p className="text-xs text-slate-500 font-sans flex items-center gap-3">
              <span>Source: {resource.source || 'Prashasak AI Curated'}</span>
              <span>•</span>
              <span>Size: {resource.fileSize || '2.4 MB'}</span>
            </p>
          </div>

          {/* Description */}
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/80 text-xs text-slate-700 font-sans leading-relaxed">
            {resource.description}
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center gap-3">
            <a
              href="#"
              onClick={(e) => { e.preventDefault(); alert("Opening resource viewer..."); }}
              className="flex items-center gap-2 py-2.5 px-4 rounded-xl bg-[#0B1628] hover:bg-[#132238] text-white text-xs font-semibold shadow-sm transition-all"
            >
              <ExternalLink className="w-4 h-4" />
              <span>Open Resource</span>
            </a>

            <button
              onClick={() => alert("Downloading resource...")}
              className="flex items-center gap-2 py-2.5 px-4 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-all"
            >
              <Download className="w-4 h-4" />
              <span>Download</span>
            </button>

            <button
              onClick={() => onToggleBookmark(resource.id)}
              className={`flex items-center gap-2 py-2.5 px-4 rounded-xl border text-xs font-semibold transition-all ${
                isBookmarked
                  ? 'bg-amber-50 text-amber-700 border-amber-300'
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
              }`}
            >
              <Bookmark className={`w-4 h-4 ${isBookmarked ? 'fill-amber-500 text-amber-500' : ''}`} />
              <span>{isBookmarked ? 'Saved' : 'Save'}</span>
            </button>
          </div>

          {/* Why This Matters For UPSC */}
          <div className="space-y-2">
            <h3 className="font-serif font-bold text-slate-900 text-sm flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-600" />
              <span>Why This Matters For UPSC</span>
            </h3>
            <p className="text-xs text-slate-600 font-sans leading-relaxed bg-amber-50/60 p-3.5 rounded-xl border border-amber-200/60">
              {resource.whyItMatters || "Offers critical conceptual clarity and official analytical perspectives required for both Mains answers and personality test discussions."}
            </p>
          </div>

          {/* Key Topics */}
          <div className="space-y-2">
            <h3 className="font-serif font-bold text-slate-900 text-sm">Key Topics Covered</h3>
            <div className="flex flex-wrap gap-2">
              {(resource.keyTopics || ["Constitutional Framework", "Policy Analysis", "Governance", "Current Context"]).map((topic) => (
                <span key={topic} className="px-3 py-1 rounded-xl bg-slate-100 text-slate-700 text-xs font-medium border border-slate-200/60">
                  {topic}
                </span>
              ))}
            </div>
          </div>

          {/* CTA: Practice Interview Questions */}
          <div className="pt-4 border-t border-slate-100 flex items-center justify-between">
            <div>
              <h4 className="font-serif font-bold text-slate-900 text-xs">Ready to test your understanding?</h4>
              <p className="text-[11px] text-slate-500">Practice AI interview questions based on this resource.</p>
            </div>

            <button
              onClick={() => { onClose(); navigate('/interview'); }}
              className="flex items-center gap-2 py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-sm transition-all group"
            >
              <span>Practice Questions</span>
              <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
