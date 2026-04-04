import { create } from "zustand";

type ChatConfig = {
  id: string;
  chat_label: string;
  chat_type?: string;
  personality_mode?: string;
  auto_reply_mode: string;
};

type ChatState = {
  chats: ChatConfig[];
  activeChatId: string | null;
  setChats: (chats: ChatConfig[]) => void;
  setActiveChatId: (id: string) => void;
};

export const useChatStore = create<ChatState>((set) => ({
  chats: [],
  activeChatId: null,
  setChats: (chats) => set({ chats }),
  setActiveChatId: (id) => set({ activeChatId: id })
}));
