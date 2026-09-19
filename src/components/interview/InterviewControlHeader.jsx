import React, { useState, useEffect } from 'react';
import { Pause, Play, Clock, HelpCircle } from 'lucide-react';
import { interviewSession } from '../../data/interviewData';

export default function InterviewControlHeader() {
  const [timeSeconds, setTimeSeconds] = useState(interviewSession.timeRemainingSeconds);
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

      {/* RIGHT CONTROLS: QUESTION COUNTER, TIMER & QUOTE */}
      <div className="flex flex-wrap items-center gap-3">
        
        {/* QUOTE BOX (Hidden on small mobile) */}
        <div className="hidden lg:block text-right pr-2">
          <p className="text-[11.5px] italic font-semibold text-slate-700 font-serif">
            {interviewSession.quote}
          </p>
        </div>

        {/* QUESTION COUNT PILL */}
        <div className="bg-[#0B1628] text-white px-3.5 py-1.5 rounded-xl text-xs font-bold flex items-center gap-1.5 shadow-2xs">
          <span className="text-slate-400">Question</span>
          <span className="text-amber-400 font-black">
            {interviewSession.currentQuestionIndex.toString().padStart(2, '0')}
          </span>
          <span className="text-slate-400">/ {interviewSession.totalQuestions}</span>
        </div>

        {/* TIMER PILL */}
        <div className="bg-white border border-slate-200 px-3.5 py-1.5 rounded-xl text-xs font-extrabold text-slate-800 flex items-center gap-1.5 shadow-2xs">
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
