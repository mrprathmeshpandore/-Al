import React, { useState } from 'react';
import { Search, SlidersHorizontal, X } from 'lucide-react';
import { qbCategories, qbDifficulties, qbTypes } from '../../data/questionBankData';

export default function QuestionBankFilterPanel({
  searchQuery,
  onSearchChange,
  selectedCategory,
  onCategoryChange,
  selectedDifficulty,
  onDifficultyChange,
  selectedType,
  onTypeChange,
  onResetFilters
}) {
  const [showFilters, setShowFilters] = useState(true);

  return (
    <div className="bg-white rounded-2xl p-5 sm:p-6 border border-slate-200/80 shadow-2xs space-y-5">
      
      {/* SEARCH BAR & FILTERS TOGGLE BUTTON */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search questions, topics, or keywords..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full bg-slate-50/70 border border-slate-200/80 rounded-xl pl-10 pr-4 py-2.5 text-xs font-semibold text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#0B1628]/20 focus:bg-white transition-all"
          />
          {searchQuery && (
            <button
              onClick={() => onSearchChange('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`px-4 py-2.5 rounded-xl text-xs font-bold border flex items-center gap-2 transition-all cursor-pointer ${
            showFilters 
              ? 'bg-[#0B1628] text-white border-[#0B1628] shadow-2xs' 
              : 'bg-white hover:bg-slate-50 text-slate-700 border-slate-200'
          }`}
        >
          <SlidersHorizontal className="w-4 h-4" />
          <span>Filters</span>
        </button>
      </div>

      {/* EXPANDABLE FILTERS SECTION */}
      {showFilters && (
        <div className="space-y-4 pt-2 border-t border-slate-100 font-sans">
          
          {/* CATEGORIES */}
          <div className="space-y-2">
            <label className="text-xs font-bold text-slate-700 block">
              Categories
            </label>
            <div className="flex flex-wrap items-center gap-2">
              {qbCategories.map((cat) => {
                const isActive = selectedCategory === cat.id;
                return (
                  <button
                    key={cat.id}
                    onClick={() => onCategoryChange(cat.id)}
                    className={`px-3 py-1.5 rounded-full text-xs font-bold transition-all cursor-pointer ${
                      isActive 
                        ? 'bg-[#0B1628] text-white shadow-2xs scale-102' 
                        : 'bg-slate-100 hover:bg-slate-200/70 text-slate-600'
                    }`}
                  >
                    {cat.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* DIFFICULTY & QUESTION TYPE ROW */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t border-slate-100">
            
            {/* DIFFICULTY LEVEL */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-700 block">
                Difficulty Level
              </label>
              <div className="flex items-center gap-2 flex-wrap">
                {qbDifficulties.map((diff) => {
                  const isActive = selectedDifficulty === diff.id;
                  return (
                    <button
                      key={diff.id}
                      onClick={() => onDifficultyChange(diff.id)}
                      className={`px-3.5 py-1.5 rounded-full text-xs font-bold border transition-all cursor-pointer ${
                        isActive 
                          ? 'bg-[#0B1628] text-white border-[#0B1628]' 
                          : 'bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-200'
                      }`}
                    >
                      {diff.label}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* QUESTION TYPE */}
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-700 block">
                Question Type
              </label>
              <div className="flex items-center gap-2 flex-wrap">
                {qbTypes.map((type) => {
                  const isActive = selectedType === type.id;
                  return (
                    <button
                      key={type.id}
                      onClick={() => onTypeChange(type.id)}
                      className={`px-3.5 py-1.5 rounded-full text-xs font-bold border transition-all cursor-pointer ${
                        isActive 
                          ? 'bg-[#0B1628] text-white border-[#0B1628]' 
                          : 'bg-slate-50 hover:bg-slate-100 text-slate-700 border-slate-200'
                      }`}
                    >
                      {type.label}
                    </button>
                  );
                })}
              </div>
            </div>

          </div>

          {/* RESET FILTERS LINK */}
          {(selectedCategory !== 'all' || selectedDifficulty !== 'all' || selectedType !== 'all' || searchQuery) && (
            <div className="pt-2 flex justify-end">
              <button
                onClick={onResetFilters}
                className="text-xs font-bold text-amber-600 hover:text-amber-700 hover:underline cursor-pointer"
              >
                Reset All Filters
              </button>
            </div>
          )}

        </div>
      )}

    </div>
  );
}
