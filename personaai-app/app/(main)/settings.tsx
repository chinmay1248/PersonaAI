import { useState, useEffect } from "react";
import { router } from "expo-router";
import { Pressable, StyleSheet, Text, View, Switch, TextInput, ActivityIndicator } from "react-native";

import { AppScreen } from "@/components/AppScreen";
import { colors } from "@/constants/colors";
import { useAuthStore } from "@/store/authStore";
import { useOverlayStore } from "@/store/overlayStore";
import { messageTrainingService } from "@/services/messageTrainingService";

interface TrainingStats {
  total_samples_trained: number;
  whatsapp_samples: number;
  manual_samples: number;
  last_training_time: string | null;
  accuracy_score: number;
  most_common_slang: string[];
}

export default function SettingsScreen() {
  const logout = useAuthStore((state) => state.logout);
  const { isOverlayActive, toggleOverlay, allowedGroups, addAllowedGroup, removeAllowedGroup } = useOverlayStore();
  const [newGroup, setNewGroup] = useState("");
  const [isAutoTrainingEnabled, setIsAutoTrainingEnabled] = useState(true);
  const [trainingStats, setTrainingStats] = useState<TrainingStats | null>(null);
  const [isLoadingStats, setIsLoadingStats] = useState(true);

  useEffect(() => {
    loadTrainingStats();
  }, []);

  async function loadTrainingStats() {
    try {
      const stats = await messageTrainingService.getTrainingStats();
      setTrainingStats(stats);
    } catch (error) {
      console.error("Failed to load training stats:", error);
    } finally {
      setIsLoadingStats(false);
    }
  }

  async function handleAutoTrainingToggle(enabled: boolean) {
    try {
      setIsAutoTrainingEnabled(enabled);
      if (enabled) {
        await messageTrainingService.enableAutoTraining();
      } else {
        await messageTrainingService.disableAutoTraining();
      }
      loadTrainingStats();
    } catch (error) {
      console.error("Failed to toggle auto-training:", error);
      setIsAutoTrainingEnabled(!enabled);
    }
  }

  function handleLogout() {
    logout();
    router.replace("/(auth)/login");
  }

  function handleAddGroup() {
    if (newGroup.trim()) {
      addAllowedGroup(newGroup.trim());
      setNewGroup("");
    }
  }

  return (
    <AppScreen title="Settings" subtitle="Manage your WhatsApp Extension and AI training.">
      {/* AI Learning Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🤖 AI Learning from Your Messages</Text>
        <View style={styles.row}>
          <Text style={styles.text}>Auto-learn from WhatsApp</Text>
          <Switch
            value={isAutoTrainingEnabled}
            onValueChange={handleAutoTrainingToggle}
            trackColor={{ true: colors.primary }}
          />
        </View>
        <Text style={styles.subtleText}>
          The AI automatically learns your communication style from messages you send, so replies sound exactly like you.
        </Text>

        {/* Training Statistics */}
        {isLoadingStats ? (
          <ActivityIndicator color={colors.primary} />
        ) : trainingStats ? (
          <View style={styles.statsContainer}>
            <View style={styles.statRow}>
              <Text style={styles.statLabel}>📊 Total Messages Learned</Text>
              <Text style={styles.statValue}>{trainingStats.total_samples_trained}</Text>
            </View>
            <View style={styles.statRow}>
              <Text style={styles.statLabel}>📱 WhatsApp Messages</Text>
              <Text style={styles.statValue}>{trainingStats.whatsapp_samples}</Text>
            </View>
            <View style={styles.statRow}>
              <Text style={styles.statLabel}>✍️ Manual Samples</Text>
              <Text style={styles.statValue}>{trainingStats.manual_samples}</Text>
            </View>
            <View style={styles.statRow}>
              <Text style={styles.statLabel}>🎯 Learning Accuracy</Text>
              <Text style={styles.statValue}>{Math.round(trainingStats.accuracy_score * 100)}%</Text>
            </View>

            {trainingStats.most_common_slang.length > 0 && (
              <View style={styles.statRow}>
                <Text style={styles.statLabel}>💬 Your Slang Patterns</Text>
                <Text style={styles.statValue}>{trainingStats.most_common_slang.join(", ")}</Text>
              </View>
            )}

            {trainingStats.last_training_time && (
              <Text style={styles.subtleText}>
                Last trained: {new Date(trainingStats.last_training_time).toLocaleDateString()}
              </Text>
            )}
          </View>
        ) : null}
      </View>

      {/* WhatsApp Overlay Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>WhatsApp Native Overlay</Text>
        <View style={styles.row}>
          <Text style={styles.text}>Enable WhatsApp Extension</Text>
          <Switch value={isOverlayActive} onValueChange={toggleOverlay} trackColor={{ true: colors.primary }} />
        </View>
        <Text style={styles.subtitle}>Allowed Groups</Text>
        {allowedGroups.map((group) => (
          <View key={group} style={styles.groupRow}>
            <Text style={styles.text}>{group}</Text>
            <Pressable onPress={() => removeAllowedGroup(group)}>
              <Text style={styles.dangerText}>Remove</Text>
            </Pressable>
          </View>
        ))}
        <View style={styles.inputRow}>
          <TextInput
            style={styles.input}
            placeholder="E.g. College Friends"
            value={newGroup}
            onChangeText={setNewGroup}
            onSubmitEditing={handleAddGroup}
          />
          <Pressable onPress={handleAddGroup} style={styles.addButton}>
            <Text style={styles.addButtonLabel}>Add</Text>
          </Pressable>
        </View>
      </View>

      <Pressable onPress={handleLogout} style={styles.button}>
        <Text style={styles.buttonLabel}>Logout</Text>
      </Pressable>
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  section: {
    backgroundColor: colors.surface,
    padding: 16,
    borderRadius: 16,
    marginBottom: 24,
    gap: 12
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: colors.text,
    marginBottom: 8
  },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 8
  },
  text: {
    fontSize: 14,
    color: colors.text,
    fontWeight: "500"
  },
  subtitle: {
    fontWeight: "600",
    color: colors.text,
    marginTop: 12,
    marginBottom: 8
  },
  subtleText: {
    fontSize: 13,
    color: colors.textSecondary,
    fontStyle: "italic",
    marginTop: 8
  },
  groupRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: colors.border
  },
  dangerText: {
    color: colors.accent,
    fontSize: 13,
    fontWeight: "600"
  },
  inputRow: {
    flexDirection: "row",
    gap: 8,
    marginTop: 12
  },
  input: {
    flex: 1,
    backgroundColor: colors.canvas,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 13,
    color: colors.text
  },
  addButton: {
    backgroundColor: colors.primary,
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 10,
    justifyContent: "center"
  },
  addButtonLabel: {
    color: "#FFFFFF",
    fontWeight: "600",
    fontSize: 13
  },
  button: {
    backgroundColor: colors.primary,
    borderRadius: 16,
    paddingVertical: 14,
    alignItems: "center"
  },
  buttonLabel: {
    color: "#FFFFFF",
    fontWeight: "700",
    fontSize: 16
  },
  statsContainer: {
    backgroundColor: colors.canvas,
    borderRadius: 12,
    padding: 12,
    marginTop: 12,
    gap: 10
  },
  statRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: colors.border
  },
  statLabel: {
    fontSize: 13,
    color: colors.text,
    fontWeight: "500",
    flex: 1
  },
  statValue: {
    fontSize: 14,
    color: colors.primary,
    fontWeight: "700"
  }
});
    marginTop: 8
  },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center"
  },
  groupRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    backgroundColor: colors.canvas,
    padding: 12,
    borderRadius: 8
  },
  inputRow: {
    flexDirection: "row",
    gap: 8
  },
  input: {
    flex: 1,
    backgroundColor: colors.canvas,
    padding: 12,
    borderRadius: 8,
    color: colors.text
  },
  text: {
    color: colors.text
  },
  dangerText: {
    color: colors.danger,
    fontWeight: "600"
  },
  addButton: {
    backgroundColor: colors.primary,
    paddingHorizontal: 20,
    justifyContent: "center",
    borderRadius: 8
  },
  addButtonLabel: {
    color: "#fff",
    fontWeight: "700"
  },
  button: {
    backgroundColor: colors.danger,
    borderRadius: 16,
    paddingVertical: 14,
    alignItems: "center"
  },
  buttonLabel: {
    color: "#FFFFFF",
    fontWeight: "700"
  }
});
