import Constants from "expo-constants";

// URL RULES (platform):
// - NEVER hardcode ports
// - Always call backend via EXPO_PUBLIC_BACKEND_URL and prefix with /api

function getBackendBaseUrl(): string {
  const fromEnv = process.env.EXPO_PUBLIC_BACKEND_URL;
  if (fromEnv) return fromEnv;

  // Fallback to expo config if needed (some environments provide via app config).
  const fromConfig = (Constants.expoConfig?.extra as any)?.EXPO_PUBLIC_BACKEND_URL;
  if (typeof fromConfig === "string" && fromConfig.length > 0) return fromConfig;

  throw new Error("Missing EXPO_PUBLIC_BACKEND_URL");
}

export const API_BASE_URL = `${getBackendBaseUrl()}/api`;

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  const text = await res.text();
  const json = text ? JSON.parse(text) : undefined;

  if (!res.ok) {
    const message = json?.detail || json?.message || `HTTP ${res.status}`;
    throw new Error(message);
  }

  return json as T;
}
