import React from 'react';
import { resourceCategories } from '../../data/resourcesData';

export default function CategoryFilters({ activeCategory, setActiveCategory }) {
  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-none">
      {resourceCategories.map((cat) => {
        const isActive = activeCategory === cat.id;
        return (
          <button
            key={cat.id}
            onClick={() => setActiveCategory(cat.id)}
            className={`
              px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all duration-200 shadow-2xs border
              ${isActive
                ? 'bg-[#0B1628] text-white border-[#0B1628] shadow-md'
                : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50 hover:border-slate-300'
              }
            `}
          >
            {cat.label}
          </button>
        );
      })}
    </div>
  );
}
