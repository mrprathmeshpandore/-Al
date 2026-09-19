import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, LogOut, Trash2 } from 'lucide-react';

export default function DangerZoneCard({ onTriggerLogout, onTriggerDeleteAccount }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.35 }}
      className="bg-rose-50/60 rounded-2xl p-6 border border-rose-200/80 shadow-2xs space-y-4"
    >
      <div className="flex items-center gap-2">
        <div className="p-1.5 rounded-lg bg-rose-100 text-rose-700">
          <AlertTriangle className="w-4 h-4" />
        </div>
        <div>
          <h3 className="font-serif font-bold text-rose-900 text-base">Danger Zone</h3>
          <p className="text-xs text-rose-600 font-sans">
            These actions are permanent and cannot be undone.
          </p>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-4 pt-1">
        {/* Log Out Button Box */}
        <div className="flex-1 flex items-center justify-between p-3.5 rounded-xl bg-white border border-rose-200 shadow-2xs">
          <div className="flex items-center gap-3">
            <button
              onClick={onTriggerLogout}
              className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-rose-100 hover:bg-rose-200 text-rose-700 text-xs font-bold transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Log Out</span>
            </button>
            <span className="text-xs text-slate-500 font-sans hidden sm:inline">
              Sign out from your account
            </span>
          </div>
        </div>

        {/* Delete Account Button Box */}
        <div className="flex-1 flex items-center justify-between p-3.5 rounded-xl bg-white border border-rose-200 shadow-2xs">
          <div className="flex items-center gap-3">
            <button
              onClick={onTriggerDeleteAccount}
              className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold shadow-2xs transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              <span>Delete Account</span>
            </button>
            <span className="text-xs text-slate-500 font-sans hidden sm:inline">
              Permanently delete your account and all data
            </span>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
