import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";
import type { Project } from "./project";

type ProjectContextValue = {
  currentProject?: Project;
  setCurrentProject: (p?: Project) => Promise<void>;
  isHydrating: boolean;
};

const STORAGE_KEY = "tikauditor_current_project";

const Ctx = createContext<ProjectContextValue | undefined>(undefined);

export function ProjectProvider({ children }: { children: React.ReactNode }) {
  const [currentProject, setCurrentProjectState] = useState<Project | undefined>(undefined);
  const [isHydrating, setIsHydrating] = useState(true);

  useEffect(() => {
    void (async () => {
      try {
        const raw = await AsyncStorage.getItem(STORAGE_KEY);
        if (raw) setCurrentProjectState(JSON.parse(raw) as Project);
      } catch {
        // ignore
      } finally {
        setIsHydrating(false);
      }
    })();
  }, []);

  const value = useMemo<ProjectContextValue>(() => {
    return {
      currentProject,
      isHydrating,
      setCurrentProject: async (p?: Project) => {
        setCurrentProjectState(p);
        try {
          if (!p) await AsyncStorage.removeItem(STORAGE_KEY);
          else await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(p));
        } catch {
          // ignore
        }
      },
    };
  }, [currentProject, isHydrating]);

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useProject() {
  const v = useContext(Ctx);
  if (!v) throw new Error("useProject must be used within ProjectProvider");
  return v;
}
