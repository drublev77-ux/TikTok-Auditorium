import React from "react";
import { Redirect } from "expo-router";
import { useProject } from "../src/store/ProjectContext";

export default function Index() {
  const { currentProject, isHydrating } = useProject();

  if (isHydrating) return null;
  if (currentProject?.id) return <Redirect href="/(tabs)/dashboard" />;
  return <Redirect href="/projects" />;
}
