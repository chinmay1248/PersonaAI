import { useEffect, useState } from "react";
import { Alert, Pressable, StyleSheet, Text, View } from "react-native";

import { AppScreen } from "@/components/AppScreen";
import { ChatConfigCard } from "@/components/ChatConfigCard";
import { chatService } from "@/services/chatService";
import { useChatStore } from "@/store/chatStore";
import { useOverlayStore } from "@/store/overlayStore";

export default function ChatConfigsScreen() {
  const { chats, setChats, activeChatId, setActiveChatId } = useChatStore();
  const syncAllowedGroups = useOverlayStore((state) => state.syncAllowedGroups);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    chatService.getConfigs()
      .then((data) => {
        setChats(data);
        syncAllowedGroups(data.map((chat: { chat_label: string }) => chat.chat_label));
        setLoading(false);
      })
      .catch((error) => {
        Alert.alert("Failed to load", error.message);
        setLoading(false);
      });
  }, []);

  return (
    <AppScreen title="Chat configurations" subtitle="Manage your active persona mapping for specific friend groups or contexts.">
      {loading ? <Text style={styles.text}>Loading chats...</Text> : null}
      
      {!loading && chats.length === 0 ? (
        <Text style={styles.text}>No chats config mapped yet. Use onboarding to create one.</Text>
      ) : null}

      <View style={{ gap: 12 }}>
        {chats.map((chat) => (
          <Pressable 
            key={chat.id} 
            onPress={() => setActiveChatId(chat.id)}
            style={{ opacity: activeChatId === chat.id ? 1 : 0.6 }}
          >
            <ChatConfigCard 
              label={chat.chat_label} 
              type={chat.chat_type} 
              personality={chat.personality_mode} 
              autoReplyMode={chat.auto_reply_mode || "OFF"} 
            />
          </Pressable>
        ))}
      </View>
    </AppScreen>
  );
}

const styles = StyleSheet.create({
  text: {
    color: "#6B7280",
    marginBottom: 12
  }
});
