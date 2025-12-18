import React from "react";
import {
  StyleSheet,
  Text,
  View,
} from "react-native";
import { useTranslation } from "react-i18next";
import { router, Stack } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

import { AppScreen } from "../../src/components/AppScreen";
import { Button } from "../../src/components/Button";
import { colors } from "../../src/theme/colors";
import { useBillingStore } from "../../src/store/billingStore";

export default function PendingPaymentScreen() {
  const { t } = useTranslation();
  const currentPaymentRequest = useBillingStore((s) => s.currentPaymentRequest);
  const setSelectedPlan = useBillingStore((s) => s.setSelectedPlan);
  const setCurrentPaymentRequest = useBillingStore((s) => s.setCurrentPaymentRequest);

  const handleGoBack = () => {
    setSelectedPlan(null);
    setCurrentPaymentRequest(null);
    router.replace("/(tabs)/dashboard");
  };

  return (
    <>
      <Stack.Screen
        options={{
          title: t("pendingPayment"),
          headerStyle: { backgroundColor: colors.bg },
          headerTintColor: colors.text,
          headerBackVisible: false,
        }}
      />
      <AppScreen>
        <View style={styles.container}>
          <View style={styles.iconContainer}>
            <View style={styles.iconCircle}>
              <Ionicons name="time-outline" size={64} color={colors.primary2} />
            </View>
          </View>

          <Text style={styles.title}>{t("pendingPayment")}</Text>
          <Text style={styles.description}>{t("paymentPending")}</Text>

          {currentPaymentRequest && (
            <View style={styles.detailsCard}>
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Тариф:</Text>
                <Text style={styles.detailValue}>{currentPaymentRequest.plan_name}</Text>
              </View>
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Сумма:</Text>
                <Text style={styles.detailValue}>${currentPaymentRequest.amount_usd} USD</Text>
              </View>
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Способ оплаты:</Text>
                <Text style={styles.detailValue}>
                  {currentPaymentRequest.payment_method === "crypto"
                    ? "Криптовалюта"
                    : currentPaymentRequest.payment_method === "bank"
                    ? "Банк. перевод"
                    : "PayPal"}
                </Text>
              </View>
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Статус:</Text>
                <View style={styles.statusBadge}>
                  <Ionicons name="hourglass-outline" size={14} color={colors.primary2} />
                  <Text style={styles.statusText}>Ожидает подтверждения</Text>
                </View>
              </View>
            </View>
          )}

          <View style={styles.infoCard}>
            <Ionicons name="mail-outline" size={24} color={colors.primary2} />
            <Text style={styles.infoText}>
              Мы уведомим вас по email, когда подписка будет активирована
            </Text>
          </View>

          <Button
            title="Вернуться на главную"
            onPress={handleGoBack}
            variant="secondary"
          />
        </View>
      </AppScreen>
    </>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 24,
  },
  iconContainer: {
    marginBottom: 24,
  },
  iconCircle: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: colors.primary2 + "20",
    alignItems: "center",
    justifyContent: "center",
  },
  title: {
    color: colors.text,
    fontSize: 24,
    fontWeight: "800",
    textAlign: "center",
  },
  description: {
    color: colors.muted,
    fontSize: 15,
    textAlign: "center",
    marginTop: 12,
    lineHeight: 22,
  },
  detailsCard: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 16,
    padding: 20,
    width: "100%",
    marginTop: 24,
    gap: 12,
  },
  detailRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  detailLabel: {
    color: colors.muted,
    fontSize: 14,
  },
  detailValue: {
    color: colors.text,
    fontSize: 14,
    fontWeight: "600",
  },
  statusBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    backgroundColor: colors.primary2 + "20",
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    color: colors.primary2,
    fontSize: 12,
    fontWeight: "600",
  },
  infoCard: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    backgroundColor: colors.card,
    borderRadius: 16,
    padding: 16,
    width: "100%",
    marginTop: 16,
    marginBottom: 24,
  },
  infoText: {
    color: colors.muted,
    fontSize: 14,
    flex: 1,
  },
});
