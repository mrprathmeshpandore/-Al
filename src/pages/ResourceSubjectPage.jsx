import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, Search, Bookmark, ArrowRight, FileText, CheckCircle2 } from 'lucide-react';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import ResourceDetailModal from '../components/resources/ResourceDetailModal';
import { subjects, mockDetailedResources, savedResourcesList } from '../data/resourcesData';

export default function ResourceSubjectPage() {
  const { subjectSlug } = useParams();
  const navigate = useNavigate();

  const [subFilter, setSubFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedResource, setSelectedResource] = useState(null);
  const [savedIds, setSavedIds] = useState(savedResourcesList.map(i => i.id));

  const currentSubject = subjects.find(s => s.slug === subjectSlug) || {
    name: subjectSlug ? subjectSlug.charAt(0).toUpperCase() + subjectSlug.slice(1).replace('-', ' ') : 'Subject Details',
    slug: subjectSlug || 'all',
    count: 30
  };

  const subFilterOptions = ['All', 'PDF', 'Notes', 'PYQs', 'Articles', 'Videos', 'Guides'];

  const handleToggleBookmark = (id) => {
    if (savedIds.includes(id)) {
      setSavedIds(savedIds.filter(i => i !== id));
    } else {
      setSavedIds([...savedIds, id]);
    }
  };

  // Filter items
  const filteredItems = mockDetailedResources.filter(item => {
    const matchesSubject = item.subject.toLowerCase().includes(currentSubject.name.toLowerCase()) || currentSubject.slug === 'all';
    const matchesFilter = subFilter === 'All' || item.type.toLowerCase() === subFilter.toLowerCase();
    const matchesSearch = searchQuery === '' || item.title.toLowerCase().includes(searchQuery.toLowerCase()) || item.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSubject && matchesFilter && matchesSearch;
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
                {currentSubject.name} Resources
              </h1>
              <p className="text-xs lg:text-sm text-slate-500 font-sans mt-1">
                Explore curated study material, notes, previous year questions, and interview frameworks for {currentSubject.name}.
              </p>
            </div>

            <div className="relative w-full md:w-72">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={`Search inside ${currentSubject.name}...`}
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
                className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-colors ${
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

        {/* Resources Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {(filteredItems.length > 0 ? filteredItems : mockDetailedResources).map((item, idx) => {
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
                        {item.type}
                      </span>
                      <span className="text-[11px] text-slate-400 font-mono">{item.fileSize}</span>
                    </div>

                    <button
                      onClick={() => handleToggleBookmark(item.id)}
                      className="p-1.5 text-slate-400 hover:text-amber-600 hover:bg-amber-50 rounded-lg transition-colors"
                    >
                      <Bookmark className={`w-4 h-4 ${isBookmarked ? 'fill-amber-500 text-amber-500' : ''}`} />
                    </button>
                  </div>

                  <h3 className="font-serif font-bold text-slate-900 text-sm mb-1.5 group-hover:text-amber-900 transition-colors">
                    {item.title}
                  </h3>

                  <p className="text-xs text-slate-500 font-sans line-clamp-3 leading-relaxed mb-4">
                    {item.description}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                  <button
                    onClick={() => setSelectedResource(item)}
                    className="flex items-center gap-1 text-xs font-bold text-[#0B1628] hover:text-amber-700 transition-colors"
                  >
                    <span>Open Resource</span>
                    <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" />
                  </button>

                  <span className="text-[10px] text-slate-400 font-sans">{item.duration}</span>
                </div>
              </motion.div>
            );
          })}
        </div>

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
