import { useState } from "react";

import { aiService } from "@/services/aiService";

export function useReplies() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function generateReply(payload: {
    chat_config_id: string;
    incoming_messages: string[];
    conversation_history: Array<{ role: string; text: string }>;
    count?: number;
  }) {
    setLoading(true);
    setError(null);
    try {
      return await aiService.generateReply(payload);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate reply");
      throw err;
    } finally {
      setLoading(false);
    }
  }

  return { loading, error, generateReply };
}
