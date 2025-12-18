import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { resources, type SupportedLang } from "./resources";

const STORAGE_KEY = "tikauditor_lang";

export async function initI18n(): Promise<void> {
  if (i18n.isInitialized) return;

  let lang: SupportedLang = "ru";
  try {
    const saved = await AsyncStorage.getItem(STORAGE_KEY);
    if (saved === "ru" || saved === "en") lang = saved;
  } catch {
    // ignore
  }

  await i18n
    .use(initReactI18next)
    .init({
      resources,
      lng: lang,
      fallbackLng: "en",
      interpolation: { escapeValue: false },
    });
}

export async function setLang(lang: SupportedLang): Promise<void> {
  await i18n.changeLanguage(lang);
  try {
    await AsyncStorage.setItem(STORAGE_KEY, lang);
  } catch {
    // ignore
  }
}

export default i18n;
