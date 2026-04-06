import { useEffect } from "react";
import { Stack } from "expo-router";
import { NativeEventEmitter, NativeModules } from "react-native";
import { useOverlayStore } from "@/store/overlayStore";

const { PersonaAIModule } = NativeModules;

export default function MainLayout() {
  const { isOverlayActive } = useOverlayStore();

  useEffect(() => {
    if (!PersonaAIModule) {
      console.debug("PersonaAIModule not available - WhatsApp integration disabled");
      return;
    }

    try {
      const eventEmitter = new NativeEventEmitter(PersonaAIModule);
      const subscription = eventEmitter.addListener("OnWhatsAppMessagesScraped", (payload: string) => {
        if (isOverlayActive) {
          console.log("Received payload across bridge:", payload);
          // Auto-training logic will be added in next version
        }
      });

      return () => {
        subscription.remove();
      };
    } catch (error) {
      console.debug("Failed to setup native event listeners:", error);
      // Gracefully handle if native modules fail to initialize
    }
  }, [isOverlayActive]);

  return <Stack screenOptions={{ headerShown: true }} />;
}
