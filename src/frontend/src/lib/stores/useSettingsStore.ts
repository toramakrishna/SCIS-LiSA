import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SettingsState {
  showSQLQuery: boolean;
  toggleShowSQLQuery: () => void;
  setShowSQLQuery: (show: boolean) => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      showSQLQuery: true, // Default: show SQL queries
      toggleShowSQLQuery: () => set((state) => ({ showSQLQuery: !state.showSQLQuery })),
      setShowSQLQuery: (show: boolean) => set({ showSQLQuery: show }),
    }),
    {
      name: 'scislisa-settings', // localStorage key
    }
  )
);
