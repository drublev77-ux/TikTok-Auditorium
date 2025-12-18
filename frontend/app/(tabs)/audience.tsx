import React, { useState } from "react";
import {
  StyleSheet,
  Text,
  View,
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  Alert,
  Platform,
} from "react-native";
import { useTranslation } from "react-i18next";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { router } from "expo-router";

import { AppScreen } from "../../src/components/AppScreen";
import { Button } from "../../src/components/Button";
import { AvatarCard } from "../../src/components/AvatarCard";
import { colors } from "../../src/theme/colors";
import { useProject } from "../../src/store/ProjectContext";
import { useAvatarStore } from "../../src/store/avatarStore";
import { listAudienceAvatars, deleteAudienceAvatar } from "../../src/api/audience";
import type { AudienceAvatar } from "../../src/api/audience";

export default function AudienceTab() {
  const { t } = useTranslation();
  const { currentProject } = useProject();
  const queryClient = useQueryClient();
  const setSelectedAvatar = useAvatarStore((s) => s.setSelectedAvatar);
  const [refreshing, setRefreshing] = useState(false);

  const projectId = currentProject?.id;

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["audience-avatars", projectId],
    queryFn: () => listAudienceAvatars(projectId!),
    enabled: !!projectId,
  });

  const deleteMutation = useMutation({
    mutationFn: deleteAudienceAvatar,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["audience-avatars", projectId] });
    },
  });

  const handleRefresh = async () => {
    setRefreshing(true);
    await refetch();
    setRefreshing(false);
  };

  const handleAvatarPress = (avatar: AudienceAvatar) => {
    setSelectedAvatar(avatar);
    router.push("/audience/details");
  };

  const handleDelete = (avatar: AudienceAvatar) => {
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

  if (!projectId) {
    return (
      <AppScreen>
        <View style={styles.center}>
          <Text style={styles.muted}>{t("loading")}</Text>
        </View>
      </AppScreen>
    );
  }

  return (
    <AppScreen>
      <View style={styles.header}>
        <View style={{ flex: 1 }}>
          <Text style={styles.title}>{t("audienceAvatars")}</Text>
          <Text style={styles.subtitle}>{currentProject?.name}</Text>
        </View>
        <Button
          title={t("createAvatar")}
          onPress={() => router.push("/audience/create")}
          variant="secondary"
        />
      </View>

      {error ? (
        <View style={styles.card}>
          <Text style={styles.errorText}>
            {error instanceof Error ? error.message : String(error)}
          </Text>
          <View style={{ height: 12 }} />
          <Button title={t("loading")} onPress={() => refetch()} />
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
        <View style={styles.emptyCard}>
          <Text style={styles.emptyText}>{t("emptyAvatars")}</Text>
          <View style={{ height: 16 }} />
          <Button
            title={t("createAvatar")}
            onPress={() => router.push("/audience/create")}
            variant="primary"
          />
        </View>
      ) : null}

      {!isLoading && data?.length ? (
        <ScrollView
          style={styles.list}
          contentContainerStyle={{ paddingBottom: 24 }}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={handleRefresh}
              tintColor={colors.primary2}
            />
          }
        >
          {data.map((avatar) => (
            <AvatarCard
              key={avatar.id}
              avatar={avatar}
              onPress={() => handleAvatarPress(avatar)}
            />
          ))}
        </ScrollView>
      ) : null}
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    marginBottom: 16,
  },
  title: {
    color: colors.text,
    fontSize: 24,
    fontWeight: "800",
  },
  subtitle: {
    color: colors.muted,
    marginTop: 4,
    fontSize: 14,
  },
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
  },
  muted: {
    color: colors.muted,
  },
  card: {
    marginTop: 16,
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 16,
    padding: 14,
  },
  emptyCard: {
    marginTop: 32,
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 16,
    padding: 24,
    alignItems: "center",
  },
  emptyText: {
    color: colors.muted,
    textAlign: "center",
    fontSize: 15,
  },
  errorText: {
    color: colors.danger,
    fontWeight: "700",
  },
  list: {
    flex: 1,
    marginTop: 8,
  },
});
