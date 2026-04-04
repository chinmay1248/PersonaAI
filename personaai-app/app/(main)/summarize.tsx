import { useState } from "react";
import { Alert, Pressable, StyleSheet, Text, TextInput, View } from "react-native";

import { AppScreen } from "@/components/AppScreen";
import { colors } from "@/constants/colors";
import { aiService } from "@/services/aiService";

export default function SummarizeScreen() {
  const [messages, setMessages] = useState("bro sun\nkal project deadline hai\nmeeting 3pm pe hai");
  const [summary, setSummary] = useState<{ summary: string; action_items: string[] } | null>(null);

  async function handleSummarize() {
    try {
      const response = await aiService.summarize(messages.split("\n").filter(Boolean));
      setSummary(response);
    } catch (error) {
      Alert.alert("Summarization failed", error instanceof Error ? error.message : "Please try again");
    }
  }

  return (
    <AppScreen title="Unread summary" subtitle="Paste a stack of unread messages and get the condensed version back.">
      <TextInput
        style={styles.input}
        value={messages}
        onChangeText={setMessages}
        placeholder="One message per line"
        multiline
        numberOfLines={6}
      />
      <Pressable onPress={handleSummarize} style={styles.button}>
        <Text style={styles.buttonLabel}>Summarize</Text>
      </Pressable>
      {summary ? (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Summary</Text>
          <Text style={styles.cardText}>{summary.summary}</Text>
          <Text style={styles.cardTitle}>Action items</Text>
          {summary.action_items.map((item) => (
            <Text key={item} style={styles.cardText}>
              • {item}
            </Text>
          ))}
        </View>
      ) : null}
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  input: {
    minHeight: 160,
    textAlignVertical: "top",
    backgroundColor: colors.surface,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: 14,
    paddingVertical: 14
  },
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
  cardTitle: {
    fontWeight: "700",
    color: colors.text
  },
  cardText: {
    color: colors.muted,
    lineHeight: 20
  }
});
