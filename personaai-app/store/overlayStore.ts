import { create } from "zustand";

import { storageService } from "@/services/storageService";

export type ScrapedChatCapture = {
  chatTitle: string;
  matchedGroup: string;
  allMessages: string[];
  incomingMessages: string[];
  outgoingMessages: string[];
  capturedAt: string;
};

type OverlayState = {
  isOverlayActive: boolean;
  autoTrainingEnabled: boolean;
  allowedGroups: string[];
  lastCapture: ScrapedChatCapture | null;
  lastTrainingStatus: string | null;
  lastError: string | null;
  toggleOverlay: () => void;
  setAutoTrainingEnabled: (enabled: boolean) => void;
  addAllowedGroup: (group: string) => void;
  removeAllowedGroup: (group: string) => void;
  setLastCapture: (capture: ScrapedChatCapture | null) => void;
  setLastTrainingStatus: (status: string | null) => void;
  setLastError: (error: string | null) => void;
};

const OVERLAY_ACTIVE_KEY = "overlayActive";
const AUTO_TRAINING_KEY = "overlayAutoTraining";
const ALLOWED_GROUPS_KEY = "overlayAllowedGroups";

function readStoredGroups(): string[] {
  const stored = storageService.getString(ALLOWED_GROUPS_KEY);
  if (!stored) {
    return ["Friends Group"];
  }

  try {
    const parsed = JSON.parse(stored);
    return Array.isArray(parsed) ? parsed.filter((value): value is string => typeof value === "string") : ["Friends Group"];
  } catch {
    return ["Friends Group"];
  }
}

function persistGroups(groups: string[]) {
  storageService.setString(ALLOWED_GROUPS_KEY, JSON.stringify(groups));
}

export const useOverlayStore = create<OverlayState>((set) => ({
  isOverlayActive: storageService.getBoolean(OVERLAY_ACTIVE_KEY) ?? false,
  autoTrainingEnabled: storageService.getBoolean(AUTO_TRAINING_KEY) ?? true,
  allowedGroups: readStoredGroups(),
  lastCapture: null,
  lastTrainingStatus: null,
  lastError: null,
  toggleOverlay: () =>
    set((state) => {
      const nextValue = !state.isOverlayActive;
      storageService.setBoolean(OVERLAY_ACTIVE_KEY, nextValue);
      return { isOverlayActive: nextValue };
    }),
  setAutoTrainingEnabled: (enabled) =>
    set(() => {
      storageService.setBoolean(AUTO_TRAINING_KEY, enabled);
      return { autoTrainingEnabled: enabled };
    }),
  addAllowedGroup: (group) =>
    set((state) => {
      const normalized = group.trim();
      if (!normalized || state.allowedGroups.some((existing) => existing.toLowerCase() === normalized.toLowerCase())) {
        return state;
      }

      const nextGroups = [...state.allowedGroups, normalized];
      persistGroups(nextGroups);
      return { allowedGroups: nextGroups };
    }),
  removeAllowedGroup: (group) =>
    set((state) => {
      const nextGroups = state.allowedGroups.filter((existing) => existing !== group);
      const groupsToStore = nextGroups.length > 0 ? nextGroups : ["Friends Group"];
      persistGroups(groupsToStore);
      return { allowedGroups: groupsToStore };
    }),
  setLastCapture: (capture) => set(() => ({ lastCapture: capture })),
  setLastTrainingStatus: (status) => set(() => ({ lastTrainingStatus: status })),
  setLastError: (error) => set(() => ({ lastError: error })),
}));
