import { create } from "zustand";
import type { SubscriptionPlan, PaymentRequest } from "../api/billing";

type BillingState = {
  selectedPlan: SubscriptionPlan | null;
  setSelectedPlan: (plan: SubscriptionPlan | null) => void;
  currentPaymentRequest: PaymentRequest | null;
  setCurrentPaymentRequest: (request: PaymentRequest | null) => void;
};

export const useBillingStore = create<BillingState>((set) => ({
  selectedPlan: null,
  setSelectedPlan: (plan) => set({ selectedPlan: plan }),
  currentPaymentRequest: null,
  setCurrentPaymentRequest: (request) => set({ currentPaymentRequest: request }),
}));
