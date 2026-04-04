import { api } from "@/services/api";

export const toneService = {
  async train(samples: string[]) {
    const response = await api.post("/tone/train", { samples });
    return response.data;
  },
  async getProfile() {
    const response = await api.get("/tone/profile");
    return response.data;
  }
};
