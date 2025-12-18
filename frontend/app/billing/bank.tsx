import React, { useState } from "react";
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  TouchableOpacity,
  Alert,
  Platform,
} from "react-native";
import { useTranslation } from "react-i18next";
import { useMutation, useQuery } from "@tanstack/react-query";
import { router, Stack } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import * as Clipboard from "expo-clipboard";

import { AppScreen } from "../../src/components/AppScreen";
import { Button } from "../../src/components/Button";
import { colors } from "../../src/theme/colors";
import { useBillingStore } from "../../src/store/billingStore";
import { useProject } from "../../src/store/ProjectContext";
import { getPaymentMethods, createPaymentRequest } from "../../src/api/billing";

export default function BankPaymentScreen() {
  const { t } = useTranslation();
  const selectedPlan = useBillingStore((s) => s.selectedPlan);
  const setCurrentPaymentRequest = useBillingStore((s) => s.setCurrentPaymentRequest);
  const { currentProject } = useProject();

  const [copiedField, setCopiedField] = useState<string | null>(null);

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

  const handleCopy = async (text: string, field: string) => {
    await Clipboard.setStringAsync(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const handleConfirmPayment = () => {
    if (!currentProject) return;

    createPaymentMutation.mutate({
      org_id: currentProject.org_id,
      plan_id: selectedPlan!.id,
      payment_method: "bank",
    });
  };

  if (!selectedPlan) {
    router.replace("/billing");
    return null;
  }

  const bankDetails = paymentMethods?.bank;
  const paymentReference = `TIKAUD-${currentProject?.org_id || "ORG"}-${selectedPlan.id.toUpperCase()}`;

  return (
    <>
      <Stack.Screen
        options={{
          title: t("bankTransfer"),
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

          <Text style={styles.sectionTitle}>{t("bankDetails")}</Text>

          {/* Account Number */}
          <View style={styles.detailCard}>
            <View style={styles.detailHeader}>
              <Ionicons name="card-outline" size={20} color={colors.primary2} />
              <Text style={styles.detailLabel}>{t("accountNumber")}</Text>
            </View>
            <Text style={styles.detailValue} selectable>
              {bankDetails?.account_number || "BY43POIS30140008401005002629"}
            </Text>
            <TouchableOpacity
              style={styles.copyButton}
              onPress={() => handleCopy(bankDetails?.account_number || "", "account")}
            >
              <Ionicons
                name={copiedField === "account" ? "checkmark" : "copy-outline"}
                size={18}
                color={copiedField === "account" ? colors.success : colors.primary2}
              />
              <Text style={[styles.copyText, copiedField === "account" && { color: colors.success }]}>
                {copiedField === "account" ? t("copied") : t("copyAddress")}
              </Text>
            </TouchableOpacity>
          </View>

          {/* BIC */}
          <View style={styles.detailCard}>
            <View style={styles.detailHeader}>
              <Ionicons name="business-outline" size={20} color={colors.primary2} />
              <Text style={styles.detailLabel}>{t("bicCode")}</Text>
            </View>
            <Text style={styles.detailValue} selectable>
              {bankDetails?.bic || "POISBY2X"}
            </Text>
            <TouchableOpacity
              style={styles.copyButton}
              onPress={() => handleCopy(bankDetails?.bic || "", "bic")}
            >
              <Ionicons
                name={copiedField === "bic" ? "checkmark" : "copy-outline"}
                size={18}
                color={copiedField === "bic" ? colors.success : colors.primary2}
              />
              <Text style={[styles.copyText, copiedField === "bic" && { color: colors.success }]}>
                {copiedField === "bic" ? t("copied") : t("copyAddress")}
              </Text>
            </TouchableOpacity>
          </View>

          {/* Payment Reference */}
          <View style={styles.detailCard}>
            <View style={styles.detailHeader}>
              <Ionicons name="document-text-outline" size={20} color={colors.primary2} />
              <Text style={styles.detailLabel}>{t("paymentReference")}</Text>
            </View>
            <Text style={styles.detailValue} selectable>
              {paymentReference}
            </Text>
            <TouchableOpacity
              style={styles.copyButton}
              onPress={() => handleCopy(paymentReference, "ref")}
            >
              <Ionicons
                name={copiedField === "ref" ? "checkmark" : "copy-outline"}
                size={18}
                color={copiedField === "ref" ? colors.success : colors.primary2}
              />
              <Text style={[styles.copyText, copiedField === "ref" && { color: colors.success }]}>
                {copiedField === "ref" ? t("copied") : t("copyAddress")}
              </Text>
            </TouchableOpacity>
          </View>

          {/* Warning */}
          <View style={styles.warningCard}>
            <Ionicons name="information-circle" size={24} color={colors.primary2} />
            <Text style={styles.warningText}>
              Обязательно укажите назначение платежа для быстрой идентификации вашего платежа
            </Text>
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
  sectionTitle: {
    color: colors.text,
    fontSize: 20,
    fontWeight: "800",
    marginBottom: 16,
  },
  detailCard: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
  },
  detailHeader: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 8,
  },
  detailLabel: {
    color: colors.muted,
    fontSize: 13,
  },
  detailValue: {
    color: colors.text,
    fontSize: 16,
    fontWeight: "600",
    fontFamily: Platform.OS === "ios" ? "Menlo" : "monospace",
    marginBottom: 12,
  },
  copyButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    alignSelf: "flex-start",
  },
  copyText: {
    color: colors.primary2,
    fontSize: 13,
    fontWeight: "600",
  },
  warningCard: {
    backgroundColor: colors.primary2 + "15",
    borderRadius: 16,
    padding: 16,
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 12,
    marginTop: 8,
    marginBottom: 24,
  },
  warningText: {
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
