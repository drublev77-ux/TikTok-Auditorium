import React, { useState } from "react";
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
} from "react-native";
import { useTranslation } from "react-i18next";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { router, Stack } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

import { AppScreen } from "../../src/components/AppScreen";
import { Button } from "../../src/components/Button";
import { HashtagInput } from "../../src/components/HashtagInput";
import { colors } from "../../src/theme/colors";
import { useProject } from "../../src/store/ProjectContext";
import { createAudienceAvatar } from "../../src/api/audience";

export default function CreateAvatarScreen() {
  const { t } = useTranslation();
  const { currentProject } = useProject();
  const queryClient = useQueryClient();

  const [name, setName] = useState("");
  const [hashtags, setHashtags] = useState<string[]>([]);
  const [geolocation, setGeolocation] = useState("");
  const [notes, setNotes] = useState("");
  const [errors, setErrors] = useState<Record<string, string>>({});

  const mutation = useMutation({
    mutationFn: createAudienceAvatar,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["audience-avatars", currentProject?.id] });
      router.back();
    },
    onError: (err) => {
      const msg = err instanceof Error ? err.message : "Error";
      if (Platform.OS === "web") {
        window.alert(msg);
      } else {
        Alert.alert("Error", msg);
      }
    },
  });

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {};
    if (!name.trim()) newErrors.name = t("nameRequired");
    if (hashtags.length === 0) newErrors.hashtags = t("hashtagRequired");
    if (!geolocation.trim()) newErrors.geolocation = t("geoRequired");
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = () => {
    if (!validate()) return;
    if (!currentProject?.id) return;

    mutation.mutate({
      project_id: currentProject.id,
      name: name.trim(),
      hashtags,
      geolocation: geolocation.trim(),
      language: currentProject.language || "ru",
      notes: notes.trim() || undefined,
    });
  };

  return (
    <>
      <Stack.Screen
        options={{
          title: t("createAvatar"),
          headerStyle: { backgroundColor: colors.bg },
          headerTintColor: colors.text,
          headerBackTitle: t("cancel"),
        }}
      />
      <AppScreen>
        <KeyboardAvoidingView
          style={{ flex: 1 }}
          behavior={Platform.OS === "ios" ? "padding" : "height"}
        >
          <ScrollView
            style={styles.scroll}
            contentContainerStyle={styles.scrollContent}
            keyboardShouldPersistTaps="handled"
          >
            {/* Avatar Name */}
            <View style={styles.field}>
              <Text style={styles.label}>{t("avatarName")} *</Text>
              <TextInput
                style={[styles.input, errors.name && styles.inputError]}
                value={name}
                onChangeText={setName}
                placeholder={t("avatarName")}
                placeholderTextColor={colors.muted}
                autoCapitalize="words"
              />
              {errors.name ? <Text style={styles.errorText}>{errors.name}</Text> : null}
            </View>

            {/* Hashtags */}
            <View style={styles.field}>
              <Text style={styles.label}>{t("hashtags")} *</Text>
              <HashtagInput
                value={hashtags}
                onChange={setHashtags}
                placeholder={t("hashtagsPlaceholder")}
              />
              {errors.hashtags ? <Text style={styles.errorText}>{errors.hashtags}</Text> : null}
            </View>

            {/* Geolocation */}
            <View style={styles.field}>
              <Text style={styles.label}>{t("geolocation")} *</Text>
              <View style={styles.inputWithIcon}>
                <Ionicons name="location-outline" size={20} color={colors.muted} style={styles.inputIcon} />
                <TextInput
                  style={[styles.inputFlex, errors.geolocation && styles.inputError]}
                  value={geolocation}
                  onChangeText={setGeolocation}
                  placeholder={t("geolocationPlaceholder")}
                  placeholderTextColor={colors.muted}
                />
              </View>
              {errors.geolocation ? <Text style={styles.errorText}>{errors.geolocation}</Text> : null}
            </View>

            {/* Notes */}
            <View style={styles.field}>
              <Text style={styles.label}>{t("notes")}</Text>
              <TextInput
                style={[styles.input, styles.textArea]}
                value={notes}
                onChangeText={setNotes}
                placeholder={t("notesPlaceholder")}
                placeholderTextColor={colors.muted}
                multiline
                numberOfLines={4}
                textAlignVertical="top"
              />
            </View>

            <View style={styles.actions}>
              <Button
                title={t("save")}
                onPress={handleSave}
                loading={mutation.isPending}
                variant="primary"
              />
              <View style={{ height: 12 }} />
              <Button
                title={t("cancel")}
                onPress={() => router.back()}
                variant="secondary"
              />
            </View>
          </ScrollView>
        </KeyboardAvoidingView>
      </AppScreen>
    </>
  );
}

const styles = StyleSheet.create({
  scroll: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 40,
  },
  field: {
    marginBottom: 20,
  },
  label: {
    color: colors.text,
    fontSize: 15,
    fontWeight: "600",
    marginBottom: 8,
  },
  input: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 12,
    padding: 14,
    color: colors.text,
    fontSize: 16,
  },
  inputError: {
    borderColor: colors.danger,
  },
  inputWithIcon: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 12,
  },
  inputIcon: {
    marginLeft: 14,
  },
  inputFlex: {
    flex: 1,
    padding: 14,
    color: colors.text,
    fontSize: 16,
  },
  textArea: {
    minHeight: 100,
    paddingTop: 14,
  },
  errorText: {
    color: colors.danger,
    fontSize: 13,
    marginTop: 6,
  },
  actions: {
    marginTop: 24,
  },
});
