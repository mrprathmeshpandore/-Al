import React, { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import ResourcesHeader from '../components/resources/ResourcesHeader';
import CategoryFilters from '../components/resources/CategoryFilters';
import UpscEssentialsSection from '../components/resources/UpscEssentialsSection';
import LearnPracticeCard from '../components/resources/LearnPracticeCard';
import StudyMaterialSection from '../components/resources/StudyMaterialSection';
import InterviewResourcesSection from '../components/resources/InterviewResourcesSection';
import SavedResourcesCard from '../components/resources/SavedResourcesCard';
import ResourceDetailModal from '../components/resources/ResourceDetailModal';
import PdfUploadModal from '../components/resources/PdfUploadModal';
import { resourcesApi } from '../services/resourcesApi';
import { AlertCircle, RefreshCw } from 'lucide-react';

export default function ResourcesPage() {
  const [activeCategory, setActiveCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedResource, setSelectedResource] = useState(null);
  
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [apiResources, setApiResources] = useState([]);
  const [categorySummaries, setCategorySummaries] = useState([]);
  const [subjectSummaries, setSubjectSummaries] = useState([]);
  const [bookmarkedResources, setBookmarkedResources] = useState([]);
  
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Parallel API calls to backend endpoints
      const params = {};
      if (activeCategory && activeCategory.toLowerCase() !== 'all') {
        params.category = activeCategory;
      }
      if (searchQuery.trim()) {
        params.search = searchQuery.trim();
      }

      const [resourcesData, categoriesData, subjectsData, bookmarksData] = await Promise.all([
        resourcesApi.getResources(params).catch(() => []),
        resourcesApi.getCategories().catch(() => []),
        resourcesApi.getSubjects().catch(() => []),
        resourcesApi.getBookmarkedResources().catch(() => [])
      ]);

      setApiResources(resourcesData || []);
      setCategorySummaries(categoriesData || []);
      setSubjectSummaries(subjectsData || []);
      setBookmarkedResources(bookmarksData || []);
    } catch (err) {
      console.error("Error loading resources from backend API:", err);
      setError(err.message || "Failed to load resources from backend API.");
    } finally {
      setIsLoading(false);
    }
  }, [activeCategory, searchQuery]);

  useEffect(() => {
    const timer = setTimeout(() => {
      loadData();
    }, 200);
    return () => clearTimeout(timer);
  }, [loadData]);

  const savedIds = bookmarkedResources.map((b) => b.id);

  const handleToggleBookmark = async (resourceId) => {
    try {
      if (savedIds.includes(resourceId)) {
        await resourcesApi.removeBookmark(resourceId);
        setBookmarkedResources((prev) => prev.filter((b) => b.id !== resourceId));
      } else {
        await resourcesApi.addBookmark(resourceId);
        // Refresh bookmarks list
        const updatedBookmarks = await resourcesApi.getBookmarkedResources().catch(() => []);
        setBookmarkedResources(updatedBookmarks);
      }
    } catch (err) {
      console.error("Error toggling bookmark:", err);
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6 pb-12">
        {/* Header */}
        <ResourcesHeader
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          onOpenUploadModal={() => setIsUploadModalOpen(true)}
        />

        {/* Category Filter Horizontal Tabs */}
        <CategoryFilters
          activeCategory={activeCategory}
          setActiveCategory={setActiveCategory}
          categories={categorySummaries}
        />

        {/* Error Banner */}
        {error && (
          <div className="p-4 rounded-2xl bg-red-50 border border-red-200 text-red-700 text-xs font-sans flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
              <span>{error}</span>
            </div>
            <button
              onClick={loadData}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-red-100 hover:bg-red-200 font-bold transition-colors cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Retry</span>
            </button>
          </div>
        )}

        {/* Main Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content Column (Left 2 cols) */}
          <div className="lg:col-span-2 space-y-8">
            {/* UPSC Essentials Section (Built-in Official Resources) */}
            <UpscEssentialsSection
              onOpenResource={setSelectedResource}
              onToggleBookmark={handleToggleBookmark}
              savedIds={savedIds}
              resources={apiResources.filter((r) => r.is_official || r.category?.toLowerCase().includes('syllabus'))}
              isLoading={isLoading}
            />

            {/* Study Material Subject Grid (Backend Subject Counts) */}
            <StudyMaterialSection subjectCounts={subjectSummaries} />

            {/* Interview Resources Section */}
            <InterviewResourcesSection
              onOpenResource={setSelectedResource}
              resources={apiResources}
              isLoading={isLoading}
            />
          </div>

          {/* Right Column (Saved Resources & Learn to Practice) */}
          <div className="space-y-6">
            {/* Learn -> Practice Workflow Card */}
            <LearnPracticeCard onUploadSuccess={loadData} />

            {/* Saved Resources Card */}
            <SavedResourcesCard
              bookmarkedResources={bookmarkedResources}
              onToggleBookmark={handleToggleBookmark}
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

        {/* Optional Personal PDF Upload Modal */}
        <PdfUploadModal
          isOpen={isUploadModalOpen}
          onClose={() => setIsUploadModalOpen(false)}
          onUploadSuccess={() => {
            loadData();
          }}
        />
      </div>
    </DashboardLayout>
  );
}
