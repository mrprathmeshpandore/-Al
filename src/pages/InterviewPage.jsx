import React, { useState, useEffect } from 'react';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import InterviewControlHeader from '../components/interview/InterviewControlHeader';
import InterviewerCard from '../components/interview/InterviewerCard';
import QuestionHeaderCard from '../components/interview/QuestionHeaderCard';
import QuestionMetadataCard from '../components/interview/QuestionMetadataCard';
import InterviewProgressCard from '../components/interview/InterviewProgressCard';
import AnswerArea from '../components/interview/AnswerArea';
import InterviewTipsCard from '../components/interview/InterviewTipsCard';
import { 
  startInterview, 
  getInterviewSession,
  getNextInterviewQuestion, 
  submitInterviewAnswer, 
  evaluateInterviewAnswer 
} from '../services/interviewApi';


export default function InterviewPage() {
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [interviewState, setInterviewState] = useState('LOADING'); // 'LOADING', 'IDLE', 'PROCESSING'
  const [sessionId, setSessionId] = useState(null);
  const [sessionQuestions, setSessionQuestions] = useState([]);
  const [totalQuestions, setTotalQuestions] = useState(5);
  const [currentIndex, setCurrentIndex] = useState(1);
  const [sessionError, setSessionError] = useState(null);

  useEffect(() => {
    async function initSession() {
      try {
        let session;
        const savedSessionId = localStorage.getItem('prashasak_current_interview_session');
        
        if (savedSessionId) {
          try {
            session = await getInterviewSession(savedSessionId);
            // If the session is completed, we should probably start a new one, but for now we just load it
            if (session.status === 'COMPLETED' || session.status === 'ABANDONED') {
                session = await startInterview({ interview_type: 'FULL_INTERVIEW', total_questions: 5 });
                localStorage.setItem('prashasak_current_interview_session', session.session_id);
            }
          } catch (e) {
            // Invalid or expired session ID
            session = await startInterview({ interview_type: 'FULL_INTERVIEW', total_questions: 5 });
            localStorage.setItem('prashasak_current_interview_session', session.session_id);
          }
        } else {
          session = await startInterview({
            interview_type: 'FULL_INTERVIEW',
            total_questions: 5,
          });
          localStorage.setItem('prashasak_current_interview_session', session.session_id);
        }
        
        console.log("INTERVIEW API RESPONSE:", session);

        setSessionId(session.session_id);
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
            question: session.current_question.text, // Map backend 'text' to frontend 'question'
            promptText: session.current_question.explanation || session.current_question.why_this_matters || "Take your time to think and answer.",
            typeLabel: session.current_question.type
          });
        }
        
        setInterviewState('IDLE');
      } catch (err) {
        console.error("Failed to start/load interview session", err);
        setSessionError(err.message || "Failed to start interview session.");
        setInterviewState('IDLE');
      }
    }
    initSession();
  }, []);

  const handleNextQuestion = async () => {
    if (!sessionId) return;
    setInterviewState('LOADING');
    try {
      const nextQRes = await getNextInterviewQuestion(sessionId);
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
      console.error("Failed to fetch next question", err);
      // Just keep current question on error
    } finally {
      setInterviewState('IDLE');
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

  return (
    <DashboardLayout>
      <div className="space-y-6">
        
        {/* TOP CONTROL HEADER */}
        <InterviewControlHeader />

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
              className="mt-4 px-6 py-2 bg-red-600 text-white rounded-full font-bold hover:bg-red-700"
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
                onStateChange={(state) => setInterviewState(state)}
                onNextQuestion={handleNextQuestion}
                onSubmitAnswer={handleSubmitAnswer}
                currentQuestionText={currentQuestion.question}
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

      </div>
    </DashboardLayout>
  );
}
