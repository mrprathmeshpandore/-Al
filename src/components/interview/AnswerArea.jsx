import React, { useState, useEffect, useRef } from 'react';
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
  Volume2,
  AlertCircle,
  Edit3,
  RefreshCw
} from 'lucide-react';
import { voiceApi } from '../../services/voiceApi';

export default function AnswerArea({ 
  onStateChange, 
  onNextQuestion, 
  onSubmitAnswer, 
  onSkipQuestion, 
  onStartNewSession,
  currentQuestionText,
  sessionLanguage = 'en-IN',
  feedbackMode = 'REAL_BOARD'
}) {

  // ...

  const handleSkip = async () => {
    if (isNavigating) return;
    setIsNavigating(true);
    try {
      if (onSkipQuestion) await onSkipQuestion();
    } finally {
      setIsNavigating(false);
      setModeState('IDLE');
      setTypedAnswer('');
      setTranscript('');
      setRecordingSeconds(0);
      setEvaluation(null);
    }
  };
  // STATES: 'IDLE' | 'LISTENING' | 'TRANSCRIBING' | 'TRANSCRIBED' | 'TEXT_MODE' | 'PROCESSING' | 'FEEDBACK' | 'MIC_DENIED' | 'STT_ERROR'
  const [modeState, setModeState] = useState('IDLE');
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [typedAnswer, setTypedAnswer] = useState('');
  const [transcript, setTranscript] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isSynthesizing, setIsSynthesizing] = useState(false);
  const [ttsAudioUrl, setTtsAudioUrl] = useState(null);
  const [evaluation, setEvaluation] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Reset TTS audio URL when question changes so we don't play old audio
  useEffect(() => {
    setTtsAudioUrl(null);
  }, [currentQuestionText]);

  // TIMER FOR RECORDING DURATION
  useEffect(() => {
    let interval = null;
    if (modeState === 'LISTENING') {
      interval = setInterval(() => {
        setRecordingSeconds(prev => prev + 1);
      }, 1000);
    } else if (modeState !== 'TRANSCRIBING' && modeState !== 'TRANSCRIBED') {
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

  // TTS PLAYBACK HANDLER FOR QUESTION
  const handlePlayTTS = async () => {
    if (!currentQuestionText) return;
    setIsSynthesizing(true);
    try {
      if (ttsAudioUrl) {
        const audio = new Audio(ttsAudioUrl);
        audio.play();
        setIsSynthesizing(false);
        return;
      }
      const audioUrl = await voiceApi.synthesizeSpeech(currentQuestionText, sessionLanguage);
      setTtsAudioUrl(audioUrl);
      const audio = new Audio(audioUrl);
      audio.play();
    } catch (err) {
      // Browser SpeechSynthesis Fallback
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(currentQuestionText);
        utterance.lang = sessionLanguage || 'en-IN';
        utterance.rate = 0.95;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
      }
    } finally {
      setIsSynthesizing(false);
    }
  };

  const handleStartVoice = async () => {
    setErrorMessage('');
    audioChunksRef.current = [];
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setErrorMessage('Microphone access is not supported in your browser. You can type your answer instead.');
      setModeState('MIC_DENIED');
      return;
    }

    try {
      let options = {};
      if (typeof MediaRecorder !== 'undefined') {
        if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
          options = { mimeType: 'audio/webm;codecs=opus' };
        } else if (MediaRecorder.isTypeSupported('audio/webm')) {
          options = { mimeType: 'audio/webm' };
        } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
          options = { mimeType: 'audio/mp4' };
        } else if (MediaRecorder.isTypeSupported('audio/ogg')) {
          options = { mimeType: 'audio/ogg' };
        }
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      });
      const mediaRecorder = new MediaRecorder(stream, options);
      mediaRecorderRef.current = mediaRecorder;

      const actualMimeType = mediaRecorder.mimeType || options.mimeType || 'audio/webm';

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: actualMimeType });
        // Clean up tracks
        stream.getTracks().forEach(track => track.stop());
        await processAudioTranscription(audioBlob);
      };

      mediaRecorder.start();
      setModeState('LISTENING');
    } catch (err) {
      console.error("Mic error:", err);
      let errorMsg = 'Microphone access was denied.';
      if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        errorMsg = 'No microphone found. Please connect a microphone.';
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        errorMsg = 'Your microphone is being used by another application or is not readable.';
      } else {
        errorMsg = err.message || 'Microphone access was denied.';
      }
      setErrorMessage(`${errorMsg} You can type your answer instead.`);
      setModeState('MIC_DENIED');
    }
  };

  const handleStopVoice = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setModeState('TRANSCRIBING');
    } else {
      setModeState('IDLE');
    }
  };

  const processAudioTranscription = async (audioBlob) => {
    setModeState('TRANSCRIBING');
    try {
      const result = await voiceApi.transcribeAudio(audioBlob, sessionLanguage);
      const textResult = (result.text || '').trim();
      if (!textResult) {
        setErrorMessage('माईकमधून कोणताही स्पष्ट आवाज ऐकू आला नाही. कृपया माईक जवळ घेऊन स्पष्ट बोला किंवा उत्तर टाइप करा. (No clear speech detected. Please speak louder or type your answer.)');
        setModeState('STT_ERROR');
        return;
      }
      setTranscript(textResult);
      setTypedAnswer(textResult);
      setModeState('TRANSCRIBED');
    } catch (err) {
      setErrorMessage(err.message || 'Voice transcription failed. You can try recording again or type your answer.');
      setModeState('STT_ERROR');
    }
  };

  const handleSubmitFinalAnswer = async () => {
    const finalAnswerText = typedAnswer.trim() || transcript.trim();
    if (!finalAnswerText) return;

    setErrorMessage('');
    setModeState('PROCESSING');
    try {
      if (onSubmitAnswer) {
        const evalResult = await onSubmitAnswer(finalAnswerText, recordingSeconds || 30);
        setEvaluation(evalResult);
      }

      if (feedbackMode === 'REAL_BOARD') {
        if (onNextQuestion) await onNextQuestion();
        setModeState('IDLE');
        setTypedAnswer('');
        setTranscript('');
        setRecordingSeconds(0);
        setEvaluation(null);
      } else {
        setModeState('FEEDBACK');
      }
    } catch (err) {
      console.error("Answer submission/evaluation error:", err);
      setErrorMessage(typeof err === 'object' ? (err.detail || err.message || JSON.stringify(err)) : String(err));
      setModeState('TEXT_MODE');
    }
  };

  const [isNavigating, setIsNavigating] = useState(false);

  const handleContinueNext = async () => {
    if (isNavigating) return;
    setIsNavigating(true);
    try {
      if (onNextQuestion) await onNextQuestion();
    } catch (err) {
      console.error("Error advancing to next question:", err);
    } finally {
      setIsNavigating(false);
      setModeState('IDLE');
      setTypedAnswer('');
      setTranscript('');
      setRecordingSeconds(0);
      setEvaluation(null);
    }
  };

  const formatRecTime = (sec) => {
    const mins = Math.floor(sec / 60);
    const secs = sec % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="w-full bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-2xs space-y-6">
      
      {/* OPTIONAL TTS BUTTON BANNER */}
      {currentQuestionText && (
        <div className="flex items-center justify-between bg-slate-50 border border-slate-200/80 px-4 py-2.5 rounded-xl">
          <div className="flex items-center gap-2">
            <Volume2 className="w-4 h-4 text-amber-600" />
            <span className="text-xs font-semibold text-slate-700">Listen to AI Question Voice</span>
          </div>
          <button
            onClick={handlePlayTTS}
            disabled={isSynthesizing}
            className="text-xs font-bold text-amber-600 hover:text-amber-700 bg-amber-50 hover:bg-amber-100 border border-amber-200 px-3 py-1 rounded-full flex items-center gap-1 cursor-pointer transition-colors"
          >
            {isSynthesizing ? 'Synthesizing...' : 'Play Question Audio 🔊'}
          </button>
        </div>
      )}

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
              Stop & Transcribe Answer →
            </button>
          </motion.div>
        )}

        {/* STATE: TRANSCRIBING */}
        {modeState === 'TRANSCRIBING' && (
          <motion.div
            key="transcribing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex flex-col items-center justify-center text-center space-y-4 py-8"
          >
            <div className="w-12 h-12 rounded-full border-4 border-amber-500/20 border-t-amber-600 animate-spin" />
            <div>
              <h4 className="text-sm font-bold text-[#0B1628]">Transcribing Speech to Text...</h4>
              <p className="text-xs text-slate-500 font-medium mt-1">Processing recorded audio with AI speech model.</p>
            </div>
          </motion.div>
        )}

        {/* STATE: TRANSCRIBED PREVIEW & EDITING */}
        {modeState === 'TRANSCRIBED' && (
          <motion.div
            key="transcribed"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="space-y-4"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Edit3 className="w-4 h-4 text-amber-600" />
                <h4 className="text-xs font-bold text-[#0B1628]">Review & Edit Voice Transcript</h4>
              </div>
              <span className="text-[11px] font-semibold text-slate-400">
                Duration: {formatRecTime(recordingSeconds)}
              </span>
            </div>

            {errorMessage && (
              <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl flex items-center gap-2 font-medium">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}

            <textarea
              rows={4}
              value={typedAnswer}
              onChange={(e) => setTypedAnswer(e.target.value)}
              placeholder="Edit your transcribed speech before final submission..."
              className="w-full bg-slate-50 border border-slate-200 rounded-xl p-4 text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all resize-none"
            />

            <div className="flex items-center justify-between pt-1">
              <button
                type="button"
                onClick={handleStartVoice}
                className="px-4 py-2 rounded-full text-xs font-bold text-slate-600 hover:text-slate-900 border border-slate-200 flex items-center gap-1.5 cursor-pointer"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Re-record</span>
              </button>

              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => setModeState('TEXT_MODE')}
                  className="px-4 py-2 rounded-full text-xs font-bold text-slate-600 hover:text-slate-900 border border-slate-200"
                >
                  Switch to Type
                </button>
                <button
                  type="button"
                  onClick={handleSubmitFinalAnswer}
                  disabled={!(typedAnswer.trim() || transcript.trim()) || modeState === 'PROCESSING'}
                  className="bg-[#0B1628] hover:bg-[#152744] text-white px-6 py-2 rounded-full text-xs font-bold flex items-center gap-1.5 shadow-md disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                >
                  <span>Submit Answer</span>
                  <Send className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
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

            {errorMessage && (
              <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl flex items-center justify-between gap-2 font-medium">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
                  <span>{typeof errorMessage === 'object' ? (errorMessage.detail || errorMessage.message || JSON.stringify(errorMessage)) : String(errorMessage)}</span>
                </div>
                {(String(errorMessage).includes('COMPLETED') || String(errorMessage).includes('completed')) && onStartNewSession && (
                  <button
                    type="button"
                    onClick={async () => {
                      setErrorMessage('');
                      await onStartNewSession();
                    }}
                    className="px-3 py-1 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-xs font-bold shrink-0 cursor-pointer shadow-2xs transition-colors flex items-center gap-1.5"
                  >
                    <RefreshCw className="w-3 h-3" />
                    <span>Start New Session</span>
                  </button>
                )}
              </div>
            )}

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
                  onClick={handleSkip}
                  className="px-4 py-2 rounded-full text-xs font-bold text-amber-700 bg-amber-50 hover:bg-amber-100 border border-amber-200 cursor-pointer"
                >
                  <span>Skip Question ⏭️</span>
                </button>
                <button
                  type="button"
                  onClick={() => setModeState('IDLE')}
                  className="px-4 py-2 rounded-full text-xs font-bold text-slate-600 hover:text-slate-900 border border-slate-200"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleSubmitFinalAnswer}
                  disabled={!(typedAnswer.trim() || transcript.trim()) || modeState === 'PROCESSING'}
                  className="bg-[#0B1628] hover:bg-[#152744] text-white px-5 py-2 rounded-full text-xs font-bold flex items-center gap-1.5 shadow-md disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
                >
                  <span>Submit Answer</span>
                  <Send className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </motion.div>
        )}

        {/* STATE: MIC_DENIED OR STT_ERROR */}
        {(modeState === 'MIC_DENIED' || modeState === 'STT_ERROR') && (
          <motion.div
            key="error_state"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="p-5 bg-rose-50 border border-rose-200 rounded-2xl text-center space-y-4"
          >
            <div className="w-10 h-10 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center mx-auto">
              <AlertCircle className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-rose-900">
                {modeState === 'MIC_DENIED' ? 'Microphone Access Denied' : 'Voice Transcription Failed'}
              </h4>
              <p className="text-xs text-rose-700 font-medium mt-1">
                {errorMessage || 'Voice input is currently unavailable.'}
              </p>
            </div>
            <div className="flex items-center justify-center gap-3">
              <button
                onClick={handleStartVoice}
                className="px-4 py-2 rounded-full text-xs font-bold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 cursor-pointer"
              >
                Try Again
              </button>
              <button
                onClick={() => setModeState('TEXT_MODE')}
                className="bg-[#0B1628] hover:bg-[#152744] text-white px-5 py-2 rounded-full text-xs font-bold cursor-pointer"
              >
                Type Answer Instead
              </button>
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
        {modeState === 'FEEDBACK' && evaluation && (
          <motion.div
            key="feedback"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-4"
          >
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2">
                <span className={`px-3 py-1 rounded-full text-xs font-extrabold border ${
                  evaluation.overall_score >= 8 ? 'bg-emerald-100 text-emerald-800 border-emerald-300' :
                  evaluation.overall_score >= 6 ? 'bg-amber-100 text-amber-800 border-amber-300' :
                  'bg-rose-100 text-rose-800 border-rose-300'
                }`}>
                  {evaluation.overall_score >= 8 ? 'Excellent' : evaluation.overall_score >= 6 ? 'Good Start' : 'Needs Work'} · {Math.round(evaluation.overall_score * 10)}%
                </span>
                <span className="text-xs font-bold text-slate-500">AI Evaluation Feedback</span>
              </div>
            </div>

            <p className="text-xs font-semibold text-slate-700 leading-relaxed bg-slate-50 p-3.5 rounded-xl border border-slate-200/60">
              {evaluation.overall_feedback}
            </p>

            <div className="pt-2 flex items-center justify-end gap-3">
              <button
                onClick={() => {
                  setErrorMessage('');
                  setEvaluation(null);
                  setModeState('TEXT_MODE');
                }}
                className="px-4 py-2 rounded-full text-xs font-bold text-slate-600 hover:text-slate-900 border border-slate-200 flex items-center gap-1.5 cursor-pointer"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Retry Question</span>
              </button>

              <button
                type="button"
                onClick={handleContinueNext}
                disabled={isNavigating}
                className="bg-[#0B1628] hover:bg-[#152744] text-white px-6 py-2 rounded-full text-xs font-bold inline-flex items-center gap-2 shadow-md cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isNavigating ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Next Question...</span>
                  </>
                ) : (
                  <span>Continue →</span>
                )}
              </button>
            </div>
          </motion.div>
        )}

      </AnimatePresence>

    </div>
  );
}
