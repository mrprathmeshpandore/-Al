import React from 'react';
import { motion } from 'framer-motion';
import { Check } from 'lucide-react';
import { profileSteps } from '../../data/profileData';

export default function ProfileStepper({ currentStep, onStepClick, stepStatuses }) {
  return (
    <div className="w-full bg-white rounded-2xl p-4 sm:p-6 border border-slate-200/80 shadow-2xs">
      
      {/* DESKTOP HORIZONTAL STEPPER */}
      <div className="hidden md:flex items-center justify-between relative">
        {profileSteps.map((step, index) => {
          const isCurrent = currentStep === step.id;
          const isCompleted = stepStatuses[step.key] === 'Completed';

          return (
            <React.Fragment key={step.id}>
              {/* STEP ITEM */}
              <button
                onClick={() => onStepClick(step.id)}
                className="flex items-center gap-3 group cursor-pointer focus:outline-none text-left"
              >
                {/* STEP NUMBER CIRCLE */}
                <div 
                  className={`
                    w-9 h-9 rounded-full flex items-center justify-center font-bold text-xs transition-all duration-300 shrink-0
                    ${isCurrent 
                      ? 'bg-[#0B1628] text-white ring-4 ring-[#0B1628]/15 shadow-sm scale-105' 
                      : isCompleted 
                        ? 'bg-emerald-600 text-white shadow-2xs' 
                        : 'bg-slate-100 border border-slate-200 text-slate-500 group-hover:border-slate-300'
                    }
                  `}
                >
                  {isCompleted ? <Check className="w-4 h-4 stroke-[3]" /> : step.id}
                </div>

                {/* STEP LABELS */}
                <div className="flex flex-col">
                  <span className={`text-xs font-bold transition-colors ${isCurrent ? 'text-[#0B1628]' : 'text-slate-700 group-hover:text-[#0B1628]'}`}>
                    {step.title}
                  </span>
                  <span className="text-[10.5px] font-medium text-slate-400 -mt-0.5">
                    {step.subtitle}
                  </span>
                </div>
              </button>

              {/* CONNECTING LINE */}
              {index < profileSteps.length - 1 && (
                <div className="flex-1 h-[2px] mx-4 bg-slate-200 relative">
                  <motion.div
                    className="h-full bg-emerald-500"
                    initial={{ width: '0%' }}
                    animate={{ width: isCompleted ? '100%' : '0%' }}
                    transition={{ duration: 0.3 }}
                  />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* MOBILE COMPACT STEPPER */}
      <div className="md:hidden space-y-2">
        <div className="flex items-center justify-between text-xs font-bold text-[#0B1628]">
          <span>Step {currentStep} of {profileSteps.length}: {profileSteps[currentStep - 1].title}</span>
          <span className="text-amber-600 font-semibold">{profileSteps[currentStep - 1].subtitle}</span>
        </div>
        <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
          <div 
            className="h-full bg-[#0B1628] transition-all duration-300 rounded-full"
            style={{ width: `${(currentStep / profileSteps.length) * 100}%` }}
          />
        </div>
      </div>

    </div>
  );
}
