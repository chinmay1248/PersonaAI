import { Platform } from "react-native";
import axios from "axios";

import { storageService } from "@/services/storageService";

// In production, EXPO_PUBLIC_BACKEND_URL is set to the Railway cloud URL.
// During local development it falls back automatically to the right localhost address.
const CLOUD_URL = process.env.EXPO_PUBLIC_BACKEND_URL;
const LOCAL_URL = Platform.OS === "android" ? "http://10.0.2.2:8000/v1" : "http://localhost:8000/v1";
const BASE_URL = CLOUD_URL ?? LOCAL_URL;

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 15000
});

api.interceptors.request.use((config) => {
  const accessToken = storageService.getString("accessToken");
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});
