import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, ChevronDown, Quote } from 'lucide-react';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import CurrentAffairsHeader from '../components/currentAffairs/CurrentAffairsHeader';
import CategoryFilters from '../components/currentAffairs/CategoryFilters';
import FeaturedCurrentAffair from '../components/currentAffairs/FeaturedCurrentAffair';
import TodayHighlightsCard from '../components/currentAffairs/TodayHighlightsCard';
import CurrentAffairCard from '../components/currentAffairs/CurrentAffairCard';
import UpscFocusAreasCard from '../components/currentAffairs/UpscFocusAreasCard';
import CurrentAffairDetailModal from '../components/currentAffairs/CurrentAffairDetailModal';
import { currentAffairsList, featuredAffair } from '../data/currentAffairsData';

export default function CurrentAffairsPage() {
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [articles, setArticles] = useState(currentAffairsList);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [sortBy, setSortBy] = useState('latest');

  // INTERACTIVE BOOKMARK TOGGLE
  const handleToggleBookmark = (id) => {
    setArticles(prev => prev.map(art => 
      art.id === id ? { ...art, isBookmarked: !art.isBookmarked } : art
    ));
    if (selectedArticle && selectedArticle.id === id) {
      setSelectedArticle(prev => ({ ...prev, isBookmarked: !prev.isBookmarked }));
    }
  };

  // FILTERED ARTICLES BY CATEGORY & SEARCH
  const filteredArticles = useMemo(() => {
    return articles.filter(art => {
      const matchesCategory = activeCategory === 'all' || art.category === activeCategory;
      const matchesSearch = !searchQuery.trim() || 
        art.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        art.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
        art.categoryLabel.toLowerCase().includes(searchQuery.toLowerCase()) ||
        art.subcategory.toLowerCase().includes(searchQuery.toLowerCase());

      return matchesCategory && matchesSearch;
    });
  }, [articles, activeCategory, searchQuery]);

  return (
    <DashboardLayout>
      <div className="space-y-8">
        
        {/* HEADER BANNER */}
        <CurrentAffairsHeader />

        {/* CATEGORY FILTER TABS */}
        <CategoryFilters 
          activeCategory={activeCategory} 
          onSelectCategory={(catId) => setActiveCategory(catId)}
        />

        {/* MAIN 2-COLUMN GRID */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* LEFT COLUMN (8 cols on desktop) */}
          <div className="lg:col-span-8 space-y-8">
            
            {/* FEATURED CURRENT AFFAIR CARD */}
            <FeaturedCurrentAffair 
              onOpenDetail={(item) => setSelectedArticle(item)}
            />

            {/* LATEST CURRENT AFFAIRS SECTION */}
            <div className="space-y-5">
              
              {/* SECTION TITLE & SORT DROPDOWN */}
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold text-[#0B1628] tracking-tight">
                  Latest Current Affairs
                </h2>

                <div className="flex items-center gap-3">
                  <div className="relative hidden sm:block">
                    <input
                      type="text"
                      placeholder="Search topics..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-48 bg-white border border-slate-200/80 rounded-full pl-8 pr-3 py-1.5 text-xs font-semibold text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:border-[#0B1628]"
                    />
                    <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
                  </div>

                  <div className="relative">
                    <button className="bg-white border border-slate-200/80 px-3 py-1.5 rounded-xl text-xs font-bold text-slate-700 flex items-center gap-1.5 shadow-2xs hover:border-slate-300">
                      <span>Sort by: {sortBy === 'latest' ? 'Latest' : 'Bookmarked'}</span>
                      <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                    </button>
                  </div>
                </div>
              </div>

              {/* GRID OF CARDS */}
              {filteredArticles.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                  {filteredArticles.map((art) => (
                    <CurrentAffairCard
                      key={art.id}
                      item={art}
                      onOpenDetail={(item) => setSelectedArticle(item)}
                      onToggleBookmark={handleToggleBookmark}
                    />
                  ))}
                </div>
              ) : (
                <div className="bg-white rounded-2xl p-8 border border-slate-200 text-center space-y-2">
                  <p className="text-sm font-bold text-[#0B1628]">No topics found in this category.</p>
                  <p className="text-xs text-slate-500">Try selecting "All Topics" or adjusting your search query.</p>
                  <button
                    onClick={() => { setActiveCategory('all'); setSearchQuery(''); }}
                    className="mt-2 text-xs font-bold text-amber-600 hover:underline"
                  >
                    Reset Filters
                  </button>
                </div>
              )}

            </div>

          </div>

          {/* RIGHT SIDEBAR COLUMN (4 cols on desktop) */}
          <div className="lg:col-span-4 space-y-6">
            
            {/* TODAY'S HIGHLIGHTS WIDGET */}
            <TodayHighlightsCard 
              onSelectHighlight={(targetId) => {
                const found = articles.find(a => a.id === targetId) || featuredAffair;
                setSelectedArticle(found);
              }}
            />

            {/* UPSC FOCUS AREAS WIDGET */}
            <UpscFocusAreasCard 
              onSelectPaper={(paper) => {
                setSearchQuery(paper);
              }}
            />

            {/* BOTTOM MOTIVATIONAL QUOTE CARD */}
            <div className="bg-gradient-to-br from-amber-500/10 via-amber-100/30 to-slate-100/80 rounded-2xl p-5 border border-amber-200/60 shadow-2xs space-y-3 relative overflow-hidden">
              <Quote className="w-6 h-6 text-amber-600 opacity-60" />
              <p className="text-xs font-bold italic text-slate-800 leading-relaxed font-serif">
                “Current affairs are not just events, but opportunities to think deeply about the world you want to serve.”
              </p>
              <div className="w-8 h-1 bg-amber-500 rounded-full" />
            </div>

          </div>

        </div>

        {/* CURRENT AFFAIR DETAIL MODAL */}
        <AnimatePresence>
          {selectedArticle && (
            <CurrentAffairDetailModal
              article={selectedArticle}
              onClose={() => setSelectedArticle(null)}
              onToggleBookmark={handleToggleBookmark}
            />
          )}
        </AnimatePresence>

      </div>
    </DashboardLayout>
  );
}
