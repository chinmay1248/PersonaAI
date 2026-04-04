import { router } from "expo-router";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { AppScreen } from "@/components/AppScreen";
import { colors } from "@/constants/colors";

export default function PrivacySetupScreen() {
  return (
    <AppScreen title="Privacy and control" subtitle="Later phases will add per-chat privacy zones, exports, and deletion tools.">
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Current scaffold</Text>
        <Text style={styles.cardText}>Local development uses placeholder encryption hooks and token storage.</Text>
      </View>
      <Pressable onPress={() => router.replace("/(main)/home")} style={styles.button}>
        <Text style={styles.buttonLabel}>Finish onboarding</Text>
      </Pressable>
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: 16,
    borderRadius: 18,
    backgroundColor: colors.card,
    gap: 8
  },
  cardTitle: {
    fontWeight: "700",
    color: colors.text
  },
  cardText: {
    color: colors.muted,
    lineHeight: 20
  },
  button: {
    backgroundColor: colors.primary,
    borderRadius: 16,
    paddingVertical: 14,
    alignItems: "center"
  },
  buttonLabel: {
    color: "#FFFFFF",
    fontWeight: "700"
  }
});
