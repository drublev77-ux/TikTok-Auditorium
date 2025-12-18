import { Stack } from "expo-router";
import { colors } from "../../src/theme/colors";

export default function AudienceLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: colors.bg },
        headerTintColor: colors.text,
        contentStyle: { backgroundColor: colors.bg },
      }}
    />
  );
}
