import { create } from "zustand";

import { storageService } from "@/services/storageService";

type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  userId: string | null;
  setSession: (session: { accessToken: string; refreshToken: string; userId: string }) => void;
  logout: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: storageService.getString("accessToken"),
  refreshToken: storageService.getString("refreshToken"),
  userId: storageService.getString("userId"),
  setSession: ({ accessToken, refreshToken, userId }) => {
    storageService.setString("accessToken", accessToken);
    storageService.setString("refreshToken", refreshToken);
    storageService.setString("userId", userId);
    set({ accessToken, refreshToken, userId });
  },
  logout: () => {
    storageService.delete("accessToken");
    storageService.delete("refreshToken");
    storageService.delete("userId");
    set({ accessToken: null, refreshToken: null, userId: null });
  }
}));
