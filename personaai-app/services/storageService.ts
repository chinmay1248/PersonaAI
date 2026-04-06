import { MMKV } from 'react-native-mmkv';

// Create persistent storage instance
const mmkvStorage = new MMKV();

export const storageService = {
  setString(key: string, value: string) {
    mmkvStorage.set(key, value);
  },
  getString(key: string) {
    return mmkvStorage.getString(key) ?? null;
  },
  setNumber(key: string, value: number) {
    mmkvStorage.set(key, value);
  },
  getNumber(key: string): number | null {
    const value = mmkvStorage.getNumber(key);
    return value !== undefined ? value : null;
  },
  setBoolean(key: string, value: boolean) {
    mmkvStorage.set(key, value);
  },
  getBoolean(key: string): boolean | null {
    const value = mmkvStorage.getBoolean(key);
    return value !== undefined ? value : null;
  },
  delete(key: string) {
    mmkvStorage.delete(key);
  },
  clear() {
    mmkvStorage.clearAll();
  }
};
