import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  LayoutDashboard, 
  Mic, 
  BookOpen, 
  Newspaper, 
  Folder, 
  BarChart3, 
  Settings, 
  ChevronRight,
  LogOut,
  X
} from 'lucide-react';
import { sidebarNavigation, sidebarSecondaryNav, userProfile } from '../../data/dashboardData';

const iconMap = {
  layoutDashboard: LayoutDashboard,
  mic: Mic,
  bookOpen: BookOpen,
  newspaper: Newspaper,
  folder: Folder,
  barChart3: BarChart3,
  settings: Settings,
};

export default function Sidebar({ isOpen, onClose }) {
  const location = useLocation();
  const currentTab = new URLSearchParams(location.search).get('tab') || 'dashboard';

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {isOpen && (
        <div 
          onClick={onClose}
          className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-40 lg:hidden transition-opacity"
        />
      )}

      {/* Sidebar Container */}
      <aside className={`
        fixed top-0 left-0 bottom-0 z-50
        w-[260px] bg-[#FAF8F5] border-r border-slate-200/80
        flex flex-col justify-between p-4 transition-transform duration-300 ease-in-out
        lg:translate-x-0 ${isOpen ? 'translate-x-0 shadow-2xl' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="flex flex-col h-full overflow-y-auto custom-scrollbar space-y-6">
          
          {/* TOP LOGO HEADER */}
          <div className="flex items-center justify-between pt-1 px-2">
            <Link to="/" className="flex items-center gap-2.5 group">
              <div className="w-9 h-9 rounded-lg bg-[#0B1628] text-white flex items-center justify-center shadow-md group-hover:bg-[#152744] transition-colors">
                <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                  <path d="M12 2L4 6v2h16V6l-8-4zm-6 8v8h2v-8H6zm4 0v8h2v-8h-2zm4 0v8h2v-8h-2zm4 0v8h2v-8h-2zM3 20v2h18v-2H3z" />
                </svg>
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-1">
                  <span className="font-marathi text-xl font-extrabold text-[#0B1628] tracking-tight">
                    प्रशासक
                  </span>
                  <span className="font-sans text-lg font-black text-[#E86A24]">
                    AI
                  </span>
                </div>
                <span className="font-marathi text-[9.5px] font-medium text-slate-500 -mt-1">
                  तयारी विचारांची, उद्याच्या भारतासाठी.
                </span>
              </div>
            </Link>

            {/* Mobile Close Button */}
            <button 
              onClick={onClose}
              className="lg:hidden p-1.5 text-slate-500 hover:text-slate-800 rounded-lg hover:bg-slate-200/50"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* PRIMARY NAVIGATION */}
          <nav className="space-y-1.5 pt-2">
            {sidebarNavigation.map((item) => {
              const IconComponent = iconMap[item.icon] || LayoutDashboard;
              const isActive = location.pathname === item.path || 
                (item.path !== '/' && item.path !== '/dashboard' && location.pathname.startsWith(item.path)) || 
                (location.pathname === '/dashboard' && currentTab === item.id);

              return (
                <Link
                  key={item.id}
                  to={item.path}
                  onClick={() => onClose && onClose()}
                  className={`
                    flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all duration-200 group relative
                    ${isActive 
                      ? 'bg-[#0B1628] text-white shadow-md shadow-slate-900/10 font-semibold' 
                      : 'text-slate-600 hover:text-[#0B1628] hover:bg-slate-200/50'
                    }
                  `}
                >
                  <IconComponent className={`w-4 h-4 transition-transform group-hover:scale-110 ${isActive ? 'text-amber-400' : 'text-slate-500 group-hover:text-[#0B1628]'}`} />
                  <span>{item.label}</span>
                  {isActive && (
                    <motion.div 
                      layoutId="activeSidePill"
                      className="absolute left-0 w-1 h-6 bg-amber-500 rounded-r-full"
                    />
                  )}
                </Link>
              );
            })}
          </nav>

          <div className="h-px bg-slate-200 my-2 mx-2" />

          {/* SECONDARY NAVIGATION */}
          <nav className="space-y-1.5">
            {sidebarSecondaryNav.map((item) => {
              const IconComponent = iconMap[item.icon] || BarChart3;
              const isActive = location.pathname === item.path || currentTab === item.id;

              return (
                <Link
                  key={item.id}
                  to={item.path}
                  onClick={() => onClose && onClose()}
                  className={`
                    flex items-center gap-3 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all duration-200 group
                    ${isActive 
                      ? 'bg-[#0B1628] text-white shadow-md shadow-slate-900/10 font-semibold' 
                      : 'text-slate-600 hover:text-[#0B1628] hover:bg-slate-200/50'
                    }
                  `}
                >
                  <IconComponent className={`w-4 h-4 ${isActive ? 'text-amber-400' : 'text-slate-500 group-hover:text-[#0B1628]'}`} />
                  <span>{item.label}</span>
                </Link>
              );
            })}
          </nav>

          {/* BOTTOM INSPIRATIONAL QUOTE CARD (As in Reference Image) */}
          <div className="mt-auto pt-4">
            <div className="p-3.5 rounded-2xl bg-gradient-to-br from-amber-500/10 via-amber-100/30 to-slate-100/60 border border-amber-200/60 relative overflow-hidden group">
              <div className="absolute right-0 bottom-0 opacity-10 text-4xl select-none font-serif text-slate-800">
                🏛️
              </div>
              <p className="text-[11.5px] italic text-slate-700 font-medium leading-snug">
                “Discipline today for a better tomorrow.”
              </p>
              <span className="text-[10px] font-bold text-amber-700 uppercase tracking-wider block mt-1">
                — UPSC
              </span>
            </div>
          </div>

          {/* USER PROFILE MINI CARD AT BOTTOM */}
          <div className="pt-2 border-t border-slate-200/80">
            <Link to="/profile" onClick={() => onClose && onClose()}>
              <div className={`flex items-center justify-between p-2 rounded-xl hover:bg-slate-200/40 transition-colors cursor-pointer group ${location.pathname === '/profile' ? 'bg-amber-500/10 border border-amber-200' : ''}`}>
                <div className="flex items-center gap-3">
                  <img 
                    src={userProfile.avatar} 
                    alt={userProfile.name}
                    className="w-9 h-9 rounded-full object-cover ring-2 ring-amber-500/30" 
                  />
                  <div className="flex flex-col">
                    <span className="text-xs font-bold text-[#0B1628] group-hover:text-amber-700 transition-colors">
                      {userProfile.name}
                    </span>
                    <span className="text-[10.5px] font-medium text-slate-500">
                      {userProfile.role}
                    </span>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-[#0B1628] group-hover:translate-x-0.5 transition-all" />
              </div>
            </Link>
          </div>

        </div>
      </aside>
    </>
  );
}
