import React, { useState, useEffect } from 'react';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import InterviewControlHeader from '../components/interview/InterviewControlHeader';
import InterviewerCard from '../components/interview/InterviewerCard';
import QuestionHeaderCard from '../components/interview/QuestionHeaderCard';
import QuestionMetadataCard from '../components/interview/QuestionMetadataCard';
import InterviewProgressCard from '../components/interview/InterviewProgressCard';
import AnswerArea from '../components/interview/AnswerArea';
import InterviewTipsCard from '../components/interview/InterviewTipsCard';
import InterviewReportModal from '../components/interview/InterviewReportModal';
import { 
  startInterview, 
  getInterviewSession,
  getNextInterviewQuestion, 
  submitInterviewAnswer, 
  evaluateInterviewAnswer,
  completeInterview,
  skipInterviewQuestion,
  getInterviewSessionReport
} from '../services/interviewApi';


export default function InterviewPage() {
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [interviewState, setInterviewState] = useState('LOADING'); // 'LOADING', 'IDLE', 'PROCESSING'
  const [sessionId, setSessionId] = useState(null);
  const [sessionQuestions, setSessionQuestions] = useState([]);
  const [totalQuestions, setTotalQuestions] = useState(5);
  const [currentIndex, setCurrentIndex] = useState(1);
  const [sessionError, setSessionError] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState(() => localStorage.getItem('prashasak_interview_language') || 'en-IN');

  // Report Modal State
  const [reportData, setReportData] = useState(null);
  const [isReportOpen, setIsReportOpen] = useState(false);
  const [feedbackMode, setFeedbackMode] = useState('REAL_BOARD'); // 'REAL_BOARD' | 'INSTANT_PRACTICE'

  useEffect(() => {
    async function initSession() {
      try {
        let session;
        const savedSessionId = localStorage.getItem('prashasak_current_interview_session');
        const lang = localStorage.getItem('prashasak_interview_language') || 'en-IN';
        
        if (savedSessionId) {
          try {
            session = await getInterviewSession(savedSessionId);
            if (session.status === 'COMPLETED' || session.status === 'ABANDONED') {
              session = await startInterview({ interview_type: 'FULL_INTERVIEW', total_questions: 5, language: lang });
              localStorage.setItem('prashasak_current_interview_session', session.session_id);
            }
          } catch (e) {
            session = await startInterview({ interview_type: 'FULL_INTERVIEW', total_questions: 5, language: lang });
            localStorage.setItem('prashasak_current_interview_session', session.session_id);
          }
        } else {
          session = await startInterview({
            interview_type: 'FULL_INTERVIEW',
            total_questions: 5,
            language: lang,
          });
          localStorage.setItem('prashasak_current_interview_session', session.session_id);
        }
        
        console.log("INTERVIEW API RESPONSE:", session);

        setSessionId(session.session_id);
        if (session.language) {
          setSelectedLanguage(session.language);
        }
        if (session.total_questions) {
          setTotalQuestions(session.total_questions);
        }
        if (session.current_question_index) {
          setCurrentIndex(session.current_question_index);
        }
        if (session.questions) {
          setSessionQuestions(session.questions);
        }
        
        if (session.current_question) {
          setCurrentQuestion({
            ...session.current_question,
            question: session.current_question.text,
            promptText: session.current_question.explanation || session.current_question.why_this_matters || "Take your time to think and answer.",
            typeLabel: session.current_question.type
          });
        }
        
        setInterviewState('IDLE');
      } catch (err) {
        console.error("Failed to start/load interview session", err);
        const errMsg = typeof err === 'string' ? err : (err?.message || "Failed to start interview session.");
        setSessionError(typeof errMsg === 'string' ? errMsg : String(errMsg));
        setInterviewState('IDLE');
      }
    }
    initSession();
  }, []);

  const finishInterviewSession = async (activeSessionId) => {
    const targetSessionId = activeSessionId || sessionId;
    if (!targetSessionId) return;
    setInterviewState('LOADING');
    setIsReportOpen(true);
    try {
      await completeInterview(targetSessionId);
      const report = await getInterviewSessionReport(targetSessionId);
      setReportData(report);
    } catch (err) {
      console.error("Failed to generate report", err);
    } finally {
      setInterviewState('IDLE');
    }
  };

  const handleNextQuestion = async () => {
    if (!sessionId) return;
    
    // If we reached or exceeded total questions limit, finish session and show report!
    if (currentIndex >= totalQuestions) {
      await finishInterviewSession(sessionId);
      return;
    }

    setInterviewState('LOADING');
    try {
      let nextQRes;
      try {
        nextQRes = await getNextInterviewQuestion(sessionId);
      } catch (e) {
        // Fail-safe: Auto-skip current question on backend if not answered in DB
        await skipInterviewQuestion(sessionId);
        nextQRes = await getNextInterviewQuestion(sessionId);
      }

      if (nextQRes.questions) {
        setSessionQuestions(nextQRes.questions);
      }
      if (nextQRes.progress) {
        setCurrentIndex(nextQRes.progress.current);
        setTotalQuestions(nextQRes.progress.total);
      }
      setCurrentQuestion({
        ...nextQRes.question,
        question: nextQRes.question.text,
        promptText: nextQRes.question.explanation || nextQRes.question.why_this_matters || "Take your time to think and answer.",
        typeLabel: nextQRes.question.type
      });
    } catch (err) {
      console.error("Failed to fetch next question, completing session:", err);
      await finishInterviewSession(sessionId);
    } finally {
      setInterviewState('IDLE');
    }
  };

  const handleSkipQuestion = async () => {
    if (!sessionId) return;
    try {
      await skipInterviewQuestion(sessionId);
      setSessionQuestions(prev => prev.map(q => 
        q.sequence_number === currentIndex ? { ...q, question_status: 'SKIPPED' } : q
      ));

      if (currentIndex >= totalQuestions) {
        await finishInterviewSession(sessionId);
      } else {
        await handleNextQuestion();
      }
    } catch (err) {
      console.error("Failed to skip question", err);
      if (currentIndex >= totalQuestions) {
        await finishInterviewSession(sessionId);
      } else {
        await handleNextQuestion();
      }
    }
  };

  const handleSubmitAnswer = async (finalAnswerText, recordingSeconds) => {
    if (!sessionId) throw new Error("No active session");
    
    // Submit answer
    const submitRes = await submitInterviewAnswer(sessionId, {
      answer_text: finalAnswerText,
      answer_duration_seconds: recordingSeconds
    });
    
    // Update local question status to answered so progress card updates immediately
    setSessionQuestions(prev => prev.map(q => 
      q.sequence_number === currentIndex ? { ...q, question_status: 'ANSWERED' } : q
    ));
    
    // Evaluate answer
    const evalRes = await evaluateInterviewAnswer(submitRes.answer_id);
    return evalRes;
  };

  const handleStartNewSession = async (targetLang = null) => {
    setIsReportOpen(false);
    setReportData(null);
    setInterviewState('LOADING');
    setSessionError(null);
    const langToUse = (typeof targetLang === 'string' && targetLang) ? targetLang : (selectedLanguage || 'en-IN');
    try {
      const session = await startInterview({
        interview_type: 'FULL_INTERVIEW',
        total_questions: 5,
        language: langToUse,
      });
      localStorage.setItem('prashasak_current_interview_session', session.session_id);
      localStorage.setItem('prashasak_interview_language', langToUse);
      setSessionId(session.session_id);
      setSelectedLanguage(session.language || langToUse);
      setTotalQuestions(session.total_questions || 5);
      setCurrentIndex(1);
      setSessionQuestions(session.questions || []);
      if (session.current_question) {
        setCurrentQuestion({
          ...session.current_question,
          question: session.current_question.text,
          promptText: session.current_question.explanation || session.current_question.why_this_matters || "Take your time to think and answer.",
          typeLabel: session.current_question.type
        });
      }
    } catch (err) {
      console.error("Failed to start new session", err);
      const errMsg = typeof err === 'string' ? err : (err?.message || "Failed to start new interview session.");
      setSessionError(typeof errMsg === 'string' ? errMsg : String(errMsg));
    } finally {
      setInterviewState('IDLE');
    }
  };

  const handleLanguageChange = async (newLang) => {
    setSelectedLanguage(newLang);
    localStorage.setItem('prashasak_interview_language', newLang);
    await handleStartNewSession(newLang);
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        
        {/* TOP CONTROL HEADER */}
        <InterviewControlHeader 
          currentIndex={currentIndex} 
          totalQuestions={totalQuestions} 
          feedbackMode={feedbackMode}
          onToggleFeedbackMode={(mode) => setFeedbackMode(mode)}
          selectedLanguage={selectedLanguage}
          onLanguageChange={handleLanguageChange}
          onStartNewSession={handleStartNewSession}
        />

        {/* MAIN 2-COLUMN LAYOUT */}
        {sessionError ? (
          <div className="bg-red-50 text-red-600 p-6 rounded-2xl text-center border border-red-200">
            <h2 className="text-xl font-bold mb-2">Interview Session Error</h2>
            <p>{sessionError}</p>
            <button 
              onClick={() => {
                localStorage.removeItem('prashasak_current_interview_session');
                window.location.reload();
              }}
              className="mt-4 px-6 py-2 bg-red-600 text-white rounded-full font-bold hover:bg-red-700 cursor-pointer"
            >
              Start New Session
            </button>
          </div>
        ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* LEFT MAIN AREA (8 cols on desktop) */}
          <div className="lg:col-span-8 space-y-6">
            
            {/* AI INTERVIEWER VIEWPORT CARD */}
            <InterviewerCard 
              isSpeaking={false} 
              isProcessing={interviewState === 'PROCESSING' || interviewState === 'LOADING'} 
            />

            {/* MAIN QUESTION PRESENTATION */}
            {currentQuestion ? (
              <QuestionHeaderCard 
                questionData={currentQuestion} 
              />
            ) : (
              <div className="bg-slate-50 border border-slate-200 text-slate-500 p-8 rounded-2xl text-center shadow-sm">
                No active question found. If this persists, please restart the session.
              </div>
            )}

            {/* ANSWER CONTROLS & STATE MACHINE */}
            {currentQuestion && (
              <AnswerArea 
                key={currentQuestion.id || currentIndex}
                onStateChange={(state) => setInterviewState(state)}
                onNextQuestion={handleNextQuestion}
                onSubmitAnswer={handleSubmitAnswer}
                onSkipQuestion={handleSkipQuestion}
                onStartNewSession={handleStartNewSession}
                currentQuestionText={currentQuestion.question}
                sessionLanguage={selectedLanguage}
                feedbackMode={feedbackMode}
              />
            )}

          </div>

          {/* RIGHT SIDE PANEL (4 cols on desktop) */}
          <div className="lg:col-span-4 space-y-6">
            
            {/* CURRENT TOPIC METADATA */}
            {currentQuestion && (
              <QuestionMetadataCard 
                metadata={currentQuestion} 
              />
            )}

            {/* INTERVIEW PROGRESS FLOW */}
            <InterviewProgressCard 
              questions={sessionQuestions}
              totalQuestions={totalQuestions}
              currentIndex={currentIndex}
            />

            {/* TIPS FOR BETTER ANSWER */}
            <InterviewTipsCard />

          </div>

        </div>
        )}

        {/* 5-MINUTE COMPREHENSIVE PERFORMANCE SUMMARY REPORT MODAL */}
        <InterviewReportModal 
          isOpen={isReportOpen}
          onClose={() => setIsReportOpen(false)}
          reportData={reportData}
          onStartNewSession={handleStartNewSession}
        />

      </div>
    </DashboardLayout>
  );
}
