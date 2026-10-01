import React, { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import AuthModal from './components/auth/AuthModal';
import ProtectedRoute from './components/auth/ProtectedRoute';

// Lazy-loaded route components for optimized initial bundle loading
const LandingPage = lazy(() => import('./pages/LandingPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));
const InterviewPage = lazy(() => import('./pages/InterviewPage'));
const CurrentAffairsPage = lazy(() => import('./pages/CurrentAffairsPage'));
const QuestionBankPage = lazy(() => import('./pages/QuestionBankPage'));
const ProgressPage = lazy(() => import('./pages/ProgressPage'));
const ResourcesPage = lazy(() => import('./pages/ResourcesPage'));
const ResourceSubjectPage = lazy(() => import('./pages/ResourceSubjectPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));

function PageLoader() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-3 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
        <span className="text-xs text-slate-400 font-medium">Loading Prashasak AI...</span>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AuthModal />
        <Suspense fallback={<PageLoader />}>
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

            <Route path="*" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          </Routes>
        </Suspense>
      </AuthProvider>
    </BrowserRouter>
  );
}
