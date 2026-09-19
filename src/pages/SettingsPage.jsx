import React, { useState } from 'react';
import DashboardLayout from '../components/dashboard/DashboardLayout';
import SettingsHeader from '../components/settings/SettingsHeader';
import AccountSettingsCard from '../components/settings/AccountSettingsCard';
import InterviewPreferencesCard from '../components/settings/InterviewPreferencesCard';
import SettingsBrandCard from '../components/settings/SettingsBrandCard';
import NotificationsSettingsCard from '../components/settings/NotificationsSettingsCard';
import AppearanceSettingsCard from '../components/settings/AppearanceSettingsCard';
import PrivacyDataCard from '../components/settings/PrivacyDataCard';
import DangerZoneCard from '../components/settings/DangerZoneCard';
import { SettingsToast, LogoutModal, DeleteAccountModal } from '../components/settings/ModalsAndToasts';
import { defaultSettings } from '../data/settingsData';
import { Save } from 'lucide-react';

export default function SettingsPage() {
  const [settings, setSettings] = useState(defaultSettings);
  const [searchQuery, setSearchQuery] = useState('');
  const [showToast, setShowToast] = useState(false);
  const [logoutModalOpen, setLogoutModalOpen] = useState(false);
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);

  const updateInterviewSetting = (key, value) => {
    setSettings(prev => ({
      ...prev,
      interview: { ...prev.interview, [key]: value }
    }));
  };

  const updateNotificationSetting = (key, value) => {
    setSettings(prev => ({
      ...prev,
      notifications: { ...prev.notifications, [key]: value }
    }));
  };

  const updateAppearanceSetting = (key, value) => {
    setSettings(prev => ({
      ...prev,
      appearance: { ...prev.appearance, [key]: value }
    }));
  };

  const handleSaveChanges = () => {
    setShowToast(true);
    setTimeout(() => {
      setShowToast(false);
    }, 3000);
  };

  return (
    <DashboardLayout>
      <div className="space-y-6 pb-20">
        {/* Page Header */}
        <SettingsHeader searchQuery={searchQuery} setSearchQuery={setSearchQuery} />

        {/* Top Grid: Account | Interview Preferences | Motivational Brand Card */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <AccountSettingsCard />
          <InterviewPreferencesCard
            settings={settings.interview}
            updateInterviewSetting={updateInterviewSetting}
          />
          <SettingsBrandCard />
        </div>

        {/* Middle Grid: Notifications | Appearance | Privacy & Data */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <NotificationsSettingsCard
            settings={settings.notifications}
            updateNotificationSetting={updateNotificationSetting}
          />
          <AppearanceSettingsCard
            settings={settings.appearance}
            updateAppearanceSetting={updateAppearanceSetting}
          />
          <PrivacyDataCard />
        </div>

        {/* Bottom Danger Zone */}
        <DangerZoneCard
          onTriggerLogout={() => setLogoutModalOpen(true)}
          onTriggerDeleteAccount={() => setDeleteModalOpen(true)}
        />

        {/* Floating / Sticky Save Bar */}
        <div className="fixed bottom-6 right-6 lg:right-10 z-40">
          <button
            onClick={handleSaveChanges}
            className="flex items-center gap-2 py-3 px-6 rounded-2xl bg-[#0B1628] hover:bg-[#152744] text-white text-xs font-bold shadow-xl transition-all hover:scale-105 active:scale-95 group"
          >
            <Save className="w-4 h-4 text-amber-400 group-hover:rotate-12 transition-transform" />
            <span>Save Changes</span>
          </button>
        </div>

        {/* Confirmation Modals & Toast */}
        <SettingsToast show={showToast} message="Settings saved successfully." />
        <LogoutModal isOpen={logoutModalOpen} onClose={() => setLogoutModalOpen(false)} />
        <DeleteAccountModal isOpen={deleteModalOpen} onClose={() => setDeleteModalOpen(false)} />
      </div>
    </DashboardLayout>
  );
}
