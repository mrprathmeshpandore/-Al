import React, { useState } from 'react';
import { Volume2, VolumeX } from 'lucide-react';

export default function QuestionHeaderCard({ questionData }) {
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);

  const handleListenAgain = () => {
    setIsPlayingAudio(true);
    // Simulate text-to-speech reading animation
    setTimeout(() => {
      setIsPlayingAudio(false);
    }, 4000);
  };

  return (
    <div className="w-full bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-2xs text-center space-y-4 relative">
      
      {/* BADGE (MAIN QUESTION / FOLLOW-UP / COUNTER) */}
      <div className="inline-block">
        <span className="text-[11px] font-extrabold tracking-wider uppercase bg-[#0B1628] text-white px-3.5 py-1 rounded-full shadow-2xs">
          {questionData.type || 'MAIN QUESTION'}
        </span>
      </div>

      {/* LARGE QUESTION HEADING */}
      <h2 className="text-xl sm:text-2xl lg:text-3xl font-extrabold text-[#0B1628] tracking-tight leading-tight max-w-3xl mx-auto font-sans">
        "{questionData.question}"
      </h2>

      {/* SUPPORTING GUIDANCE TEXT */}
      <p className="text-xs sm:text-sm font-medium text-slate-500 max-w-xl mx-auto leading-relaxed">
        {questionData.promptText}
      </p>

      {/* AUDIO BUTTON */}
      <div className="pt-2">
        <button
          onClick={handleListenAgain}
          disabled={isPlayingAudio}
          className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold border transition-all cursor-pointer ${
            isPlayingAudio
              ? 'bg-amber-500/10 text-amber-700 border-amber-300 animate-pulse'
              : 'bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-200 hover:border-slate-300'
          }`}
        >
          {isPlayingAudio ? (
            <>
              <Volume2 className="w-4 h-4 text-amber-600 animate-bounce" />
              <span>Speaking Question...</span>
            </>
          ) : (
            <>
              <Volume2 className="w-4 h-4 text-slate-600" />
              <span>Listen to Question Again</span>
            </>
          )}
        </button>
      </div>

    </div>
  );
}
