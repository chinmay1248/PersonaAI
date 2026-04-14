import { create } from "zustand";

type ToneProfile = {
  formality_score: number;
  avg_message_length: number;
  emoji_frequency: number;
  slang_patterns: string[];
  detected_language_mix: string[];
  accuracy_score: number;
};

type ToneState = {
  profile: ToneProfile | null;
  setProfile: (profile: ToneProfile) => void;
};

export const useToneStore = create<ToneState>((set) => ({
  profile: null,
  setProfile: (profile) => set({ profile })
}));
