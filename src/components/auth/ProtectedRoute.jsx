import React, { useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import { Loader2 } from 'lucide-react';

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading, openAuthModal } = useAuth();

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      openAuthModal('login');
    }
  }, [loading, isAuthenticated, openAuthModal]);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#FBF9F5] flex flex-col items-center justify-center gap-3">
        <Loader2 className="w-8 h-8 animate-spin text-[#0B1628]" />
        <p className="text-xs font-bold text-slate-600">Verifying Aspirant Session...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-[#FBF9F5] flex flex-col items-center justify-center p-6 text-center">
        <div className="w-16 h-16 rounded-2xl bg-[#0B1628] text-amber-400 flex items-center justify-center font-bold text-2xl shadow-lg mb-4">
          🏛️
        </div>
        <h2 className="text-xl font-extrabold text-[#0B1628]">Authentication Required</h2>
        <p className="text-xs text-slate-600 max-w-sm mt-1 mb-5">
          Please sign in to your Prashasak AI account to access protected UPSC prep modules.
        </p>
        <button
          onClick={() => openAuthModal('login')}
          className="bg-[#0B1628] hover:bg-[#152744] text-white px-6 py-2.5 rounded-full text-xs font-bold shadow-md transition-all cursor-pointer"
        >
          Sign In / Register
        </button>
      </div>
    );
  }

  return children;
}
