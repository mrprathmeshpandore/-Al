import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import DashboardHeader from './DashboardHeader';
import { LayoutDashboard, Mic, Newspaper, User } from 'lucide-react';

export default function DashboardLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const currentTab = new URLSearchParams(location.search).get('tab') || 'dashboard';

  return (
    <div className="min-h-screen bg-[#FAF8F5] text-[#0F172A] flex font-sans antialiased">
      
      {/* DESKTOP & MOBILE SIDEBAR */}
      <Sidebar 
        isOpen={sidebarOpen} 
        onClose={() => setSidebarOpen(false)} 
      />

      {/* MAIN CONTENT WRAPPER (Shifted right by 260px on desktop) */}
      <div className="flex-1 lg:pl-[260px] flex flex-col min-w-0 transition-all duration-300 pb-16 lg:pb-0">
        
        {/* TOP STICKY HEADER */}
        <DashboardHeader 
          onMenuClick={() => setSidebarOpen(true)} 
        />

        {/* MAIN BODY AREA */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full">
          {children}
        </main>
        
      </div>

      {/* MOBILE BOTTOM NAVIGATION BAR */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-md border-t border-slate-200 z-40 px-6 py-2 flex items-center justify-around">
        <Link 
          to="/dashboard" 
          className={`flex flex-col items-center gap-0.5 text-[10px] font-semibold ${currentTab === 'dashboard' ? 'text-[#0B1628]' : 'text-slate-400'}`}
        >
          <LayoutDashboard className="w-5 h-5" />
          <span>Home</span>
        </Link>

        <Link 
          to="/dashboard?tab=interview" 
          className={`flex flex-col items-center gap-0.5 text-[10px] font-semibold ${currentTab === 'interview' ? 'text-[#0B1628]' : 'text-slate-400'}`}
        >
          <Mic className="w-5 h-5" />
          <span>AI Interview</span>
        </Link>

        <Link 
          to="/dashboard?tab=current-affairs" 
          className={`flex flex-col items-center gap-0.5 text-[10px] font-semibold ${currentTab === 'current-affairs' ? 'text-[#0B1628]' : 'text-slate-400'}`}
        >
          <Newspaper className="w-5 h-5" />
          <span>Affairs</span>
        </Link>

        <Link 
          to="/profile" 
          className={`flex flex-col items-center gap-0.5 text-[10px] font-semibold ${location.pathname === '/profile' ? 'text-[#0B1628]' : 'text-slate-400'}`}
        >
          <User className="w-5 h-5" />
          <span>Profile</span>
        </Link>
      </div>

    </div>
  );
}
