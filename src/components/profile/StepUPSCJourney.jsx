import React from 'react';
import { Target, Lightbulb } from 'lucide-react';
import { optionalSubjects, prepStages } from '../../data/profileData';

export default function StepUPSCJourney({ formData, onChange, errors }) {
  return (
    <div className="space-y-6">
      
      {/* SECTION HEADER */}
      <div className="flex items-start gap-3.5 pb-4 border-b border-slate-100">
        <div className="w-10 h-10 rounded-xl bg-purple-500/10 text-purple-600 border border-purple-200 flex items-center justify-center shrink-0 mt-0.5">
          <Target className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-[#0B1628]">UPSC Journey</h3>
          <p className="text-xs text-slate-500 font-medium leading-relaxed mt-0.5">
            Tell us about your UPSC attempt history and optional subject.
          </p>
        </div>
      </div>

      {/* FORM GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        
        {/* ATTEMPT COUNT */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>UPSC Attempt Number</span>
            <span className="text-rose-500">*</span>
          </label>
          <select
            name="attemptCount"
            value={formData.attemptCount || ''}
            onChange={onChange}
            className={`w-full bg-slate-50/50 border rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all ${
              errors?.attemptCount ? 'border-rose-400 bg-rose-50/30' : 'border-slate-200 focus:border-[#0B1628]'
            }`}
          >
            <option value="1">1st Attempt</option>
            <option value="2">2nd Attempt</option>
            <option value="3">3rd Attempt</option>
            <option value="4">4th Attempt</option>
            <option value="5">5th Attempt</option>
            <option value="6">6th+ Attempt</option>
          </select>
          {errors?.attemptCount && <p className="text-[11px] font-semibold text-rose-500 mt-1">{errors.attemptCount}</p>}
        </div>

        {/* OPTIONAL SUBJECT */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>Optional Subject</span>
            <span className="text-rose-500">*</span>
          </label>
          <select
            name="optionalSubject"
            value={formData.optionalSubject || ''}
            onChange={onChange}
            className={`w-full bg-slate-50/50 border rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all ${
              errors?.optionalSubject ? 'border-rose-400 bg-rose-50/30' : 'border-slate-200 focus:border-[#0B1628]'
            }`}
          >
            <option value="">Select Optional Subject</option>
            {optionalSubjects.map((sub) => (
              <option key={sub} value={sub}>{sub}</option>
            ))}
          </select>
          {errors?.optionalSubject && <p className="text-[11px] font-semibold text-rose-500 mt-1">{errors.optionalSubject}</p>}
        </div>

        {/* PREVIOUS INTERVIEW EXPERIENCE */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>Previous UPSC Interview Experience?</span>
            <span className="text-rose-500">*</span>
          </label>
          <div className="flex items-center gap-6 pt-2">
            {['No', 'Yes (1 Time)', 'Yes (2+ Times)'].map((exp) => (
              <label key={exp} className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-700 hover:text-[#0B1628]">
                <input
                  type="radio"
                  name="hasPreviousInterview"
                  value={exp}
                  checked={formData.hasPreviousInterview === exp}
                  onChange={onChange}
                  className="w-4 h-4 text-[#0B1628] focus:ring-[#0B1628] border-slate-300"
                />
                <span>{exp}</span>
              </label>
            ))}
          </div>
          {errors?.hasPreviousInterview && <p className="text-[11px] font-semibold text-rose-500 mt-1">{errors.hasPreviousInterview}</p>}
        </div>

        {/* PREPARATION STAGE */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>Current Preparation Stage</span>
            <span className="text-rose-500">*</span>
          </label>
          <select
            name="preparationStage"
            value={formData.preparationStage || ''}
            onChange={onChange}
            className={`w-full bg-slate-50/50 border rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all ${
              errors?.preparationStage ? 'border-rose-400 bg-rose-50/30' : 'border-slate-200 focus:border-[#0B1628]'
            }`}
          >
            {prepStages.map((stg) => (
              <option key={stg} value={stg}>{stg}</option>
            ))}
          </select>
          {errors?.preparationStage && <p className="text-[11px] font-semibold text-rose-500 mt-1">{errors.preparationStage}</p>}
        </div>

      </div>

      {/* INFO CARD */}
      <div className="p-4 rounded-xl bg-purple-500/5 border border-purple-200/60 flex items-start gap-3">
        <Lightbulb className="w-5 h-5 text-purple-600 shrink-0 mt-0.5" />
        <div className="space-y-0.5">
          <h4 className="text-xs font-bold text-[#0B1628]">Customized AI Difficulty Calibration</h4>
          <p className="text-[11.5px] font-medium text-slate-600 leading-relaxed">
            Your optional subject and attempt history allow Prashasak AI to calibrate interviewer tone and cross-examination depth.
          </p>
        </div>
      </div>

    </div>
  );
}
