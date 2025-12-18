import React, { useState } from "react";
import {
  StyleSheet,
  Text,
  View,
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  Platform,
  Modal,
  KeyboardAvoidingView,
} from "react-native";
import { useTranslation } from "react-i18next";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Ionicons } from "@expo/vector-icons";

import { AppScreen } from "../../src/components/AppScreen";
import { Button } from "../../src/components/Button";
import { colors } from "../../src/theme/colors";
import { useProject } from "../../src/store/ProjectContext";
import { listCreators, createCreator, deleteCreator, listCreatorCategories } from "../../src/api/creators";
import type { Creator } from "../../src/api/creators";

const PRESET_CATEGORIES = ["general", "fitness", "beauty", "tech", "food", "travel", "gaming", "music", "fashion"];

export default function CreatorsTab() {
  const { t } = useTranslation();
  const { currentProject } = useProject();
  const queryClient = useQueryClient();
  const [refreshing, setRefreshing] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  
  // Form state
  const [newName, setNewName] = useState("");
  const [newUrl, setNewUrl] = useState("");
  const [newCategory, setNewCategory] = useState("general");

  const projectId = currentProject?.id;

  const { data: categories } = useQuery({
    queryKey: ["creator-categories", projectId],
    queryFn: () => listCreatorCategories(projectId!),
    enabled: !!projectId,
  });

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["creators", projectId, selectedCategory],
    queryFn: () => listCreators(projectId!, selectedCategory || undefined),
    enabled: !!projectId,
  });

  const createMutation = useMutation({
    mutationFn: createCreator,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["creators", projectId] });
      queryClient.invalidateQueries({ queryKey: ["creator-categories", projectId] });
      setModalVisible(false);
      setNewName("");
      setNewUrl("");
      setNewCategory("general");
    },
    onError: (err) => {
      const msg = err instanceof Error ? err.message : "Error";
      Platform.OS === "web" ? window.alert(msg) : Alert.alert("Error", msg);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteCreator,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["creators", projectId] });
    },
  });

  const handleRefresh = async () => {
    setRefreshing(true);
    await refetch();
    setRefreshing(false);
  };

  const handleAdd = () => {
    if (!newName.trim() || !newUrl.trim() || !projectId) return;
    createMutation.mutate({
      project_id: projectId,
      name: newName.trim(),
      tiktok_url: newUrl.trim(),
      category: newCategory,
    });
  };

  const handleDelete = (item: Creator) => {
    if (Platform.OS === "web") {
      if (window.confirm(t("confirmDelete"))) {
        deleteMutation.mutate(item.id);
      }
    } else {
      Alert.alert(t("delete"), t("confirmDelete"), [
        { text: t("no"), style: "cancel" },
        { text: t("yes"), style: "destructive", onPress: () => deleteMutation.mutate(item.id) },
      ]);
    }
  };

  const allCategories = [...new Set([...PRESET_CATEGORIES, ...(categories || [])])];

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
          <Text style={styles.title}>{t("creatorsList")}</Text>
          <Text style={styles.subtitle}>{currentProject?.name}</Text>
        </View>
        <TouchableOpacity style={styles.addBtn} onPress={() => setModalVisible(true)}>
          <Ionicons name="add" size={24} color={colors.text} />
        </TouchableOpacity>
      </View>

      {/* Category Filter */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterRow}>
        <TouchableOpacity
          style={[styles.filterChip, !selectedCategory && styles.filterChipActive]}
          onPress={() => setSelectedCategory(null)}
        >
          <Text style={[styles.filterText, !selectedCategory && styles.filterTextActive]}>
            {t("allCategories")}
          </Text>
        </TouchableOpacity>
        {allCategories.map((cat) => (
          <TouchableOpacity
            key={cat}
            style={[styles.filterChip, selectedCategory === cat && styles.filterChipActive]}
            onPress={() => setSelectedCategory(cat === selectedCategory ? null : cat)}
          >
            <Text style={[styles.filterText, selectedCategory === cat && styles.filterTextActive]}>
              {cat}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {error ? (
        <View style={styles.card}>
          <Text style={styles.errorText}>{error instanceof Error ? error.message : "Error"}</Text>
        </View>
      ) : null}

      {isLoading ? (
        <View style={styles.center}>
          <ActivityIndicator color={colors.primary2} />
          <Text style={styles.muted}>{t("loading")}</Text>
        </View>
      ) : null}

      {!isLoading && !data?.length ? (
        <View style={styles.emptyCard}>
          <Ionicons name="people-outline" size={48} color={colors.border} />
          <Text style={styles.emptyText}>{t("emptyCreators")}</Text>
          <View style={{ height: 16 }} />
          <Button title={t("addCreator")} onPress={() => setModalVisible(true)} variant="primary" />
        </View>
      ) : null}

      {!isLoading && data?.length ? (
        <ScrollView
          style={styles.list}
          contentContainerStyle={{ paddingBottom: 24 }}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={handleRefresh} tintColor={colors.primary2} />}
        >
          {data.map((item) => (
            <View key={item.id} style={styles.itemCard}>
              <View style={styles.itemHeader}>
                <View style={styles.itemIcon}>
                  <Ionicons name="person-outline" size={24} color={colors.primary2} />
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={styles.itemName}>{item.name}</Text>
                  <View style={styles.categoryBadge}>
                    <Text style={styles.categoryText}>{item.category}</Text>
                  </View>
                </View>
                <TouchableOpacity onPress={() => handleDelete(item)} hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
                  <Ionicons name="trash-outline" size={20} color={colors.danger} />
                </TouchableOpacity>
              </View>
              
              <Text style={styles.itemUrl} numberOfLines={1}>{item.tiktok_url}</Text>
              
              <View style={styles.metricsRow}>
                <View style={styles.metricBox}>
                  <Text style={styles.metricLabel}>{t("followers")}</Text>
                  <Text style={styles.metricValue}>{item.followers ?? "—"}</Text>
                </View>
                <View style={styles.metricBox}>
                  <Text style={styles.metricLabel}>{t("avgViews")}</Text>
                  <Text style={styles.metricValue}>{item.avg_views ?? "—"}</Text>
                </View>
                <View style={[styles.metricBox, styles.matchBox]}>
                  <Text style={styles.metricLabel}>{t("audienceMatch")}</Text>
                  <Text style={[styles.metricValue, styles.matchValue]}>
                    {item.audience_match_score ? `${item.audience_match_score}%` : "—"}
                  </Text>
                </View>
              </View>
              
              {!item.followers && (
                <Text style={styles.placeholderText}>{t("metricsPlaceholder")}</Text>
              )}
            </View>
          ))}
        </ScrollView>
      ) : null}

      {/* Add Modal */}
      <Modal visible={modalVisible} animationType="slide" transparent>
        <KeyboardAvoidingView style={styles.modalOverlay} behavior={Platform.OS === "ios" ? "padding" : "height"}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>{t("addCreator")}</Text>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <Ionicons name="close" size={24} color={colors.text} />
              </TouchableOpacity>
            </View>
            
            <Text style={styles.label}>{t("creatorName")}</Text>
            <TextInput
              style={styles.input}
              value={newName}
              onChangeText={setNewName}
              placeholder={t("creatorName")}
              placeholderTextColor={colors.muted}
            />
            
            <Text style={styles.label}>{t("tiktokUrl")}</Text>
            <TextInput
              style={styles.input}
              value={newUrl}
              onChangeText={setNewUrl}
              placeholder="https://tiktok.com/@creator"
              placeholderTextColor={colors.muted}
              autoCapitalize="none"
              keyboardType="url"
            />
            
            <Text style={styles.label}>{t("category")}</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.categoryPicker}>
              {PRESET_CATEGORIES.map((cat) => (
                <TouchableOpacity
                  key={cat}
                  style={[styles.categoryChip, newCategory === cat && styles.categoryChipActive]}
                  onPress={() => setNewCategory(cat)}
                >
                  <Text style={[styles.categoryChipText, newCategory === cat && styles.categoryChipTextActive]}>
                    {cat}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
            
            <View style={{ height: 20 }} />
            <Button
              title={t("save")}
              onPress={handleAdd}
              loading={createMutation.isPending}
              disabled={!newName.trim() || !newUrl.trim()}
              variant="primary"
            />
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", gap: 12, marginBottom: 12 },
  title: { color: colors.text, fontSize: 24, fontWeight: "800" },
  subtitle: { color: colors.muted, marginTop: 4, fontSize: 14 },
  addBtn: { backgroundColor: colors.primary2, width: 44, height: 44, borderRadius: 22, alignItems: "center", justifyContent: "center" },
  filterRow: { marginBottom: 16, flexGrow: 0 },
  filterChip: { backgroundColor: colors.card, borderColor: colors.border, borderWidth: 1, borderRadius: 20, paddingHorizontal: 14, paddingVertical: 8, marginRight: 8 },
  filterChipActive: { backgroundColor: colors.primary2, borderColor: colors.primary2 },
  filterText: { color: colors.muted, fontSize: 13, fontWeight: "600" },
  filterTextActive: { color: colors.bg },
  center: { flex: 1, alignItems: "center", justifyContent: "center", gap: 12 },
  muted: { color: colors.muted },
  card: { backgroundColor: colors.card, borderColor: colors.border, borderWidth: 1, borderRadius: 16, padding: 14 },
  errorText: { color: colors.danger, fontWeight: "700" },
  emptyCard: { marginTop: 32, backgroundColor: colors.card, borderColor: colors.border, borderWidth: 1, borderRadius: 16, padding: 24, alignItems: "center" },
  emptyText: { color: colors.muted, textAlign: "center", fontSize: 15, marginTop: 12 },
  list: { flex: 1 },
  itemCard: { backgroundColor: colors.card, borderColor: colors.border, borderWidth: 1, borderRadius: 16, padding: 16, marginBottom: 12 },
  itemHeader: { flexDirection: "row", alignItems: "center", gap: 12 },
  itemIcon: { width: 44, height: 44, borderRadius: 22, backgroundColor: colors.primary2 + "20", alignItems: "center", justifyContent: "center" },
  itemName: { color: colors.text, fontSize: 16, fontWeight: "700" },
  categoryBadge: { backgroundColor: colors.card2, borderRadius: 8, paddingHorizontal: 8, paddingVertical: 2, alignSelf: "flex-start", marginTop: 4 },
  categoryText: { color: colors.primary2, fontSize: 11, fontWeight: "600" },
  itemUrl: { color: colors.muted, fontSize: 12, marginTop: 8 },
  metricsRow: { flexDirection: "row", marginTop: 12, gap: 8 },
  metricBox: { flex: 1, backgroundColor: colors.card2, borderRadius: 12, padding: 10, alignItems: "center" },
  matchBox: { backgroundColor: colors.primary2 + "15" },
  metricLabel: { color: colors.muted, fontSize: 10 },
  metricValue: { color: colors.text, fontSize: 14, fontWeight: "700", marginTop: 2 },
  matchValue: { color: colors.primary2 },
  placeholderText: { color: colors.muted, fontSize: 11, textAlign: "center", marginTop: 10, fontStyle: "italic" },
  modalOverlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.7)", justifyContent: "flex-end" },
  modalContent: { backgroundColor: colors.bg, borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 24, paddingBottom: 40 },
  modalHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 16 },
  modalTitle: { color: colors.text, fontSize: 20, fontWeight: "800" },
  label: { color: colors.text, fontSize: 14, fontWeight: "600", marginBottom: 8, marginTop: 12 },
  input: { backgroundColor: colors.card, borderColor: colors.border, borderWidth: 1, borderRadius: 12, padding: 14, color: colors.text, fontSize: 16 },
  categoryPicker: { marginTop: 8, flexGrow: 0 },
  categoryChip: { backgroundColor: colors.card, borderColor: colors.border, borderWidth: 1, borderRadius: 16, paddingHorizontal: 14, paddingVertical: 8, marginRight: 8 },
  categoryChipActive: { backgroundColor: colors.primary2, borderColor: colors.primary2 },
  categoryChipText: { color: colors.muted, fontSize: 13 },
  categoryChipTextActive: { color: colors.bg, fontWeight: "600" },
});
