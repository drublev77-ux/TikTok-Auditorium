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

const TOKEN_ICONS: Record<string, string> = {
  USDT: "💵",
  USDC: "💵",
  ETH: "⬡",
  BTC: "₿",
};

export default function CryptoPaymentScreen() {
  const { t } = useTranslation();
  const selectedPlan = useBillingStore((s) => s.selectedPlan);
  const setCurrentPaymentRequest = useBillingStore((s) => s.setCurrentPaymentRequest);
  const { currentProject } = useProject();

  const [selectedNetwork, setSelectedNetwork] = useState<string | null>(null);
  const [selectedToken, setSelectedToken] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

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

  const handleCopyAddress = async () => {
    if (paymentMethods?.crypto?.wallet_address) {
      await Clipboard.setStringAsync(paymentMethods.crypto.wallet_address);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleConfirmPayment = () => {
    if (!selectedNetwork || !selectedToken || !currentProject) return;

    // We need an org_id. For simplicity, we'll use the project's org_id
    // In a real app, you'd have this from user context
    createPaymentMutation.mutate({
      org_id: currentProject.org_id,
      plan_id: selectedPlan!.id,
      payment_method: "crypto",
      crypto_network: selectedNetwork,
      crypto_token: selectedToken,
    });
  };

  if (!selectedPlan) {
    router.replace("/billing");
    return null;
  }

  const networks = paymentMethods?.crypto?.networks || [];
  const tokens = paymentMethods?.crypto?.supported_tokens || [];
  const walletAddress = paymentMethods?.crypto?.wallet_address || "";

  return (
    <>
      <Stack.Screen
        options={{
          title: t("cryptoPayment"),
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
            <Text style={styles.amountHint}>
              в эквиваленте {selectedToken || "USDT/USDC/ETH/BTC"}
            </Text>
          </View>

          {/* Select Network */}
          <Text style={styles.sectionTitle}>{t("selectNetwork")}</Text>
          <View style={styles.optionsGrid}>
            {networks.map((network) => (
              <TouchableOpacity
                key={network.id}
                style={[
                  styles.optionCard,
                  selectedNetwork === network.id && styles.optionCardSelected,
                ]}
                onPress={() => setSelectedNetwork(network.id)}
              >
                <Text style={[
                  styles.optionText,
                  selectedNetwork === network.id && styles.optionTextSelected,
                ]}>
                  {network.name}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* Select Token */}
          <Text style={styles.sectionTitle}>{t("selectToken")}</Text>
          <View style={styles.optionsGrid}>
            {tokens.map((token) => (
              <TouchableOpacity
                key={token}
                style={[
                  styles.optionCard,
                  selectedToken === token && styles.optionCardSelected,
                ]}
                onPress={() => setSelectedToken(token)}
              >
                <Text style={styles.tokenIcon}>{TOKEN_ICONS[token]}</Text>
                <Text style={[
                  styles.optionText,
                  selectedToken === token && styles.optionTextSelected,
                ]}>
                  {token}
                </Text>
              </TouchableOpacity>
            ))}
          </View>

          {/* Wallet Address */}
          <Text style={styles.sectionTitle}>{t("walletAddress")}</Text>
          <View style={styles.addressCard}>
            <Text style={styles.addressText} selectable>
              {walletAddress}
            </Text>
            <TouchableOpacity style={styles.copyButton} onPress={handleCopyAddress}>
              <Ionicons
                name={copied ? "checkmark" : "copy-outline"}
                size={20}
                color={copied ? colors.success : colors.primary2}
              />
              <Text style={[styles.copyText, copied && { color: colors.success }]}>
                {copied ? t("copied") : t("copyAddress")}
              </Text>
            </TouchableOpacity>
          </View>

          {/* QR Code Placeholder */}
          <View style={styles.qrCard}>
            <View style={styles.qrPlaceholder}>
              <Ionicons name="qr-code-outline" size={120} color={colors.border} />
            </View>
            <Text style={styles.qrHint}>
              Сканируйте QR-код или скопируйте адрес выше
            </Text>
          </View>

          {/* Confirm Button */}
          <View style={styles.actions}>
            <Text style={styles.infoText}>{t("afterPayment")}</Text>
            <Button
              title={t("iHavePaid")}
              onPress={handleConfirmPayment}
              loading={createPaymentMutation.isPending}
              disabled={!selectedNetwork || !selectedToken}
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
  amountHint: {
    color: colors.primary2,
    fontSize: 14,
    marginTop: 4,
  },
  sectionTitle: {
    color: colors.text,
    fontSize: 17,
    fontWeight: "700",
    marginBottom: 12,
    marginTop: 8,
  },
  optionsGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
    marginBottom: 16,
  },
  optionCard: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  optionCardSelected: {
    backgroundColor: colors.primary + "20",
    borderColor: colors.primary,
  },
  optionText: {
    color: colors.muted,
    fontSize: 14,
    fontWeight: "600",
  },
  optionTextSelected: {
    color: colors.text,
  },
  tokenIcon: {
    fontSize: 18,
  },
  addressCard: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
  },
  addressText: {
    color: colors.text,
    fontSize: 13,
    fontFamily: Platform.OS === "ios" ? "Menlo" : "monospace",
    marginBottom: 12,
  },
  copyButton: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    alignSelf: "flex-start",
  },
  copyText: {
    color: colors.primary2,
    fontSize: 14,
    fontWeight: "600",
  },
  qrCard: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: 16,
    padding: 24,
    alignItems: "center",
    marginBottom: 24,
  },
  qrPlaceholder: {
    width: 160,
    height: 160,
    backgroundColor: "#fff",
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
  },
  qrHint: {
    color: colors.muted,
    fontSize: 13,
    textAlign: "center",
    marginTop: 12,
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
