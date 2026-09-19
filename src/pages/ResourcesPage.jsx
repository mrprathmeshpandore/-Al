import React, { useState } from 'react';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import ResourcesHeader from '../components/resources/ResourcesHeader';
import CategoryFilters from '../components/resources/CategoryFilters';
import UpscEssentialsSection from '../components/resources/UpscEssentialsSection';
import LearnPracticeCard from '../components/resources/LearnPracticeCard';
import StudyMaterialSection from '../components/resources/StudyMaterialSection';
import InterviewResourcesSection from '../components/resources/InterviewResourcesSection';
import SavedResourcesCard from '../components/resources/SavedResourcesCard';
import ResourceDetailModal from '../components/resources/ResourceDetailModal';
import { savedResourcesList } from '../data/resourcesData';

export default function ResourcesPage() {
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedResource, setSelectedResource] = useState(null);
  const [savedIds, setSavedIds] = useState(savedResourcesList.map(item => item.id));

  const handleToggleBookmark = (id) => {
    if (savedIds.includes(id)) {
      setSavedIds(savedIds.filter(item => item !== id));
    } else {
      setSavedIds([...savedIds, id]);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6 pb-12">
        {/* Page Header */}
        <ResourcesHeader searchQuery={searchQuery} setSearchQuery={setSearchQuery} />

        {/* Category Filter Horizontal Buttons */}
        <CategoryFilters activeCategory={activeCategory} setActiveCategory={setActiveCategory} />

        {/* Main Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content Column (Left 2 cols) */}
          <div className="lg:col-span-2 space-y-8">
            {/* UPSC Essentials Section */}
            <UpscEssentialsSection
              onOpenResource={setSelectedResource}
              onToggleBookmark={handleToggleBookmark}
              savedIds={savedIds}
            />

            {/* Study Material Subject Grid */}
            <StudyMaterialSection />

            {/* Interview Resources Section */}
            <InterviewResourcesSection
              onOpenResource={setSelectedResource}
            />
          </div>

          {/* Right Column (Saved Resources & Learn to Practice) */}
          <div className="space-y-6">
            {/* Learn -> Practice Workflow Card */}
            <LearnPracticeCard />

            {/* Saved Resources & Motto Card */}
            <SavedResourcesCard
              onToggleBookmark={handleToggleBookmark}
              savedIds={savedIds}
              onOpenResource={setSelectedResource}
            />
          </div>
        </div>

        {/* Resource Detail Modal */}
        <ResourceDetailModal
          resource={selectedResource}
          onClose={() => setSelectedResource(null)}
          onToggleBookmark={handleToggleBookmark}
          isBookmarked={selectedResource ? savedIds.includes(selectedResource.id) : false}
        />
      </div>
    </DashboardLayout>
  );
}
