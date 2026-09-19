import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { UserCheck, Sparkles, X, Volume2 } from 'lucide-react';
import { interviewers } from '../../data/interviewData';

export default function InterviewerCard({ isSpeaking, isProcessing }) {
  const [selectedInterviewer, setSelectedInterviewer] = useState(interviewers[0]);
  const [showAvatarModal, setShowAvatarModal] = useState(false);

  return (
    <div className="w-full bg-[#0B1628] rounded-2xl border border-slate-800 shadow-md overflow-hidden relative group">
      
      {/* INTERVIEWER PORTRAIT / VIEWPORT AREA */}
      <div className="relative w-full h-[320px] sm:h-[360px] md:h-[400px] flex items-center justify-center overflow-hidden bg-[#0A1220]">
        
        {/* BACKGROUND REALISTIC CINEMATIC OFFICE COMPOSITION */}
        <img 
          src={selectedInterviewer.image} 
          alt={selectedInterviewer.name}
          className={`w-full h-full object-cover object-[center_20%] transition-transform duration-700 ${
            isSpeaking ? 'scale-105 filter brightness-105' : 'scale-100'
          }`}
          onError={(e) => {
            // High quality fallback
            e.target.src = "https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&q=80&w=1200";
          }}
        />

        {/* SOFT CINEMATIC VIGNETTE & LIGHTING OVERLAYS */}
        <div className="absolute inset-0 bg-gradient-to-t from-[#0B1628] via-transparent to-black/40 pointer-events-none" />
        <div className="absolute inset-0 bg-gradient-to-r from-black/20 via-transparent to-black/20 pointer-events-none" />

        {/* INDIAN GOVERNANCE MOTIF: ASHOKA STAMP IN CORNER */}
        <div className="absolute top-4 right-4 text-white/60 text-right pointer-events-none flex items-center gap-2 bg-black/40 backdrop-blur-md px-3 py-1 rounded-full border border-white/10">
          <span className="text-[10px] font-serif tracking-widest uppercase font-bold text-amber-300">
            सत्यमेव जयते
          </span>
        </div>

        {/* TOP LEFT STATUS BADGE */}
        <div className="absolute top-4 left-4 flex items-center gap-2 bg-[#0B1628]/85 backdrop-blur-md px-3.5 py-1.5 rounded-full border border-slate-700/80 shadow-md z-10">
          <div className="relative flex items-center justify-center">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="absolute w-4 h-4 rounded-full bg-emerald-500/30 animate-ping" />
          </div>
          <div className="flex flex-col">
            <span className="text-xs font-bold text-white leading-none">
              AI Interviewer
            </span>
            <span className="text-[9.5px] font-semibold text-emerald-400 leading-none mt-0.5">
              {selectedInterviewer.status}
            </span>
          </div>
        </div>

        {/* SPEECH BUBBLE FROM INTERVIEWER (POSITIONED AT BOTTOM LEFT WITHOUT BLOCKING FACE) */}
        <motion.div 
          initial={{ opacity: 0, y: 10, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.4 }}
          className="absolute left-4 sm:left-6 bottom-4 sm:bottom-6 z-10 max-w-xs sm:max-w-sm bg-white/95 backdrop-blur-md p-3.5 sm:p-4 rounded-2xl shadow-xl border border-slate-200/90 text-slate-800"
        >
          <div className="flex items-start gap-2.5">
            <div className="w-2 h-2 rounded-full bg-amber-500 shrink-0 mt-1.5 animate-ping" />
            <div className="space-y-0.5">
              <span className="text-[10px] font-bold tracking-wider text-amber-700 uppercase block">
                {selectedInterviewer.name}
              </span>
              <p className="text-xs font-semibold text-slate-800 leading-relaxed font-sans">
                {isProcessing 
                  ? "Evaluating your response against UPSC criteria..." 
                  : `"${selectedInterviewer.initialSpeech}"`
                }
              </p>
            </div>
          </div>
        </motion.div>

        {/* BOTTOM RIGHT OVERLAY BUTTON: CHANGE AVATAR */}
        <button
          onClick={() => setShowAvatarModal(true)}
          className="absolute bottom-4 right-4 z-10 bg-white/95 hover:bg-white text-slate-800 border border-slate-200 px-3.5 py-1.5 rounded-full text-xs font-bold flex items-center gap-1.5 shadow-md backdrop-blur-xs transition-all hover:scale-105 cursor-pointer"
        >
          <UserCheck className="w-3.5 h-3.5 text-amber-600" />
          <span>Change Avatar</span>
        </button>

      </div>

      {/* AVATAR SELECTOR MODAL */}
      <AnimatePresence>
        {showAvatarModal && (
          <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="bg-white rounded-2xl p-6 max-w-lg w-full border border-slate-200 shadow-2xl space-y-4"
            >
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-amber-600" />
                  <h3 className="text-base font-bold text-[#0B1628]">Select AI Interviewer</h3>
                </div>
                <button 
                  onClick={() => setShowAvatarModal(false)}
                  className="p-1 text-slate-400 hover:text-slate-700 rounded-lg cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-3">
                {interviewers.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => {
                      setSelectedInterviewer(item);
                      setShowAvatarModal(false);
                    }}
                    className={`w-full flex items-center gap-3.5 p-3 rounded-xl border text-left transition-all cursor-pointer ${
                      selectedInterviewer.id === item.id 
                        ? 'border-[#0B1628] bg-amber-500/10 shadow-2xs' 
                        : 'border-slate-200 hover:bg-slate-50'
                    }`}
                  >
                    <img 
                      src={item.image} 
                      alt={item.name} 
                      className="w-12 h-12 rounded-full object-cover object-[center_20%] border-2 border-white shadow-xs shrink-0"
                    />
                    <div className="flex-1 min-w-0">
                      <h4 className="text-xs font-bold text-[#0B1628] truncate">{item.name}</h4>
                      <p className="text-[11px] font-medium text-slate-500 truncate">{item.role}</p>
                    </div>
                    {selectedInterviewer.id === item.id && (
                      <span className="text-xs font-bold text-amber-600 bg-amber-100 px-2 py-0.5 rounded-full">Active</span>
                    )}
                  </button>
                ))}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

    </div>
  );
}
