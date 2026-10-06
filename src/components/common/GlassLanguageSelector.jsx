import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Check } from 'lucide-react';

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
      {/* CAPSULE TRIGGER BUTTON - LIGHT GLASS DESIGN */}
      <button
        type="button"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        className={`group relative flex items-center justify-between gap-2 px-3 py-1.5 rounded-xl text-xs font-extrabold transition-all duration-200 cursor-pointer backdrop-blur-md shadow-2xs border ${
          isOpen
            ? 'bg-slate-100 text-[#0B1628] border-slate-300 ring-2 ring-[#0B1628]/10 shadow-xs'
            : 'bg-white hover:bg-slate-50 text-slate-800 hover:text-[#0B1628] border-slate-200 hover:border-slate-300'
        }`}
        title="Select Interview Language"
      >
        <div className="flex items-center gap-1.5 relative z-10">
          <span className="text-sm leading-none select-none">{currentLang.flag}</span>
          <span className="font-bold tracking-tight text-[#0B1628]">{currentLang.name}</span>
        </div>

        <ChevronDown
          className={`w-3.5 h-3.5 text-slate-500 group-hover:text-[#0B1628] transition-transform duration-300 shrink-0 relative z-10 ${
            isOpen ? 'rotate-180 text-[#0B1628]' : ''
          }`}
        />
      </button>

      {/* FLOATING LIQUID LIGHT GLASS DROPDOWN PANEL */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -6, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.96 }}
            transition={{ duration: 0.16, ease: [0.16, 1, 0.3, 1] }}
            role="listbox"
            className="absolute top-full right-0 mt-2 w-44 z-50 p-1.5 rounded-2xl bg-white/95 backdrop-blur-2xl border border-slate-200/90 shadow-xl shadow-slate-900/10 space-y-1 overflow-hidden"
          >
            {/* Ambient Lighting Glow */}
            <div className="absolute -top-10 -right-10 w-24 h-24 bg-amber-500/10 rounded-full blur-2xl pointer-events-none" />
            <div className="absolute -bottom-10 -left-10 w-24 h-24 bg-indigo-500/10 rounded-full blur-2xl pointer-events-none" />

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
                      ? 'bg-[#0B1628] text-white font-extrabold border-[#0B1628] shadow-sm shadow-slate-900/15'
                      : 'text-slate-700 hover:text-[#0B1628] bg-transparent hover:bg-slate-100/80 border-transparent hover:border-slate-200/60'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <span className="text-sm leading-none select-none">{lang.flag}</span>
                    <span className="font-bold tracking-tight">{lang.name}</span>
                  </div>

                  {isSelected && (
                    <motion.div
                      initial={{ scale: 0.5, opacity: 0 }}
                      animate={{ scale: 1, opacity: 1 }}
                      transition={{ duration: 0.15 }}
                    >
                      <Check className="w-3.5 h-3.5 text-amber-400 shrink-0 stroke-[2.5]" />
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
