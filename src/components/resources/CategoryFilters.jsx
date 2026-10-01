import React from 'react';

export default function CategoryFilters({ activeCategory, setActiveCategory, categories = [] }) {
  // Built-in standard category tabs if backend categories list is loading/populating
  const displayCategories = categories.length > 0 
    ? [{ id: 'all', label: 'All' }, ...categories.map(c => ({ id: c.category.toLowerCase(), label: c.category, count: c.resource_count }))]
    : [
        { id: 'all', label: 'All' },
        { id: 'syllabus & guidance', label: 'Syllabus & Guidance' },
        { id: 'general studies', label: 'General Studies' },
        { id: 'interview & daf', label: 'Interview & DAF' }
      ];

  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
      {displayCategories.map((cat) => {
        const isActive = activeCategory.toLowerCase() === cat.id.toLowerCase();
        return (
          <button
            key={cat.id}
            onClick={() => setActiveCategory(cat.id)}
            className={`
              px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all duration-200 shadow-2xs border cursor-pointer
              ${isActive
                ? 'bg-[#0B1628] text-white border-[#0B1628] shadow-md'
                : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50 hover:border-slate-300'
              }
            `}
          >
            {cat.label} {cat.count !== undefined && `(${cat.count})`}
          </button>
        );
      })}
    </div>
  );
}
