import { router } from "expo-router";
import { useState } from "react";
import { Pressable, StyleSheet, Text, TextInput } from "react-native";

import { AppScreen } from "@/components/AppScreen";
import { colors } from "@/constants/colors";

export default function SelectChatsScreen() {
  const [chatName, setChatName] = useState("Friends Group");

  return (
    <AppScreen title="Select your first chat" subtitle="Start with one conversation type so we can tune the first reply experience.">
      <TextInput style={styles.input} value={chatName} onChangeText={setChatName} placeholder="Chat label" />
      <Pressable
        onPress={() => router.push({ pathname: "/(onboarding)/personality-setup", params: { chatName } })}
        style={styles.button}
      >
        <Text style={styles.buttonLabel}>Continue</Text>
      </Pressable>
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  input: {
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
