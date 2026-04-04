import { useState } from "react";

import { toneService } from "@/services/toneService";
import { useToneStore } from "@/store/toneStore";

export function useToneProfile() {
  const { profile, setProfile } = useToneStore();
  const [loading, setLoading] = useState(false);

  async function refreshProfile() {
    setLoading(true);
    try {
      const nextProfile = await toneService.getProfile();
      setProfile(nextProfile);
      return nextProfile;
    } finally {
      setLoading(false);
    }
  }

  return { profile, loading, refreshProfile };
}
