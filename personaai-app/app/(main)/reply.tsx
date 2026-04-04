import { useEffect, useState } from "react";
import { Alert, Pressable, StyleSheet, Text, TextInput } from "react-native";

import { AppScreen } from "@/components/AppScreen";
import { FeedbackButtons } from "@/components/FeedbackButtons";
import { LoadingReplies } from "@/components/LoadingReplies";
import { MoodBadge } from "@/components/MoodBadge";
import { ReplyList } from "@/components/ReplyList";
import { colors } from "@/constants/colors";
import { useReplies } from "@/hooks/useReplies";
import { useChatStore } from "@/store/chatStore";
import { chatService } from "@/services/chatService";

export default function ReplyScreen() {
  const [message, setMessage] = useState("Hey bro u free tomorrow?");
  const [result, setResult] = useState<{ detected_mood: string; suggestions: Array<{ id: string; rank: number; text: string }> } | null>(null);
  const { loading, generateReply } = useReplies();
  const { chats, setChats, activeChatId } = useChatStore();

  useEffect(() => {
    if (chats.length === 0) {
      chatService.getConfigs().then(setChats).catch(console.error);
    }
  }, []);

  async function handleGenerate() {
    const targetChatId = activeChatId || chats[0]?.id;
    if (!targetChatId) {
       Alert.alert("Missing chat", "Please ensure at least one chat config exists.");
       return;
    }
    
    try {
      const response = await generateReply({
        chat_config_id: targetChatId,
        incoming_messages: [message],
        conversation_history: [{ role: "them", text: "what's the scene?" }],
        count: 3
      });
      setResult(response);
    } catch (error) {
      Alert.alert("Reply generation failed", error instanceof Error ? error.message : "Please try again");
    }
  }

  return (
    <AppScreen title="Reply generator" subtitle={activeChatId ? "Using selected chat mode." : "Using default personality."}>
      <TextInput
        style={styles.input}
        value={message}
        onChangeText={setMessage}
        placeholder="Paste incoming messages here"
        multiline
      />
      <Pressable onPress={handleGenerate} style={styles.button}>
        <Text style={styles.buttonLabel}>Generate replies</Text>
      </Pressable>
      {loading ? <LoadingReplies /> : null}
      {result ? (
        <>
          <MoodBadge mood={result.detected_mood} />
          <ReplyList replies={result.suggestions} />
          <FeedbackButtons />
        </>
      ) : null}
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  input: {
    minHeight: 120,
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
  }
});
