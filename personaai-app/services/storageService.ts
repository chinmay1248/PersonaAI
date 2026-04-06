import { MMKV } from 'react-native-mmkv';

// Lazy-initialize MMKV with fallback to in-memory storage if native module fails
let mmkvStorage: MMKV | null = null;
const memoryFallback: Record<string, string | number | boolean> = {};

function getStorage(): MMKV | null {
  if (mmkvStorage) return mmkvStorage;
  try {
    mmkvStorage = new MMKV();
    return mmkvStorage;
  } catch (error) {
    console.warn('MMKV initialization failed, using in-memory fallback:', error);
    return null;
  }
}

export const storageService = {
  setString(key: string, value: string) {
    const storage = getStorage();
    if (storage) {
      storage.set(key, value);
    } else {
      memoryFallback[key] = value;
    }
  },
  getString(key: string): string | null {
    const storage = getStorage();
    if (storage) {
      return storage.getString(key) ?? null;
    }
    const val = memoryFallback[key];
    return typeof val === 'string' ? val : null;
  },
  setNumber(key: string, value: number) {
    const storage = getStorage();
    if (storage) {
      storage.set(key, value);
    } else {
      memoryFallback[key] = value;
    }
  },
  getNumber(key: string): number | null {
    const storage = getStorage();
    if (storage) {
      const value = storage.getNumber(key);
      return value !== undefined ? value : null;
    }
    const val = memoryFallback[key];
    return typeof val === 'number' ? val : null;
  },
  setBoolean(key: string, value: boolean) {
    const storage = getStorage();
    if (storage) {
      storage.set(key, value);
    } else {
      memoryFallback[key] = value;
    }
  },
  getBoolean(key: string): boolean | null {
    const storage = getStorage();
    if (storage) {
      const value = storage.getBoolean(key);
      return value !== undefined ? value : null;
    }
    const val = memoryFallback[key];
    return typeof val === 'boolean' ? val : null;
  },
  delete(key: string) {
    const storage = getStorage();
    if (storage) {
      storage.delete(key);
    } else {
      delete memoryFallback[key];
    }
  },
  clear() {
    const storage = getStorage();
    if (storage) {
      storage.clearAll();
    } else {
      Object.keys(memoryFallback).forEach((k) => delete memoryFallback[k]);
    }
  }
};
