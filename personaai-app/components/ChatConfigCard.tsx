import { StyleSheet, Text, View } from "react-native";

import { colors } from "@/constants/colors";

type ChatConfigCardProps = {
  label: string;
  type?: string;
  personality?: string;
  autoReplyMode: string;
};

export function ChatConfigCard({ label, type, personality, autoReplyMode }: ChatConfigCardProps) {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>{label}</Text>
      <Text style={styles.meta}>Type: {type ?? "Not set"}</Text>
      <Text style={styles.meta}>Personality: {personality ?? "Balanced"}</Text>
      <Text style={styles.meta}>Auto reply: {autoReplyMode}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: 16,
    borderRadius: 18,
    backgroundColor: colors.card,
    gap: 6
  },
  title: {
    fontSize: 18,
    fontWeight: "700",
    color: colors.text
  },
  meta: {
    color: colors.muted
  }
});
