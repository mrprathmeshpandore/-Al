import React from 'react';
import { motion } from 'framer-motion';
import { Bell, Calendar, Newspaper, Mic, Mail } from 'lucide-react';

export default function NotificationsSettingsCard({ settings, updateNotificationSetting }) {
  const items = [
    { key: 'dailyPractice', label: 'Daily Practice Reminder', desc: 'Remind me to practice daily', icon: Calendar, color: 'text-amber-600 bg-amber-50' },
    { key: 'currentAffairs', label: 'Current Affairs Alerts', desc: 'Get notified about important updates', icon: Newspaper, color: 'text-blue-600 bg-blue-50' },
    { key: 'interviewUpdates', label: 'Interview Updates', desc: 'Notify about new features and updates', icon: Mic, color: 'text-purple-600 bg-purple-50' },
    { key: 'email', label: 'Email Notifications', desc: 'Receive updates on your email', icon: Mail, color: 'text-emerald-600 bg-emerald-50' }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.2 }}
      className="bg-white rounded-2xl p-6 border border-amber-950/5 shadow-2xs space-y-4 flex flex-col justify-between"
    >
      <div>
        <div className="flex items-center gap-2 mb-1">
          <div className="p-1.5 rounded-lg bg-amber-50 text-amber-600">
            <Bell className="w-4 h-4" />
          </div>
          <h3 className="font-serif font-bold text-slate-900 text-lg">Notifications</h3>
        </div>
        <p className="text-xs text-slate-500 font-sans mb-4">
          Stay updated with important alerts and reminders.
        </p>

        <div className="space-y-3.5">
          {items.map((item) => {
            const IconComp = item.icon;
            const isEnabled = settings[item.key];
            return (
              <div key={item.key} className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-2.5">
                  <div className={`p-1.5 rounded-lg ${item.color}`}>
                    <IconComp className="w-4 h-4" />
                  </div>
                  <div>
                    <label className="text-xs font-bold text-slate-800 font-sans block">{item.label}</label>
                    <span className="text-[11px] text-slate-400 font-sans">{item.desc}</span>
                  </div>
                </div>

                <button
                  onClick={() => updateNotificationSetting(item.key, !isEnabled)}
                  className={`w-11 h-6 rounded-full transition-colors relative flex items-center px-0.5 ${
                    isEnabled ? 'bg-blue-600' : 'bg-slate-300'
                  }`}
                >
                  <span
                    className={`w-5 h-5 rounded-full bg-white shadow-md transform transition-transform ${
                      isEnabled ? 'translate-x-5' : 'translate-x-0'
                    }`}
                  />
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}
