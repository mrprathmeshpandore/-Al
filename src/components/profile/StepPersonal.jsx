import React from 'react';
import { User, Lightbulb, Calendar, MapPin } from 'lucide-react';
import { indianStates, maharashtraDistricts } from '../../data/profileData';

export default function StepPersonal({ formData, onChange, errors }) {
  return (
    <div className="space-y-6">
      
      {/* SECTION HEADER */}
      <div className="flex items-start gap-3.5 pb-4 border-b border-slate-100">
        <div className="w-10 h-10 rounded-xl bg-amber-500/10 text-amber-600 border border-amber-200 flex items-center justify-center shrink-0 mt-0.5">
          <User className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-[#0B1628]">Personal Information</h3>
          <p className="text-xs text-slate-500 font-medium leading-relaxed mt-0.5">
            Let's start with the basics. This helps us personalize your interview experience.
          </p>
        </div>
      </div>

      {/* FORM GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        
        {/* FULL NAME */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>Full Name</span>
            <span className="text-rose-500">*</span>
          </label>
          <input
            type="text"
            name="fullName"
            value={formData.fullName || ''}
            onChange={onChange}
            placeholder="e.g. Pratham Pandore"
            className={`w-full bg-slate-50/50 border rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all ${
              errors?.fullName ? 'border-rose-400 bg-rose-50/30' : 'border-slate-200 focus:border-[#0B1628]'
            }`}
          />
          {errors?.fullName && <p className="text-[11px] font-semibold text-rose-500 mt-1">{errors.fullName}</p>}
        </div>

        {/* DATE OF BIRTH */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>Date of Birth</span>
            <span className="text-rose-500">*</span>
          </label>
          <div className="relative">
            <input
              type="date"
              name="dob"
              value={formData.dob || ''}
              onChange={onChange}
              className={`w-full bg-slate-50/50 border rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all ${
                errors?.dob ? 'border-rose-400 bg-rose-50/30' : 'border-slate-200 focus:border-[#0B1628]'
              }`}
            />
          </div>
          {errors?.dob && <p className="text-[11px] font-semibold text-rose-500 mt-1">{errors.dob}</p>}
        </div>

        {/* HOME STATE */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>Home State</span>
            <span className="text-rose-500">*</span>
          </label>
          <select
            name="homeState"
            value={formData.homeState || ''}
            onChange={onChange}
            className={`w-full bg-slate-50/50 border rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all ${
              errors?.homeState ? 'border-rose-400 bg-rose-50/30' : 'border-slate-200 focus:border-[#0B1628]'
            }`}
          >
            <option value="">Select State</option>
            {indianStates.map((st) => (
              <option key={st} value={st}>{st}</option>
            ))}
          </select>
          {errors?.homeState && <p className="text-[11px] font-semibold text-rose-500 mt-1">{errors.homeState}</p>}
        </div>

        {/* DISTRICT */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>District</span>
            <span className="text-rose-500">*</span>
          </label>
          <select
            name="district"
            value={formData.district || ''}
            onChange={onChange}
            className={`w-full bg-slate-50/50 border rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all ${
              errors?.district ? 'border-rose-400 bg-rose-50/30' : 'border-slate-200 focus:border-[#0B1628]'
            }`}
          >
            <option value="">Select District</option>
            {maharashtraDistricts.map((d) => (
              <option key={d} value={d}>{d}</option>
            ))}
          </select>
          {errors?.district && <p className="text-[11px] font-semibold text-rose-500 mt-1">{errors.district}</p>}
        </div>

        {/* CURRENT CITY */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>Current City</span>
            <span className="text-rose-500">*</span>
          </label>
          <input
            type="text"
            name="currentCity"
            value={formData.currentCity || ''}
            onChange={onChange}
            placeholder="e.g. Pune"
            className={`w-full bg-slate-50/50 border rounded-xl px-3.5 py-2.5 text-xs font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all ${
              errors?.currentCity ? 'border-rose-400 bg-rose-50/30' : 'border-slate-200 focus:border-[#0B1628]'
            }`}
          />
          {errors?.currentCity && <p className="text-[11px] font-semibold text-rose-500 mt-1">{errors.currentCity}</p>}
        </div>

        {/* GENDER RADIO BUTTONS */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 flex items-center gap-1">
            <span>Gender</span>
            <span className="text-rose-500">*</span>
          </label>
          <div className="flex items-center gap-6 pt-2">
            {['Male', 'Female', 'Other'].map((g) => (
              <label key={g} className="flex items-center gap-2 cursor-pointer text-xs font-semibold text-slate-700 hover:text-[#0B1628]">
                <input
                  type="radio"
                  name="gender"
                  value={g}
                  checked={formData.gender === g}
                  onChange={onChange}
                  className="w-4 h-4 text-[#0B1628] focus:ring-[#0B1628] border-slate-300"
                />
                <span>{g}</span>
              </label>
            ))}
          </div>
          {errors?.gender && <p className="text-[11px] font-semibold text-rose-500 mt-1">{errors.gender}</p>}
        </div>

      </div>

      {/* WHY DO WE ASK THIS? INFORMATIONAL CARD */}
      <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-200/60 flex items-start gap-3">
        <Lightbulb className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
        <div className="space-y-0.5">
          <h4 className="text-xs font-bold text-[#0B1628]">Why do we ask this?</h4>
          <p className="text-[11.5px] font-medium text-slate-600 leading-relaxed">
            Your home state and background help us generate relevant and personalized questions during the interview practice sessions.
          </p>
        </div>
      </div>

    </div>
  );
}
