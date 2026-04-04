import { StyleSheet, Text, View } from "react-native";

import { colors } from "@/constants/colors";

export function MoodBadge({ mood }: { mood: string }) {
  return (
    <View style={styles.badge}>
      <Text style={styles.text}>Mood: {mood}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    alignSelf: "flex-start",
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 999,
    backgroundColor: colors.primarySoft
  },
  text: {
    color: colors.primary,
    fontWeight: "600"
  }
});
