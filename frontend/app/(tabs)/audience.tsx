import React from "react";
import { StyleSheet, Text, View } from "react-native";
import { useTranslation } from "react-i18next";
import { AppScreen } from "../../src/components/AppScreen";
import { colors } from "../../src/theme/colors";

export default function AudienceTab() {
  const { t } = useTranslation();
  return (
    <AppScreen>
      <View style={styles.card}>
        <Text style={styles.h}>{t("audience")}</Text>
        <Text style={styles.p}>MVP: здесь появится создание и просмотр аватара ЦА.</Text>
      </View>
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  card: { backgroundColor: colors.card, borderColor: colors.border, borderWidth: 1, borderRadius: 16, padding: 14 },
  h: { color: colors.text, fontSize: 18, fontWeight: "800" },
  p: { color: colors.muted, marginTop: 8 },
});
