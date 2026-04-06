import { useEffect } from "react";
import { Stack } from "expo-router";
import { NativeModules, Platform } from "react-native";
import { useOverlayStore } from "@/store/overlayStore";

export default function MainLayout() {
  const { isOverlayActive } = useOverlayStore();

  useEffect(() => {
    // Only attempt native module access on Android
    if (Platform.OS !== "android") return;

    try {
      const PersonaAIModule = NativeModules?.PersonaAIModule;
      if (!PersonaAIModule) {
        console.debug("PersonaAIModule not available - WhatsApp integration disabled");
        return;
      }

      // Dynamically import NativeEventEmitter to avoid crash if module is unavailable
      const { NativeEventEmitter } = require("react-native");
      const eventEmitter = new NativeEventEmitter(PersonaAIModule);
      const subscription = eventEmitter.addListener("OnWhatsAppMessagesScraped", (payload: string) => {
        if (isOverlayActive) {
          console.log("Received payload across bridge:", payload);
        }
      });

      return () => {
        subscription.remove();
      };
    } catch (error) {
      console.debug("Failed to setup native event listeners:", error);
    }
  }, [isOverlayActive]);

  return <Stack screenOptions={{ headerShown: true }} />;
}
