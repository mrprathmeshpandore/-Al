import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, ArrowRight, CheckCircle2 } from 'lucide-react';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import ProfileHeroHeader from '../components/profile/ProfileHeroHeader';
import ProfileStepper from '../components/profile/ProfileStepper';
import StepPersonal from '../components/profile/StepPersonal';
import StepEducation from '../components/profile/StepEducation';
import StepUPSCJourney from '../components/profile/StepUPSCJourney';
import StepInterests from '../components/profile/StepInterests';
import StepPerspective from '../components/profile/StepPerspective';
import ProfileCompletionCard from '../components/profile/ProfileCompletionCard';
import ProfilePreviewCard from '../components/profile/ProfilePreviewCard';
import StepsOverviewCard from '../components/profile/StepsOverviewCard';
import ProfileMotivationalBanner from '../components/profile/ProfileMotivationalBanner';
import { initialProfileData, profileSteps } from '../data/profileData';

export default function ProfilePage() {
  const [activeStep, setActiveStep] = useState(1);
  const [profileData, setProfileData] = useState(initialProfileData);
  const [errors, setErrors] = useState({});
  const [isSubmitted, setIsSubmitted] = useState(false);

  // DYNAMIC COMPLETION STATUS LOGIC
  const stepStatuses = useMemo(() => {
    const statuses = {};
    
    // Step 1: Personal
    const p = profileData.personal || {};
    if (p.fullName && p.dob && p.homeState && p.district && p.currentCity && p.gender) {
      statuses.personal = 'Completed';
    } else if (p.fullName || p.homeState) {
      statuses.personal = 'In Progress';
    } else {
      statuses.personal = 'Not Started';
    }

    // Step 2: Education
    const e = profileData.education || {};
    if (e.degree && e.university && e.specialization) {
      statuses.education = 'Completed';
    } else if (e.degree || e.university) {
      statuses.education = 'In Progress';
    } else {
      statuses.education = 'Not Started';
    }

    // Step 3: UPSC Journey
    const u = profileData.upscJourney || {};
    if (u.attemptCount && u.optionalSubject && u.preparationStage) {
      statuses.upscJourney = 'Completed';
    } else if (u.optionalSubject) {
      statuses.upscJourney = 'In Progress';
    } else {
      statuses.upscJourney = 'Not Started';
    }

    // Step 4: Interests
    const i = profileData.interests || {};
    if (i.hobbies) {
      statuses.interests = 'Completed';
    } else if (i.sports || i.readingBooks) {
      statuses.interests = 'In Progress';
    } else {
      statuses.interests = 'Not Started';
    }

    // Step 5: Perspective
    const pr = profileData.perspective || {};
    if (pr.whyCivilServices || pr.keyFocusAreas) {
      statuses.perspective = 'Completed';
    } else {
      statuses.perspective = 'Not Started';
    }

    return statuses;
  }, [profileData]);

  // CALCULATE OVERALL COMPLETION PERCENTAGE (20% per completed step)
  const completionPercentage = useMemo(() => {
    const completedCount = Object.values(stepStatuses).filter(s => s === 'Completed').length;
    return completedCount * 20;
  }, [stepStatuses]);

  // FORM INPUT CHANGE HANDLER
  const handleInputChange = (stepKey) => (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [stepKey]: {
        ...prev[stepKey],
        [name]: value
      }
    }));

    // Clear error for this field if present
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  // PHOTO UPLOAD HANDLER
  const handlePhotoUpload = (newPhotoUrl) => {
    setProfileData(prev => ({
      ...prev,
      personal: {
        ...prev.personal,
        photoUrl: newPhotoUrl
      }
    }));
  };

  // STEP VALIDATION
  const validateCurrentStep = () => {
    const currentErrors = {};

    if (activeStep === 1) {
      const p = profileData.personal || {};
      if (!p.fullName?.trim()) currentErrors.fullName = 'Full Name is required';
      if (!p.dob) currentErrors.dob = 'Date of birth is required';
      if (!p.homeState) currentErrors.homeState = 'Home state is required';
      if (!p.district) currentErrors.district = 'District is required';
      if (!p.currentCity?.trim()) currentErrors.currentCity = 'Current city is required';
      if (!p.gender) currentErrors.gender = 'Gender is required';
    } else if (activeStep === 2) {
      const e = profileData.education || {};
      if (!e.degree?.trim()) currentErrors.degree = 'Graduation degree is required';
      if (!e.university?.trim()) currentErrors.university = 'University / Institution is required';
      if (!e.specialization?.trim()) currentErrors.specialization = 'Subject / Specialization is required';
    } else if (activeStep === 3) {
      const u = profileData.upscJourney || {};
      if (!u.optionalSubject) currentErrors.optionalSubject = 'Please select your optional subject';
    } else if (activeStep === 4) {
      const i = profileData.interests || {};
      if (!i.hobbies?.trim()) currentErrors.hobbies = 'Please list at least one hobby';
    }

    setErrors(currentErrors);
    return Object.keys(currentErrors).length === 0;
  };

  // NAVIGATION HANDLERS
  const handleNext = () => {
    if (validateCurrentStep()) {
      if (activeStep < 5) {
        setActiveStep(prev => prev + 1);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        // Complete Profile
        setIsSubmitted(true);
      }
    }
  };

  const handleBack = () => {
    if (activeStep > 1) {
      setActiveStep(prev => prev - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-8">
        
        {/* HERO HEADER */}
        <ProfileHeroHeader />

        {/* STEPPER BAR */}
        <ProfileStepper 
          currentStep={activeStep} 
          onStepClick={(stepId) => setActiveStep(stepId)}
          stepStatuses={stepStatuses}
        />

        {/* MAIN BODY 2-COLUMN GRID */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* LEFT FORM AREA (8 cols on desktop) */}
          <div className="lg:col-span-8 space-y-6">
            
            {/* SUCCESS BANNER WHEN PROFILE COMPLETED */}
            {isSubmitted && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="bg-emerald-500/10 border border-emerald-300 p-5 rounded-2xl flex items-center justify-between gap-4"
              >
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="w-6 h-6 text-emerald-600 shrink-0" />
                  <div>
                    <h4 className="text-sm font-bold text-[#0B1628]">Profile Setup Completed!</h4>
                    <p className="text-xs text-slate-600 font-medium">Your UPSC DAF parameters are saved. AI will now generate custom interview questions for you.</p>
                  </div>
                </div>
                <a 
                  href="/dashboard"
                  className="bg-[#0B1628] text-white text-xs font-bold px-4 py-2 rounded-xl shrink-0 hover:bg-[#152744] transition-colors"
                >
                  Go to Dashboard
                </a>
              </motion.div>
            )}

            {/* FORM CONTAINER CARD */}
            <div className="bg-white rounded-2xl p-6 sm:p-8 border border-slate-200/80 shadow-2xs space-y-8">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeStep}
                  initial={{ opacity: 0, x: 15 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -15 }}
                  transition={{ duration: 0.3 }}
                >
                  {activeStep === 1 && (
                    <StepPersonal 
                      formData={profileData.personal} 
                      onChange={handleInputChange('personal')} 
                      errors={errors}
                    />
                  )}

                  {activeStep === 2 && (
                    <StepEducation 
                      formData={profileData.education} 
                      onChange={handleInputChange('education')} 
                      errors={errors}
                    />
                  )}

                  {activeStep === 3 && (
                    <StepUPSCJourney 
                      formData={profileData.upscJourney} 
                      onChange={handleInputChange('upscJourney')} 
                      errors={errors}
                    />
                  )}

                  {activeStep === 4 && (
                    <StepInterests 
                      formData={profileData.interests} 
                      onChange={handleInputChange('interests')} 
                      errors={errors}
                    />
                  )}

                  {activeStep === 5 && (
                    <StepPerspective 
                      formData={profileData.perspective} 
                      onChange={handleInputChange('perspective')} 
                      errors={errors}
                    />
                  )}
                </motion.div>
              </AnimatePresence>

              {/* BOTTOM NAVIGATION BUTTONS */}
              <div className="pt-6 border-t border-slate-100 flex items-center justify-between gap-4">
                <button
                  type="button"
                  onClick={handleBack}
                  disabled={activeStep === 1}
                  className={`px-5 py-2.5 rounded-full text-xs font-bold flex items-center gap-2 border transition-all ${
                    activeStep === 1 
                      ? 'border-slate-200 text-slate-300 cursor-not-allowed bg-slate-50' 
                      : 'border-slate-200 text-slate-700 hover:text-[#0B1628] hover:border-slate-300 hover:bg-slate-50 cursor-pointer'
                  }`}
                >
                  <ArrowLeft className="w-4 h-4" />
                  <span>Back</span>
                </button>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  type="button"
                  onClick={handleNext}
                  className="bg-[#0B1628] hover:bg-[#152744] text-white px-6 py-2.5 rounded-full text-xs font-bold inline-flex items-center gap-2 shadow-md shadow-slate-900/10 transition-all cursor-pointer"
                >
                  <span>{activeStep === 5 ? 'Complete Profile →' : 'Save & Continue →'}</span>
                  {activeStep < 5 && <ArrowRight className="w-4 h-4 text-amber-400" />}
                </motion.button>
              </div>

            </div>

            {/* BOTTOM MOTIVATIONAL BANNER */}
            <ProfileMotivationalBanner />

          </div>

          {/* RIGHT COLUMN (4 cols on desktop) */}
          <div className="lg:col-span-4 space-y-6">
            {/* PROFILE COMPLETION PERCENTAGE CARD */}
            <ProfileCompletionCard percentage={completionPercentage} />

            {/* DYNAMIC PROFILE PREVIEW CARD */}
            <ProfilePreviewCard 
              formData={profileData} 
              onPhotoUpload={handlePhotoUpload}
            />

            {/* STEPS OVERVIEW LIST */}
            <StepsOverviewCard 
              currentStep={activeStep} 
              stepStatuses={stepStatuses}
              onStepClick={(s) => setActiveStep(s)}
            />
          </div>

        </div>

      </div>
    </DashboardLayout>
  );
}
