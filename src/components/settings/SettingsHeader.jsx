import React from 'react';
import { Search, Bell } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function SettingsHeader({ searchQuery, setSearchQuery }) {
  const { user } = useAuth();
  const userName = user?.full_name || 'UPSC Candidate';
  const userInitials = userName.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || 'UA';

  return (
    <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 pb-2 border-b border-slate-200/60">
      <div>
        <span className="text-[11px] font-bold tracking-widest uppercase text-amber-700 font-sans block mb-1">
          SETTINGS
        </span>
        <h1 className="font-serif text-2xl lg:text-3xl font-extrabold text-[#0B1628] tracking-tight">
          Settings
        </h1>
        <p className="text-xs lg:text-sm text-slate-600 font-sans mt-1 leading-relaxed">
          Manage your account and tailor your Prashasak AI experience.
        </p>
        <p className="text-xs text-amber-800 font-sans font-medium italic mt-0.5">
          A more focused you, for a stronger India.
        </p>
      </div>

      <div className="flex items-center gap-3 w-full lg:w-auto justify-between lg:justify-end">
        {/* Search Bar */}
        <div className="relative flex-1 lg:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search settings, account, or preferences..."
            className="w-full pl-9 pr-12 py-2 text-xs bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500/50 shadow-2xs font-sans transition-all"
          />
          <kbd className="hidden sm:inline-block absolute right-3 top-1/2 -translate-y-1/2 px-1.5 py-0.5 text-[10px] font-mono text-slate-400 bg-slate-100 rounded border border-slate-200">
            Ctrl K
          </kbd>
        </div>

        {/* Notifications & Profile */}
        <div className="flex items-center gap-2">
          <button className="p-2 rounded-xl bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors relative shadow-2xs">
            <Bell className="w-4 h-4" />
            <span className="w-2 h-2 rounded-full bg-amber-500 absolute top-1.5 right-1.5 ring-2 ring-white" />
          </button>

          <div
            title={userName}
            className="w-9 h-9 rounded-full bg-[#0B1628] text-amber-400 border border-amber-500/40 font-serif font-bold text-xs flex items-center justify-center ring-2 ring-amber-500/20 shadow-2xs cursor-pointer"
          >
            {userInitials}
          </div>
        </div>
      </div>
    </div>
  );
}
