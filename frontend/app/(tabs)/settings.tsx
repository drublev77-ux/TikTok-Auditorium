import React from "react";
import { StyleSheet, Text, View } from "react-native";
import { useTranslation } from "react-i18next";
import { AppScreen } from "../../src/components/AppScreen";
import { Button } from "../../src/components/Button";
import { colors } from "../../src/theme/colors";
import { setLang } from "../../src/i18n";

export default function SettingsTab() {
  const { t, i18n } = useTranslation();

  return (
    <AppScreen>
      <View style={styles.card}>
        <Text style={styles.h}>{t("settings")}</Text>
        <Text style={styles.p}>{t("switchLanguage")}</Text>

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
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  card: { backgroundColor: colors.card, borderColor: colors.border, borderWidth: 1, borderRadius: 16, padding: 14 },
  h: { color: colors.text, fontSize: 18, fontWeight: "800" },
  p: { color: colors.muted, marginTop: 8 },
  row: { flexDirection: "row", gap: 12, marginTop: 8 },
});
