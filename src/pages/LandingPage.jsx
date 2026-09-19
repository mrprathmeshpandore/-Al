import React from 'react';
import Navbar from '../components/Navbar';
import Hero from '../components/Hero';
import StatsSection from '../components/StatsSection';
import InterviewSection from '../components/InterviewSection';
import FooterBanner from '../components/FooterBanner';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#FBF9F5] text-[#1E293B] relative font-sans overflow-x-hidden">
      {/* Top Navbar */}
      <Navbar />

      {/* Main Content Sections */}
      <main className="space-y-4">
        {/* Cinematic Hero Section */}
        <Hero />

        {/* 5 Card Statistics Section */}
        <StatsSection />

        {/* AI Interview Simulation & Features Grid */}
        <InterviewSection />
      </main>

      {/* Bottom Quote & Civic Banner */}
      <FooterBanner />
    </div>
  );
}
