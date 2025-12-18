import React from "react";
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  TouchableOpacity,
} from "react-native";
import { useTranslation } from "react-i18next";
import { router, Stack } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

import { AppScreen } from "../../src/components/AppScreen";
import { colors } from "../../src/theme/colors";
import { useBillingStore } from "../../src/store/billingStore";

type PaymentMethodOption = {
  id: "crypto" | "bank" | "paypal";
  icon: string;
  title: string;
  subtitle: string;
  color: string;
};

export default function PaymentMethodScreen() {
  const { t } = useTranslation();
  const selectedPlan = useBillingStore((s) => s.selectedPlan);

  const paymentMethods: PaymentMethodOption[] = [
    {
      id: "crypto",
      icon: "logo-bitcoin",
      title: t("crypto"),
      subtitle: "USDT, USDC, ETH, BTC",
      color: "#F7931A",
    },
    {
      id: "bank",
      icon: "business-outline",
      title: t("bankTransfer"),
      subtitle: "USD, SWIFT",
      color: colors.primary2,
    },
    {
      id: "paypal",
      icon: "logo-paypal",
      title: t("paypal"),
      subtitle: "PayPal Business",
      color: "#0070BA",
    },
  ];

  const handleSelectMethod = (method: PaymentMethodOption) => {
    if (method.id === "crypto") {
      router.push("/billing/crypto");
    } else if (method.id === "bank") {
      router.push("/billing/bank");
    } else {
      router.push("/billing/paypal");
    }
  };

  if (!selectedPlan) {
    router.replace("/billing");
    return null;
  }

  return (
    <>
      <Stack.Screen
        options={{
          title: t("paymentMethod"),
          headerStyle: { backgroundColor: colors.bg },
          headerTintColor: colors.text,
        }}
      />
      <AppScreen>
        <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent}>
          {/* Selected Plan Summary */}
          <View style={styles.planSummary}>
            <Text style={styles.planLabel}>{t("choosePlan")}:</Text>
            <View style={styles.planRow}>
              <Text style={styles.planName}>{selectedPlan.name}</Text>
              <Text style={styles.planPrice}>
                ${selectedPlan.price_usd}{t("perMonth")}
              </Text>
            </View>
          </View>

          <Text style={styles.title}>{t("selectPaymentMethod")}</Text>

          <View style={styles.methodsContainer}>
            {paymentMethods.map((method) => (
              <TouchableOpacity
                key={method.id}
                style={styles.methodCard}
                onPress={() => handleSelectMethod(method)}
                activeOpacity={0.7}
              >
                <View style={[styles.methodIcon, { backgroundColor: method.color + "20" }]}>
                  <Ionicons name={method.icon as any} size={28} color={method.color} />
                </View>
                <View style={styles.methodText}>
                  <Text style={styles.methodTitle}>{method.title}</Text>
                  <Text style={styles.methodSubtitle}>{method.subtitle}</Text>
                </View>
                <Ionicons name="chevron-forward" size={22} color={colors.muted} />
              </TouchableOpacity>
            ))}
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
  planSummary: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 16,
    padding: 16,
    marginBottom: 24,
  },
  planLabel: {
    color: colors.muted,
    fontSize: 13,
    marginBottom: 8,
  },
  planRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  planName: {
    color: colors.text,
    fontSize: 20,
    fontWeight: "800",
  },
  planPrice: {
    color: colors.primary2,
    fontSize: 20,
    fontWeight: "700",
  },
  title: {
    color: colors.text,
    fontSize: 22,
    fontWeight: "800",
    marginBottom: 20,
  },
  methodsContainer: {
    gap: 12,
  },
  methodCard: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 16,
    padding: 16,
    flexDirection: "row",
    alignItems: "center",
  },
  methodIcon: {
    width: 56,
    height: 56,
    borderRadius: 28,
    alignItems: "center",
    justifyContent: "center",
    marginRight: 16,
  },
  methodText: {
    flex: 1,
  },
  methodTitle: {
    color: colors.text,
    fontSize: 17,
    fontWeight: "700",
  },
  methodSubtitle: {
    color: colors.muted,
    fontSize: 13,
    marginTop: 4,
  },
});
