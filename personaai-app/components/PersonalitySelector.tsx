import { Pressable, StyleSheet, Text, View } from "react-native";

import { colors } from "@/constants/colors";
import { personalities } from "@/constants/personalities";

type PersonalitySelectorProps = {
  value: string;
  onChange: (value: string) => void;
};

export function PersonalitySelector({ value, onChange }: PersonalitySelectorProps) {
  return (
    <View style={styles.container}>
      {personalities.map((personality) => {
        const selected = value === personality.id;
        return (
          <Pressable
            key={personality.id}
            onPress={() => onChange(personality.id)}
            style={[styles.option, selected && styles.optionSelected]}
          >
            <Text style={[styles.label, selected && styles.labelSelected]}>{personality.label}</Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10
  },
  option: {
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: colors.border,
    backgroundColor: colors.surface
  },
  optionSelected: {
    backgroundColor: colors.primary,
    borderColor: colors.primary
  },
  label: {
    color: colors.text
  },
  labelSelected: {
    color: "#FFFFFF",
    fontWeight: "700"
  }
});
