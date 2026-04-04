import { router } from "expo-router";
import { useState } from "react";
import { Pressable, StyleSheet, Text } from "react-native";

import { AppScreen } from "@/components/AppScreen";
import { PersonalitySelector } from "@/components/PersonalitySelector";
import { colors } from "@/constants/colors";

export default function PersonalitySetupScreen() {
  const [personality, setPersonality] = useState("funny");

  return (
    <AppScreen title="Choose the baseline vibe" subtitle="This becomes the starting mode before tone learning fine-tunes the output.">
      <PersonalitySelector value={personality} onChange={setPersonality} />
      <Pressable onPress={() => router.push("/(onboarding)/teach-ai")} style={styles.button}>
        <Text style={styles.buttonLabel}>Next</Text>
      </Pressable>
    </AppScreen>
  );
}

const styles = StyleSheet.create({
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
