import { useState } from "react";
import { router } from "expo-router";
import { Alert, Pressable, StyleSheet, Text, View, Switch, TextInput } from "react-native";

import { AppScreen } from "@/components/AppScreen";
import { colors } from "@/constants/colors";
import { messageTrainingService } from "@/services/messageTrainingService";
import { whatsappIntegrationService } from "@/services/whatsappIntegrationService";
import { useAuthStore } from "@/store/authStore";
import { useOverlayStore } from "@/store/overlayStore";

export default function SettingsScreen() {
  const logout = useAuthStore((state) => state.logout);
  const {
    isOverlayActive,
    autoTrainingEnabled,
    toggleOverlay,
    setAutoTrainingEnabled,
    allowedGroups,
    addAllowedGroup,
    removeAllowedGroup,
    lastCapture,
    lastTrainingStatus,
    lastError,
    setLastError,
  } = useOverlayStore();
  const [newGroup, setNewGroup] = useState("");

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

  async function handleAutoTrainingToggle(enabled: boolean) {
    try {
      if (enabled) {
        await messageTrainingService.enableAutoTraining();
      } else {
        await messageTrainingService.disableAutoTraining();
      }
      setAutoTrainingEnabled(enabled);
      setLastError(null);
    } catch (error) {
      Alert.alert("Could not update auto-training", error instanceof Error ? error.message : "Please try again.");
    }
  }

  return (
    <AppScreen title="Settings" subtitle="Manage your WhatsApp Extension and settings.">
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>WhatsApp Native Overlay</Text>
        <View style={styles.row}>
          <Text style={styles.text}>Enable WhatsApp Extension</Text>
          <Switch value={isOverlayActive} onValueChange={toggleOverlay} trackColor={{ true: colors.primary }} />
        </View>
        <View style={styles.row}>
          <Text style={styles.text}>Auto-train from my outgoing messages</Text>
          <Switch
            value={autoTrainingEnabled}
            onValueChange={handleAutoTrainingToggle}
            trackColor={{ true: colors.primary }}
          />
        </View>
        <Pressable onPress={() => whatsappIntegrationService.requestAccessibilityPermission()} style={styles.secondaryButton}>
          <Text style={styles.secondaryButtonLabel}>Open Accessibility Settings</Text>
        </Pressable>
        <Pressable onPress={() => whatsappIntegrationService.requestOverlayPermission()} style={styles.secondaryButton}>
          <Text style={styles.secondaryButtonLabel}>Open Overlay Permission</Text>
        </Pressable>
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
        {lastCapture ? (
          <View style={styles.statusBlock}>
            <Text style={styles.sectionTitle}>Latest capture</Text>
            <Text style={styles.statusText}>Group: {lastCapture.matchedGroup}</Text>
            <Text style={styles.statusText}>Incoming: {lastCapture.incomingMessages.length}</Text>
            <Text style={styles.statusText}>Your messages: {lastCapture.outgoingMessages.length}</Text>
            <Text style={styles.statusText}>Captured: {new Date(lastCapture.capturedAt).toLocaleString()}</Text>
          </View>
        ) : null}
        {lastTrainingStatus ? <Text style={styles.statusText}>{lastTrainingStatus}</Text> : null}
        {lastError ? <Text style={styles.errorText}>{lastError}</Text> : null}
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
    color: colors.text
  },
  subtitle: {
    fontWeight: "600",
    color: colors.text,
    marginTop: 12,
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
  secondaryButton: {
    backgroundColor: colors.canvas,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: 14,
    paddingVertical: 12,
  },
  secondaryButtonLabel: {
    color: colors.text,
    fontWeight: "600",
    textAlign: "center",
  },
  statusBlock: {
    gap: 6,
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  statusText: {
    color: colors.muted,
    lineHeight: 18,
  },
  errorText: {
    color: "#EF4444",
    lineHeight: 18,
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
  }
});
