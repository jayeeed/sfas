import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { FaceModel } from '@/types';

interface SettingsState {
  defaultModel: FaceModel;
  theme: 'light' | 'dark' | 'system';
}

interface SettingsActions {
  setDefaultModel: (model: FaceModel) => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
}

type SettingsStore = SettingsState & SettingsActions;

export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set) => ({
      // State
      defaultModel: 'mobilefacenet',
      theme: 'system',

      // Actions
      setDefaultModel: (defaultModel) => set({ defaultModel }),
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'settings-storage',
    }
  )
);
