import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Search, Bookmark, ArrowRight, FileText, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import ResourceDetailModal from '../components/resources/ResourceDetailModal';
import { resourcesApi } from '../services/resourcesApi';

const slugToSubjectNameMap = {
  'polity': 'Polity',
  'governance': 'Governance',
  'economy': 'Economy',
  'history': 'History',
  'geography': 'Geography',
  'environment': 'Environment',
  'ethics': 'Ethics',
  'science-technology': 'Science & Tech',
  'international-relations': 'International Relations',
  'society': 'Society'
};

export default function ResourceSubjectPage() {
  const { subjectSlug } = useParams();
  const navigate = useNavigate();

  const [subFilter, setSubFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedResource, setSelectedResource] = useState(null);
  
  const [subjectResources, setSubjectResources] = useState([]);
  const [bookmarkedResources, setBookmarkedResources] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const subjectName = slugToSubjectNameMap[subjectSlug] || 
    (subjectSlug ? subjectSlug.charAt(0).toUpperCase() + subjectSlug.slice(1).replace('-', ' ') : 'General Studies');

  const subFilterOptions = ['All', 'PDF', 'Notes', 'PYQs', 'Articles', 'Guides'];

  const loadSubjectData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [allRes, bookmarks] = await Promise.all([
        resourcesApi.getResources({ subject: subjectName }),
        resourcesApi.getBookmarkedResources().catch(() => [])
      ]);

      setSubjectResources(allRes || []);
      setBookmarkedResources(bookmarks || []);
    } catch (err) {
      console.error("Error loading subject resources:", err);
      setError(err.message || "Failed to load resources for this subject.");
    } finally {
      setIsLoading(false);
    }
  }, [subjectName]);

  useEffect(() => {
    loadSubjectData();
  }, [loadSubjectData]);

  const savedIds = bookmarkedResources.map(b => b.id);

  const handleToggleBookmark = async (resourceId) => {
    try {
      if (savedIds.includes(resourceId)) {
        await resourcesApi.removeBookmark(resourceId);
        setBookmarkedResources(prev => prev.filter(b => b.id !== resourceId));
      } else {
        await resourcesApi.addBookmark(resourceId);
        const updatedBookmarks = await resourcesApi.getBookmarkedResources().catch(() => []);
        setBookmarkedResources(updatedBookmarks);
      }
    } catch (err) {
      console.error("Error toggling bookmark:", err);
    }
  };

  // Filter items based on subFilter and searchQuery
  const filteredItems = subjectResources.filter(item => {
    const matchesFilter = subFilter === 'All' || 
      (item.resource_type && item.resource_type.toLowerCase() === subFilter.toLowerCase()) ||
      (item.category && item.category.toLowerCase().includes(subFilter.toLowerCase()));
    const matchesSearch = searchQuery === '' || 
      item.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
      (item.description && item.description.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesFilter && matchesSearch;
  });

  return (
    <DashboardLayout>
      <div className="space-y-6 pb-12">
        {/* Top Back Navigation */}
        <div className="flex items-center justify-between">
          <Link
            to="/resources"
            className="flex items-center gap-2 text-xs font-bold text-slate-600 hover:text-amber-800 transition-colors group"
          >
            <ArrowLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
            <span>Back to All Resources</span>
          </Link>
        </div>

        {/* Subject Header Banner */}
        <div className="bg-white rounded-3xl p-6 lg:p-8 border border-amber-950/5 shadow-sm space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <span className="px-3 py-1 rounded-xl bg-amber-50 text-amber-800 text-xs font-bold border border-amber-200">
                SUBJECT HUB
              </span>
              <h1 className="font-serif font-extrabold text-2xl lg:text-3xl text-[#0B1628] mt-2">
                {subjectName} Resources
              </h1>
              <p className="text-xs lg:text-sm text-slate-500 font-sans mt-1">
                Explore built-in official resources and study material for {subjectName}.
              </p>
            </div>

            <div className="relative w-full md:w-72">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={`Search inside ${subjectName}...`}
                className="w-full pl-9 pr-4 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500/50"
              />
            </div>
          </div>

          {/* Sub-filters */}
          <div className="flex items-center gap-2 overflow-x-auto pt-2 border-t border-slate-100 scrollbar-none">
            {subFilterOptions.map((opt) => (
              <button
                key={opt}
                onClick={() => setSubFilter(opt)}
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-colors cursor-pointer ${
                  subFilter === opt
                    ? 'bg-[#0B1628] text-white shadow-2xs'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {opt}
              </button>
            ))}
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="p-4 rounded-2xl bg-red-50 border border-red-200 text-red-700 text-xs font-sans flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
              <span>{error}</span>
            </div>
            <button
              onClick={loadSubjectData}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-red-100 hover:bg-red-200 font-bold transition-colors cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry</span>
            </button>
          </div>
        )}

        {/* Loading Skeleton */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((n) => (
              <div key={n} className="bg-white rounded-2xl p-5 border border-slate-100 animate-pulse h-48 space-y-3">
                <div className="h-4 bg-slate-100 rounded w-1/3" />
                <div className="h-5 bg-slate-100 rounded w-3/4" />
                <div className="h-12 bg-slate-100 rounded w-full" />
              </div>
            ))}
          </div>
        ) : filteredItems.length > 0 ? (
          /* Resources Grid */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredItems.map((item, idx) => {
              const isBookmarked = savedIds.includes(item.id);
              return (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 15 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: idx * 0.08 }}
                  className="bg-white rounded-2xl p-5 border border-amber-950/5 shadow-2xs hover:shadow-md transition-all flex flex-col justify-between group"
                >
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span className="px-2.5 py-0.5 rounded-md bg-amber-50 text-amber-700 font-bold text-[10px] border border-amber-200">
                          {item.resource_type ? item.resource_type.toUpperCase() : 'PDF'}
                        </span>
                        {item.is_official && (
                          <span className="flex items-center gap-1 text-[10px] text-emerald-600 font-medium">
                            <CheckCircle2 className="w-3 h-3" /> Official
                          </span>
                        )}
                      </div>

                      <button
                        onClick={() => handleToggleBookmark(item.id)}
                        className="p-1.5 text-slate-400 hover:text-amber-600 hover:bg-amber-50 rounded-lg transition-colors cursor-pointer"
                      >
                        <Bookmark className={`w-4 h-4 ${isBookmarked ? 'fill-amber-500 text-amber-500' : ''}`} />
                      </button>
                    </div>

                    <h3 className="font-serif font-bold text-slate-900 text-sm mb-1.5 group-hover:text-amber-900 transition-colors line-clamp-2">
                      {item.title}
                    </h3>

                    <p className="text-xs text-slate-500 font-sans line-clamp-3 leading-relaxed mb-4">
                      {item.description}
                    </p>
                  </div>

                  <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                    <button
                      onClick={() => setSelectedResource(item)}
                      className="flex items-center gap-1 text-xs font-bold text-[#0B1628] hover:text-amber-700 transition-colors cursor-pointer"
                    >
                      <span>Open Resource</span>
                      <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
                    </button>

                    <span className="text-[10px] text-slate-400 font-sans">{item.source || 'UPSC Official'}</span>
                  </div>
                </motion.div>
              );
            })}
          </div>
        ) : (
          /* Empty State */
          <div className="p-12 bg-white rounded-3xl border border-amber-950/5 text-center space-y-3">
            <FileText className="w-10 h-10 mx-auto text-slate-300 stroke-[1.5]" />
            <h3 className="font-serif font-bold text-slate-800 text-base">No resources found for {subjectName}</h3>
            <p className="text-xs text-slate-500 max-w-md mx-auto">
              There are currently no resources matching your filter inside {subjectName}. You can upload personal PDFs to add materials to this subject.
            </p>
          </div>
        )}

        {/* Modal */}
        <ResourceDetailModal
          resource={selectedResource}
          onClose={() => setSelectedResource(null)}
          onToggleBookmark={handleToggleBookmark}
          isBookmarked={selectedResource ? savedIds.includes(selectedResource.id) : false}
        />
      </div>
    </DashboardLayout>
  );
}
