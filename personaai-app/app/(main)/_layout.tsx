import { useEffect } from "react";
import { Stack } from "expo-router";
import { NativeEventEmitter, NativeModules } from "react-native";
import { useOverlayStore } from "@/store/overlayStore";

const { PersonaAIModule } = NativeModules;

export default function MainLayout() {
  const { isOverlayActive } = useOverlayStore();

  useEffect(() => {
    if (!PersonaAIModule) return;

    const eventEmitter = new NativeEventEmitter(PersonaAIModule);
    const subscription = eventEmitter.addListener("OnWhatsAppMessagesScraped", (payload: string) => {
      if (isOverlayActive) {
        console.log("Safely received payload across bridge:", payload);
        // We will beam this to Python `/ai/summarize` and trigger the Overlay view from here.
      }
    });

    return () => {
      subscription.remove();
    };
  }, [isOverlayActive]);

  return <Stack screenOptions={{ headerShown: true }} />;
}
