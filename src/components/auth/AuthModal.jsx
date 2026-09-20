import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Mail, Lock, User, ArrowRight, AlertCircle, Loader2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function AuthModal() {
  const {
    isAuthModalOpen,
    closeAuthModal,
    authModalMode,
    setAuthModalMode,
    login,
    register,
  } = useAuth();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  if (!isAuthModalOpen) return null;

  const isRegister = authModalMode === 'register';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      if (isRegister) {
        if (!fullName.trim()) {
          throw new Error('Full name is required');
        }
        if (password.length < 8) {
          throw new Error('Password must be at least 8 characters long');
        }
        await register(email, fullName, password);
      } else {
        await login(email, password);
      }
      // Reset form
      setEmail('');
      setPassword('');
      setFullName('');
    } catch (err) {
      setError(err.message || 'Authentication failed. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const toggleMode = () => {
    setError('');
    setAuthModalMode(isRegister ? 'login' : 'register');
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#0B1628]/60 backdrop-blur-md">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
          className="relative w-full max-w-md bg-white rounded-3xl shadow-2xl border border-slate-200/80 overflow-hidden"
        >
          {/* Header Banner */}
          <div className="bg-[#0B1628] text-white p-6 relative">
            <button
              onClick={closeAuthModal}
              className="absolute top-5 right-5 p-1.5 text-slate-400 hover:text-white rounded-full transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-3 mb-2">
              <div className="w-9 h-9 rounded-xl bg-white/10 text-white flex items-center justify-center font-bold text-lg">
                🏛️
              </div>
              <div>
                <span className="font-marathi text-xl font-bold">प्रशासक</span>{' '}
                <span className="text-[#E86A24] font-black">AI</span>
              </div>
            </div>

            <h3 className="text-lg font-extrabold text-white tracking-tight">
              {isRegister ? 'Create your UPSC Account' : 'Welcome back, Aspirant'}
            </h3>
            <p className="text-xs text-slate-300 mt-1">
              {isRegister
                ? 'Begin your AI-powered DAF prep & interview simulations.'
                : 'Sign in to access your DAF profile & interview prep.'}
            </p>
          </div>

          {/* Form Content */}
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {error && (
              <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-xs font-semibold flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-500" />
                <span>{error}</span>
              </div>
            )}

            {isRegister && (
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Full Name
                </label>
                <div className="relative">
                  <User className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="e.g. Rahul Sharma"
                    className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-900 focus:outline-none focus:border-[#0B1628] focus:bg-white transition-all"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="aspirant@upsc.gov.in"
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-900 focus:outline-none focus:border-[#0B1628] focus:bg-white transition-all"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder={isRegister ? 'Minimum 8 characters' : 'Enter your password'}
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-medium text-slate-900 focus:outline-none focus:border-[#0B1628] focus:bg-white transition-all"
                />
              </div>
            </div>

            <motion.button
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={submitting}
              className="w-full bg-[#0B1628] hover:bg-[#152744] text-white py-3 rounded-xl text-xs font-bold flex items-center justify-center gap-2 shadow-md transition-colors cursor-pointer mt-2"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-amber-400" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <span>{isRegister ? 'Create Account & Continue' : 'Sign In to Prashasak AI'}</span>
                  <ArrowRight className="w-4 h-4 text-amber-400" />
                </>
              )}
            </motion.button>

            {/* Toggle Mode */}
            <div className="pt-3 text-center border-t border-slate-100">
              <button
                type="button"
                onClick={toggleMode}
                className="text-xs font-semibold text-slate-600 hover:text-[#0B1628] transition-colors cursor-pointer"
              >
                {isRegister ? (
                  <span>Already have an account? <strong className="text-[#E86A24]">Sign In</strong></span>
                ) : (
                  <span>Don't have an account? <strong className="text-[#E86A24]">Create Account</strong></span>
                )}
              </button>
            </div>
          </form>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
