import React, { useMemo, useState } from "react";
import { Keyboard, KeyboardAvoidingView, Platform, StyleSheet, Text, View } from "react-native";
import { useTranslation } from "react-i18next";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { router } from "expo-router";

import { AppScreen } from "../../src/components/AppScreen";
import { Button } from "../../src/components/Button";
import { Input } from "../../src/components/Input";
import { colors } from "../../src/theme/colors";
import { createOrg, createProject } from "../../src/api/projects";

export default function CreateProjectScreen() {
  const { t } = useTranslation();
  const qc = useQueryClient();

  const [orgName, setOrgName] = useState("");
  const [projectName, setProjectName] = useState("");
  const [timezone, setTimezone] = useState("UTC");
  const [lang, setLang] = useState<"ru" | "en">("ru");

  const canSave = useMemo(() => {
    return orgName.trim().length >= 2 && projectName.trim().length >= 2;
  }, [orgName, projectName]);

  const mutation = useMutation({
    mutationFn: async () => {
      const org = await createOrg(orgName.trim());
      const project = await createProject({
        org_id: org.id,
        name: projectName.trim(),
        timezone,
        language: lang,
      });
      return project;
    },
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: ["projects"] });
      router.back();
    },
  });

  return (
    <KeyboardAvoidingView behavior={Platform.OS === "ios" ? "padding" : "height"} style={{ flex: 1 }}>
      <AppScreen>
        <View style={styles.header}>
          <Text style={styles.title}>{t("createProject")}</Text>
          <Text style={styles.subtitle}>{t("projects")}</Text>
        </View>

        <View style={{ height: 16 }} />

        <Input label={t("orgName")} value={orgName} onChangeText={setOrgName} autoCapitalize="words" />
        <View style={{ height: 12 }} />

        <Input label={t("projectName")} value={projectName} onChangeText={setProjectName} autoCapitalize="words" />
        <View style={{ height: 12 }} />

        <Input label={t("timezone")} value={timezone} onChangeText={setTimezone} autoCapitalize="none" />
        <View style={{ height: 12 }} />

        <View style={styles.langRow}>
          <Text style={styles.langLabel}>{t("language")}</Text>
          <View style={styles.langPills}>
            <Button title="RU" onPress={() => setLang("ru")} variant={lang === "ru" ? "primary" : "secondary"} />
            <Button title="EN" onPress={() => setLang("en")} variant={lang === "en" ? "primary" : "secondary"} />
          </View>
        </View>

        <View style={{ flex: 1 }} />

        {mutation.error ? <Text style={styles.errorText}>{String((mutation.error as Error).message)}</Text> : null}

        <View style={styles.actions}>
          <Button
            title={t("cancel")}
            onPress={() => {
              Keyboard.dismiss();
              router.back();
            }}
            variant="ghost"
          />
          <Button
            title={t("save")}
            onPress={() => mutation.mutate()}
            loading={mutation.isPending}
            disabled={!canSave}
          />
        </View>
      </AppScreen>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  header: { gap: 6 },
  title: { color: colors.text, fontSize: 26, fontWeight: "800" },
  subtitle: { color: colors.muted },
  actions: { flexDirection: "row", gap: 12, paddingTop: 12 },
  errorText: { color: colors.danger, marginBottom: 12, fontWeight: "700" },
  langRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 12,
    paddingTop: 4,
  },
  langLabel: { color: colors.muted, fontSize: 12, fontWeight: "800" },
  langPills: { flexDirection: "row", gap: 10 },
});
