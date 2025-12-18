import { apiFetch } from "./http";

export type SubscriptionPlan = {
  id: string;
  name: string;
  price_usd: number;
  features: string[];
};

export type CryptoNetwork = {
  id: string;
  name: string;
  chain_id: number | null;
};

export type PaymentMethods = {
  methods: string[];
  crypto: {
    wallet_address: string;
    supported_tokens: string[];
    networks: CryptoNetwork[];
  };
  bank: {
    account_number: string;
    bic: string;
    currency: string;
    bank_name: string;
  };
  paypal: {
    account: string;
    email: string;
  };
};

export type PaymentRequest = {
  id: string;
  org_id: string;
  plan_id: string;
  plan_name: string;
  amount_usd: number;
  payment_method: string;
  status: "pending" | "confirmed" | "expired" | "cancelled";
  payment_details: Record<string, any>;
  created_at: string;
  expires_at: string;
};

export type Subscription = {
  id: string;
  org_id: string;
  plan_id: string;
  plan_name: string;
  status: "active" | "expired" | "cancelled";
  started_at: string;
  expires_at: string;
};

export type CreatePaymentPayload = {
  org_id: string;
  plan_id: string;
  payment_method: "crypto" | "bank" | "paypal";
  crypto_network?: string;
  crypto_token?: string;
};

export async function getSubscriptionPlans(): Promise<SubscriptionPlan[]> {
  return apiFetch<SubscriptionPlan[]>("/billing/plans");
}

export async function getPaymentMethods(): Promise<PaymentMethods> {
  return apiFetch<PaymentMethods>("/billing/payment-methods");
}

export async function createPaymentRequest(
  payload: CreatePaymentPayload
): Promise<PaymentRequest> {
  return apiFetch<PaymentRequest>("/billing/payment-requests", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getPaymentRequests(orgId: string): Promise<PaymentRequest[]> {
  return apiFetch<PaymentRequest[]>(`/billing/payment-requests?org_id=${orgId}`);
}

export async function getSubscription(
  orgId: string
): Promise<Subscription | { subscription: null }> {
  return apiFetch<Subscription | { subscription: null }>(
    `/billing/subscription?org_id=${orgId}`
  );
}
