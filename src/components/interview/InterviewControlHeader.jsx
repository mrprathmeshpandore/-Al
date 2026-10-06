import React, { useState, useEffect } from 'react';
import { Pause, Play, Clock, ShieldCheck, Zap, RefreshCw } from 'lucide-react';
import GlassLanguageSelector from '../common/GlassLanguageSelector';

export default function InterviewControlHeader({ 
  currentIndex = 1, 
  totalQuestions = 5, 
  feedbackMode = 'REAL_BOARD', 
  onToggleFeedbackMode,
  selectedLanguage = 'en-IN',
  onLanguageChange,
  onStartNewSession 
}) {
  const [timeSeconds, setTimeSeconds] = useState(1800); // Default 30 mins
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    if (isPaused) return;
    const interval = setInterval(() => {
      setTimeSeconds(prev => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(interval);
  }, [isPaused]);

  const formatTime = (totalSec) => {
    const mins = Math.floor(totalSec / 60);
    const secs = totalSec % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-2">
      
      {/* PAGE TITLE & SUBTITLE */}
      <div>
        <h1 className="text-xl sm:text-2xl font-bold text-[#0B1628] tracking-tight">
          AI Interview
        </h1>
        <p className="text-xs sm:text-sm font-medium text-slate-500 mt-0.5">
          Simulate. Reflect. Improve.
        </p>
      </div>

      {/* RIGHT CONTROLS: MODE TOGGLE, LANGUAGE, QUESTION COUNTER, TIMER */}
      <div className="flex flex-wrap items-center gap-2.5">
        
        {/* MULTILINGUAL GLASS LANGUAGE SELECTOR */}
        <GlassLanguageSelector 
          selectedLanguage={selectedLanguage} 
          onLanguageChange={onLanguageChange} 
        />

        {/* HYBRID FEEDBACK MODE TOGGLE */}
        <div className="bg-slate-100 p-1 rounded-xl flex items-center gap-1 border border-slate-200 text-xs">
          <button
            onClick={() => onToggleFeedbackMode && onToggleFeedbackMode('REAL_BOARD')}
            className={`px-3 py-1 rounded-lg font-bold flex items-center gap-1.5 transition-all cursor-pointer ${
              feedbackMode === 'REAL_BOARD'
                ? 'bg-[#0B1628] text-white shadow-2xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
            title="Real UPSC Board Mode: Complete interview without interruptions, full report at the end."
          >
            <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
            <span className="hidden sm:inline">UPSC Board Mode</span>
            <span className="sm:hidden">Real</span>
          </button>

          <button
            onClick={() => onToggleFeedbackMode && onToggleFeedbackMode('INSTANT_PRACTICE')}
            className={`px-3 py-1 rounded-lg font-bold flex items-center gap-1.5 transition-all cursor-pointer ${
              feedbackMode === 'INSTANT_PRACTICE'
                ? 'bg-[#0B1628] text-white shadow-2xs'
                : 'text-slate-600 hover:text-slate-900'
            }`}
            title="Practice Mode: Instant feedback right after every answer."
          >
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span className="hidden sm:inline">Practice Mode</span>
            <span className="sm:hidden">Instant</span>
          </button>
        </div>

        {/* NEW SESSION BUTTON */}
        {onStartNewSession && (
          <button
            onClick={() => onStartNewSession && onStartNewSession()}
            className="bg-white hover:bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-xl text-xs font-bold text-slate-700 hover:text-[#0B1628] transition-all shadow-2xs cursor-pointer flex items-center gap-1.5"
            title="Start a new interview session"
          >
            <RefreshCw className="w-3.5 h-3.5 text-amber-600" />
            <span className="hidden sm:inline">New Session</span>
          </button>
        )}

        {/* QUESTION COUNT PILL */}
        <div className="bg-[#0B1628] text-white px-3.5 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 shadow-2xs">
          <span className="text-slate-400">Q</span>
          <span className="text-amber-400 font-black">
            {currentIndex.toString().padStart(2, '0')}
          </span>
          <span className="text-slate-400">/ {totalQuestions}</span>
        </div>

        {/* TIMER PILL */}
        <div className="bg-white border border-slate-200 px-3 py-1.5 rounded-xl text-xs font-extrabold text-slate-800 flex items-center gap-1.5 shadow-2xs">
          <Clock className="w-3.5 h-3.5 text-amber-600" />
          <span>{formatTime(timeSeconds)}</span>
        </div>

        {/* PAUSE BUTTON */}
        <button
          onClick={() => setIsPaused(!isPaused)}
          className="bg-white hover:bg-slate-50 border border-slate-200 p-2 rounded-xl text-slate-700 hover:text-[#0B1628] transition-all shadow-2xs cursor-pointer"
          aria-label={isPaused ? "Resume Interview" : "Pause Interview"}
        >
          {isPaused ? <Play className="w-4 h-4 fill-current text-emerald-600" /> : <Pause className="w-4 h-4 fill-current" />}
        </button>

      </div>

    </div>
  );
}
