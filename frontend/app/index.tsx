import React, { useEffect } from "react";
import { Redirect } from "expo-router";
import { useProjectStore } from "../src/store/projectStore";

export default function Index() {
  const currentProject = useProjectStore((s) => s.currentProject);

  // If user already selected a project before  go straight to tabs
  if (currentProject?.id) return <Redirect href="/(tabs)/dashboard" />;

  return <Redirect href="/projects" />;
}
