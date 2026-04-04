import { create } from "zustand";

type OverlayState = {
  isOverlayActive: boolean;
  allowedGroups: string[];
  toggleOverlay: () => void;
  addAllowedGroup: (group: string) => void;
  removeAllowedGroup: (group: string) => void;
};

export const useOverlayStore = create<OverlayState>((set) => ({
  isOverlayActive: false,
  allowedGroups: ["Dev Team", "Friends"],
  toggleOverlay: () => set((state) => ({ isOverlayActive: !state.isOverlayActive })),
  addAllowedGroup: (group) => set((state) => ({ allowedGroups: [...state.allowedGroups, group] })),
  removeAllowedGroup: (group) => set((state) => ({ allowedGroups: state.allowedGroups.filter((g) => g !== group) }))
}));
