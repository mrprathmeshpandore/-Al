import React, { useRef } from 'react';
import { Camera, MapPin, GraduationCap, BookOpen } from 'lucide-react';

export default function ProfilePreviewCard({ formData, onPhotoUpload }) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        onPhotoUpload(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const name = formData.personal?.fullName || "Pratham Pandore";
  const state = formData.personal?.homeState || "Maharashtra";
  const city = formData.personal?.currentCity || formData.personal?.district || "Pune";
  const degree = formData.education?.degree || "Not added yet";
  const optional = formData.upscJourney?.optionalSubject || "Not added yet";

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-2xs overflow-hidden relative group">
      
      {/* CARD TOP BANNER WITH TRICOLOR MOTIF */}
      <div className="h-24 bg-gradient-to-r from-amber-500/20 via-sky-400/10 to-emerald-500/20 relative p-4 flex justify-end">
        <button
          onClick={() => fileInputRef.current?.click()}
          className="bg-white/90 hover:bg-white text-slate-700 hover:text-[#0B1628] border border-slate-200/80 px-2.5 py-1 rounded-lg text-[11px] font-bold flex items-center gap-1.5 shadow-2xs backdrop-blur-xs transition-all h-fit cursor-pointer"
        >
          <Camera className="w-3.5 h-3.5" />
          <span>Edit Photo</span>
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="hidden"
        />
      </div>

      {/* AVATAR OVERLAY & PROFILE BODY */}
      <div className="px-6 pb-6 pt-0 text-center relative space-y-4">
        
        {/* CENTERED AVATAR IMAGE */}
        <div className="relative inline-block -mt-12">
          <img
            src={formData.personal?.photoUrl || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&q=80&w=250"}
            alt={name}
            className="w-20 h-20 sm:w-22 sm:h-22 rounded-full object-cover border-4 border-white shadow-md ring-2 ring-amber-500/30 mx-auto"
          />
        </div>

        {/* NAME & ROLE */}
        <div className="space-y-0.5">
          <h3 className="text-lg font-bold text-[#0B1628] tracking-tight">
            {name}
          </h3>
          <p className="text-xs font-semibold text-slate-500">
            UPSC Aspirant
          </p>
        </div>

        {/* MOTTO QUOTE */}
        <p className="text-[11.5px] italic font-medium text-slate-600 bg-slate-50 border border-slate-100 p-2.5 rounded-xl">
          “Discipline today for a better tomorrow.”
        </p>

        {/* DYNAMIC DETAILS LIST */}
        <div className="pt-2 space-y-2 text-left text-xs font-medium text-slate-600 border-t border-slate-100">
          <div className="flex items-center gap-2.5">
            <MapPin className="w-4 h-4 text-amber-600 shrink-0" />
            <span>{state}, {city}</span>
          </div>

          <div className="flex items-center gap-2.5">
            <GraduationCap className="w-4 h-4 text-blue-600 shrink-0" />
            <span className={degree === "Not added yet" ? "text-slate-400 italic" : "text-slate-700 font-semibold"}>
              {degree}
            </span>
          </div>

          <div className="flex items-center gap-2.5">
            <BookOpen className="w-4 h-4 text-purple-600 shrink-0" />
            <span className={optional === "Not added yet" ? "text-slate-400 italic" : "text-slate-700 font-semibold"}>
              Optional: {optional}
            </span>
          </div>
        </div>

      </div>

    </div>
  );
}
