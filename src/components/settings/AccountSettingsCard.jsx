import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { User, Mail, ShieldCheck, ArrowRight } from 'lucide-react';

export default function AccountSettingsCard({ onShowToast }) {
  const navigate = useNavigate();

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="bg-white rounded-2xl p-6 border border-amber-950/5 shadow-2xs space-y-4 flex flex-col justify-between"
    >
      <div>
        <div className="flex items-center gap-2 mb-1">
          <div className="p-1.5 rounded-lg bg-blue-50 text-blue-600">
            <User className="w-4 h-4" />
          </div>
          <h3 className="font-serif font-bold text-slate-900 text-lg">Account</h3>
        </div>
        <p className="text-xs text-slate-500 font-sans mb-4">
          Manage your profile information, email and password.
        </p>

        <div className="space-y-3">
          {/* Profile Info */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50/70 border border-slate-100 hover:bg-slate-50 transition-colors">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-white shadow-2xs text-slate-700">
                <User className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-slate-800 font-sans">Profile Information</h4>
                <p className="text-[11px] text-slate-500 font-sans">Name, profile photo, bio</p>
              </div>
            </div>
            <button
              onClick={() => navigate('/profile')}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-semibold transition-colors"
            >
              <span>Edit</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Email & Password */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50/70 border border-slate-100 hover:bg-slate-50 transition-colors">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-white shadow-2xs text-emerald-600">
                <Mail className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-slate-800 font-sans">Email & Password</h4>
                <p className="text-[11px] text-slate-500 font-sans">Manage your email and password</p>
              </div>
            </div>
            <button
              onClick={() => onShowToast && onShowToast("Redirecting to security settings...")}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-colors"
            >
              <span>Manage</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Linked Accounts */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-slate-50/70 border border-slate-100 hover:bg-slate-50 transition-colors">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-white shadow-2xs text-amber-600">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-slate-800 font-sans">Linked Accounts</h4>
                <p className="text-[11px] text-slate-500 font-sans">Connect Google account (optional)</p>
              </div>
            </div>
            <button
              onClick={() => onShowToast && onShowToast("Google connection initialized.")}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-colors"
            >
              <span>Connect</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
