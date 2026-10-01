import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronLeft, ChevronRight, Quote, Loader2 } from 'lucide-react';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import QuestionBankHeader from '../components/questionBank/QuestionBankHeader';
import QuestionBankFilterPanel from '../components/questionBank/QuestionBankFilterPanel';
import QuestionCard from '../components/questionBank/QuestionCard';
import QuestionBankStatsCard from '../components/questionBank/QuestionBankStatsCard';
import PopularTopicsCard from '../components/questionBank/PopularTopicsCard';
import StartPracticingCtaCard from '../components/questionBank/StartPracticingCtaCard';
import QuestionDetailModal from '../components/questionBank/QuestionDetailModal';
import { questionsApi } from '../services/questionsApi';

export default function QuestionBankPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState('all');
  const [selectedType, setSelectedType] = useState('all');
  const [sortBy, setSortBy] = useState('latest');
  const [currentPage, setCurrentPage] = useState(1);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedQuestion, setSelectedQuestion] = useState(null);

  useEffect(() => {
    async function fetchBackendQuestions() {
      try {
        setLoading(true);
        const data = await questionsApi.getQuestions({
          category: selectedCategory !== 'all' ? selectedCategory : undefined,
          difficulty: selectedDifficulty !== 'all' ? selectedDifficulty : undefined,
          question_type: selectedType !== 'all' ? selectedType : undefined,
        });
        if (Array.isArray(data)) {
          setQuestions(data.map(q => ({
            id: q.id,
            question: q.question_text,
            description: q.explanation || q.why_this_matters || 'Practice answering with structured administrative rationale.',
            category: q.category || q.subject || 'Polity & Governance',
            difficulty: q.difficulty ? q.difficulty.charAt(0) + q.difficulty.slice(1).toLowerCase() : 'Moderate',
            qType: q.question_type || 'MAIN',
            isBookmarked: false,
            tags: [q.subject || 'General Studies', q.topic || 'Governance'].filter(Boolean),
            whyMatters: q.why_this_matters,
            explanation: q.explanation,
          })));
        }
      } catch (err) {
        console.error('Failed to load questions:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchBackendQuestions();
  }, [selectedCategory, selectedDifficulty, selectedType]);

  // INTERACTIVE BOOKMARK TOGGLE
  const handleToggleBookmark = (id) => {
    setQuestions(prev => prev.map(q => 
      q.id === id ? { ...q, isBookmarked: !q.isBookmarked } : q
    ));
    if (selectedQuestion && selectedQuestion.id === id) {
      setSelectedQuestion(prev => ({ ...prev, isBookmarked: !prev.isBookmarked }));
    }
  };

  // SEARCH FILTERING
  const filteredQuestions = useMemo(() => {
    return questions.filter(q => {
      const matchesSearch = !searchQuery.trim() ||
        q.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
        q.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        q.tags?.some(t => t.toLowerCase().includes(searchQuery.toLowerCase()));

      return matchesSearch;
    });
  }, [questions, searchQuery]);

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
                Showing 1–{filteredQuestions.length} of {questions.length} questions
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
                  <option value="difficulty">Difficulty</option>
                </select>
              </div>
            </div>

            {/* QUESTION CARDS LIST */}
            {loading ? (
              <div className="p-12 text-center text-slate-500 font-semibold bg-white rounded-2xl border border-slate-200">
                <Loader2 className="w-8 h-8 animate-spin text-[#0B1628] mx-auto mb-2" />
                <p className="text-xs">Loading Question Bank from Backend...</p>
              </div>
            ) : filteredQuestions.length > 0 ? (
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
          </div>

          {/* RIGHT SIDEBAR (4 cols on desktop) */}
          <div className="lg:col-span-4 space-y-6">
            {/* STATS CARD */}
            <QuestionBankStatsCard totalCount={questions.length} />

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
