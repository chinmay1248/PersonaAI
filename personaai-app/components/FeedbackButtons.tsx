import { Pressable, StyleSheet, Text, View } from "react-native";

import { colors } from "@/constants/colors";

type FeedbackButtonsProps = {
  onLike?: () => void;
  onDislike?: () => void;
};

export function FeedbackButtons({ onLike, onDislike }: FeedbackButtonsProps) {
  return (
    <View style={styles.container}>
      <Pressable onPress={onLike} style={[styles.button, styles.like]}>
        <Text style={styles.label}>Like</Text>
      </Pressable>
      <Pressable onPress={onDislike} style={[styles.button, styles.dislike]}>
        <Text style={styles.label}>Dislike</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    gap: 12
  },
  button: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 14,
    alignItems: "center"
  },
  like: {
    backgroundColor: colors.success
  },
  dislike: {
    backgroundColor: colors.danger
  },
  label: {
    color: "#FFFFFF",
    fontWeight: "700"
  }
});
