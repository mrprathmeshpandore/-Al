import React from 'react';
import { motion } from 'framer-motion';
import { Mic, BarChart2, Clock, MessageSquare } from 'lucide-react';
import { interviewOptions } from '../../data/settingsData';

export default function InterviewPreferencesCard({ settings, updateInterviewSetting }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.1 }}
      className="bg-white rounded-2xl p-6 border border-amber-950/5 shadow-2xs space-y-4 flex flex-col justify-between"
    >
      <div>
        <div className="flex items-center gap-2 mb-1">
          <div className="p-1.5 rounded-lg bg-emerald-50 text-emerald-600">
            <Mic className="w-4 h-4" />
          </div>
          <h3 className="font-serif font-bold text-slate-900 text-lg">Interview Preferences</h3>
        </div>
        <p className="text-xs text-slate-500 font-sans mb-4">
          Customize your interview experience.
        </p>

        <div className="space-y-3.5">
          {/* Answer Mode */}
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2.5">
              <div className="p-1.5 rounded-lg bg-slate-100 text-slate-600">
                <Mic className="w-4 h-4" />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-800 font-sans block">Answer Mode</label>
                <span className="text-[11px] text-slate-400 font-sans">Voice / Text</span>
              </div>
            </div>
            <select
              value={settings.answerMode}
              onChange={(e) => updateInterviewSetting('answerMode', e.target.value)}
              className="px-3 py-1.5 text-xs font-semibold bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500/20 text-slate-700"
            >
              {interviewOptions.answerModes.map((mode) => (
                <option key={mode} value={mode}>{mode}</option>
              ))}
            </select>
          </div>

          {/* Difficulty */}
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2.5">
              <div className="p-1.5 rounded-lg bg-slate-100 text-slate-600">
                <BarChart2 className="w-4 h-4" />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-800 font-sans block">Interview Difficulty</label>
                <span className="text-[11px] text-slate-400 font-sans">Easy / Medium / Hard</span>
              </div>
            </div>
            <select
              value={settings.difficulty}
              onChange={(e) => updateInterviewSetting('difficulty', e.target.value)}
              className="px-3 py-1.5 text-xs font-semibold bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500/20 text-slate-700"
            >
              {interviewOptions.difficulties.map((diff) => (
                <option key={diff} value={diff}>{diff}</option>
              ))}
            </select>
          </div>

          {/* Duration */}
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-2.5">
              <div className="p-1.5 rounded-lg bg-slate-100 text-slate-600">
                <Clock className="w-4 h-4" />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-800 font-sans block">Interview Duration</label>
                <span className="text-[11px] text-slate-400 font-sans">5 / 10 / 15 / 20 minutes</span>
              </div>
            </div>
            <select
              value={settings.duration}
              onChange={(e) => updateInterviewSetting('duration', e.target.value)}
              className="px-3 py-1.5 text-xs font-semibold bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500/20 text-slate-700"
            >
              {interviewOptions.durations.map((dur) => (
                <option key={dur} value={dur}>{dur}</option>
              ))}
            </select>
          </div>

          {/* Follow-up Questions Toggle */}
          <div className="flex items-center justify-between gap-4 pt-1">
            <div className="flex items-center gap-2.5">
              <div className="p-1.5 rounded-lg bg-slate-100 text-slate-600">
                <MessageSquare className="w-4 h-4" />
              </div>
              <div>
                <label className="text-xs font-bold text-slate-800 font-sans block">Follow-up Questions</label>
                <span className="text-[11px] text-slate-400 font-sans">Enable AI follow-up questions</span>
              </div>
            </div>
            <button
              onClick={() => updateInterviewSetting('followUpQuestions', !settings.followUpQuestions)}
              className={`w-11 h-6 rounded-full transition-colors relative flex items-center px-0.5 ${
                settings.followUpQuestions ? 'bg-blue-600' : 'bg-slate-300'
              }`}
            >
              <span
                className={`w-5 h-5 rounded-full bg-white shadow-md transform transition-transform ${
                  settings.followUpQuestions ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
