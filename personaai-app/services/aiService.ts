import { api } from "@/services/api";

export const aiService = {
  async generateReply(payload: {
    chat_config_id: string;
    incoming_messages: string[];
    conversation_history: Array<{ role: string; text: string }>;
    count?: number;
  }) {
    const response = await api.post("/ai/generate-reply", payload);
    return response.data;
  },
  async summarize(messages: string[]) {
    const response = await api.post("/ai/summarize", { messages });
    return response.data;
  }
};
