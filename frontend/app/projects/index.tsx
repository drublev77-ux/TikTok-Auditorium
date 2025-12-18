import React from "react";
import { useTranslation } from "react-i18next";
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from "react-native";
import { FlashList } from "@shopify/flash-list";
import { useQuery } from "@tanstack/react-query";
import { router } from "expo-router";

import { AppScreen } from "../../src/components/AppScreen";
import { Button } from "../../src/components/Button";
import { colors } from "../../src/theme/colors";
import { listProjects } from "../../src/api/projects";
import { useProjectStore } from "../../src/store/projectStore";

export default function ProjectsScreen() {
  const { t } = useTranslation();
  const setCurrentProject = useProjectStore((s) => s.setCurrentProject);

  const { data, isLoading, error, refetch, isRefetching } = useQuery({
    queryKey: ["projects"],
    queryFn: () => listProjects(),
  });

  return (
    <AppScreen>
      <View style={styles.header}>
        <View style={{ flex: 1 }}>
          <Text style={styles.title}>{t("projects")}</Text>
          <Text style={styles.subtitle}>{t("appName")}</Text>
        </View>
        <Button title={t("createProject")} onPress={() => router.push("/projects/create")} variant="secondary" />
      </View>

      {error ? (
        <View style={styles.card}>
          <Text style={styles.errorText}>{String((error as Error).message)}</Text>
          <View style={{ height: 12 }} />
          <Button title={t("loading")} onPress={() => refetch()} loading={isRefetching} />
        </View>
      ) : null}

      {isLoading ? (
        <View style={styles.center}>
          <ActivityIndicator color={colors.primary2} />
          <View style={{ height: 12 }} />
          <Text style={styles.muted}>{t("loading")}</Text>
        </View>
      ) : null}

      {!isLoading && !data?.length ? (
        <View style={styles.card}>
          <Text style={styles.muted}>{t("emptyProjects")}</Text>
        </View>
      ) : null}

      {!isLoading && data?.length ? (
        <FlashList
          data={data}
          estimatedItemSize={84}
          keyExtractor={(item) => item.id}
          contentContainerStyle={{ paddingBottom: 24 }}
          renderItem={({ item }) => (
            <Pressable
              onPress={() => {
                setCurrentProject(item);
                router.replace("/(tabs)/dashboard");
              }}
              style={({ pressed }) => [styles.projectRow, pressed && { opacity: 0.8 }]}
            >
              <View style={{ flex: 1 }}>
                <Text style={styles.projectName}>{item.name}</Text>
                <Text style={styles.projectMeta}>
                  {item.timezone} • {item.language.toUpperCase()}
                </Text>
              </View>
              <Text style={styles.open}>{t("open")}</Text>
            </Pressable>
          )}
        />
      ) : null}
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: 12 },
  title: { color: colors.text, fontSize: 26, fontWeight: "800" },
  subtitle: { color: colors.muted, marginTop: 4 },
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  muted: { color: colors.muted },
  card: {
    marginTop: 16,
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 16,
    padding: 14,
  },
  projectRow: {
    marginTop: 12,
    backgroundColor: colors.card2,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 16,
    padding: 14,
    minHeight: 64,
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
  },
  projectName: { color: colors.text, fontWeight: "800", fontSize: 16 },
  projectMeta: { color: colors.muted, marginTop: 6, fontSize: 12 },
  open: { color: colors.primary2, fontWeight: "800" },
  errorText: { color: colors.danger, fontWeight: "700" },
});
