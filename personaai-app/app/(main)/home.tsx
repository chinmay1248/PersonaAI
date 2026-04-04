import { Link } from "expo-router";
import { StyleSheet, Text, View } from "react-native";

import { AppScreen } from "@/components/AppScreen";
import { colors } from "@/constants/colors";

export default function HomeScreen() {
  return (
    <AppScreen title="PersonaAI" subtitle="Phase 1 screens are scaffolded and ready to connect to live backend flows.">
      <View style={styles.card}>
        <Text style={styles.title}>Quick actions</Text>
        <Link href="/(main)/reply" style={styles.link}>
          Generate a reply
        </Link>
        <Link href="/(main)/summarize" style={styles.link}>
          Summarize unread messages
        </Link>
        <Link href="/(main)/chat-configs" style={styles.link}>
          Manage chat configs
        </Link>
        <Link href="/(main)/tone-profile" style={styles.link}>
          View tone profile
        </Link>
      </View>
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: 18,
    borderRadius: 18,
    backgroundColor: colors.surface,
    gap: 12
  },
  title: {
    fontSize: 18,
    fontWeight: "700",
    color: colors.text
  },
  link: {
    color: colors.accent,
    fontSize: 16
  }
});
