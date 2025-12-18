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
  Switch,
} from "react-native";
import { useTranslation } from "react-i18next";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Ionicons } from "@expo/vector-icons";

import { AppScreen } from "../../src/components/AppScreen";
import { Button } from "../../src/components/Button";
import { colors } from "../../src/theme/colors";
import { useProject } from "../../src/store/ProjectContext";
import {
  generateContentIdeas,
  listContentPlans,
  createContentPlan,
  deleteContentPlan,
} from "../../src/api/planner";
import type { ContentIdea, ContentPlan } from "../../src/api/planner";

const CONTENT_TYPES = [
  { id: "video", icon: "videocam-outline" },
  { id: "trend", icon: "trending-up-outline" },
  { id: "educational", icon: "school-outline" },
  { id: "promotional", icon: "megaphone-outline" },
];

export default function PlannerTab() {
  const { t } = useTranslation();
  const { currentProject } = useProject();
  const queryClient = useQueryClient();
  const [refreshing, setRefreshing] = useState(false);
  
  // Generate Ideas State
  const [showIdeaModal, setShowIdeaModal] = useState(false);
  const [topic, setTopic] = useState("");
  const [contentType, setContentType] = useState<"video" | "trend" | "educational" | "promotional">("video");
  const [generatedIdeas, setGeneratedIdeas] = useState<ContentIdea[]>([]);
  const [showIdeasResult, setShowIdeasResult] = useState(false);
  
  // Add Post State
  const [showAddModal, setShowAddModal] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDate, setNewDate] = useState("");
  const [newTime, setNewTime] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const [hasAdLabel, setHasAdLabel] = useState(false);

  const projectId = currentProject?.id;

  const { data: plans, isLoading, refetch } = useQuery({
    queryKey: ["content-plans", projectId],
    queryFn: () => listContentPlans(projectId!),
    enabled: !!projectId,
  });

  const generateMutation = useMutation({
    mutationFn: generateContentIdeas,
    onSuccess: (data) => {
      setGeneratedIdeas(data.ideas || []);
      setShowIdeaModal(false);
      setShowIdeasResult(true);
    },
    onError: (err) => {
      const msg = err instanceof Error ? err.message : "Error";
      Platform.OS === "web" ? window.alert(msg) : Alert.alert("Error", msg);
    },
  });

  const createMutation = useMutation({
    mutationFn: createContentPlan,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["content-plans", projectId] });
      setShowAddModal(false);
      resetAddForm();
    },
  });

  const deleteMutation = useMutation({
    mutationFn: deleteContentPlan,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["content-plans", projectId] });
    },
  });

  const resetAddForm = () => {
    setNewTitle("");
    setNewDate("");
    setNewTime("");
    setNewDescription("");
    setHasAdLabel(false);
  };

  const handleGenerate = () => {
    if (!topic.trim() || !projectId) return;
    generateMutation.mutate({
      project_id: projectId,
      topic: topic.trim(),
      content_type: contentType,
      count: 5,
    });
  };

  const handleUseIdea = (idea: ContentIdea) => {
    setNewTitle(idea.title);
    setNewDescription(idea.description);
    setShowIdeasResult(false);
    setShowAddModal(true);
  };

  const handleAddPost = () => {
    if (!newTitle.trim() || !newDate || !newTime || !projectId) return;
    createMutation.mutate({
      project_id: projectId,
      title: newTitle.trim(),
      scheduled_date: newDate,
      scheduled_time: newTime,
      content_type: contentType,
      description: newDescription.trim() || undefined,
      has_ad_label: hasAdLabel,
      status: "scheduled",
    });
  };

  const handleDelete = (plan: ContentPlan) => {
    if (Platform.OS === "web") {
      if (window.confirm(t("confirmDelete"))) {
        deleteMutation.mutate(plan.id);
      }
    } else {
      Alert.alert(t("delete"), t("confirmDelete"), [
        { text: t("no"), style: "cancel" },
        { text: t("yes"), style: "destructive", onPress: () => deleteMutation.mutate(plan.id) },
      ]);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await refetch();
    setRefreshing(false);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "draft": return colors.muted;
      case "scheduled": return colors.primary2;
      case "published": return colors.success;
      default: return colors.muted;
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
          <Text style={styles.title}>{t("contentPlanner")}</Text>
          <Text style={styles.subtitle}>{currentProject?.name}</Text>
        </View>
      </View>

      {/* Action Buttons */}
      <View style={styles.actionsRow}>
        <TouchableOpacity style={styles.actionBtn} onPress={() => setShowIdeaModal(true)}>
          <Ionicons name="bulb-outline" size={20} color={colors.text} />
          <Text style={styles.actionText}>{t("generateIdeas")}</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.actionBtn, styles.primaryBtn]} onPress={() => setShowAddModal(true)}>
          <Ionicons name="add" size={20} color={colors.text} />
          <Text style={styles.actionText}>{t("addPost")}</Text>
        </TouchableOpacity>
      </View>

      {isLoading ? (
        <View style={styles.center}>
          <ActivityIndicator color={colors.primary2} />
        </View>
      ) : !plans?.length ? (
        <View style={styles.emptyCard}>
          <Ionicons name="calendar-outline" size={48} color={colors.border} />
          <Text style={styles.emptyText}>{t("emptyPlanner")}</Text>
        </View>
      ) : (
        <ScrollView
          style={styles.list}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={handleRefresh} tintColor={colors.primary2} />}
        >
          <Text style={styles.sectionTitle}>{t("scheduledPosts")}</Text>
          {plans.map((plan) => (
            <View key={plan.id} style={styles.planCard}>
              <View style={styles.planHeader}>
                <View style={[styles.statusDot, { backgroundColor: getStatusColor(plan.status) }]} />
                <Text style={styles.planTitle} numberOfLines={1}>{plan.title}</Text>
                <TouchableOpacity onPress={() => handleDelete(plan)}>
                  <Ionicons name="trash-outline" size={18} color={colors.danger} />
                </TouchableOpacity>
              </View>
              <View style={styles.planMeta}>
                <View style={styles.metaItem}>
                  <Ionicons name="calendar-outline" size={14} color={colors.muted} />
                  <Text style={styles.metaText}>{plan.scheduled_date}</Text>
                </View>
                <View style={styles.metaItem}>
                  <Ionicons name="time-outline" size={14} color={colors.muted} />
                  <Text style={styles.metaText}>{plan.scheduled_time}</Text>
                </View>
                {plan.has_ad_label && (
                  <View style={styles.adBadge}>
                    <Text style={styles.adBadgeText}>AD</Text>
                  </View>
                )}
              </View>
              {plan.description && (
                <Text style={styles.planDesc} numberOfLines={2}>{plan.description}</Text>
              )}
            </View>
          ))}
        </ScrollView>
      )}

      {/* Generate Ideas Modal */}
      <Modal visible={showIdeaModal} animationType="slide" transparent>
        <KeyboardAvoidingView style={styles.modalOverlay} behavior={Platform.OS === "ios" ? "padding" : "height"}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>{t("generateIdeas")}</Text>
              <TouchableOpacity onPress={() => setShowIdeaModal(false)}>
                <Ionicons name="close" size={24} color={colors.text} />
              </TouchableOpacity>
            </View>
            
            <Text style={styles.label}>{t("topic")}</Text>
            <TextInput
              style={styles.input}
              value={topic}
              onChangeText={setTopic}
              placeholder={t("topicPlaceholder")}
              placeholderTextColor={colors.muted}
            />
            
            <Text style={styles.label}>{t("contentType")}</Text>
            <View style={styles.typeRow}>
              {CONTENT_TYPES.map((type) => (
                <TouchableOpacity
                  key={type.id}
                  style={[styles.typeChip, contentType === type.id && styles.typeChipActive]}
                  onPress={() => setContentType(type.id as any)}
                >
                  <Ionicons
                    name={type.icon as any}
                    size={18}
                    color={contentType === type.id ? colors.bg : colors.muted}
                  />
                  <Text style={[styles.typeText, contentType === type.id && styles.typeTextActive]}>
                    {t(type.id)}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
            
            <View style={{ height: 20 }} />
            <Button
              title={generateMutation.isPending ? t("generating") : t("generateBtn")}
              onPress={handleGenerate}
              loading={generateMutation.isPending}
              disabled={!topic.trim()}
              variant="primary"
            />
          </View>
        </KeyboardAvoidingView>
      </Modal>

      {/* Ideas Result Modal */}
      <Modal visible={showIdeasResult} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { maxHeight: "80%" }]}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>{t("contentIdeas")}</Text>
              <TouchableOpacity onPress={() => setShowIdeasResult(false)}>
                <Ionicons name="close" size={24} color={colors.text} />
              </TouchableOpacity>
            </View>
            
            <ScrollView style={{ flex: 1 }}>
              {generatedIdeas.map((idea, idx) => (
                <View key={idx} style={styles.ideaCard}>
                  <Text style={styles.ideaTitle}>{idea.title}</Text>
                  <Text style={styles.ideaDesc}>{idea.description}</Text>
                  
                  <View style={styles.ideaMeta}>
                    <Text style={styles.ideaLabel}>{t("hook")}:</Text>
                    <Text style={styles.ideaValue}>{idea.hook}</Text>
                  </View>
                  <View style={styles.ideaMeta}>
                    <Text style={styles.ideaLabel}>{t("bestTime")}:</Text>
                    <Text style={styles.ideaValue}>{idea.best_posting_time}</Text>
                  </View>
                  <View style={styles.ideaMeta}>
                    <Text style={styles.ideaLabel}>{t("duration")}:</Text>
                    <Text style={styles.ideaValue}>{idea.estimated_duration}</Text>
                  </View>
                  
                  <View style={styles.hashtagsRow}>
                    {idea.hashtags?.slice(0, 5).map((tag, i) => (
                      <Text key={i} style={styles.hashtagChip}>{tag}</Text>
                    ))}
                  </View>
                  
                  <TouchableOpacity style={styles.useBtn} onPress={() => handleUseIdea(idea)}>
                    <Text style={styles.useBtnText}>{t("useIdea")}</Text>
                  </TouchableOpacity>
                </View>
              ))}
            </ScrollView>
          </View>
        </View>
      </Modal>

      {/* Add Post Modal */}
      <Modal visible={showAddModal} animationType="slide" transparent>
        <KeyboardAvoidingView style={styles.modalOverlay} behavior={Platform.OS === "ios" ? "padding" : "height"}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>{t("addPost")}</Text>
              <TouchableOpacity onPress={() => { setShowAddModal(false); resetAddForm(); }}>
                <Ionicons name="close" size={24} color={colors.text} />
              </TouchableOpacity>
            </View>
            
            <ScrollView>
              <Text style={styles.label}>{t("postTitle")}</Text>
              <TextInput
                style={styles.input}
                value={newTitle}
                onChangeText={setNewTitle}
                placeholder={t("postTitle")}
                placeholderTextColor={colors.muted}
              />
              
              <View style={styles.row}>
                <View style={{ flex: 1 }}>
                  <Text style={styles.label}>{t("scheduledDate")}</Text>
                  <TextInput
                    style={styles.input}
                    value={newDate}
                    onChangeText={setNewDate}
                    placeholder="2024-12-25"
                    placeholderTextColor={colors.muted}
                  />
                </View>
                <View style={{ width: 12 }} />
                <View style={{ flex: 1 }}>
                  <Text style={styles.label}>{t("scheduledTime")}</Text>
                  <TextInput
                    style={styles.input}
                    value={newTime}
                    onChangeText={setNewTime}
                    placeholder="18:00"
                    placeholderTextColor={colors.muted}
                  />
                </View>
              </View>
              
              <Text style={styles.label}>{t("notes")}</Text>
              <TextInput
                style={[styles.input, { minHeight: 80 }]}
                value={newDescription}
                onChangeText={setNewDescription}
                placeholder={t("notesPlaceholder")}
                placeholderTextColor={colors.muted}
                multiline
              />
              
              <View style={styles.switchRow}>
                <View>
                  <Text style={styles.switchLabel}>{t("adLabel")}</Text>
                  <Text style={styles.switchHint}>{t("adLabelHint")}</Text>
                </View>
                <Switch
                  value={hasAdLabel}
                  onValueChange={setHasAdLabel}
                  trackColor={{ true: colors.primary }}
                />
              </View>
            </ScrollView>
            
            <View style={{ height: 16 }} />
            <Button
              title={t("save")}
              onPress={handleAddPost}
              loading={createMutation.isPending}
              disabled={!newTitle.trim() || !newDate || !newTime}
              variant="primary"
            />
          </View>
        </KeyboardAvoidingView>
      </Modal>
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  header: { flexDirection: "row", alignItems: "center", marginBottom: 16 },
  title: { color: colors.text, fontSize: 24, fontWeight: "800" },
  subtitle: { color: colors.muted, marginTop: 4, fontSize: 14 },
  actionsRow: { flexDirection: "row", gap: 12, marginBottom: 20 },
  actionBtn: { flex: 1, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 8, backgroundColor: colors.card, borderColor: colors.border, borderWidth: 1, borderRadius: 12, paddingVertical: 12 },
  primaryBtn: { backgroundColor: colors.primary },
  actionText: { color: colors.text, fontSize: 14, fontWeight: "600" },
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  muted: { color: colors.muted },
  emptyCard: { marginTop: 32, backgroundColor: colors.card, borderColor: colors.border, borderWidth: 1, borderRadius: 16, padding: 24, alignItems: "center" },
  emptyText: { color: colors.muted, textAlign: "center", fontSize: 15, marginTop: 12 },
  list: { flex: 1 },
  sectionTitle: { color: colors.text, fontSize: 18, fontWeight: "700", marginBottom: 12 },
  planCard: { backgroundColor: colors.card, borderColor: colors.border, borderWidth: 1, borderRadius: 14, padding: 14, marginBottom: 10 },
  planHeader: { flexDirection: "row", alignItems: "center", gap: 10 },
  statusDot: { width: 8, height: 8, borderRadius: 4 },
  planTitle: { flex: 1, color: colors.text, fontSize: 15, fontWeight: "700" },
  planMeta: { flexDirection: "row", alignItems: "center", gap: 16, marginTop: 10 },
  metaItem: { flexDirection: "row", alignItems: "center", gap: 4 },
  metaText: { color: colors.muted, fontSize: 12 },
  adBadge: { backgroundColor: colors.primary, paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 },
  adBadgeText: { color: colors.bg, fontSize: 10, fontWeight: "700" },
  planDesc: { color: colors.muted, fontSize: 13, marginTop: 8 },
  modalOverlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.7)", justifyContent: "flex-end" },
  modalContent: { backgroundColor: colors.bg, borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: 24, paddingBottom: 40 },
  modalHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 20 },
  modalTitle: { color: colors.text, fontSize: 20, fontWeight: "800" },
  label: { color: colors.text, fontSize: 14, fontWeight: "600", marginBottom: 8, marginTop: 12 },
  input: { backgroundColor: colors.card, borderColor: colors.border, borderWidth: 1, borderRadius: 12, padding: 14, color: colors.text, fontSize: 16 },
  typeRow: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  typeChip: { flexDirection: "row", alignItems: "center", gap: 6, backgroundColor: colors.card, borderColor: colors.border, borderWidth: 1, borderRadius: 10, paddingHorizontal: 12, paddingVertical: 8 },
  typeChipActive: { backgroundColor: colors.primary2, borderColor: colors.primary2 },
  typeText: { color: colors.muted, fontSize: 12 },
  typeTextActive: { color: colors.bg, fontWeight: "600" },
  ideaCard: { backgroundColor: colors.card, borderColor: colors.border, borderWidth: 1, borderRadius: 14, padding: 14, marginBottom: 12 },
  ideaTitle: { color: colors.text, fontSize: 16, fontWeight: "700" },
  ideaDesc: { color: colors.muted, fontSize: 13, marginTop: 6, lineHeight: 20 },
  ideaMeta: { flexDirection: "row", marginTop: 8 },
  ideaLabel: { color: colors.primary2, fontSize: 12, fontWeight: "600", width: 100 },
  ideaValue: { color: colors.text, fontSize: 12, flex: 1 },
  hashtagsRow: { flexDirection: "row", flexWrap: "wrap", gap: 6, marginTop: 10 },
  hashtagChip: { backgroundColor: colors.card2, color: colors.primary2, fontSize: 11, paddingHorizontal: 8, paddingVertical: 4, borderRadius: 8, overflow: "hidden" },
  useBtn: { backgroundColor: colors.primary, borderRadius: 10, paddingVertical: 10, alignItems: "center", marginTop: 12 },
  useBtnText: { color: colors.text, fontSize: 14, fontWeight: "700" },
  row: { flexDirection: "row" },
  switchRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginTop: 16, paddingVertical: 12, borderTopWidth: 1, borderTopColor: colors.border },
  switchLabel: { color: colors.text, fontSize: 14, fontWeight: "600" },
  switchHint: { color: colors.muted, fontSize: 12, marginTop: 2 },
});
