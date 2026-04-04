import { router } from "expo-router";
import { useState } from "react";
import { Alert, Pressable, StyleSheet, Text, TextInput } from "react-native";

import { AppScreen } from "@/components/AppScreen";
import { colors } from "@/constants/colors";
import { toneService } from "@/services/toneService";

export default function TeachAiScreen() {
  const [samples, setSamples] = useState("haha bro that's wild\nyaar chill, sab theek hai");

  async function handleTrain() {
    try {
      const lines = samples.split("\n").map((value) => value.trim()).filter(Boolean);
      await toneService.train(lines);
      router.push("/(onboarding)/privacy-setup");
    } catch (error) {
      Alert.alert("Training failed", error instanceof Error ? error.message : "Please try again");
    }
  }

  return (
    <AppScreen title="Teach PersonaAI your style" subtitle="Paste a few real messages so the first tone profile feels personal.">
      <TextInput
        style={styles.input}
        value={samples}
        onChangeText={setSamples}
        placeholder="One message per line"
        multiline
        numberOfLines={7}
      />
      <Pressable onPress={handleTrain} style={styles.button}>
        <Text style={styles.buttonLabel}>Train tone</Text>
      </Pressable>
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  input: {
    minHeight: 180,
    textAlignVertical: "top",
    backgroundColor: colors.surface,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: 14,
    paddingVertical: 14
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
