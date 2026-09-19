import React from 'react';
import { Compass, Lightbulb } from 'lucide-react';

export default function StepPerspective({ formData, onChange, errors }) {
  return (
    <div className="space-y-6">
      
      {/* SECTION HEADER */}
      <div className="flex items-start gap-3.5 pb-4 border-b border-slate-100">
        <div className="w-10 h-10 rounded-xl bg-orange-500/10 text-orange-600 border border-orange-200 flex items-center justify-center shrink-0 mt-0.5">
          <Compass className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-[#0B1628]">Perspective & Values</h3>
          <p className="text-xs text-slate-500 font-medium leading-relaxed mt-0.5">
            Share your motivation and governance vision for personalized evaluation.
          </p>
        </div>
      </div>

      {/* FORM FIELDS */}
      <div className="space-y-5">
        
        {/* WHY CIVIL SERVICES */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
              <span>Why do you want to join the Civil Services?</span>
            </label>
            <span className="text-[10px] font-medium text-slate-400">
              {(formData.whyCivilServices || '').length}/300 chars
            </span>
          </div>
          <textarea
            name="whyCivilServices"
            rows={3}
            maxLength={300}
            value={formData.whyCivilServices || ''}
            onChange={onChange}
            placeholder="Express your core motivation, governance vision, or commitment to public service..."
            className="w-full bg-slate-50/50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all resize-none"
          />
        </div>

        {/* KEY FOCUS AREAS */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>Your Key Focus Areas / Priorities in Administration</span>
          </label>
          <textarea
            name="keyFocusAreas"
            rows={2}
            maxLength={250}
            value={formData.keyFocusAreas || ''}
            onChange={onChange}
            placeholder="e.g. Health delivery in aspirational districts, Digital Public Infrastructure..."
            className="w-full bg-slate-50/50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all resize-none"
          />
        </div>

        {/* SOMETHING FOR THE BOARD TO KNOW */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>Anything specific you want the Interview Board to know? (Optional)</span>
          </label>
          <textarea
            name="boardNotes"
            rows={2}
            maxLength={250}
            value={formData.boardNotes || ''}
            onChange={onChange}
            placeholder="e.g. Passionate about rural tech adoption, background in debate competitions..."
            className="w-full bg-slate-50/50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all resize-none"
          />
        </div>

      </div>

      {/* FINAL STEP NOTE */}
      <div className="p-4 rounded-xl bg-orange-500/5 border border-orange-200/60 flex items-start gap-3">
        <Lightbulb className="w-5 h-5 text-orange-600 shrink-0 mt-0.5" />
        <div className="space-y-0.5">
          <h4 className="text-xs font-bold text-[#0B1628]">Profile Readiness</h4>
          <p className="text-[11.5px] font-medium text-slate-600 leading-relaxed">
            Completing your profile allows Prashasak AI to synthesize your DAF and build tailored interview simulation rounds.
          </p>
        </div>
      </div>

    </div>
  );
}
