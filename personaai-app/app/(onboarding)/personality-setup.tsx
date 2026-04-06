import { router, useLocalSearchParams } from "expo-router";
import { useState } from "react";
import { Alert, Pressable, StyleSheet, Text } from "react-native";

import { AppScreen } from "@/components/AppScreen";
import { PersonalitySelector } from "@/components/PersonalitySelector";
import { colors } from "@/constants/colors";
import { chatService } from "@/services/chatService";
import { useChatStore } from "@/store/chatStore";

export default function PersonalitySetupScreen() {
  const { chatName } = useLocalSearchParams<{ chatName: string }>();
  const [personality, setPersonality] = useState("funny");
  const [loading, setLoading] = useState(false);
  const setChats = useChatStore((state) => state.setChats);
  const setActiveChatId = useChatStore((state) => state.setActiveChatId);

  async function handleNext() {
    setLoading(true);
    try {
      const config = await chatService.createConfig({
        chat_label: chatName || "Friends Group",
        chat_type: "group",
        personality_mode: personality,
        auto_reply_mode: "OFF",
      });
      setChats([config]);
      setActiveChatId(config.id);
      router.push("/(onboarding)/teach-ai");
    } catch (error) {
      Alert.alert("Setup failed", error instanceof Error ? error.message : "Could not create chat config. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppScreen title="Choose the baseline vibe" subtitle="This becomes the starting mode before tone learning fine-tunes the output.">
      <PersonalitySelector value={personality} onChange={setPersonality} />
      <Pressable onPress={handleNext} style={[styles.button, loading && styles.buttonDisabled]} disabled={loading}>
        <Text style={styles.buttonLabel}>{loading ? "Creating..." : "Next"}</Text>
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
  buttonDisabled: {
    opacity: 0.6
  },
  buttonLabel: {
    color: "#FFFFFF",
    fontWeight: "700"
  }
});
