import { useEffect, useState } from "react";

import { toneService } from "@/services/toneService";
import { useToneStore } from "@/store/toneStore";

export function useToneProfile() {
  const { profile, setProfile } = useToneStore();
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState<{
    total_samples_trained: number;
    whatsapp_samples: number;
    manual_samples: number;
    last_training_time: string | null;
    accuracy_score: number;
    most_common_slang: string[];
  } | null>(null);

  async function refreshProfile() {
    setLoading(true);
    try {
      const [nextProfile, nextStats] = await Promise.all([
        toneService.getProfile(),
        toneService.getTrainingStats(),
      ]);
      setProfile(nextProfile);
      setStats(nextStats);
      return nextProfile;
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refreshProfile();
  }, []);

  return { profile, stats, loading, refreshProfile };
}
