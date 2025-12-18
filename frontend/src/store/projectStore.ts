import React from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export type Project = {
  id: string;
  org_id: string;
  name: string;
  timezone: string;
  language: "ru" | "en";
  created_at: string;
};

type ProjectState = {
  currentProject?: Project;
  setCurrentProject: (p?: Project) => void;
};

export const useProjectStore = create<ProjectState>()(
  persist(
    (set) => ({
      currentProject: undefined,
      setCurrentProject: (p) => set({ currentProject: p }),
    }),
    {
      name: "tikauditor_project",
      storage: createJSONStorage(() => AsyncStorage),
      // keep only what we need
      partialize: (s) => ({ currentProject: s.currentProject }),
    }
  )
);
