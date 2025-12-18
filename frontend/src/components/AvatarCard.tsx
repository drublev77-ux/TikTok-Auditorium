import React from "react";
import { View, Text, TouchableOpacity, StyleSheet, ScrollView } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../theme/colors";
import type { AudienceAvatar } from "../api/audience";

type Props = {
  avatar: AudienceAvatar;
  onPress: () => void;
};

export function AvatarCard({ avatar, onPress }: Props) {
  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.7}>
      <View style={styles.header}>
        <View style={styles.iconCircle}>
          <Ionicons name="person-circle-outline" size={32} color={colors.primary2} />
        </View>
        <View style={styles.headerText}>
          <Text style={styles.name} numberOfLines={1}>{avatar.name}</Text>
          <View style={styles.geoRow}>
            <Ionicons name="location-outline" size={14} color={colors.muted} />
            <Text style={styles.geo}>{avatar.geolocation}</Text>
          </View>
        </View>
        <Ionicons name="chevron-forward" size={22} color={colors.muted} />
      </View>
      
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.tagsRow}>
        {avatar.hashtags.slice(0, 5).map((tag) => (
          <View key={tag} style={styles.tag}>
            <Text style={styles.tagText}>{tag}</Text>
          </View>
        ))}
        {avatar.hashtags.length > 5 && (
          <View style={styles.moreTag}>
            <Text style={styles.moreText}>+{avatar.hashtags.length - 5}</Text>
          </View>
        )}
      </ScrollView>
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
  },
  iconCircle: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.card2,
    alignItems: "center",
    justifyContent: "center",
    marginRight: 12,
  },
  headerText: {
    flex: 1,
  },
  name: {
    color: colors.text,
    fontSize: 17,
    fontWeight: "700",
  },
  geoRow: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: 4,
    gap: 4,
  },
  geo: {
    color: colors.muted,
    fontSize: 13,
  },
  tagsRow: {
    marginTop: 12,
    flexDirection: "row",
  },
  tag: {
    backgroundColor: colors.card2,
    borderRadius: 12,
    paddingHorizontal: 10,
    paddingVertical: 5,
    marginRight: 6,
  },
  tagText: {
    color: colors.primary2,
    fontSize: 12,
    fontWeight: "600",
  },
  moreTag: {
    backgroundColor: colors.border,
    borderRadius: 12,
    paddingHorizontal: 10,
    paddingVertical: 5,
  },
  moreText: {
    color: colors.muted,
    fontSize: 12,
    fontWeight: "600",
  },
});
