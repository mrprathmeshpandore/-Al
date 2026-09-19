import React from 'react';
import { Heart, Lightbulb } from 'lucide-react';

export default function StepInterests({ formData, onChange, errors }) {
  return (
    <div className="space-y-6">
      
      {/* SECTION HEADER */}
      <div className="flex items-start gap-3.5 pb-4 border-b border-slate-100">
        <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-600 border border-emerald-200 flex items-center justify-center shrink-0 mt-0.5">
          <Heart className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-[#0B1628]">Beyond Academics</h3>
          <p className="text-xs text-slate-500 font-medium leading-relaxed mt-0.5">
            Share your hobbies, interests, and extra-curricular achievements.
          </p>
        </div>
      </div>

      {/* FORM GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        
        {/* HOBBIES */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>Hobbies</span>
            <span className="text-rose-500">*</span>
          </label>
          <input
            type="text"
            name="hobbies"
            value={formData.hobbies || ''}
            onChange={onChange}
            placeholder="e.g. Photography, Landscape Sketching"
            className={`w-full bg-slate-50/50 border rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all ${
              errors?.hobbies ? 'border-rose-400 bg-rose-50/30' : 'border-slate-200 focus:border-[#0B1628]'
            }`}
          />
          {errors?.hobbies && <p className="text-[11px] font-semibold text-rose-500 mt-1">{errors.hobbies}</p>}
        </div>

        {/* SPORTS */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>Sports / Physical Activities</span>
          </label>
          <input
            type="text"
            name="sports"
            value={formData.sports || ''}
            onChange={onChange}
            placeholder="e.g. Badminton, Marathon Running, Chess"
            className="w-full bg-slate-50/50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all"
          />
        </div>

        {/* BOOKS / READING */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>Books / Favorite Reading Genres</span>
          </label>
          <input
            type="text"
            name="readingBooks"
            value={formData.readingBooks || ''}
            onChange={onChange}
            placeholder="e.g. Indian Constitutional History, Biographies"
            className="w-full bg-slate-50/50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all"
          />
        </div>

        {/* AREAS OF INTEREST */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>Special Areas of Interest</span>
          </label>
          <input
            type="text"
            name="areasOfInterest"
            value={formData.areasOfInterest || ''}
            onChange={onChange}
            placeholder="e.g. Digital Governance, Renewable Energy"
            className="w-full bg-slate-50/50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all"
          />
        </div>

        {/* COMMUNITY / SOCIAL ACTIVITIES */}
        <div className="space-y-1.5 md:col-span-2">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>Social / Community Work / Leadership Roles</span>
          </label>
          <input
            type="text"
            name="communityActivities"
            value={formData.communityActivities || ''}
            onChange={onChange}
            placeholder="e.g. NSS Volunteer, Student NGO Coordinator"
            className="w-full bg-slate-50/50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all"
          />
        </div>

      </div>

      {/* DAF INTERVIEW TIP CARD */}
      <div className="p-4 rounded-xl bg-emerald-500/5 border border-emerald-200/60 flex items-start gap-3">
        <Lightbulb className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
        <div className="space-y-0.5">
          <h4 className="text-xs font-bold text-[#0B1628]">DAF Question Generation Example</h4>
          <p className="text-[11.5px] font-medium text-slate-600 leading-relaxed">
            If you enter <span className="font-semibold text-slate-800">"Photography"</span>, AI will later simulate interview questions like: <span className="italic">"You mentioned photography as a hobby. What has photography taught you about keen observation and administrative patience?"</span>
          </p>
        </div>
      </div>

    </div>
  );
}
