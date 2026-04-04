import { PropsWithChildren, ReactNode } from "react";
import { SafeAreaView, ScrollView, StyleSheet, Text, View } from "react-native";

import { colors } from "@/constants/colors";
import { typography } from "@/constants/typography";

type AppScreenProps = PropsWithChildren<{
  title: string;
  subtitle?: string;
  footer?: ReactNode;
}>;

export function AppScreen({ title, subtitle, footer, children }: AppScreenProps) {
  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <Text style={styles.title}>{title}</Text>
          {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
        </View>
        <View style={styles.body}>{children}</View>
        {footer ? <View style={styles.footer}>{footer}</View> : null}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: colors.canvas
  },
  content: {
    padding: 20,
    gap: 20
  },
  header: {
    gap: 8
  },
  title: {
    fontSize: typography.title,
    fontWeight: "700",
    color: colors.text
  },
  subtitle: {
    fontSize: typography.body,
    lineHeight: 22,
    color: colors.muted
  },
  body: {
    gap: 14
  },
  footer: {
    marginTop: 8
  }
});
