import { NativeEventEmitter, NativeModules, Platform } from "react-native";

type MessageListener = (payload: string) => void;

function getPersonaModule() {
  if (Platform.OS !== "android") {
    return null;
  }

  return NativeModules?.PersonaAIModule ?? null;
}

export const whatsappIntegrationService = {
  isAvailable() {
    return Boolean(getPersonaModule());
  },

  requestAccessibilityPermission() {
    getPersonaModule()?.requestAccessibilityPermission?.();
  },

  requestOverlayPermission() {
    getPersonaModule()?.requestOverlayPermission?.();
  },

  subscribe(listener: MessageListener) {
    const module = getPersonaModule();
    if (!module) {
      return () => undefined;
    }

    const emitter = new NativeEventEmitter(module);
    const subscription = emitter.addListener("OnWhatsAppMessagesScraped", listener);
    return () => subscription.remove();
  },
};
