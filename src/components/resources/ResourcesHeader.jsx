import React from 'react';
import { Search, Bell, Upload } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export default function ResourcesHeader({ searchQuery, setSearchQuery, onOpenUploadModal }) {
  const { user } = useAuth();
  const userName = user?.full_name || 'UPSC Aspirant';
  const userInitials = userName.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || 'UA';

  return (
    <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 pb-2 border-b border-slate-200/60">
      <div>
        <span className="text-[11px] font-bold tracking-widest uppercase text-amber-700 font-sans block mb-1">
          BUILT-IN UPSC KNOWLEDGE BASE
        </span>
        <h1 className="font-serif text-2xl lg:text-3xl font-extrabold text-[#0B1628] tracking-tight">
          Your UPSC Knowledge Hub
        </h1>
        <p className="text-xs lg:text-sm text-slate-600 font-sans mt-1 max-w-2xl leading-relaxed">
          Access built-in official UPSC resources, study materials, and guides — no PDF upload required.
        </p>
      </div>

      {/* Right Header Controls */}
      <div className="flex flex-wrap items-center gap-3 w-full lg:w-auto justify-between lg:justify-end">
        {/* Search Bar */}
        <div className="relative flex-1 lg:w-64">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search resources..."
            className="w-full pl-9 pr-4 py-2 text-xs bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500/50 shadow-2xs font-sans transition-all"
          />
        </div>

        {/* Upload Personal Material CTA */}
        {onOpenUploadModal && (
          <button
            onClick={onOpenUploadModal}
            className="flex items-center gap-2 px-3.5 py-2 text-xs font-bold text-white bg-[#0B1628] hover:bg-amber-900 rounded-xl shadow-2xs transition-all cursor-pointer whitespace-nowrap"
          >
            <Upload className="w-3.5 h-3.5 text-amber-400" />
            <span>Add Personal Material</span>
          </button>
        )}

        {/* Notifications & Dynamic Profile Badge */}
        <div className="flex items-center gap-2">
          <button className="p-2 rounded-xl bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 transition-colors relative shadow-2xs">
            <Bell className="w-4 h-4" />
            <span className="w-2 h-2 rounded-full bg-amber-500 absolute top-1.5 right-1.5 ring-2 ring-white" />
          </button>

          <div
            title={userName}
            className="w-9 h-9 rounded-full bg-[#0B1628] text-amber-400 border border-amber-500/40 font-serif font-bold text-xs flex items-center justify-center ring-2 ring-amber-500/20 cursor-pointer shadow-2xs"
          >
            {userInitials}
          </div>
        </div>
      </div>
    </div>
  );
}
