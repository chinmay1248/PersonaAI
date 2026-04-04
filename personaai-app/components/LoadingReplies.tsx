import { ActivityIndicator, StyleSheet, Text, View } from "react-native";

import { colors } from "@/constants/colors";

export function LoadingReplies() {
  return (
    <View style={styles.container}>
      <ActivityIndicator color={colors.primary} />
      <Text style={styles.text}>Generating replies that sound like you...</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
    borderRadius: 18,
    backgroundColor: colors.surface,
    alignItems: "center",
    gap: 10
  },
  text: {
    color: colors.muted
  }
});
