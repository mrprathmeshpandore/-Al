import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import DashboardPage from './pages/DashboardPage';
import ProfilePage from './pages/ProfilePage';
import InterviewPage from './pages/InterviewPage';
import CurrentAffairsPage from './pages/CurrentAffairsPage';
import QuestionBankPage from './pages/QuestionBankPage';
import ProgressPage from './pages/ProgressPage';
import ResourcesPage from './pages/ResourcesPage';
import ResourceSubjectPage from './pages/ResourceSubjectPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/interview" element={<InterviewPage />} />
        <Route path="/current-affairs" element={<CurrentAffairsPage />} />
        <Route path="/current-affairs/:id" element={<CurrentAffairsPage />} />
        <Route path="/question-bank" element={<QuestionBankPage />} />
        <Route path="/question-bank/:id" element={<QuestionBankPage />} />
        <Route path="/progress" element={<ProgressPage />} />
        <Route path="/resources" element={<ResourcesPage />} />
        <Route path="/resources/:subjectSlug" element={<ResourceSubjectPage />} />
        <Route path="*" element={<DashboardPage />} />
      </Routes>
    </BrowserRouter>
  );
}
