import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Shield, ClipboardList, Bookmark, Download, FileText, ShieldCheck, ChevronRight } from 'lucide-react';
import { privacyLinks } from '../../data/settingsData';

const iconMap = {
  clipboardList: ClipboardList,
  bookmark: Bookmark,
  download: Download,
  fileText: FileText,
  shieldCheck: ShieldCheck
};

export default function PrivacyDataCard() {
  const navigate = useNavigate();

  const handleItemClick = (item) => {
    if (item.path) {
      navigate(item.path);
    } else if (item.id === 'download-data') {
      alert("Preparing data export package...");
    } else {
      alert(`Opening ${item.title}`);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.3 }}
      className="bg-white rounded-2xl p-6 border border-amber-950/5 shadow-2xs space-y-4 flex flex-col justify-between"
    >
      <div>
        <div className="flex items-center gap-2 mb-1">
          <div className="p-1.5 rounded-lg bg-sky-50 text-sky-600">
            <Shield className="w-4 h-4" />
          </div>
          <h3 className="font-serif font-bold text-slate-900 text-lg">Privacy & Data</h3>
        </div>
        <p className="text-xs text-slate-500 font-sans mb-4">
          Manage your data and privacy settings.
        </p>

        <div className="space-y-2">
          {privacyLinks.map((item) => {
            const IconComp = iconMap[item.icon] || FileText;
            return (
              <div
                key={item.id}
                onClick={() => handleItemClick(item)}
                className="flex items-center justify-between p-2.5 rounded-xl bg-slate-50/70 border border-slate-100 hover:bg-slate-50 cursor-pointer group transition-colors"
              >
                <div className="flex items-center gap-2.5">
                  <div className="p-1.5 rounded-lg bg-white shadow-2xs text-slate-600 group-hover:text-blue-600 transition-colors">
                    <IconComp className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-800 font-sans group-hover:text-blue-900 transition-colors">
                      {item.title}
                    </h4>
                    <p className="text-[10.5px] text-slate-400 font-sans">{item.description}</p>
                  </div>
                </div>

                <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-slate-600 group-hover:translate-x-0.5 transition-all" />
              </div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}
