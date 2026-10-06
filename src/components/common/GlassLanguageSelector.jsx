import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Check, Globe } from 'lucide-react';

const LANGUAGES = [
  { code: 'en-IN', name: 'English', flag: '🇬🇧' },
  { code: 'mr-IN', name: 'मराठी', flag: '🇮🇳' },
  { code: 'hi-IN', name: 'हिंदी', flag: '🇮🇳' },
];

export default function GlassLanguageSelector({ selectedLanguage = 'en-IN', onLanguageChange }) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef(null);

  // Find currently active language object
  const currentLang = LANGUAGES.find((l) => l.code === selectedLanguage) || LANGUAGES[0];

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (code) => {
    if (onLanguageChange) {
      onLanguageChange(code);
    }
    setIsOpen(false);
  };

  return (
    <div className="relative inline-block text-left" ref={containerRef}>
      {/* CAPSULE TRIGGER BUTTON */}
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        className={`group relative flex items-center justify-between gap-2.5 px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all duration-300 cursor-pointer backdrop-blur-xl shadow-lg border ${
          isOpen
            ? 'bg-[#0B1628]/90 text-white border-violet-400/50 shadow-violet-500/20 ring-2 ring-violet-500/20'
            : 'bg-[#0B1628]/75 hover:bg-[#0B1628]/90 text-slate-100 hover:text-white border-white/15 hover:border-violet-400/40 shadow-violet-950/20'
        }`}
        title="Select Interview Language"
      >
        {/* Subtle interior glow */}
        <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-violet-500/10 via-transparent to-indigo-500/10 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />

        <div className="flex items-center gap-2 relative z-10">
          <span className="text-sm leading-none select-none">{currentLang.flag}</span>
          <span className="font-bold tracking-tight text-white">{currentLang.name}</span>
        </div>

        <ChevronDown
          className={`w-3.5 h-3.5 text-violet-300/80 group-hover:text-white transition-transform duration-300 shrink-0 relative z-10 ${
            isOpen ? 'rotate-180 text-violet-300' : ''
          }`}
        />
      </button>

      {/* FLOATING LIQUID GLASS DROPDOWN PANEL */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -6, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.95 }}
            transition={{ duration: 0.18, ease: [0.16, 1, 0.3, 1] }}
            role="listbox"
            className="absolute top-full right-0 mt-2 w-44 z-50 p-1.5 rounded-2xl bg-[#0B1628]/90 backdrop-blur-2xl border border-white/20 shadow-2xl shadow-violet-950/60 space-y-1 overflow-hidden"
          >
            {/* Ambient Violet Backlight Glow */}
            <div className="absolute -top-10 -right-10 w-24 h-24 bg-violet-600/20 rounded-full blur-2xl pointer-events-none" />
            <div className="absolute -bottom-10 -left-10 w-24 h-24 bg-indigo-600/20 rounded-full blur-2xl pointer-events-none" />

            {LANGUAGES.map((lang) => {
              const isSelected = lang.code === selectedLanguage;
              return (
                <button
                  key={lang.code}
                  type="button"
                  role="option"
                  aria-selected={isSelected}
                  onClick={() => handleSelect(lang.code)}
                  className={`relative w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold transition-all duration-200 cursor-pointer border ${
                    isSelected
                      ? 'bg-gradient-to-r from-violet-600/50 to-indigo-600/40 text-white border-violet-400/40 shadow-md shadow-violet-900/30'
                      : 'text-slate-300 hover:text-white bg-white/0 hover:bg-white/10 border-transparent hover:border-white/10'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <span className="text-sm leading-none select-none">{lang.flag}</span>
                    <span className="font-medium tracking-wide">{lang.name}</span>
                  </div>

                  {isSelected && (
                    <motion.div
                      initial={{ scale: 0.5, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ duration: 0.15 }}
                    >
                      <Check className="w-3.5 h-3.5 text-violet-300 shrink-0 stroke-[2.5]" />
                    </motion.div>
                  )}
                </button>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
