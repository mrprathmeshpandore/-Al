import React from 'react';
import { profileSteps } from '../../data/profileData';

export default function StepsOverviewCard({ currentStep, stepStatuses, onStepClick }) {
  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-2xs space-y-4">
      <h4 className="text-sm font-bold text-[#0B1628]">
        Steps Overview
      </h4>

      <div className="space-y-2.5">
        {profileSteps.map((step) => {
          const status = stepStatuses[step.key] || 'Not Started';
          const isCurrent = currentStep === step.id;

          let badgeStyle = "bg-slate-100 text-slate-500 border-slate-200";
          if (status === 'Completed') {
            badgeStyle = "bg-emerald-50 text-emerald-700 border-emerald-200";
          } else if (status === 'In Progress') {
            badgeStyle = "bg-amber-50 text-amber-700 border-amber-200";
          }

          return (
            <button
              key={step.id}
              onClick={() => onStepClick(step.id)}
              className={`w-full flex items-center justify-between p-2.5 rounded-xl border text-left transition-all ${
                isCurrent 
                  ? 'border-[#0B1628] bg-slate-50/60 shadow-2xs' 
                  : 'border-slate-100 hover:border-slate-200 hover:bg-slate-50/30'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <span className={`w-5 h-5 rounded-full text-[11px] font-bold flex items-center justify-center ${
                  isCurrent ? 'bg-[#0B1628] text-white' : 'bg-slate-100 text-slate-600'
                }`}>
                  {step.id}
                </span>
                <span className="text-xs font-bold text-slate-800">
                  {step.title} Information
                </span>
              </div>

              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${badgeStyle}`}>
                {status}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
