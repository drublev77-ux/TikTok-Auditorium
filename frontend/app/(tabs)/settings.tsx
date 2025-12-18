import React from "react";
import { StyleSheet, Text, View, TouchableOpacity, ScrollView } from "react-native";
import { useTranslation } from "react-i18next";
import { router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import { AppScreen } from "../../src/components/AppScreen";
import { Button } from "../../src/components/Button";
import { colors } from "../../src/theme/colors";
import { setLang } from "../../src/i18n";

export default function SettingsTab() {
  const { t, i18n } = useTranslation();

  return (
    <AppScreen>
      <ScrollView style={styles.scroll}>
        {/* Billing Card */}
        <TouchableOpacity
          style={styles.billingCard}
          onPress={() => router.push("/billing")}
          activeOpacity={0.7}
        >
          <View style={styles.billingIcon}>
            <Ionicons name="card-outline" size={28} color={colors.primary} />
          </View>
          <View style={styles.billingText}>
            <Text style={styles.billingTitle}>{t("billing")}</Text>
            <Text style={styles.billingSubtitle}>{t("choosePlan")}</Text>
          </View>
          <Ionicons name="chevron-forward" size={22} color={colors.muted} />
        </TouchableOpacity>

        {/* Language Card */}
        <View style={styles.card}>
          <Text style={styles.h}>{t("switchLanguage")}</Text>

          <View style={{ height: 12 }} />

          <View style={styles.row}>
            <Button
              title={t("ru")}
              onPress={() => setLang("ru")}
              variant={i18n.language === "ru" ? "primary" : "secondary"}
            />
            <Button
              title={t("en")}
              onPress={() => setLang("en")}
              variant={i18n.language === "en" ? "primary" : "secondary"}
            />
          </View>
        </View>
      </ScrollView>
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  scroll: {
    flex: 1,
  },
  billingCard: {
    backgroundColor: colors.card,
    borderColor: colors.primary,
    borderWidth: 1,
    borderRadius: 16,
    padding: 16,
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 16,
  },
  billingIcon: {
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: colors.primary + "20",
    alignItems: "center",
    justifyContent: "center",
    marginRight: 14,
  },
  billingText: {
    flex: 1,
  },
  billingTitle: {
    color: colors.text,
    fontSize: 17,
    fontWeight: "700",
  },
  billingSubtitle: {
    color: colors.muted,
    fontSize: 13,
    marginTop: 2,
  },
  card: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 16,
    padding: 14,
  },
  h: {
    color: colors.text,
    fontSize: 18,
    fontWeight: "800",
  },
  p: {
    color: colors.muted,
    marginTop: 8,
  },
  row: {
    flexDirection: "row",
    gap: 12,
    marginTop: 8,
  },
});
