import React from "react";
import { StyleSheet, Text, View } from "react-native";
import { useTranslation } from "react-i18next";
import { AppScreen } from "../../src/components/AppScreen";
import { Button } from "../../src/components/Button";
import { colors } from "../../src/theme/colors";
import { useProject } from "../../src/store/ProjectContext";
import { router } from "expo-router";

export default function DashboardTab() {
  const { t } = useTranslation();
  const { currentProject: project, setCurrentProject: setProject } = useProject();

  return (
    <AppScreen>
      <View style={styles.card}>
        <Text style={styles.h}>{t("dashboard")}</Text>
        <Text style={styles.p}>{project ? `${project.name} • ${project.timezone}` : "No project selected"}</Text>
        <View style={{ height: 12 }} />
        <Button
          title={t("projects")}
          onPress={() => {
            setProject(undefined);
            router.replace("/projects");
          }}
          variant="secondary"
        />
      </View>
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 16,
    padding: 14,
  },
  h: { color: colors.text, fontSize: 18, fontWeight: "800" },
  p: { color: colors.muted, marginTop: 8 },
});
