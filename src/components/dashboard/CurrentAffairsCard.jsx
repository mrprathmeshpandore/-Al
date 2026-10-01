import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, ChevronRight, Newspaper } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { currentAffairsApi } from '../../services/currentAffairsApi';

export default function CurrentAffairsCard() {
  const navigate = useNavigate();
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadCurrentAffairs() {
      try {
        setLoading(true);
        const data = await currentAffairsApi.getCurrentAffairs({ limit: 4 });
        if (Array.isArray(data)) {
          setArticles(data);
        } else if (data?.articles) {
          setArticles(data.articles);
        }
      } catch (err) {
        console.error('Failed to load current affairs on dashboard:', err);
      } finally {
        setLoading(false);
      }
    }
    loadCurrentAffairs();
  }, []);

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-2xs space-y-4">
      {/* HEADER */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-[#0B1628] tracking-tight">
          Current Affairs Intelligence
        </h3>
        <button
          onClick={() => navigate('/current-affairs')}
          className="text-xs font-semibold text-slate-500 hover:text-[#0B1628] flex items-center gap-1 transition-colors cursor-pointer"
        >
          <span>View All</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* ITEMS LIST */}
      <div className="space-y-3">
        {loading ? (
          <div className="p-4 text-center text-slate-400 text-xs font-medium">
            Loading latest current affairs...
          </div>
        ) : articles.length > 0 ? (
          articles.slice(0, 4).map((item, idx) => (
            <motion.div
              key={item.id || idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: idx * 0.07 }}
              onClick={() => navigate('/current-affairs')}
              className="flex items-center justify-between p-3 rounded-xl border border-slate-100 hover:border-amber-200/80 hover:bg-amber-500/5 transition-all duration-200 cursor-pointer group"
            >
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-9 h-9 rounded-lg bg-amber-50 border border-amber-200/60 text-amber-700 flex items-center justify-center shrink-0">
                  <Newspaper className="w-4 h-4" />
                </div>

                <div className="min-w-0">
                  <h4 className="text-xs sm:text-sm font-bold text-[#0B1628] group-hover:text-amber-600 transition-colors truncate">
                    {item.title}
                  </h4>
                  <p className="text-[11px] font-medium text-slate-400 mt-0.5 truncate">
                    {item.category} · <span className="text-slate-500">{item.source_name || 'UPSC News'}</span>
                  </p>
                </div>
              </div>

              <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-[#0B1628] group-hover:translate-x-1 transition-all shrink-0 ml-2" />
            </motion.div>
          ))
        ) : (
          <div className="p-4 text-center border border-dashed border-slate-200 rounded-xl text-xs text-slate-500 font-medium">
            No current affairs articles found.
          </div>
        )}
      </div>
    </div>
  );
}
