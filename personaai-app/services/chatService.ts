import { api } from "@/services/api";

export type ChatConfigPayload = {
  chat_label: string;
  chat_type?: string;
  personality_mode?: string;
  auto_reply_mode?: string;
};

export const chatService = {
  async getConfigs() {
    const response = await api.get("/chats/config");
    return response.data;
  },
  async createConfig(payload: ChatConfigPayload) {
    const response = await api.post("/chats/config", payload);
    return response.data;
  }
};
