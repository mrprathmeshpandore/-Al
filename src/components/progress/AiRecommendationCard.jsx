import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Lightbulb, ArrowRight, RefreshCw, CheckCircle2, Circle, Play, SkipForward } from 'lucide-react';
import { coachApi } from '../../services/coachApi';

export default function AiRecommendationCard() {
  const navigate = useNavigate();
  const [todayData, setTodayData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);

  const fetchTodayPlan = async () => {
    try {
      setLoading(true);
      setError(null);
      let data = await coachApi.getTodayPlan();
      // If no active plan for today, auto-generate daily plan
      if (!data.plan && (!data.tasks || data.tasks.length === 0)) {
        const newPlan = await coachApi.generateDailyPlan(false);
        data = await coachApi.getTodayPlan();
      }
      setTodayData(data);
    } catch (err) {
      setError(err.message || 'Failed to load AI recommendations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTodayPlan();
  }, []);

  const handleRefresh = async () => {
    try {
      setGenerating(true);
      setError(null);
      await coachApi.refreshCoach('DAILY');
      await fetchTodayPlan();
    } catch (err) {
      setError(err.message || 'Failed to regenerate plan');
    } finally {
      setGenerating(false);
    }
  };

  const mapSourceToRoute = (taskType, sourceType) => {
    const type = (taskType || sourceType || '').toUpperCase();
    if (type.includes('DAF')) return '/daf';
    if (type.includes('CURRENT_AFFAIRS')) return '/current-affairs';
    if (type.includes('RESOURCE')) return '/resources';
    if (type.includes('QUESTION') || type.includes('WEAK') || type.includes('FOLLOW_UP') || type.includes('COUNTER')) return '/questions';
    return '/interview';
  };

  const handleCompleteTask = async (taskId, e) => {
    e.stopPropagation();
    try {
      await coachApi.completeTask(taskId);
      fetchTodayPlan();
    } catch (err) {
      console.error('Failed to complete task', err);
    }
  };

  const handleSkipTask = async (taskId, e) => {
    e.stopPropagation();
    try {
      await coachApi.skipTask(taskId);
      fetchTodayPlan();
    } catch (err) {
      console.error('Failed to skip task', err);
    }
  };

  const handleStartTask = (task) => {
    if (task.id && task.status === 'PENDING') {
      coachApi.startTask(task.id).catch(() => {});
    }
    const targetRoute = mapSourceToRoute(task.task_type, task.source_type);
    navigate(targetRoute);
  };

  const plan = todayData?.plan;
  const tasks = todayData?.tasks || [];
  const primaryTask = tasks.find((t) => t.status !== 'COMPLETED' && t.status !== 'SKIPPED') || tasks[0];

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.3 }}
      className="bg-white rounded-2xl p-6 border border-amber-950/5 shadow-sm flex flex-col justify-between"
    >
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-amber-50 text-amber-600">
              <Lightbulb className="w-4 h-4" />
            </div>
            <h3 className="font-serif font-bold text-slate-900 text-base">AI Preparation Coach</h3>
          </div>
          <button
            onClick={handleRefresh}
            disabled={generating || loading}
            title="Refresh AI Preparation Plan"
            className="p-1.5 rounded-lg text-slate-400 hover:text-amber-600 hover:bg-amber-50 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${generating ? 'animate-spin text-amber-600' : ''}`} />
          </button>
        </div>

        {generating ? (
          <div className="p-4 my-2 text-center bg-amber-50/50 rounded-xl border border-amber-100 text-amber-800 text-xs font-medium">
            Creating your personalized preparation plan...
          </div>
        ) : loading ? (
          <div className="p-4 my-2 text-center text-slate-400 text-xs">
            Loading today's practice plan...
          </div>
        ) : error ? (
          <div className="p-3 my-2 text-rose-600 bg-rose-50 rounded-xl text-xs">
            {error}
          </div>
        ) : (
          <>
            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2 font-sans">
              {plan?.title || 'Daily Preparation Focus'}
            </h4>

            <p className="text-xs text-slate-600 italic bg-amber-50/50 p-3 rounded-xl border border-amber-100/60 leading-relaxed font-sans mb-4">
              “{plan?.summary || 'Focus on consistent question practice and balanced administrative reasoning.'}”
            </p>

            {tasks.length > 0 && (
              <div className="space-y-2 mb-4">
                <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  Today's Recommended Tasks ({todayData?.completed_tasks || 0}/{todayData?.total_tasks || tasks.length})
                </div>
                <div className="max-h-48 overflow-y-auto space-y-1.5 pr-1">
                  {tasks.map((task) => {
                    const isDone = task.status === 'COMPLETED';
                    const isSkipped = task.status === 'SKIPPED';
                    return (
                      <div
                        key={task.id}
                        onClick={() => handleStartTask(task)}
                        className={`flex items-center justify-between p-2.5 rounded-xl border text-xs cursor-pointer transition-all ${
                          isDone
                            ? 'bg-emerald-50/60 border-emerald-200/80 text-emerald-900 line-through opacity-75'
                            : isSkipped
                            ? 'bg-slate-50 border-slate-200 text-slate-400 line-through'
                            : 'bg-white border-slate-200/80 hover:border-amber-300 hover:shadow-sm text-slate-800'
                        }`}
                      >
                        <div className="flex items-center gap-2 pr-2 min-w-0">
                          {isDone ? (
                            <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                          ) : (
                            <Circle className="w-4 h-4 text-amber-500 flex-shrink-0" />
                          )}
                          <span className="truncate font-medium">{task.title}</span>
                        </div>
                        {!isDone && !isSkipped && (
                          <div className="flex items-center gap-1 flex-shrink-0">
                            <button
                              onClick={(e) => handleCompleteTask(task.id, e)}
                              className="p-1 text-emerald-600 hover:bg-emerald-100/60 rounded"
                              title="Mark Complete"
                            >
                              <CheckCircle2 className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={(e) => handleSkipTask(task.id, e)}
                              className="p-1 text-slate-400 hover:bg-slate-200/60 rounded"
                              title="Skip Task"
                            >
                              <SkipForward className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </>
        )}
      </div>

      <button
        onClick={() => primaryTask ? handleStartTask(primaryTask) : navigate('/interview')}
        disabled={loading || generating}
        className="w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-amber-500 hover:bg-amber-600 text-white text-xs font-semibold shadow-sm transition-all group disabled:opacity-50 mt-2"
      >
        <span>{primaryTask ? `Practice Now: ${primaryTask.title}` : 'Start Recommended Practice'}</span>
        <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
      </button>
    </motion.div>
  );
}
