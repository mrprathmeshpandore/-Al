import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { ChevronDown } from 'lucide-react';
import { performanceData } from '../../data/progressData';

export default function PerformanceChartCard() {
  const [selectedTimeframe, setSelectedTimeframe] = useState(performanceData.selectedTimeframe);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const points = performanceData.points;
  const maxScore = 100;

  // Chart dimensions & scaling
  const width = 500;
  const height = 200;
  const paddingX = 40;
  const paddingY = 20;

  const chartWidth = width - paddingX * 2;
  const chartHeight = height - paddingY * 2;

  // Compute SVG coordinates for data points
  const coords = points.map((pt, index) => {
    const x = paddingX + (index / (points.length - 1)) * chartWidth;
    const y = height - paddingY - (pt.score / maxScore) * chartHeight;
    return { x, y, score: pt.score, label: pt.label };
  });

  // Construct SVG path string for smooth line / linear line
  const pathD = coords.reduce((acc, curr, idx) => {
    return idx === 0 ? `M ${curr.x} ${curr.y}` : `${acc} L ${curr.x} ${curr.y}`;
  }, '');

  // Gradient area path
  const areaD = `${pathD} L ${coords[coords.length - 1].x} ${height - paddingY} L ${coords[0].x} ${height - paddingY} Z`;

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
      className="bg-white rounded-2xl p-6 border border-amber-950/5 shadow-sm flex flex-col justify-between"
    >
      {/* Header with Title and Dropdown */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-serif font-bold text-slate-900 text-lg">Performance Over Time</h3>
          <p className="text-xs text-slate-500 font-sans">Overall average score progression across evaluations</p>
        </div>

        <div className="relative">
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 text-xs font-medium text-slate-700 bg-slate-50/50 hover:bg-slate-100 transition-colors"
          >
            {selectedTimeframe}
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {dropdownOpen && (
            <div className="absolute right-0 mt-1 w-36 bg-white border border-slate-200 rounded-xl shadow-lg py-1 z-20">
              {performanceData.timeframeOptions.map((option) => (
                <button
                  key={option}
                  onClick={() => {
                    setSelectedTimeframe(option);
                    setDropdownOpen(false);
                  }}
                  className={`w-full text-left px-3 py-1.5 text-xs ${
                    selectedTimeframe === option
                      ? 'bg-amber-50 text-amber-900 font-semibold'
                      : 'text-slate-600 hover:bg-slate-50'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Line Chart Section */}
      <div className="relative w-full pt-2">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto overflow-visible">
          <defs>
            <linearGradient id="performanceGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#2563eb" stopOpacity="0.2" />
              <stop offset="100%" stopColor="#2563eb" stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          {[0, 20, 40, 60, 80, 100].map((val) => {
            const y = height - paddingY - (val / maxScore) * chartHeight;
            return (
              <g key={val}>
                <line
                  x1={paddingX}
                  y1={y}
                  x2={width - paddingX}
                  y2={y}
                  stroke="#f1f5f9"
                  strokeWidth="1"
                  strokeDasharray={val === 0 || val === 100 ? "0" : "3 3"}
                />
                <text x={paddingX - 10} y={y + 3} textAnchor="end" className="text-[10px] fill-slate-400 font-sans">
                  {val}
                </text>
              </g>
            );
          })}

          {/* Area fill */}
          <path d={areaD} fill="url(#performanceGradient)" />

          {/* Main Trend Line */}
          <motion.path
            d={pathD}
            fill="none"
            stroke="#2563eb"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1.2, ease: "easeOut" }}
          />

          {/* Data Points and Callout */}
          {coords.map((pt, idx) => {
            const isLast = idx === coords.length - 1;
            return (
              <g key={idx}>
                {/* Point circle */}
                <circle
                  cx={pt.x}
                  cy={pt.y}
                  r={isLast ? "5" : "4"}
                  fill={isLast ? "#1d4ed8" : "#3b82f6"}
                  stroke="#ffffff"
                  strokeWidth="2"
                  className="transition-all hover:r-6 cursor-pointer"
                />

                {/* X Axis Labels */}
                <text
                  x={pt.x}
                  y={height - 2}
                  textAnchor="middle"
                  className="text-[10px] fill-slate-500 font-medium font-sans"
                >
                  {pt.label}
                </text>

                {/* Callout Badge for latest score (Week 6 -> 78%) */}
                {isLast && (
                  <g transform={`translate(${pt.x - 18}, ${pt.y - 28})`}>
                    <rect
                      x="0"
                      y="0"
                      width="36"
                      height="20"
                      rx="4"
                      fill="#0b1628"
                      className="shadow-md"
                    />
                    <text
                      x="18"
                      y="13"
                      textAnchor="middle"
                      fill="#ffffff"
                      fontSize="10"
                      fontWeight="bold"
                      fontFamily="sans-serif"
                    >
                      {pt.score}%
                    </text>
                  </g>
                )}
              </g>
            );
          })}
        </svg>
      </div>
    </motion.div>
  );
}
