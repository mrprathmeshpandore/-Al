import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronLeft, ChevronRight, Quote } from 'lucide-react';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import QuestionBankHeader from '../components/questionBank/QuestionBankHeader';
import QuestionBankFilterPanel from '../components/questionBank/QuestionBankFilterPanel';
import QuestionCard from '../components/questionBank/QuestionCard';
import QuestionBankStatsCard from '../components/questionBank/QuestionBankStatsCard';
import PopularTopicsCard from '../components/questionBank/PopularTopicsCard';
import StartPracticingCtaCard from '../components/questionBank/StartPracticingCtaCard';
import QuestionDetailModal from '../components/questionBank/QuestionDetailModal';
import { questionsList, questionBankStats } from '../data/questionBankData';

export default function QuestionBankPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState('all');
  const [selectedType, setSelectedType] = useState('all');
  const [sortBy, setSortBy] = useState('latest');
  const [currentPage, setCurrentPage] = useState(1);
  const [questions, setQuestions] = useState(questionsList);
  const [selectedQuestion, setSelectedQuestion] = useState(null);

  // INTERACTIVE BOOKMARK TOGGLE
  const handleToggleBookmark = (id) => {
    setQuestions(prev => prev.map(q => 
      q.id === id ? { ...q, isBookmarked: !q.isBookmarked } : q
    ));
    if (selectedQuestion && selectedQuestion.id === id) {
      setSelectedQuestion(prev => ({ ...prev, isBookmarked: !prev.isBookmarked }));
    }
  };

  // MULTI-FILTER & SEARCH LOGIC
  const filteredQuestions = useMemo(() => {
    return questions.filter(q => {
      const matchesSearch = !searchQuery.trim() ||
        q.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
        q.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        q.tags?.some(t => t.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchesCategory = selectedCategory === 'all' || q.category === selectedCategory;
      const matchesDifficulty = selectedDifficulty === 'all' || q.difficulty.toLowerCase() === selectedDifficulty;
      const matchesType = selectedType === 'all' || q.qType === selectedType;

      return matchesSearch && matchesCategory && matchesDifficulty && matchesType;
    });
  }, [questions, searchQuery, selectedCategory, selectedDifficulty, selectedType]);

  const handleResetFilters = () => {
    setSearchQuery('');
    setSelectedCategory('all');
    setSelectedDifficulty('all');
    setSelectedType('all');
    setCurrentPage(1);
  };

  return (
    <DashboardLayout>
      <div className="space-y-8">
        
        {/* HEADER BANNER */}
        <QuestionBankHeader />

        {/* SEARCH & FILTER PANEL */}
        <QuestionBankFilterPanel
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          selectedCategory={selectedCategory}
          onCategoryChange={setSelectedCategory}
          selectedDifficulty={selectedDifficulty}
          onDifficultyChange={setSelectedDifficulty}
          selectedType={selectedType}
          onTypeChange={setSelectedType}
          onResetFilters={handleResetFilters}
        />

        {/* MAIN 2-COLUMN GRID */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* LEFT MAIN AREA (8 cols on desktop) */}
          <div className="lg:col-span-8 space-y-6">
            
            {/* STATUS HEADER & SORT DROPDOWN */}
            <div className="flex items-center justify-between pb-1">
              <span className="text-xs font-bold text-slate-600">
                Showing 1–{filteredQuestions.length} of {questionBankStats.totalQuestions} questions
              </span>

              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold text-slate-400 hidden sm:inline">Sort by:</span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="bg-white border border-slate-200/80 rounded-xl px-3 py-1.5 text-xs font-bold text-slate-700 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 shadow-2xs"
                >
                  <option value="latest">Latest</option>
                  <option value="practiced">Most Practiced</option>
                  <option value="saved">Most Saved</option>
                  <option value="difficulty">Difficulty</option>
                </select>
              </div>
            </div>

            {/* QUESTION CARDS LIST */}
            {filteredQuestions.length > 0 ? (
              <div className="space-y-4">
                {filteredQuestions.map((q) => (
                  <QuestionCard
                    key={q.id}
                    item={q}
                    onOpenDetail={(item) => setSelectedQuestion(item)}
                    onToggleBookmark={handleToggleBookmark}
                  />
                ))}
              </div>
            ) : (
              <div className="bg-white rounded-2xl p-8 border border-slate-200 text-center space-y-2">
                <p className="text-sm font-bold text-[#0B1628]">No questions found matching your filters.</p>
                <p className="text-xs text-slate-500">Try adjusting your category, difficulty, or search keywords.</p>
                <button
                  onClick={handleResetFilters}
                  className="mt-2 text-xs font-bold text-amber-600 hover:underline cursor-pointer"
                >
                  Reset All Filters
                </button>
              </div>
            )}

            {/* PAGINATION BAR */}
            <div className="pt-4 flex items-center justify-between border-t border-slate-200/60">
              <button
                disabled={currentPage === 1}
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                className="px-3.5 py-1.5 rounded-xl text-xs font-bold text-slate-600 hover:text-[#0B1628] border border-slate-200 bg-white disabled:opacity-40 cursor-pointer flex items-center gap-1"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>Prev</span>
              </button>

              <div className="flex items-center gap-1">
                {[1, 2, 3, 4, 5].map((pageNum) => (
                  <button
                    key={pageNum}
                    onClick={() => setCurrentPage(pageNum)}
                    className={`w-8 h-8 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                      currentPage === pageNum
                        ? 'bg-[#0B1628] text-white shadow-2xs'
                        : 'bg-white hover:bg-slate-100 text-slate-600 border border-slate-200'
                    }`}
                  >
                    {pageNum}
                  </button>
                ))}
              </div>

              <button
                onClick={() => setCurrentPage(p => p + 1)}
                className="px-3.5 py-1.5 rounded-xl text-xs font-bold text-slate-600 hover:text-[#0B1628] border border-slate-200 bg-white cursor-pointer flex items-center gap-1"
              >
                <span>Next</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>

          </div>

          {/* RIGHT SIDEBAR (4 cols on desktop) */}
          <div className="lg:col-span-4 space-y-6">
            
            {/* STATS CARD */}
            <QuestionBankStatsCard />

            {/* POPULAR TOPICS WIDGET */}
            <PopularTopicsCard
              onSelectTopic={(catId) => {
                setSelectedCategory(catId);
                window.scrollTo({ top: 300, behavior: 'smooth' });
              }}
            />

            {/* START PRACTICING CTA CARD */}
            <StartPracticingCtaCard />

            {/* MOTIVATIONAL QUOTE CARD */}
            <div className="bg-gradient-to-br from-amber-500/10 via-amber-100/30 to-slate-100/80 rounded-2xl p-5 border border-amber-200/60 shadow-2xs space-y-3 relative overflow-hidden">
              <Quote className="w-6 h-6 text-amber-600 opacity-60" />
              <p className="text-xs font-bold italic text-slate-800 leading-relaxed font-serif">
                “The right questions don't just test knowledge, they shape leadership.”
              </p>
              <div className="w-8 h-1 bg-amber-500 rounded-full" />
            </div>

          </div>

        </div>

        {/* QUESTION DETAIL MODAL */}
        <AnimatePresence>
          {selectedQuestion && (
            <QuestionDetailModal
              item={selectedQuestion}
              onClose={() => setSelectedQuestion(null)}
              onToggleBookmark={handleToggleBookmark}
            />
          )}
        </AnimatePresence>

      </div>
    </DashboardLayout>
  );
}
