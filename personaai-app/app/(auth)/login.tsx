import { Link, router } from "expo-router";
import { useState } from "react";
import { Alert, Pressable, StyleSheet, Text, TextInput } from "react-native";

import { AppScreen } from "@/components/AppScreen";
import { colors } from "@/constants/colors";
import { authService } from "@/services/authService";
import { useAuthStore } from "@/store/authStore";

export default function LoginScreen() {
  const [email, setEmail] = useState("demo@persona.ai");
  const [password, setPassword] = useState("StrongPass123");
  const setSession = useAuthStore((state) => state.setSession);

  async function handleLogin() {
    try {
      const session = await authService.login({ email, password });
      setSession({
        accessToken: session.access_token,
        refreshToken: session.refresh_token,
        userId: session.user_id
      });
      router.replace("/(onboarding)/select-chats");
    } catch (error) {
      Alert.alert("Login failed", error instanceof Error ? error.message : "Please try again");
    }
  }

  return (
    <AppScreen title="Welcome back" subtitle="Sign in to continue teaching PersonaAI how you speak.">
      <TextInput style={styles.input} value={email} onChangeText={setEmail} placeholder="Email" />
      <TextInput
        style={styles.input}
        value={password}
        onChangeText={setPassword}
        placeholder="Password"
        secureTextEntry
      />
      <Pressable onPress={handleLogin} style={styles.button}>
        <Text style={styles.buttonLabel}>Login</Text>
      </Pressable>
      <Link href="/(auth)/register" style={styles.link}>
        Create an account
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
