import { Pressable, StyleSheet, Text } from "react-native";

import { colors } from "@/constants/colors";

type ReplyCardProps = {
  rank: number;
  text: string;
  onPress?: () => void;
};

export function ReplyCard({ rank, text, onPress }: ReplyCardProps) {
  return (
    <Pressable onPress={onPress} style={styles.card}>
      <Text style={styles.rank}>Option {rank}</Text>
      <Text style={styles.text}>{text}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    padding: 16,
    borderRadius: 18,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    gap: 10
  },
  rank: {
    color: colors.primary,
    fontWeight: "700"
  },
  text: {
    color: colors.text,
    fontSize: 16,
    lineHeight: 22
  }
});
