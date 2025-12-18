import React from "react";
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  TouchableOpacity,
  Alert,
  Platform,
  Linking,
} from "react-native";
import { useTranslation } from "react-i18next";
import { useMutation, useQuery } from "@tanstack/react-query";
import { router, Stack } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

import { AppScreen } from "../../src/components/AppScreen";
import { Button } from "../../src/components/Button";
import { colors } from "../../src/theme/colors";
import { useBillingStore } from "../../src/store/billingStore";
import { useProject } from "../../src/store/ProjectContext";
import { getPaymentMethods, createPaymentRequest } from "../../src/api/billing";

export default function PayPalPaymentScreen() {
  const { t } = useTranslation();
  const selectedPlan = useBillingStore((s) => s.selectedPlan);
  const setCurrentPaymentRequest = useBillingStore((s) => s.setCurrentPaymentRequest);
  const { currentProject } = useProject();

  const { data: paymentMethods } = useQuery({
    queryKey: ["payment-methods"],
    queryFn: getPaymentMethods,
  });

  const createPaymentMutation = useMutation({
    mutationFn: createPaymentRequest,
    onSuccess: (data) => {
      setCurrentPaymentRequest(data);
      router.push("/billing/pending");
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

  const handleOpenPayPal = () => {
    const paypalAccount = paymentMethods?.paypal?.account || "TPFTECHNOLOGI";
    const paypalUrl = `https://paypal.me/${paypalAccount}/${selectedPlan?.price_usd || 50}`;
    Linking.openURL(paypalUrl);
  };

  const handleConfirmPayment = () => {
    if (!currentProject) return;

    createPaymentMutation.mutate({
      org_id: currentProject.org_id,
      plan_id: selectedPlan!.id,
      payment_method: "paypal",
    });
  };

  if (!selectedPlan) {
    router.replace("/billing");
    return null;
  }

  const paypalAccount = paymentMethods?.paypal?.account || "TPFTECHNOLOGI";

  return (
    <>
      <Stack.Screen
        options={{
          title: t("paypalPayment"),
          headerStyle: { backgroundColor: colors.bg },
          headerTintColor: colors.text,
        }}
      />
      <AppScreen>
        <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent}>
          {/* Amount */}
          <View style={styles.amountCard}>
            <Text style={styles.amountLabel}>{t("sendExactAmount")}</Text>
            <Text style={styles.amountValue}>${selectedPlan.price_usd} USD</Text>
          </View>

          {/* PayPal Logo */}
          <View style={styles.paypalCard}>
            <View style={styles.paypalLogo}>
              <Ionicons name="logo-paypal" size={64} color="#0070BA" />
            </View>
            <Text style={styles.paypalTitle}>{t("sendToPaypal")}</Text>
            <Text style={styles.paypalAccount}>{paypalAccount}</Text>

            <TouchableOpacity style={styles.openPaypalButton} onPress={handleOpenPayPal}>
              <Ionicons name="open-outline" size={20} color="#fff" />
              <Text style={styles.openPaypalText}>Открыть PayPal</Text>
            </TouchableOpacity>
          </View>

          {/* Instructions */}
          <View style={styles.instructionsCard}>
            <Text style={styles.instructionsTitle}>Инструкция:</Text>
            <View style={styles.instructionRow}>
              <Text style={styles.instructionNumber}>1</Text>
              <Text style={styles.instructionText}>
                Нажмите "Открыть PayPal" выше
              </Text>
            </View>
            <View style={styles.instructionRow}>
              <Text style={styles.instructionNumber}>2</Text>
              <Text style={styles.instructionText}>
                Отправьте ${selectedPlan.price_usd} USD на аккаунт {paypalAccount}
              </Text>
            </View>
            <View style={styles.instructionRow}>
              <Text style={styles.instructionNumber}>3</Text>
              <Text style={styles.instructionText}>
                Вернитесь и нажмите "Я оплатил"
              </Text>
            </View>
          </View>

          {/* Confirm Button */}
          <View style={styles.actions}>
            <Text style={styles.infoText}>{t("afterPayment")}</Text>
            <Button
              title={t("iHavePaid")}
              onPress={handleConfirmPayment}
              loading={createPaymentMutation.isPending}
              variant="primary"
            />
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
  amountCard: {
    backgroundColor: colors.card,
    borderColor: colors.primary,
    borderWidth: 2,
    borderRadius: 20,
    padding: 24,
    alignItems: "center",
    marginBottom: 24,
  },
  amountLabel: {
    color: colors.muted,
    fontSize: 14,
  },
  amountValue: {
    color: colors.text,
    fontSize: 36,
    fontWeight: "800",
    marginTop: 8,
  },
  paypalCard: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 20,
    padding: 24,
    alignItems: "center",
    marginBottom: 24,
  },
  paypalLogo: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: "#0070BA20",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 16,
  },
  paypalTitle: {
    color: colors.muted,
    fontSize: 14,
  },
  paypalAccount: {
    color: colors.text,
    fontSize: 24,
    fontWeight: "800",
    marginTop: 4,
  },
  openPaypalButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    backgroundColor: "#0070BA",
    paddingHorizontal: 24,
    paddingVertical: 14,
    borderRadius: 14,
    marginTop: 20,
  },
  openPaypalText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "700",
  },
  instructionsCard: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
  },
  instructionsTitle: {
    color: colors.text,
    fontSize: 16,
    fontWeight: "700",
    marginBottom: 16,
  },
  instructionRow: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 12,
    marginBottom: 12,
  },
  instructionNumber: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: colors.primary2,
    color: colors.bg,
    textAlign: "center",
    lineHeight: 24,
    fontSize: 13,
    fontWeight: "700",
  },
  instructionText: {
    color: colors.text,
    fontSize: 14,
    flex: 1,
    lineHeight: 20,
  },
  actions: {
    gap: 12,
  },
  infoText: {
    color: colors.muted,
    fontSize: 14,
    textAlign: "center",
  },
});
