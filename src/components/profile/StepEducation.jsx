import React from 'react';
import { GraduationCap, Lightbulb } from 'lucide-react';

export default function StepEducation({ formData, onChange, errors }) {
  return (
    <div className="space-y-6">
      
      {/* SECTION HEADER */}
      <div className="flex items-start gap-3.5 pb-4 border-b border-slate-100">
        <div className="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-600 border border-blue-200 flex items-center justify-center shrink-0 mt-0.5">
          <GraduationCap className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-[#0B1628]">Education & Academics</h3>
          <p className="text-xs text-slate-500 font-medium leading-relaxed mt-0.5">
            Provide details about your academic degree and background.
          </p>
        </div>
      </div>

      {/* FORM GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        
        {/* GRADUATION DEGREE */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>Graduation Degree</span>
            <span className="text-rose-500">*</span>
          </label>
          <input
            type="text"
            name="degree"
            value={formData.degree || ''}
            onChange={onChange}
            placeholder="e.g. B.Tech Computer Science, B.A. History"
            className={`w-full bg-slate-50/50 border rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all ${
              errors?.degree ? 'border-rose-400 bg-rose-50/30' : 'border-slate-200 focus:border-[#0B1628]'
            }`}
          />
          {errors?.degree && <p className="text-[11px] font-semibold text-rose-500 mt-1">{errors.degree}</p>}
        </div>

        {/* UNIVERSITY / INSTITUTION */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>University / Institution</span>
            <span className="text-rose-500">*</span>
          </label>
          <input
            type="text"
            name="university"
            value={formData.university || ''}
            onChange={onChange}
            placeholder="e.g. Savitribai Phule Pune University"
            className={`w-full bg-slate-50/50 border rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all ${
              errors?.university ? 'border-rose-400 bg-rose-50/30' : 'border-slate-200 focus:border-[#0B1628]'
            }`}
          />
          {errors?.university && <p className="text-[11px] font-semibold text-rose-500 mt-1">{errors.university}</p>}
        </div>

        {/* SUBJECT / SPECIALIZATION */}
        <div className="space-y-1.5 md:col-span-2">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>Subject / Specialization</span>
            <span className="text-rose-500">*</span>
          </label>
          <input
            type="text"
            name="specialization"
            value={formData.specialization || ''}
            onChange={onChange}
            placeholder="e.g. Artificial Intelligence & Data Systems"
            className={`w-full bg-slate-50/50 border rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all ${
              errors?.specialization ? 'border-rose-400 bg-rose-50/30' : 'border-slate-200 focus:border-[#0B1628]'
            }`}
          />
          {errors?.specialization && <p className="text-[11px] font-semibold text-rose-500 mt-1">{errors.specialization}</p>}
        </div>

        {/* POST GRADUATION (OPTIONAL) */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>Post Graduation (Optional)</span>
          </label>
          <input
            type="text"
            name="postGraduation"
            value={formData.postGraduation || ''}
            onChange={onChange}
            placeholder="e.g. M.Tech, M.A. Public Policy"
            className="w-full bg-slate-50/50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all"
          />
        </div>

        {/* OTHER QUALIFICATIONS (OPTIONAL) */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>Other Certifications / Diplomas (Optional)</span>
          </label>
          <input
            type="text"
            name="otherQualifications"
            value={formData.otherQualifications || ''}
            onChange={onChange}
            placeholder="e.g. Diploma in Cyber Law"
            className="w-full bg-slate-50/50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all"
          />
        </div>

      </div>

      {/* INFO CARD */}
      <div className="p-4 rounded-xl bg-blue-500/5 border border-blue-200/60 flex items-start gap-3">
        <Lightbulb className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
        <div className="space-y-0.5">
          <h4 className="text-xs font-bold text-[#0B1628]">Academic Relevance in Interview</h4>
          <p className="text-[11.5px] font-medium text-slate-600 leading-relaxed">
            Interview boards frequently ask technical and practical application questions from your graduation background.
          </p>
        </div>
      </div>

    </div>
  );
}
