const memoryStore = new Map<string, string>();

export const storageService = {
  setString(key: string, value: string) {
    memoryStore.set(key, value);
  },
  getString(key: string) {
    return memoryStore.get(key) ?? null;
  },
  delete(key: string) {
    memoryStore.delete(key);
  }
};
