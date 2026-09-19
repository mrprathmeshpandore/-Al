import React from 'react';
import { motion } from 'framer-motion';
import { skillMetrics } from '../../data/progressData';

export default function SkillAnalysisCard() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.15 }}
      className="bg-white rounded-2xl p-6 border border-amber-950/5 shadow-sm flex flex-col justify-between"
    >
      <div className="mb-4">
        <h3 className="font-serif font-bold text-slate-900 text-lg">Skill Analysis</h3>
        <p className="text-xs text-slate-500 font-sans">Core interview competency metrics</p>
      </div>

      <div className="space-y-4 my-auto">
        {skillMetrics.map((skill, index) => (
          <div key={skill.label} className="space-y-1.5">
            <div className="flex items-center justify-between text-xs font-medium">
              <span className="text-slate-700 font-medium font-sans">{skill.label}</span>
              <span className="text-slate-900 font-bold font-sans">{skill.score}%</span>
            </div>

            <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                whileInView={{ width: `${skill.score}%` }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, delay: index * 0.1, ease: 'easeOut' }}
                className="h-full bg-blue-600 rounded-full"
              />
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
