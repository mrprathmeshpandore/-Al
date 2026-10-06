import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Trophy, 
  CheckCircle2, 
  AlertTriangle, 
  HelpCircle, 
  RotateCcw, 
  X, 
  Award, 
  ArrowRight,
  TrendingUp,
  FileText
} from 'lucide-react';

export default function InterviewReportModal({ isOpen, onClose, reportData, onStartNewSession }) {
  if (!isOpen) return null;

  if (!reportData) {
    return (
      <AnimatePresence>
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-md p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="bg-white rounded-3xl border border-slate-200 shadow-2xl p-8 max-w-md w-full text-center space-y-6"
          >
            <div className="w-16 h-16 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-600 flex items-center justify-center mx-auto animate-pulse">
              <Trophy className="w-8 h-8 animate-bounce" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-[#0B1628]">Generating Interview Report...</h3>
              <p className="text-xs text-slate-500 mt-1 font-medium">
                Compiling 5-minute performance scorecard, key strengths, and areas to improve.
              </p>
            </div>
            <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
              <div className="bg-amber-500 h-full w-2/3 animate-pulse rounded-full" />
            </div>
          </motion.div>
        </div>
      </AnimatePresence>
    );
  }

  const {
    overall_score = 0,
    percentage = 0,
    grade = 'GOOD',
    answered_count = 0,
    skipped_count = 0,
    total_questions = 5,
    strengths = [],
    areas_to_improve = [],
    question_reports = []
  } = reportData;

  const isExcellent = percentage >= 80;
  const isGood = percentage >= 60 && percentage < 80;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-md p-4 overflow-y-auto">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="bg-white rounded-3xl border border-slate-200 shadow-2xl w-full max-w-3xl max-h-[90vh] flex flex-col overflow-hidden my-auto"
        >
          {/* HEADER BANNER */}
          <div className="bg-[#0B1628] text-white p-6 sm:p-8 relative overflow-hidden shrink-0 border-b border-slate-800">
            <div className="absolute right-0 top-0 bottom-0 w-1/3 bg-gradient-to-l from-amber-500/10 to-transparent pointer-events-none" />
            
            <div className="flex items-start justify-between relative z-10">
              <div className="flex items-center gap-3.5">
                <div className="p-3 rounded-2xl bg-amber-500/20 border border-amber-500/30 text-amber-400">
                  <Trophy className="w-7 h-7" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] uppercase tracking-widest font-black text-amber-400 bg-amber-400/10 px-2.5 py-0.5 rounded-full border border-amber-400/20">
                      Performance Summary Report
                    </span>
                  </div>
                  <h2 className="text-xl sm:text-2xl font-bold font-serif text-white mt-1">
                    AI UPSC Interview Feedback
                  </h2>
                  <p className="text-xs text-slate-400 font-sans mt-0.5">
                    Detailed 5-Minute Analysis & Actionable Insights
                  </p>
                </div>
              </div>

              <button
                onClick={onClose}
                className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* SCORE HERO BADGE */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-6 pt-6 border-t border-slate-800/80">
              <div className="bg-slate-900/80 border border-slate-800 p-3.5 rounded-2xl text-center">
                <span className="text-[11px] font-bold text-slate-400 block uppercase tracking-wider">Overall Score</span>
                <span className="text-2xl sm:text-3xl font-black text-amber-400 font-mono mt-0.5 block">
                  {percentage}%
                </span>
                <span className="text-[10.5px] font-semibold text-slate-400">
                  {overall_score.toFixed(1)} / 10.0
                </span>
              </div>

              <div className="bg-slate-900/80 border border-slate-800 p-3.5 rounded-2xl text-center">
                <span className="text-[11px] font-bold text-slate-400 block uppercase tracking-wider">Performance Grade</span>
                <span className={`text-base sm:text-lg font-black mt-1 block ${
                  isExcellent ? 'text-emerald-400' : isGood ? 'text-amber-400' : 'text-rose-400'
                }`}>
                  {isExcellent ? 'Excellent' : isGood ? 'Good Start' : 'Needs Work'}
                </span>
                <span className="text-[10.5px] font-semibold text-slate-400">
                  {isExcellent ? 'उत्कृष्ट कामगिरी' : isGood ? 'चांगली कामगिरी' : 'सुधारणेची गरज'}
                </span>
              </div>

              <div className="bg-slate-900/80 border border-slate-800 p-3.5 rounded-2xl text-center">
                <span className="text-[11px] font-bold text-slate-400 block uppercase tracking-wider">Questions Answered</span>
                <span className="text-2xl font-black text-white font-mono mt-0.5 block">
                  {answered_count} / {total_questions}
                </span>
                <span className="text-[10.5px] font-semibold text-emerald-400">
                  {Math.round((answered_count / total_questions) * 100)}% Attempted
                </span>
              </div>

              <div className="bg-slate-900/80 border border-slate-800 p-3.5 rounded-2xl text-center">
                <span className="text-[11px] font-bold text-slate-400 block uppercase tracking-wider">Skipped</span>
                <span className="text-2xl font-black text-slate-300 font-mono mt-0.5 block">
                  {skipped_count}
                </span>
                <span className="text-[10.5px] font-semibold text-slate-400">
                  Questions Skipped
                </span>
              </div>
            </div>
          </div>

          {/* SCROLLABLE REPORT BODY */}
          <div className="p-6 sm:p-8 space-y-6 overflow-y-auto">
            
            {/* SECTION 1: WHAT WENT WELL (काय जमलं) */}
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-emerald-700 font-extrabold text-sm border-b border-emerald-100 pb-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                <h3>काय चांगलं जमलं? (Key Strengths)</h3>
              </div>

              <div className="grid grid-cols-1 gap-2.5">
                {strengths && strengths.length > 0 ? (
                  strengths.map((str, idx) => (
                    <div key={idx} className="bg-emerald-50/60 border border-emerald-200/80 p-3 rounded-xl flex items-start gap-2.5 text-xs text-emerald-950 font-medium">
                      <span className="w-5 h-5 rounded-full bg-emerald-200 text-emerald-800 font-bold flex items-center justify-center shrink-0 text-[10px] mt-0.5">
                        {idx + 1}
                      </span>
                      <p className="leading-relaxed">{str}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-500 font-medium italic">General active participation in interview simulation.</p>
                )}
              </div>
            </div>

            {/* SECTION 2: AREAS FOR IMPROVEMENT (कुठे सुधारणा करायची) */}
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-amber-800 font-extrabold text-sm border-b border-amber-100 pb-2">
                <TrendingUp className="w-5 h-5 text-amber-600" />
                <h3>कुठे सुधारणा करायची? (Areas to Improve & Recommendations)</h3>
              </div>

              <div className="grid grid-cols-1 gap-2.5">
                {areas_to_improve && areas_to_improve.length > 0 ? (
                  areas_to_improve.map((imp, idx) => (
                    <div key={idx} className="bg-amber-50/60 border border-amber-200/80 p-3 rounded-xl flex items-start gap-2.5 text-xs text-amber-950 font-medium">
                      <span className="w-5 h-5 rounded-full bg-amber-200 text-amber-900 font-bold flex items-center justify-center shrink-0 text-[10px] mt-0.5">
                        {idx + 1}
                      </span>
                      <p className="leading-relaxed">{imp}</p>
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-500 font-medium italic">Practice structured delivery and citing official legal/policy frameworks.</p>
                )}
              </div>
            </div>

            {/* SECTION 3: QUESTION BY QUESTION BREAKDOWN */}
            <div className="space-y-3 pt-2">
              <div className="flex items-center justify-between border-b border-slate-200 pb-2">
                <div className="flex items-center gap-2 text-[#0B1628] font-extrabold text-sm">
                  <FileText className="w-4.5 h-4.5 text-amber-600" />
                  <h3>Question-by-Question Detailed Breakdown</h3>
                </div>
              </div>

              <div className="space-y-3">
                {question_reports.map((q, idx) => (
                  <div key={idx} className="bg-slate-50 border border-slate-200/80 rounded-2xl p-4 space-y-2">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-bold text-[#0B1628]">
                        Q{q.sequence_number}. {q.question_text}
                      </span>
                      <span className={`px-2.5 py-1 rounded-full text-[11px] font-extrabold border shrink-0 ${
                        q.status === 'SKIPPED'
                          ? 'bg-slate-200 text-slate-700 border-slate-300'
                          : q.score >= 8
                          ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                          : q.score >= 6
                          ? 'bg-amber-100 text-amber-800 border-amber-300'
                          : 'bg-rose-100 text-rose-800 border-rose-300'
                      }`}>
                        {q.status === 'SKIPPED' ? 'Skipped' : `${Math.round(q.score * 10)}% (${q.score}/10)`}
                      </span>
                    </div>

                    <p className="text-xs text-slate-600 leading-relaxed font-normal bg-white p-3 rounded-xl border border-slate-200/60">
                      {q.overall_feedback}
                    </p>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* FOOTER ACTIONS */}
          <div className="p-6 bg-slate-50 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3 shrink-0">
            <button
              onClick={onClose}
              className="w-full sm:w-auto px-6 py-2.5 rounded-full text-xs font-bold text-slate-700 bg-white border border-slate-300 hover:bg-slate-100 cursor-pointer"
            >
              Close Report
            </button>

            <button
              onClick={() => onStartNewSession && onStartNewSession()}
              className="w-full sm:w-auto px-6 py-2.5 rounded-full text-xs font-bold text-white bg-[#0B1628] hover:bg-[#152744] flex items-center justify-center gap-2 shadow-md cursor-pointer"
            >
              <RotateCcw className="w-4 h-4 text-amber-400" />
              <span>Start New Interview Session →</span>
            </button>
          </div>

        </motion.div>
      </div>
    </AnimatePresence>
  );
}
