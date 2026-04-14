import { Pressable, StyleSheet, Text, View } from "react-native";

import { AppScreen } from "@/components/AppScreen";
import { colors } from "@/constants/colors";
import { useToneProfile } from "@/hooks/useToneProfile";

export default function ToneProfileScreen() {
  const { profile, stats, loading, refreshProfile } = useToneProfile();

  return (
    <AppScreen title="Tone profile" subtitle="Profile stats are fetched from the backend tone endpoints.">
      <Pressable onPress={refreshProfile} style={styles.button}>
        <Text style={styles.buttonLabel}>{loading ? "Refreshing..." : "Refresh profile"}</Text>
      </Pressable>
      {profile ? (
        <View style={styles.card}>
          <Text style={styles.text}>Formality: {profile.formality_score}</Text>
          <Text style={styles.text}>Average message length: {profile.avg_message_length}</Text>
          <Text style={styles.text}>Emoji frequency: {profile.emoji_frequency}</Text>
          <Text style={styles.text}>Accuracy: {profile.accuracy_score}</Text>
          <Text style={styles.text}>Language mix: {profile.detected_language_mix.join(", ") || "English"}</Text>
          <Text style={styles.text}>Slang: {profile.slang_patterns.join(", ") || "None yet"}</Text>
          {stats ? (
            <>
              <Text style={styles.text}>Total trained samples: {stats.total_samples_trained}</Text>
              <Text style={styles.text}>WhatsApp samples: {stats.whatsapp_samples}</Text>
              <Text style={styles.text}>Manual samples: {stats.manual_samples}</Text>
            </>
          ) : null}
        </View>
      ) : (
        <Text style={styles.empty}>Load the profile to see what PersonaAI has learned.</Text>
      )}
    </AppScreen>
  );
}

const styles = StyleSheet.create({
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
  card: {
    padding: 16,
    borderRadius: 18,
    backgroundColor: colors.surface,
    gap: 8
  },
  text: {
    color: colors.text
  },
  empty: {
    color: colors.muted
  }
});
