import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import AuthModal from './components/auth/AuthModal';
import ProtectedRoute from './components/auth/ProtectedRoute';

import LandingPage from './pages/LandingPage';
import DashboardPage from './pages/DashboardPage';
import ProfilePage from './pages/ProfilePage';
import InterviewPage from './pages/InterviewPage';
import CurrentAffairsPage from './pages/CurrentAffairsPage';
import QuestionBankPage from './pages/QuestionBankPage';
import ProgressPage from './pages/ProgressPage';
import ResourcesPage from './pages/ResourcesPage';
import ResourceSubjectPage from './pages/ResourceSubjectPage';
import SettingsPage from './pages/SettingsPage';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AuthModal />
        <Routes>
          <Route path="/" element={<LandingPage />} />
          
          {/* Protected Application Routes */}
          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
          <Route path="/interview" element={<ProtectedRoute><InterviewPage /></ProtectedRoute>} />
          <Route path="/current-affairs" element={<ProtectedRoute><CurrentAffairsPage /></ProtectedRoute>} />
          <Route path="/current-affairs/:id" element={<ProtectedRoute><CurrentAffairsPage /></ProtectedRoute>} />
          <Route path="/question-bank" element={<ProtectedRoute><QuestionBankPage /></ProtectedRoute>} />
          <Route path="/question-bank/:id" element={<ProtectedRoute><QuestionBankPage /></ProtectedRoute>} />
          <Route path="/progress" element={<ProtectedRoute><ProgressPage /></ProtectedRoute>} />
          <Route path="/resources" element={<ProtectedRoute><ResourcesPage /></ProtectedRoute>} />
          <Route path="/resources/:subjectSlug" element={<ProtectedRoute><ResourceSubjectPage /></ProtectedRoute>} />
          <Route path="/settings" element={<ProtectedRoute><SettingsPage /></ProtectedRoute>} />

          <Route path="*" element={<DashboardPage />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
