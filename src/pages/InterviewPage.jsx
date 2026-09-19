import React, { useState } from 'react';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import InterviewControlHeader from '../components/interview/InterviewControlHeader';
import InterviewerCard from '../components/interview/InterviewerCard';
import QuestionHeaderCard from '../components/interview/QuestionHeaderCard';
import QuestionMetadataCard from '../components/interview/QuestionMetadataCard';
import InterviewProgressCard from '../components/interview/InterviewProgressCard';
import AnswerArea from '../components/interview/AnswerArea';
import InterviewTipsCard from '../components/interview/InterviewTipsCard';
import { currentQuestionData } from '../data/interviewData';

export default function InterviewPage() {
  const [currentQuestion, setCurrentQuestion] = useState(currentQuestionData);
  const [interviewState, setInterviewState] = useState('IDLE');

  const handleNextQuestion = () => {
    // Advance question flow
    setCurrentQuestion(prev => ({
      ...prev,
      id: prev.id + 1,
      type: "FOLLOW-UP QUESTION",
      question: "You mentioned data privacy. How would you as a District Collector balance AI deployment with citizen privacy rights?",
      promptText: "Consider constitutional rights under Article 21 and operational efficiency.",
      typeLabel: "Follow-up Question"
    }));
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        
        {/* TOP CONTROL HEADER */}
        <InterviewControlHeader />

        {/* MAIN 2-COLUMN LAYOUT */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          
          {/* LEFT MAIN AREA (8 cols on desktop) */}
          <div className="lg:col-span-8 space-y-6">
            
            {/* AI INTERVIEWER VIEWPORT CARD */}
            <InterviewerCard 
              isSpeaking={false} 
              isProcessing={interviewState === 'PROCESSING'} 
            />

            {/* MAIN QUESTION PRESENTATION */}
            <QuestionHeaderCard 
              questionData={currentQuestion} 
            />

            {/* ANSWER CONTROLS & STATE MACHINE */}
            <AnswerArea 
              onStateChange={(state) => setInterviewState(state)}
              onNextQuestion={handleNextQuestion}
            />

          </div>

          {/* RIGHT SIDE PANEL (4 cols on desktop) */}
          <div className="lg:col-span-4 space-y-6">
            
            {/* CURRENT TOPIC METADATA */}
            <QuestionMetadataCard 
              metadata={currentQuestion} 
            />

            {/* INTERVIEW PROGRESS FLOW */}
            <InterviewProgressCard />

            {/* TIPS FOR BETTER ANSWER */}
            <InterviewTipsCard />

          </div>

        </div>

      </div>
    </DashboardLayout>
  );
}
