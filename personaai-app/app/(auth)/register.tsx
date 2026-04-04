import { Link, router } from "expo-router";
import { useState } from "react";
import { Alert, Pressable, StyleSheet, Text, TextInput } from "react-native";

import { AppScreen } from "@/components/AppScreen";
import { colors } from "@/constants/colors";
import { authService } from "@/services/authService";
import { useAuthStore } from "@/store/authStore";

export default function RegisterScreen() {
  const [displayName, setDisplayName] = useState("Persona Builder");
  const [email, setEmail] = useState("demo@persona.ai");
  const [password, setPassword] = useState("StrongPass123");
  const setSession = useAuthStore((state) => state.setSession);

  async function handleRegister() {
    try {
      const session = await authService.register({ email, password, display_name: displayName });
      setSession({
        accessToken: session.access_token,
        refreshToken: session.refresh_token,
        userId: session.user_id
      });
      router.replace("/(onboarding)/select-chats");
    } catch (error) {
      Alert.alert("Registration failed", error instanceof Error ? error.message : "Please try again");
    }
  }

  return (
    <AppScreen title="Create your PersonaAI" subtitle="We will use this account to store chat setups and tone profiles.">
      <TextInput style={styles.input} value={displayName} onChangeText={setDisplayName} placeholder="Display name" />
      <TextInput style={styles.input} value={email} onChangeText={setEmail} placeholder="Email" />
      <TextInput
        style={styles.input}
        value={password}
        onChangeText={setPassword}
        placeholder="Password"
        secureTextEntry
      />
      <Pressable onPress={handleRegister} style={styles.button}>
        <Text style={styles.buttonLabel}>Register</Text>
      </Pressable>
      <Link href="/(auth)/login" style={styles.link}>
        Back to login
      </Link>
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
  },
  link: {
    color: colors.accent
  }
});
