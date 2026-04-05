/**
 * MessageTrainingService
 * Sends extracted messages to backend for continuous tone learning
 */

import { api } from "@/services/api";

export const messageTrainingService = {
  /**
   * Train tone profile with new messages from WhatsApp
   * Can be called continuously as new messages are scraped
   */
  async trainFromWhatsAppMessages(messages: string[]) {
    if (messages.length === 0) {
      throw new Error("No messages to train from");
    }

    const response = await api.post("/tone/train-from-messages", {
      messages,
      source: "whatsapp"
    });

    return response.data;
  },

  /**
   * Get training statistics (how many messages learned, accuracy, etc.)
   */
  async getTrainingStats() {
    const response = await api.get("/tone/training-stats");
    return response.data;
  },

  /**
   * Enable auto-training mode (continuously learn from WhatsApp)
   */
  async enableAutoTraining() {
    const response = await api.post("/tone/enable-auto-training", {});
    return response.data;
  },

  /**
   * Disable auto-training mode
   */
  async disableAutoTraining() {
    const response = await api.post("/tone/disable-auto-training", {});
    return response.data;
  }
};
