import React, { useState } from "react";
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  Alert,
  Platform,
  TouchableOpacity,
} from "react-native";
import { useTranslation } from "react-i18next";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { router, Stack } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

import { AppScreen } from "../../src/components/AppScreen";
import { Button } from "../../src/components/Button";
import { colors } from "../../src/theme/colors";
import { useProject } from "../../src/store/ProjectContext";
import { useAvatarStore } from "../../src/store/avatarStore";
import { deleteAudienceAvatar } from "../../src/api/audience";

export default function AvatarDetailsScreen() {
  const { t } = useTranslation();
  const { currentProject } = useProject();
  const queryClient = useQueryClient();
  const avatar = useAvatarStore((s) => s.selectedAvatar);
  const setSelectedAvatar = useAvatarStore((s) => s.setSelectedAvatar);

  const deleteMutation = useMutation({
    mutationFn: deleteAudienceAvatar,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["audience-avatars", currentProject?.id] });
      setSelectedAvatar(null);
      router.back();
    },
  });

  const handleDelete = () => {
    if (!avatar) return;
    if (Platform.OS === "web") {
      if (window.confirm(t("confirmDelete"))) {
        deleteMutation.mutate(avatar.id);
      }
    } else {
      Alert.alert(t("delete"), t("confirmDelete"), [
        { text: t("no"), style: "cancel" },
        {
          text: t("yes"),
          style: "destructive",
          onPress: () => deleteMutation.mutate(avatar.id),
        },
      ]);
    }
  };

  if (!avatar) {
    return (
      <>
        <Stack.Screen
          options={{
            title: t("avatarDetails"),
            headerStyle: { backgroundColor: colors.bg },
            headerTintColor: colors.text,
          }}
        />
        <AppScreen>
          <View style={styles.center}>
            <Text style={styles.muted}>{t("loading")}</Text>
          </View>
        </AppScreen>
      </>
    );
  }

  const createdDate = new Date(avatar.created_at).toLocaleDateString();
  const updatedDate = new Date(avatar.updated_at).toLocaleDateString();

  return (
    <>
      <Stack.Screen
        options={{
          title: avatar.name,
          headerStyle: { backgroundColor: colors.bg },
          headerTintColor: colors.text,
        }}
      />
      <AppScreen>
        <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent}>
          {/* Avatar Header */}
          <View style={styles.headerCard}>
            <View style={styles.avatarIcon}>
              <Ionicons name="person-circle-outline" size={64} color={colors.primary2} />
            </View>
            <Text style={styles.avatarName}>{avatar.name}</Text>
            <View style={styles.geoRow}>
              <Ionicons name="location" size={16} color={colors.primary2} />
              <Text style={styles.geoText}>{avatar.geolocation}</Text>
            </View>
            <View style={styles.metaRow}>
              <Text style={styles.metaText}>{t("created")}: {createdDate}</Text>
              <Text style={styles.metaDot}>•</Text>
              <Text style={styles.metaText}>{t("updated")}: {updatedDate}</Text>
            </View>
          </View>

          {/* Hashtags / Interests Section */}
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Ionicons name="pricetag-outline" size={20} color={colors.primary2} />
              <Text style={styles.sectionTitle}>{t("interests")}</Text>
            </View>
            <View style={styles.tagsGrid}>
              {avatar.hashtags.map((tag) => (
                <View key={tag} style={styles.tag}>
                  <Text style={styles.tagText}>{tag}</Text>
                </View>
              ))}
            </View>
          </View>

          {/* Demographics Placeholder */}
          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Ionicons name="stats-chart-outline" size={20} color={colors.primary2} />
              <Text style={styles.sectionTitle}>{t("demographics")}</Text>
            </View>
            <View style={styles.placeholderCard}>
              <Ionicons name="analytics-outline" size={48} color={colors.border} />
              <Text style={styles.placeholderText}>
                AI-анализ демографии будет доступен после подключения TikTok API
              </Text>
            </View>
          </View>

          {/* Notes Section */}
          {avatar.notes ? (
            <View style={styles.section}>
              <View style={styles.sectionHeader}>
                <Ionicons name="document-text-outline" size={20} color={colors.primary2} />
                <Text style={styles.sectionTitle}>{t("notes")}</Text>
              </View>
              <View style={styles.notesCard}>
                <Text style={styles.notesText}>{avatar.notes}</Text>
              </View>
            </View>
          ) : null}

          {/* Actions */}
          <View style={styles.actions}>
            <Button
              title={t("edit")}
              onPress={() => router.push("/audience/edit")}
              variant="secondary"
            />
            <View style={{ height: 12 }} />
            <TouchableOpacity style={styles.deleteBtn} onPress={handleDelete}>
              <Ionicons name="trash-outline" size={20} color={colors.danger} />
              <Text style={styles.deleteText}>{t("delete")}</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
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
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  muted: {
    color: colors.muted,
  },
  headerCard: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 20,
    padding: 24,
    alignItems: "center",
    marginBottom: 16,
  },
  avatarIcon: {
    marginBottom: 12,
  },
  avatarName: {
    color: colors.text,
    fontSize: 24,
    fontWeight: "800",
    textAlign: "center",
  },
  geoRow: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: 8,
    gap: 6,
  },
  geoText: {
    color: colors.primary2,
    fontSize: 15,
    fontWeight: "600",
  },
  metaRow: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: 12,
    gap: 8,
  },
  metaText: {
    color: colors.muted,
    fontSize: 12,
  },
  metaDot: {
    color: colors.muted,
  },
  section: {
    marginBottom: 20,
  },
  sectionHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 12,
  },
  sectionTitle: {
    color: colors.text,
    fontSize: 17,
    fontWeight: "700",
  },
  tagsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  tag: {
    backgroundColor: colors.card2,
    borderRadius: 16,
    paddingHorizontal: 14,
    paddingVertical: 8,
  },
  tagText: {
    color: colors.primary2,
    fontSize: 14,
    fontWeight: "600",
  },
  placeholderCard: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 16,
    padding: 32,
    alignItems: "center",
  },
  placeholderText: {
    color: colors.muted,
    fontSize: 14,
    textAlign: "center",
    marginTop: 12,
  },
  notesCard: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 16,
    padding: 16,
  },
  notesText: {
    color: colors.text,
    fontSize: 15,
    lineHeight: 22,
  },
  actions: {
    marginTop: 24,
  },
  deleteBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    paddingVertical: 14,
  },
  deleteText: {
    color: colors.danger,
    fontSize: 16,
    fontWeight: "600",
  },
});
