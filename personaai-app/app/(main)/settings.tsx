import { useState } from "react";
import { router } from "expo-router";
import { Pressable, StyleSheet, Text, View, Switch, TextInput } from "react-native";

import { AppScreen } from "@/components/AppScreen";
import { colors } from "@/constants/colors";
import { useAuthStore } from "@/store/authStore";
import { useOverlayStore } from "@/store/overlayStore";

export default function SettingsScreen() {
  const logout = useAuthStore((state) => state.logout);
  const { isOverlayActive, toggleOverlay, allowedGroups, addAllowedGroup, removeAllowedGroup } = useOverlayStore();
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

  return (
    <AppScreen title="Settings" subtitle="Manage your WhatsApp Extension and settings.">
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
