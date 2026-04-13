import { useEffect, useRef } from "react";
import { Stack } from "expo-router";
import { Platform } from "react-native";

import { messageAnalyzerService } from "@/services/messageAnalyzerService";
import { messageTrainingService } from "@/services/messageTrainingService";
import { whatsappIntegrationService } from "@/services/whatsappIntegrationService";
import { useAuthStore } from "@/store/authStore";
import { useOverlayStore } from "@/store/overlayStore";

export default function MainLayout() {
  const {
    isOverlayActive,
    autoTrainingEnabled,
    allowedGroups,
    setLastCapture,
    setLastError,
    setLastTrainingStatus,
  } = useOverlayStore();
  const accessToken = useAuthStore((state) => state.accessToken);
  const lastProcessedSignatureRef = useRef<string | null>(null);

  useEffect(() => {
    if (Platform.OS !== "android") return;
    if (!isOverlayActive) return;

    const unsubscribe = whatsappIntegrationService.subscribe((payload: string) => {
      const capture = messageAnalyzerService.parseScrapedPayload(payload, allowedGroups);
      if (!capture || !capture.matchedGroup) {
        return;
      }

      const signature = [
        capture.matchedGroup,
        capture.chatTitle,
        capture.incomingMessages.join("|"),
        capture.outgoingMessages.join("|"),
      ].join("::");
      if (signature === lastProcessedSignatureRef.current) {
        return;
      }

      lastProcessedSignatureRef.current = signature;
      setLastCapture({
        chatTitle: capture.chatTitle,
        matchedGroup: capture.matchedGroup,
        allMessages: capture.allMessages,
        incomingMessages: capture.incomingMessages,
        outgoingMessages: capture.outgoingMessages,
        capturedAt: capture.capturedAt,
      });
      setLastError(null);

      if (!autoTrainingEnabled) {
        setLastTrainingStatus(`Captured ${capture.allMessages.length} messages from ${capture.matchedGroup}.`);
        return;
      }

      if (!accessToken) {
        setLastTrainingStatus("Captured WhatsApp messages. Sign in to train your profile automatically.");
        return;
      }

      const outgoingSamples = messageAnalyzerService.selectBestSamples(
        messageAnalyzerService.deduplicateMessages(capture.outgoingMessages),
        10
      );

      if (outgoingSamples.length === 0) {
        setLastTrainingStatus(
          `Captured ${capture.allMessages.length} messages from ${capture.matchedGroup}, but could not confidently detect your outgoing messages yet.`
        );
        return;
      }

      void messageTrainingService
        .trainFromWhatsAppMessages(outgoingSamples)
        .then(() => {
          setLastTrainingStatus(`Auto-trained from ${outgoingSamples.length} of your messages in ${capture.matchedGroup}.`);
        })
        .catch((error: unknown) => {
          const message = error instanceof Error ? error.message : "Failed to auto-train from WhatsApp messages";
          setLastError(message);
        });
    });

    return unsubscribe;
  }, [
    accessToken,
    allowedGroups,
    autoTrainingEnabled,
    isOverlayActive,
    setLastCapture,
    setLastError,
    setLastTrainingStatus,
  ]);

  return <Stack screenOptions={{ headerShown: true }} />;
}
