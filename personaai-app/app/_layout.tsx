import React from "react";
import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { Text, View, Pressable, StyleSheet } from "react-native";

import { colors } from "@/constants/colors";

class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error: Error | null }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error("App crash caught by ErrorBoundary:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <View style={boundaryStyles.container}>
          <Text style={boundaryStyles.title}>Something went wrong</Text>
          <Text style={boundaryStyles.message}>
            {this.state.error?.message || "An unexpected error occurred"}
          </Text>
          <Pressable
            style={boundaryStyles.button}
            onPress={() => this.setState({ hasError: false, error: null })}
          >
            <Text style={boundaryStyles.buttonText}>Try Again</Text>
          </Pressable>
        </View>
      );
    }
    return this.props.children;
  }
}

const boundaryStyles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 32,
    backgroundColor: colors.canvas,
  },
  title: {
    fontSize: 22,
    fontWeight: "700",
    color: colors.text,
    marginBottom: 12,
  },
  message: {
    fontSize: 14,
    color: colors.muted,
    textAlign: "center",
    marginBottom: 24,
    lineHeight: 20,
  },
  button: {
    backgroundColor: colors.primary,
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 12,
  },
  buttonText: {
    color: "#FFFFFF",
    fontWeight: "700",
    fontSize: 16,
  },
});

export default function RootLayout() {
  return (
    <ErrorBoundary>
      <StatusBar style="auto" />
      <Stack
        screenOptions={{
          headerStyle: { backgroundColor: colors.canvas },
          headerTintColor: colors.text,
          contentStyle: { backgroundColor: colors.canvas }
        }}
      />
    </ErrorBoundary>
  );
}
