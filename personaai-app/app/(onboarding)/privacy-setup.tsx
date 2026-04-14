import { router } from "expo-router";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { AppScreen } from "@/components/AppScreen";
import { colors } from "@/constants/colors";

export default function PrivacySetupScreen() {
  return (
    <AppScreen
      title="Privacy and control"
      subtitle="PersonaAI only works on the chats you allow and keeps the learned tone tied to your signed-in account."
    >
      <View style={styles.card}>
        <Text style={styles.cardTitle}>What to do next</Text>
        <Text style={styles.cardText}>
          Open Settings after onboarding, add the WhatsApp groups you want PersonaAI to watch, then enable
          Accessibility access and overlay permission so captured outgoing messages can keep training your profile.
        </Text>
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
