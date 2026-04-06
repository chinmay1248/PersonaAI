import { Redirect } from "expo-router";
import { useAuthStore } from "@/store/authStore";

export default function Index() {
  const accessToken = useAuthStore((state) => state.accessToken);
  
  // If user has an existing session, skip login and go to home
  if (accessToken) {
    return <Redirect href="/(main)/home" />;
  }
  
  return <Redirect href="/(auth)/login" />;
}
