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
import { useOverlayStore } from "@/store/overlayStore";
import { chatService } from "@/services/chatService";
import { api } from "@/services/api";

export default function ReplyScreen() {
  const [message, setMessage] = useState("Hey bro u free tomorrow?");
  const [result, setResult] = useState<{ detected_mood: string; suggestions: Array<{ id: string; rank: number; text: string }> } | null>(null);
  const { loading, generateReply } = useReplies();
  const { chats, setChats, activeChatId } = useChatStore();
  const lastCapture = useOverlayStore((state) => state.lastCapture);

  useEffect(() => {
    if (chats.length === 0) {
      chatService.getConfigs().then(setChats).catch(console.error);
    }
  }, []);

  useEffect(() => {
    if (!lastCapture || lastCapture.incomingMessages.length === 0) return;
    setMessage(lastCapture.incomingMessages.join("\n"));
  }, [lastCapture?.capturedAt]);

  async function handleGenerate() {
    const matchedChatId =
      lastCapture?.matchedGroup
        ? chats.find((chat) => chat.chat_label.toLowerCase() === lastCapture.matchedGroup.toLowerCase())?.id
        : null;
    const targetChatId = activeChatId || matchedChatId || chats[0]?.id;
    if (!targetChatId) {
       Alert.alert("Missing chat", "Please go to Chat Configs and create at least one chat configuration first.");
       return;
    }
    
    try {
      const response = await generateReply({
        chat_config_id: targetChatId,
        incoming_messages: message.split("\n").map((item) => item.trim()).filter(Boolean),
        conversation_history: (lastCapture?.incomingMessages ?? ["what's the scene?"]).slice(0, 5).map((text) => ({
          role: "them",
          text,
        })),
        count: 3
      });
      setResult(response);
    } catch (error) {
      Alert.alert("Reply generation failed", error instanceof Error ? error.message : "Please try again");
    }
  }

  async function handleFeedback(rating: string) {
    if (!result || result.suggestions.length === 0) return;
    try {
      await api.post("/feedback/reply", {
        reply_suggestion_id: result.suggestions[0].id,
        rating: rating,
      });
      Alert.alert("Thanks!", "Your feedback helps PersonaAI learn your style better.");
    } catch (error) {
      console.error("Feedback failed:", error);
    }
  }

  return (
    <AppScreen
      title="Reply generator"
      subtitle={
        lastCapture?.matchedGroup
          ? `Latest capture from ${lastCapture.matchedGroup}.`
          : activeChatId
            ? "Using selected chat mode."
            : "Using default personality."
      }
    >
      <TextInput
        style={styles.input}
        value={message}
        onChangeText={setMessage}
        placeholder="Paste incoming messages here"
        multiline
      />
      <Pressable onPress={handleGenerate} style={[styles.button, loading && styles.buttonDisabled]} disabled={loading}>
        <Text style={styles.buttonLabel}>{loading ? "Generating..." : "Generate replies"}</Text>
      </Pressable>
      {loading ? <LoadingReplies /> : null}
      {result ? (
        <>
          <MoodBadge mood={result.detected_mood} />
          <ReplyList replies={result.suggestions} />
          <FeedbackButtons
            onLike={() => handleFeedback("liked")}
            onDislike={() => handleFeedback("disliked")}
          />
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
  buttonDisabled: {
    opacity: 0.6
  },
  buttonLabel: {
    color: "#FFFFFF",
    fontWeight: "700"
  }
});
