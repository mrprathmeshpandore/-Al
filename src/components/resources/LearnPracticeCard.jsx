import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Upload, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { resourcesApi } from '../../services/resourcesApi';
import { useAuth } from '../../context/AuthContext';

export default function LearnPracticeCard({ onUploadSuccess }) {
  const { isAuthenticated, openAuthModal } = useAuth();
  const fileInputRef = useRef(null);
  const [uploading, setUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [error, setError] = useState('');

  const handleCardClick = () => {
    if (!isAuthenticated) {
      openAuthModal('login');
      return;
    }
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endswith('.pdf') && file.type !== 'application/pdf') {
      setError('Please select a valid PDF file.');
      return;
    }

    setError('');
    setUploading(true);
    setStatusMessage('Uploading & Processing document...');

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('title', file.name.replace(/\.[^/.]+$/, ''));
      formData.append('category', 'Study Material');
      formData.append('subject', 'General Studies');
      formData.append('resource_type', 'pdf');

      const response = await resourcesApi.uploadPdf(formData);
      setStatusMessage('Document uploaded! Processing document...');

      setTimeout(() => {
        setStatusMessage('Processing completed!');
        setUploading(false);
        if (onUploadSuccess) onUploadSuccess(response);
      }, 2000);
    } catch (err) {
      setError(err.message || 'Failed to upload PDF.');
      setUploading(false);
      setStatusMessage('');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="bg-white rounded-2xl p-5 border border-amber-950/5 shadow-2xs flex flex-col justify-between"
    >
      <div>
        <div className="flex items-center gap-2 mb-2">
          <div className="p-1.5 rounded-lg bg-amber-50 text-amber-600">
            <Sparkles className="w-4 h-4" />
          </div>
          <h3 className="font-serif font-bold text-slate-900 text-base">Learn → Practice</h3>
        </div>

        <p className="text-xs text-slate-600 font-sans leading-relaxed mb-4">
          Found something important? Turn your study material into interview practice.
        </p>

        {/* Hidden File Input */}
        <input
          type="file"
          ref={fileInputRef}
          accept="application/pdf"
          onChange={handleFileChange}
          className="hidden"
        />

        {/* Upload dropzone card */}
        <div
          onClick={handleCardClick}
          className="border-2 border-dashed border-slate-200 hover:border-amber-500/50 rounded-xl p-4 text-center bg-slate-50/50 hover:bg-amber-50/20 transition-all cursor-pointer mb-3 group"
        >
          {uploading ? (
            <div className="flex flex-col items-center justify-center gap-1.5 py-1">
              <Loader2 className="w-5 h-5 animate-spin text-amber-600" />
              <span className="text-xs font-bold text-slate-700">{statusMessage}</span>
            </div>
          ) : statusMessage === 'Processing completed!' ? (
            <div className="flex flex-col items-center justify-center gap-1 py-1 text-emerald-600">
              <CheckCircle2 className="w-5 h-5 mb-0.5" />
              <span className="text-xs font-bold">Document Processed</span>
            </div>
          ) : (
            <>
              <div className="w-8 h-8 rounded-full bg-white shadow-2xs text-blue-600 flex items-center justify-center mx-auto mb-1.5 group-hover:scale-105 transition-transform">
                <Upload className="w-4 h-4" />
              </div>
              <span className="text-xs font-bold text-slate-700 block">Upload a PDF</span>
              <span className="text-[10px] text-amber-600 font-medium">Click to upload document</span>
            </>
          )}
        </div>

        {error && (
          <div className="p-2.5 bg-rose-50 border border-rose-200 rounded-xl text-rose-700 text-[11px] font-medium flex items-center gap-1.5 mb-3">
            <AlertCircle className="w-3.5 h-3.5 shrink-0 text-rose-500" />
            <span>{error}</span>
          </div>
        )}
      </div>

      <p className="text-[11px] text-slate-400 italic text-center font-sans leading-snug">
        Get summaries, key points, UPSC relevance, and potential interview questions using AI.
      </p>
    </motion.div>
  );
}
