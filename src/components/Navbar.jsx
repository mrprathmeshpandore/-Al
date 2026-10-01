import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Search, ArrowRight, User as UserIcon, LogOut } from 'lucide-react';
import { buttonTapHover } from '../utils/animations';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { isAuthenticated, user, openAuthModal, logout } = useAuth();
  const navigate = useNavigate();

  const navItems = [
    { label: 'Home', path: '/', active: true },
    { label: 'AI Interview', path: '/dashboard?tab=interview', active: false },
    { label: 'Question Bank', path: '/dashboard?tab=question-bank', active: false },
    { label: 'Current Affairs', path: '/dashboard?tab=current-affairs', active: false },
    { label: 'Resources', path: '/dashboard?tab=resources', active: false },
    { label: 'Pricing', path: '/#pricing', active: false },
  ];

  const navbarContainer = {
    hidden: { opacity: 0, y: -20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.6,
        ease: [0.16, 1, 0.3, 1],
        staggerChildren: 0.08,
        delayChildren: 0.1,
      },
    },
  };

  const navChildItem = {
    hidden: { opacity: 0, y: -10 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.4 } },
  };

  return (
    <motion.header
      variants={navbarContainer}
      initial="hidden"
      animate="visible"
      className="sticky top-0 z-50 glass-header px-4 lg:px-12 py-3.5 transition-all duration-300"
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* LOGO & BRAND SLOGAN */}
        <Link to="/">
          <motion.div variants={navChildItem} className="flex items-center gap-3 group cursor-pointer">
            <div className="w-10 h-10 rounded-lg bg-[#0B1628] text-white flex flex-col items-center justify-center shadow-md group-hover:bg-[#152744] transition-colors">
              <svg className="w-6 h-6 fill-current" viewBox="0 0 24 24">
                <path d="M12 2L4 6v2h16V6l-8-4zm-6 8v8h2v-8H6zm4 0v8h2v-8h-2zm4 0v8h2v-8h-2zm4 0v8h2v-8h-2zM3 20v2h18v-2H3z" />
              </svg>
            </div>
            
            <div className="flex flex-col">
              <div className="flex items-center gap-1.5">
                <span className="font-marathi text-2xl font-extrabold text-[#0B1628] tracking-tight">
                  प्रशासक
                </span>
                <span className="font-sans text-xl font-black text-[#E86A24]">
                  AI
                </span>
              </div>
              <span className="font-marathi text-[10.5px] font-medium text-[#64748B] -mt-1 tracking-normal">
                तयारी विचारांची, उद्याच्या भारतासाठी.
              </span>
            </div>
          </motion.div>
        </Link>

        {/* NAVIGATION LINKS */}
        <nav className="hidden md:flex items-center gap-7">
          {navItems.map((item, index) => (
            <motion.div key={index} variants={navChildItem}>
              <Link
                to={item.path}
                className={`relative text-[13.5px] font-medium transition-colors duration-200 py-1 ${
                  item.active ? 'text-[#0F172A] font-semibold' : 'text-[#475569] hover:text-[#0F172A]'
                }`}
              >
                {item.label}
                {item.active && (
                  <motion.div
                    layoutId="activeIndicator"
                    className="absolute bottom-0 left-0 right-0 h-[2px] bg-[#0F172A] rounded-full"
                    transition={{ type: "spring", stiffness: 380, damping: 30 }}
                  />
                )}
              </Link>
            </motion.div>
          ))}
        </nav>

        {/* RIGHT CONTROLS: SEARCH, AUTH, CTA */}
        <div className="flex items-center gap-4">
          <motion.button
            variants={navChildItem}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            className="p-2 text-[#475569] hover:text-[#0F172A] transition-colors cursor-pointer"
            aria-label="Search"
          >
            <Search className="w-4 h-4" />
          </motion.button>

          <motion.span variants={navChildItem} className="text-[#CBD5E1] text-sm hidden sm:inline">
            |
          </motion.span>

          {isAuthenticated ? (
            <div className="flex items-center gap-2.5">
              <Link
                to="/dashboard"
                className="bg-[#0B1628] hover:bg-[#152744] text-white px-4 py-1.5 rounded-full text-xs font-bold transition-all shadow-xs flex items-center gap-1.5"
              >
                <span>Dashboard</span>
                <ArrowRight className="w-3.5 h-3.5 text-[#E86A24]" />
              </Link>

              <Link
                to="/profile"
                className="flex items-center gap-2 bg-slate-100 hover:bg-slate-200 text-[#0B1628] px-3.5 py-1.5 rounded-full text-xs font-bold transition-colors"
              >
                <UserIcon className="w-3.5 h-3.5 text-[#E86A24]" />
                <span>{user?.full_name?.split(' ')[0] || 'Profile'}</span>
              </Link>

              <button
                onClick={logout}
                title="Sign Out"
                className="p-2 text-slate-500 hover:text-rose-600 transition-colors cursor-pointer"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <>
              <button
                onClick={() => openAuthModal('login')}
                className="text-[13.5px] font-semibold text-[#475569] hover:text-[#0F172A] transition-colors px-2 hidden sm:inline cursor-pointer"
              >
                Login
              </button>

              <motion.button
                variants={buttonTapHover}
                initial="rest"
                whileHover="hover"
                whileTap="tap"
                onClick={() => openAuthModal('register')}
                className="bg-[#0B1628] hover:bg-[#152744] text-white px-5 py-2.5 rounded-full text-[13.5px] font-semibold flex items-center gap-2 shadow-md shadow-slate-900/10 transition-colors cursor-pointer"
              >
                <span>Start Preparing</span>
                <ArrowRight className="w-4 h-4" />
              </motion.button>
            </>
          )}
        </div>

      </div>
    </motion.header>
  );
}
