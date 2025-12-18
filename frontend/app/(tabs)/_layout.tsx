import React from "react";
import { Tabs } from "expo-router";
import { useTranslation } from "react-i18next";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "../../src/theme/colors";

type IconProps = { color: string; size: number };

const tabIcon = (name: React.ComponentProps<typeof Ionicons>["name"]) =>
  ({ color, size }: IconProps) => <Ionicons name={name} size={size} color={color} />;

export default function TabsLayout() {
  const { t } = useTranslation();

  return (
    <Tabs
      screenOptions={{
        headerShown: true,
        headerStyle: { backgroundColor: colors.bg },
        headerTitleStyle: { color: colors.text },
        tabBarStyle: { backgroundColor: colors.bg, borderTopColor: colors.border },
        tabBarActiveTintColor: colors.primary2,
        tabBarInactiveTintColor: colors.muted,
      }}
    >
      <Tabs.Screen
        name="dashboard"
        options={{
          title: t("dashboard"),
          tabBarIcon: tabIcon("grid-outline"),
        }}
      />
      <Tabs.Screen
        name="audience"
        options={{
          title: t("audience"),
          tabBarIcon: tabIcon("people-outline"),
        }}
      />
      <Tabs.Screen
        name="competitors"
        options={{
          title: t("competitors"),
          tabBarIcon: tabIcon("analytics-outline"),
        }}
      />
      <Tabs.Screen
        name="creators"
        options={{
          title: t("creators"),
          tabBarIcon: tabIcon("megaphone-outline"),
        }}
      />
      <Tabs.Screen
        name="planner"
        options={{
          title: t("planner"),
          tabBarIcon: tabIcon("calendar-outline"),
        }}
      />
      <Tabs.Screen
        name="analytics"
        options={{
          title: t("analytics"),
          tabBarIcon: tabIcon("pulse-outline"),
        }}
      />
      <Tabs.Screen
        name="settings"
        options={{
          title: t("settings"),
          tabBarIcon: tabIcon("settings-outline"),
        }}
      />
    </Tabs>
  );
}
