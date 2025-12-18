import React from "react";
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from "react-native";
import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { router, Stack } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

import { AppScreen } from "../../src/components/AppScreen";
import { colors } from "../../src/theme/colors";
import { getSubscriptionPlans } from "../../src/api/billing";
import { useBillingStore } from "../../src/store/billingStore";
import type { SubscriptionPlan } from "../../src/api/billing";

const PLAN_ICONS: Record<string, string> = {
  basic: "star-outline",
  pro: "rocket-outline",
  agency: "business-outline",
};

const PLAN_COLORS: Record<string, string> = {
  basic: colors.primary2,
  pro: colors.primary,
  agency: "#FFD700",
};

export default function BillingPlansScreen() {
  const { t } = useTranslation();
  const setSelectedPlan = useBillingStore((s) => s.setSelectedPlan);

  const { data: plans, isLoading, error } = useQuery({
    queryKey: ["billing-plans"],
    queryFn: getSubscriptionPlans,
  });

  const handleSelectPlan = (plan: SubscriptionPlan) => {
    setSelectedPlan(plan);
    router.push("/billing/payment-method");
  };

  return (
    <>
      <Stack.Screen
        options={{
          title: t("billing"),
          headerStyle: { backgroundColor: colors.bg },
          headerTintColor: colors.text,
        }}
      />
      <AppScreen>
        <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent}>
          <Text style={styles.title}>{t("choosePlan")}</Text>
          <Text style={styles.subtitle}>
            Выберите подходящий тариф для вашего бизнеса
          </Text>

          {isLoading ? (
            <View style={styles.center}>
              <ActivityIndicator color={colors.primary2} size="large" />
            </View>
          ) : error ? (
            <View style={styles.errorCard}>
              <Text style={styles.errorText}>
                {error instanceof Error ? error.message : "Error loading plans"}
              </Text>
            </View>
          ) : (
            <View style={styles.plansContainer}>
              {plans?.map((plan) => (
                <TouchableOpacity
                  key={plan.id}
                  style={[
                    styles.planCard,
                    plan.id === "pro" && styles.planCardHighlight,
                  ]}
                  onPress={() => handleSelectPlan(plan)}
                  activeOpacity={0.8}
                >
                  {plan.id === "pro" && (
                    <View style={styles.popularBadge}>
                      <Text style={styles.popularText}>Популярный</Text>
                    </View>
                  )}
                  
                  <View style={[styles.planIcon, { backgroundColor: PLAN_COLORS[plan.id] + "20" }]}>
                    <Ionicons
                      name={PLAN_ICONS[plan.id] as any}
                      size={32}
                      color={PLAN_COLORS[plan.id]}
                    />
                  </View>

                  <Text style={styles.planName}>{plan.name}</Text>
                  
                  <View style={styles.priceRow}>
                    <Text style={styles.priceSymbol}>$</Text>
                    <Text style={styles.priceAmount}>{plan.price_usd}</Text>
                    <Text style={styles.pricePeriod}>{t("perMonth")}</Text>
                  </View>

                  <View style={styles.featuresContainer}>
                    {plan.features.map((feature, idx) => (
                      <View key={idx} style={styles.featureRow}>
                        <Ionicons
                          name="checkmark-circle"
                          size={18}
                          color={colors.success}
                        />
                        <Text style={styles.featureText}>{feature}</Text>
                      </View>
                    ))}
                  </View>

                  <View style={[
                    styles.selectButton,
                    plan.id === "pro" && styles.selectButtonHighlight,
                  ]}>
                    <Text style={[
                      styles.selectButtonText,
                      plan.id === "pro" && styles.selectButtonTextHighlight,
                    ]}>
                      {t("subscribe")}
                    </Text>
                  </View>
                </TouchableOpacity>
              ))}
            </View>
          )}
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
  title: {
    color: colors.text,
    fontSize: 28,
    fontWeight: "800",
    textAlign: "center",
  },
  subtitle: {
    color: colors.muted,
    fontSize: 15,
    textAlign: "center",
    marginTop: 8,
    marginBottom: 24,
  },
  center: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 60,
  },
  errorCard: {
    backgroundColor: colors.card,
    borderColor: colors.danger,
    borderWidth: 1,
    borderRadius: 16,
    padding: 16,
  },
  errorText: {
    color: colors.danger,
    textAlign: "center",
  },
  plansContainer: {
    gap: 16,
  },
  planCard: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 20,
    padding: 24,
    position: "relative",
    overflow: "hidden",
  },
  planCardHighlight: {
    borderColor: colors.primary,
    borderWidth: 2,
  },
  popularBadge: {
    position: "absolute",
    top: 12,
    right: 12,
    backgroundColor: colors.primary,
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
  },
  popularText: {
    color: colors.text,
    fontSize: 12,
    fontWeight: "700",
  },
  planIcon: {
    width: 64,
    height: 64,
    borderRadius: 32,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 16,
  },
  planName: {
    color: colors.text,
    fontSize: 22,
    fontWeight: "800",
  },
  priceRow: {
    flexDirection: "row",
    alignItems: "baseline",
    marginTop: 8,
  },
  priceSymbol: {
    color: colors.muted,
    fontSize: 20,
    fontWeight: "600",
  },
  priceAmount: {
    color: colors.text,
    fontSize: 40,
    fontWeight: "800",
    marginHorizontal: 2,
  },
  pricePeriod: {
    color: colors.muted,
    fontSize: 16,
  },
  featuresContainer: {
    marginTop: 20,
    gap: 10,
  },
  featureRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
  },
  featureText: {
    color: colors.text,
    fontSize: 14,
    flex: 1,
  },
  selectButton: {
    marginTop: 24,
    backgroundColor: colors.card2,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 14,
    paddingVertical: 14,
    alignItems: "center",
  },
  selectButtonHighlight: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  selectButtonText: {
    color: colors.text,
    fontSize: 16,
    fontWeight: "700",
  },
  selectButtonTextHighlight: {
    color: "#fff",
  },
});
