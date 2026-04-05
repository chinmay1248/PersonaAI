import { useEffect, useState } from "react";
import { Stack } from "expo-router";
import { NativeEventEmitter, NativeModules } from "react-native";
import { useOverlayStore } from "@/store/overlayStore";
import { messageAnalyzerService } from "@/services/messageAnalyzerService";
import { messageTrainingService } from "@/services/messageTrainingService";

const { PersonaAIModule } = NativeModules;

export default function MainLayout() {
  const { isOverlayActive } = useOverlayStore();
  const [isAutoTrainingEnabled, setIsAutoTrainingEnabled] = useState(true);

  useEffect(() => {
    if (!PersonaAIModule) return;

    const eventEmitter = new NativeEventEmitter(PersonaAIModule);
    const subscription = eventEmitter.addListener("OnWhatsAppMessagesScraped", async (payload: string) => {
      if (!isOverlayActive || !isAutoTrainingEnabled) return;

      try {
        // Extract individual messages from raw scraped text
        const allMessages = messageAnalyzerService.extractYourMessages(payload);
        
        // Remove duplicates and low-quality messages
        const uniqueMessages = messageAnalyzerService.deduplicateMessages(allMessages);
        const qualityMessages = messageAnalyzerService.filterQualityMessages(uniqueMessages);
        
        if (qualityMessages.length === 0) {
          console.log("📊 No quality messages to train from");
          return;
        }

        // Select best samples for training (prevents training on repetitive messages)
        const trainingSamples = messageAnalyzerService.selectBestSamples(qualityMessages, 15);

        console.log(`📚 Auto-training with ${trainingSamples.length} messages from WhatsApp`);

        // Send to backend for continuous tone learning
        await messageTrainingService.trainFromWhatsAppMessages(trainingSamples);

        console.log("✅ Tone profile updated with your recent messages");
      } catch (error) {
        console.error("❌ Failed to auto-train tone profile:", error);
      }
    });

    return () => {
      subscription.remove();
    };
  }, [isOverlayActive, isAutoTrainingEnabled]);

  return <Stack screenOptions={{ headerShown: true }} />;
}
