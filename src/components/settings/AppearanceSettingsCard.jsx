import React from 'react';
import { motion } from 'framer-motion';
import { Palette, Moon, Languages, Type, Activity } from 'lucide-react';
import { appearanceOptions } from '../../data/settingsData';

export default function AppearanceSettingsCard({ settings, updateAppearanceSetting }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.25 }}
      className="bg-white rounded-2xl p-6 border border-amber-950/5 shadow-2xs space-y-4 flex flex-col justify-between"
    >
      <div>
        <div className="flex items-center gap-2 mb-1">
          <div className="p-1.5 rounded-lg bg-indigo-50 text-indigo-600">
            <Palette className="w-4 h-4" />
          </div>
          <h3 className="font-serif font-bold text-slate-900 text-lg">Appearance</h3>
        </div>
        <p className="text-xs text-slate-500 font-sans mb-4">
          Customize the look and language.
        </p>

        <div className="space-y-3.5">
          {/* Theme */}
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2.5">
              <div className="p-1.5 rounded-lg bg-slate-100 text-slate-600">
                <Moon className="w-4 h-4" />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-800 font-sans block">Theme</label>
                <span className="text-[11px] text-slate-400 font-sans">Choose your theme</span>
              </div>
            </div>
            <select
              value={settings.theme}
              onChange={(e) => updateAppearanceSetting('theme', e.target.value)}
              className="px-3 py-1.5 text-xs font-semibold bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500/20 text-slate-700"
            >
              {appearanceOptions.themes.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>

          {/* Language */}
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2.5">
              <div className="p-1.5 rounded-lg bg-slate-100 text-slate-600">
                <Languages className="w-4 h-4" />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-800 font-sans block">Language</label>
                <span className="text-[11px] text-slate-400 font-sans">Choose your language</span>
              </div>
            </div>
            <select
              value={settings.language}
              onChange={(e) => updateAppearanceSetting('language', e.target.value)}
              className="px-3 py-1.5 text-xs font-semibold bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500/20 text-slate-700"
            >
              {appearanceOptions.languages.map((l) => (
                <option key={l} value={l}>{l}</option>
              ))}
            </select>
          </div>

          {/* Font Size */}
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2.5">
              <div className="p-1.5 rounded-lg bg-slate-100 text-slate-600">
                <Type className="w-4 h-4" />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-800 font-sans block">Font Size</label>
                <span className="text-[11px] text-slate-400 font-sans">Adjust text size</span>
              </div>
            </div>
            <select
              value={settings.fontSize}
              onChange={(e) => updateAppearanceSetting('fontSize', e.target.value)}
              className="px-3 py-1.5 text-xs font-semibold bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500/20 text-slate-700"
            >
              {appearanceOptions.fontSizes.map((f) => (
                <option key={f} value={f}>{f}</option>
              ))}
            </select>
          </div>

          {/* Reduced Motion Toggle */}
          <div className="flex items-center justify-between gap-4 pt-1">
            <div className="flex items-center gap-2.5">
              <div className="p-1.5 rounded-lg bg-slate-100 text-slate-600">
                <Activity className="w-4 h-4" />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-800 font-sans block">Reduced Motion</label>
                <span className="text-[11px] text-slate-400 font-sans">Minimize animations</span>
              </div>
            </div>
            <button
              onClick={() => updateAppearanceSetting('reducedMotion', !settings.reducedMotion)}
              className={`w-11 h-6 rounded-full transition-colors relative flex items-center px-0.5 ${
                settings.reducedMotion ? 'bg-blue-600' : 'bg-slate-300'
              }`}
            >
              <span
                className={`w-5 h-5 rounded-full bg-white shadow-md transform transition-transform ${
                  settings.reducedMotion ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
