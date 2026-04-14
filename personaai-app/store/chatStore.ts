import { create } from "zustand";

import { storageService } from "@/services/storageService";

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

const ACTIVE_CHAT_ID_KEY = "activeChatId";

export const useChatStore = create<ChatState>((set) => ({
  chats: [],
  activeChatId: storageService.getString(ACTIVE_CHAT_ID_KEY),
  setChats: (chats) => set({ chats }),
  setActiveChatId: (id) =>
    set(() => {
      storageService.setString(ACTIVE_CHAT_ID_KEY, id);
      return { activeChatId: id };
    })
}));
