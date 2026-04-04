import { api } from "@/services/api";

export const authService = {
  async register(payload: { email: string; password: string; display_name?: string }) {
    const response = await api.post("/auth/register", payload);
    return response.data;
  },
  async login(payload: { email: string; password: string }) {
    const response = await api.post("/auth/login", payload);
    return response.data;
  }
};
