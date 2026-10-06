import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Check } from 'lucide-react';

const UKFlag = () => (
  <svg className="w-5 h-3.5 rounded-[2px] shadow-2xs shrink-0 object-cover border border-slate-200/40" viewBox="0 0 60 30" aria-hidden="true">
    <clipPath id="uk-clip">
      <rect width="60" height="30" rx="2" />
    </clipPath>
    <g clipPath="url(#uk-clip)">
      <rect width="60" height="30" fill="#012169" />
      <path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" strokeWidth="6"/>
      <path d="M0,0 L60,30 M60,0 L0,30" stroke="#C8102E" strokeWidth="4"/>
      <path d="M30,0 V30 M0,15 H60" stroke="#fff" strokeWidth="10"/>
      <path d="M30,0 V30 M0,15 H60" stroke="#C8102E" strokeWidth="6"/>
    </g>
  </svg>
);

const IndiaFlag = () => (
  <svg className="w-5 h-3.5 rounded-[2px] shadow-2xs shrink-0 object-cover border border-slate-200/40" viewBox="0 0 60 40" aria-hidden="true">
    <clipPath id="in-clip">
      <rect width="60" height="40" rx="2" />
    </clipPath>
    <g clipPath="url(#in-clip)">
      <rect width="60" height="13.33" fill="#FF9933" />
      <rect y="13.33" width="60" height="13.33" fill="#FFFFFF" />
      <rect y="26.66" width="60" height="13.34" fill="#138808" />
      <circle cx="30" cy="20" r="4.5" fill="none" stroke="#000080" strokeWidth="0.8" />
      <circle cx="30" cy="20" r="0.8" fill="#000080" />
      {[...Array(12)].map((_, i) => (
        <line
          key={i}
          x1={30 + 4.5 * Math.cos((i * Math.PI) / 6)}
          y1={20 + 4.5 * Math.sin((i * Math.PI) / 6)}
          x2={30 - 4.5 * Math.cos((i * Math.PI) / 6)}
          y2={20 - 4.5 * Math.sin((i * Math.PI) / 6)}
          stroke="#000080"
          strokeWidth="0.4"
        />
      ))}
    </g>
  </svg>
);

const LANGUAGES = [
  { code: 'en-IN', name: 'English', FlagComponent: UKFlag },
  { code: 'mr-IN', name: 'मराठी', FlagComponent: IndiaFlag },
  { code: 'hi-IN', name: 'हिंदी', FlagComponent: IndiaFlag },
];

export default function GlassLanguageSelector({ selectedLanguage = 'en-IN', onLanguageChange }) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef(null);

  // Find currently active language object
  const currentLang = LANGUAGES.find((l) => l.code === selectedLanguage) || LANGUAGES[0];
  const CurrentFlag = currentLang.FlagComponent;

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
        <div className="flex items-center gap-2 relative z-10">
          <CurrentFlag />
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
              const Flag = lang.FlagComponent;
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
                    <Flag />
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
