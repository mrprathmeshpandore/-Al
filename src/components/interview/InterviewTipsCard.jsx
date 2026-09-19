import React from 'react';
import { Lightbulb, Check } from 'lucide-react';
import { answerTips } from '../../data/interviewData';

export default function InterviewTipsCard() {
  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-2xs space-y-3">
      <div className="flex items-center gap-2">
        <Lightbulb className="w-4 h-4 text-amber-600" />
        <h4 className="text-xs sm:text-sm font-bold text-[#0B1628]">
          Tips for a Better Answer
        </h4>
      </div>

      <ul className="space-y-2 text-xs font-semibold text-slate-600">
        {answerTips.map((tip, idx) => (
          <li key={idx} className="flex items-start gap-2">
            <Check className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
            <span>{tip}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
