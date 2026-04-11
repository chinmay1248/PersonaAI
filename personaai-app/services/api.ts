import { Platform } from "react-native";
import axios from "axios";

import { storageService } from "@/services/storageService";

// Configure API base URL based on environment
// For production: use the deployed backend URL
// For development: use local backend or staging URL

const ENV_API_URL = process.env.EXPO_PUBLIC_API_URL?.trim();
const CLOUD_URL = "https://personaai-backend-production-4490.up.railway.app/v1";
const LOCAL_URL = Platform.OS === "android" ? "http://10.0.2.2:8000/v1" : "http://localhost:8000/v1";

// Select the appropriate URL based on environment.
// EXPO_PUBLIC_API_URL always wins, which lets physical devices use a LAN URL.
const isDevelopment = process.env.NODE_ENV === "development" || process.env.EXPO_PUBLIC_ENV === "development";
const BASE_URL = ENV_API_URL || (isDevelopment ? LOCAL_URL : CLOUD_URL);

export const API_BASE_URL = BASE_URL;

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000
});

// Request interceptor - adds authentication token
api.interceptors.request.use((config) => {
  const accessToken = storageService.getString("accessToken");
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// Response interceptor - handles token refresh and errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 Unauthorized - token may be expired
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = storageService.getString("refreshToken");
        if (refreshToken) {
          // Attempt to refresh the token
          const response = await axios.post(`${BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken
          });

          const { access_token } = response.data;
          storageService.setString("accessToken", access_token);

          // Retry the original request with the new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } else {
          // No refresh token available - logout user
          storageService.delete("accessToken");
          storageService.delete("refreshToken");
          // Could dispatch a logout action here if using state management
        }
      } catch (refreshError) {
        console.error("Token refresh failed:", refreshError);
        // Clear tokens and require re-login
        storageService.delete("accessToken");
        storageService.delete("refreshToken");
        return Promise.reject(refreshError);
      }
    }

    // Log other errors for debugging
    if (error.response?.status === 500) {
      console.error("Server error:", error.response.data);
    } else if (error.message === "Network Error") {
      console.error("Network error - check your connection and backend availability");
    }

    return Promise.reject(error);
  }
);
