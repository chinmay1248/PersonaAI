// Temporary release-safe storage for Android crash isolation.
// This keeps the app usable for testing even if a native storage module is unstable.
const memoryFallback: Record<string, string | number | boolean> = {};

export const storageService = {
  setString(key: string, value: string) {
    memoryFallback[key] = value;
  },
  getString(key: string): string | null {
    const val = memoryFallback[key];
    return typeof val === 'string' ? val : null;
  },
  setNumber(key: string, value: number) {
    memoryFallback[key] = value;
  },
  getNumber(key: string): number | null {
    const val = memoryFallback[key];
    return typeof val === 'number' ? val : null;
  },
  setBoolean(key: string, value: boolean) {
    memoryFallback[key] = value;
  },
  getBoolean(key: string): boolean | null {
    const val = memoryFallback[key];
    return typeof val === 'boolean' ? val : null;
  },
  delete(key: string) {
    delete memoryFallback[key];
  },
  clear() {
    Object.keys(memoryFallback).forEach((k) => delete memoryFallback[k]);
  }
};
