import React from 'react';
import { 
  LayoutGrid, 
  Building, 
  Globe, 
  TrendingUp, 
  Landmark, 
  Leaf, 
  Cpu, 
  Users 
} from 'lucide-react';
import { caCategories } from '../../data/currentAffairsData';

const iconMap = {
  layoutGrid: LayoutGrid,
  building: Building,
  globe: Globe,
  trendingUp: TrendingUp,
  landmark: Landmark,
  leaf: Leaf,
  cpu: Cpu,
  users: Users,
};

export default function CategoryFilters({ activeCategory, onSelectCategory }) {
  return (
    <div className="w-full overflow-x-auto custom-scrollbar pb-2 pt-1">
      <div className="flex items-center gap-2.5 min-w-max">
        {caCategories.map((cat) => {
          const IconComp = iconMap[cat.icon] || LayoutGrid;
          const isActive = activeCategory === cat.id;

          return (
            <button
              key={cat.id}
              onClick={() => onSelectCategory(cat.id)}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold transition-all duration-200 cursor-pointer shrink-0
                ${isActive 
                  ? 'bg-[#0B1628] text-white shadow-md shadow-slate-900/10 scale-102' 
                  : 'bg-white hover:bg-slate-50 text-slate-700 border border-slate-200/80 hover:border-slate-300 shadow-2xs'
                }
              `}
            >
              <IconComp className={`w-3.5 h-3.5 ${isActive ? 'text-amber-400' : 'text-slate-500'}`} />
              <span>{cat.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
