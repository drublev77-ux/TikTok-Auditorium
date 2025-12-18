import React, { useEffect, useState } from "react";
import { Stack } from "expo-router";
import { QueryClientProvider } from "@tanstack/react-query";
import { initI18n } from "../src/i18n";
import { queryClient } from "../src/query/queryClient";
import { StatusBar } from "expo-status-bar";

export default function RootLayout() {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    void (async () => {
      await initI18n();
      setReady(true);
    })();
  }, []);

  if (!ready) return null;

  return (
    <QueryClientProvider client={queryClient}>
      <StatusBar style="light" />
      <Stack
        screenOptions={{
          headerShown: false,
        }}
      />
    </QueryClientProvider>
  );
}
