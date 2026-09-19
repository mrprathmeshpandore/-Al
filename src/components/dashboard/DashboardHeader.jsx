import React from 'react';
import { Search, Bell, Menu } from 'lucide-react';
import { userProfile } from '../../data/dashboardData';

export default function DashboardHeader({ onMenuClick }) {
  return (
    <header className="w-full bg-[#FAF8F5]/80 backdrop-blur-md border-b border-slate-200/60 sticky top-0 z-30 px-4 sm:px-8 py-4 transition-all">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        
        {/* LEFT GREETING */}
        <div className="flex items-center gap-3">
          <button 
            onClick={onMenuClick}
            className="lg:hidden p-2 text-slate-600 hover:text-slate-900 rounded-lg hover:bg-slate-200/60"
            aria-label="Toggle Navigation Menu"
          >
            <Menu className="w-5 h-5" />
          </button>
          
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-[#0B1628] tracking-tight flex items-center gap-2">
              <span>{userProfile.greetingTime}, {userProfile.name}</span>
              <span className="inline-block animate-bounce text-lg sm:text-xl">👋</span>
            </h1>
            <p className="text-xs sm:text-sm font-medium text-slate-500 mt-0.5">
              {userProfile.subtitle}
            </p>
          </div>
        </div>

        {/* RIGHT CONTROLS */}
        <div className="flex items-center gap-3 sm:gap-4">
          
          {/* SEARCH BAR WITH SHORTCUT */}
          <div className="relative hidden md:flex items-center">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 pointer-events-none" />
            <input 
              type="text" 
              placeholder="Search anything..." 
              className="w-56 lg:w-64 bg-white border border-slate-200/80 rounded-full pl-9 pr-14 py-2 text-xs font-medium text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:border-[#0B1628] transition-all shadow-2xs"
            />
            <kbd className="absolute right-3 top-1/2 -translate-y-1/2 bg-slate-100 border border-slate-200 text-[10px] font-semibold text-slate-500 px-1.5 py-0.5 rounded shadow-2xs">
              Ctrl K
            </kbd>
          </div>

          {/* NOTIFICATIONS ICON */}
          <button 
            className="relative p-2.5 rounded-full bg-white border border-slate-200/80 text-slate-600 hover:text-[#0B1628] hover:bg-slate-50 transition-all shadow-2xs"
            aria-label="Notifications"
          >
            <Bell className="w-4.5 h-4.5" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-rose-500 ring-2 ring-white" />
          </button>

          {/* PROFILE AVATAR */}
          <div className="flex items-center gap-2">
            <img 
              src={userProfile.avatar} 
              alt={userProfile.name} 
              className="w-9 h-9 sm:w-10 sm:h-10 rounded-full object-cover border-2 border-white shadow-xs ring-2 ring-amber-500/20"
            />
          </div>

        </div>

      </div>
    </header>
  );
}
