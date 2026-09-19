import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Mic, 
  Keyboard, 
  Square, 
  Send, 
  Sparkles, 
  ArrowRight, 
  CheckCircle2, 
  RotateCcw,
  Volume2
} from 'lucide-react';
import { mockFeedback } from '../../data/interviewData';

export default function AnswerArea({ onStateChange, onNextQuestion }) {
  // STATES: 'IDLE' | 'LISTENING' | 'TEXT_MODE' | 'PROCESSING' | 'FEEDBACK'
  const [modeState, setModeState] = useState('IDLE');
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [typedAnswer, setTypedAnswer] = useState('');

  // VOICE RECORDING TIMER
  useEffect(() => {
    let interval = null;
    if (modeState === 'LISTENING') {
      interval = setInterval(() => {
        setRecordingSeconds(prev => prev + 1);
      }, 1000);
    } else {
      setRecordingSeconds(0);
    }
    return () => clearInterval(interval);
  }, [modeState]);

  // NOTIFY PARENT COMPONENT OF INTERVIEW STATE
  useEffect(() => {
    if (onStateChange) {
      onStateChange(modeState);
    }
  }, [modeState, onStateChange]);

  const handleStartVoice = () => {
    setModeState('LISTENING');
  };

  const handleStopVoice = () => {
    setModeState('PROCESSING');
    setTimeout(() => {
      setModeState('FEEDBACK');
    }, 2500);
  };

  const handleSubmitText = () => {
    if (!typedAnswer.trim()) return;
    setModeState('PROCESSING');
    setTimeout(() => {
      setModeState('FEEDBACK');
    }, 2500);
  };

  const handleContinueNext = () => {
    setModeState('IDLE');
    setTypedAnswer('');
    if (onNextQuestion) onNextQuestion();
  };

  const formatRecTime = (sec) => {
    const mins = Math.floor(sec / 60);
    const secs = sec % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="w-full bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-2xs space-y-6">
      
      <AnimatePresence mode="wait">
        
        {/* STATE 1: IDLE DEFAULT STATE */}
        {modeState === 'IDLE' && (
          <motion.div
            key="idle"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center"
          >
            {/* LEFT CARD: VOICE INFO */}
            <div className="bg-slate-50/70 border border-slate-200/70 rounded-2xl p-5 text-center space-y-2 flex flex-col items-center justify-center min-h-[140px]">
              <div className="w-9 h-9 rounded-full bg-slate-200/70 text-slate-700 flex items-center justify-center">
                <Mic className="w-4.5 h-4.5" />
              </div>
              <h4 className="text-xs font-bold text-[#0B1628]">Answer using voice</h4>
              <p className="text-[11px] font-medium text-slate-500 leading-relaxed">
                Speak naturally, just like a real interview.
              </p>
            </div>

            {/* CENTER CTA: MAIN MICROPHONE BUTTON */}
            <div className="flex flex-col items-center justify-center text-center space-y-3">
              <motion.button
                whileHover={{ scale: 1.06 }}
                whileTap={{ scale: 0.94 }}
                onClick={handleStartVoice}
                className="w-20 h-20 sm:w-24 sm:h-24 rounded-full bg-gradient-to-tr from-amber-500 to-orange-600 text-white flex items-center justify-center shadow-lg shadow-orange-500/25 hover:shadow-orange-500/40 transition-all cursor-pointer relative group"
              >
                <div className="absolute inset-0 rounded-full bg-orange-400 opacity-0 group-hover:opacity-30 group-hover:animate-ping" />
                <Mic className="w-10 h-10 stroke-[2.2]" />
              </motion.button>

              <div>
                <h3 className="text-sm font-extrabold text-[#0B1628]">Start Answer</h3>
                <p className="text-[11px] font-semibold text-slate-400">
                  Click to start recording your answer
                </p>
              </div>
            </div>

            {/* RIGHT CARD: TEXT ANSWER OPTION */}
            <div 
              onClick={() => setModeState('TEXT_MODE')}
              className="bg-slate-50/70 hover:bg-slate-100/80 border border-slate-200/70 rounded-2xl p-5 text-center space-y-2 flex flex-col items-center justify-center min-h-[140px] cursor-pointer transition-all group"
            >
              <div className="w-9 h-9 rounded-full bg-slate-200/70 text-slate-700 flex items-center justify-center group-hover:bg-[#0B1628] group-hover:text-white transition-colors">
                <Keyboard className="w-4.5 h-4.5" />
              </div>
              <h4 className="text-xs font-bold text-[#0B1628] group-hover:text-amber-600 transition-colors">
                Type your answer instead
              </h4>
              <p className="text-[11px] font-medium text-slate-500 leading-relaxed">
                Prefer typing? Write your answer here.
              </p>
            </div>

          </motion.div>
        )}

        {/* STATE 2: LISTENING VOICE RECORDING STATE */}
        {modeState === 'LISTENING' && (
          <motion.div
            key="listening"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="flex flex-col items-center justify-center text-center space-y-5 py-4"
          >
            <div className="inline-flex items-center gap-2 bg-rose-50 border border-rose-200 px-3 py-1 rounded-full text-rose-700 text-xs font-bold animate-pulse">
              <span className="w-2.5 h-2.5 rounded-full bg-rose-600" />
              <span>RECORDING VOICE ANSWER · {formatRecTime(recordingSeconds)}</span>
            </div>

            {/* PULSING RECORDING MIC */}
            <div className="relative">
              <motion.div
                animate={{ scale: [1, 1.25, 1] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                className="absolute inset-0 rounded-full bg-rose-500/20"
              />
              <button
                onClick={handleStopVoice}
                className="w-22 h-22 rounded-full bg-gradient-to-tr from-rose-600 to-red-500 text-white flex items-center justify-center shadow-xl shadow-rose-600/30 relative z-10 cursor-pointer"
              >
                <Square className="w-8 h-8 fill-current" />
              </button>
            </div>

            {/* SIMULATED AUDIO WAVE visualizer */}
            <div className="flex items-center gap-1.5 h-8">
              {[...Array(16)].map((_, i) => (
                <motion.div
                  key={i}
                  animate={{ height: [8, Math.random() * 28 + 8, 8] }}
                  transition={{ duration: 0.5, repeat: Infinity, delay: i * 0.05 }}
                  className="w-1 bg-amber-500 rounded-full"
                />
              ))}
            </div>

            <button
              onClick={handleStopVoice}
              className="bg-[#0B1628] hover:bg-[#152744] text-white px-6 py-2.5 rounded-full text-xs font-bold shadow-md cursor-pointer"
            >
              Stop & Submit Answer →
            </button>
          </motion.div>
        )}

        {/* STATE 3: TEXT ANSWER MODE */}
        {modeState === 'TEXT_MODE' && (
          <motion.div
            key="text_mode"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="space-y-4"
          >
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold text-[#0B1628]">Type your UPSC Answer</h4>
              <button 
                onClick={() => setModeState('IDLE')}
                className="text-xs font-semibold text-slate-500 hover:text-[#0B1628]"
              >
                Switch to Voice Mode
              </button>
            </div>

            <textarea
              rows={4}
              value={typedAnswer}
              onChange={(e) => setTypedAnswer(e.target.value)}
              placeholder="Structure your response with clear governance arguments, policy references, and balanced reasoning..."
              className="w-full bg-slate-50 border border-slate-200 rounded-xl p-4 text-xs font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all resize-none"
            />

            <div className="flex items-center justify-between">
              <span className="text-[11px] font-medium text-slate-400">
                {typedAnswer.length} characters typed
              </span>

              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => setModeState('IDLE')}
                  className="px-4 py-2 rounded-full text-xs font-bold text-slate-600 hover:text-slate-900 border border-slate-200"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleSubmitText}
                  disabled={!typedAnswer.trim()}
                  className="bg-[#0B1628] hover:bg-[#152744] text-white px-5 py-2 rounded-full text-xs font-bold flex items-center gap-1.5 shadow-md disabled:opacity-50 cursor-pointer"
                >
                  <span>Submit Answer</span>
                  <Send className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </motion.div>
        )}

        {/* STATE 4: PROCESSING STATE */}
        {modeState === 'PROCESSING' && (
          <motion.div
            key="processing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex flex-col items-center justify-center text-center space-y-4 py-8"
          >
            <div className="w-12 h-12 rounded-full border-4 border-amber-500/20 border-t-amber-600 animate-spin" />
            <div>
              <h4 className="text-sm font-bold text-[#0B1628]">Analyzing Your Answer...</h4>
              <p className="text-xs text-slate-500 font-medium mt-1">Evaluating depth, clarity, and administrative reasoning.</p>
            </div>
          </motion.div>
        )}

        {/* STATE 5: FEEDBACK STATE */}
        {modeState === 'FEEDBACK' && (
          <motion.div
            key="feedback"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-4"
          >
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <span className={`px-3 py-1 rounded-full text-xs font-extrabold border ${mockFeedback.badgeColor}`}>
                  {mockFeedback.badge} · {mockFeedback.score}
                </span>
                <span className="text-xs font-bold text-slate-500">AI Evaluation Feedback</span>
              </div>
            </div>

            <p className="text-xs font-semibold text-slate-700 leading-relaxed bg-slate-50 p-3.5 rounded-xl border border-slate-200/60">
              {mockFeedback.summary}
            </p>

            <div className="pt-2 flex items-center justify-end gap-3">
              <button
                onClick={() => setModeState('IDLE')}
                className="px-4 py-2 rounded-full text-xs font-bold text-slate-600 hover:text-slate-900 border border-slate-200 flex items-center gap-1.5"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Retry Question</span>
              </button>

              <button
                onClick={handleContinueNext}
                className="bg-[#0B1628] hover:bg-[#152744] text-white px-6 py-2 rounded-full text-xs font-bold inline-flex items-center gap-2 shadow-md cursor-pointer"
              >
                <span>Continue →</span>
              </button>
            </div>
          </motion.div>
        )}

      </AnimatePresence>

    </div>
  );
}
