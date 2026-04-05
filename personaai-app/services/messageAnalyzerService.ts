/**
 * MessageAnalyzerService
 * Extracts individual messages from scraped WhatsApp text
 * Separates sender messages (us) from replies (them) based on common patterns
 */

export const messageAnalyzerService = {
  /**
   * Extracts your sent messages from raw scraped WhatsApp text
   * Identifies messages by common WhatsApp patterns
   */
  extractYourMessages(scrapedText: string): string[] {
    if (!scrapedText) return [];

    // Split by common separator
    let messages = scrapedText.split(" || ");

    // Filter out timestamps, metadata, and system messages
    const filtered = messages
      .map((msg) => msg.trim())
      .filter((msg) => {
        // Remove if it's a timestamp (HH:MM format)
        if (/^\d{1,2}:\d{2}(?: [AP]M)?$/.test(msg)) return false;

        // Remove if it's system message
        if (/^(You|Messages? and calls are end-to-end encrypted)/i.test(msg)) return false;

        // Remove very short fragments (< 3 chars)
        if (msg.length < 3) return false;

        // Remove number-only messages (usually group info)
        if (/^\d+$/.test(msg)) return false;

        return true;
      });

    return filtered;
  },

  /**
   * Deduplicates messages and removes near-duplicates
   */
  deduplicateMessages(messages: string[]): string[] {
    const seen = new Set<string>();
    const deduplicated: string[] = [];

    for (const msg of messages) {
      const normalized = msg.toLowerCase().trim();

      // Check if exact match already seen
      if (seen.has(normalized)) continue;

      // Check if similar to any existing message (>80% similar)
      const isSimilar = deduplicated.some((existing) => this.calculateSimilarity(msg, existing) > 0.8);
      if (isSimilar) continue;

      seen.add(normalized);
      deduplicated.push(msg);
    }

    return deduplicated;
  },

  /**
   * Simple similarity score between two strings (0-1)
   */
  calculateSimilarity(str1: string, str2: string): number {
    const longer = str1.length > str2.length ? str1 : str2;
    const shorter = str1.length > str2.length ? str2 : str1;

    if (longer.length === 0) return 1.0;

    const editDistance = this.levenshteinDistance(longer, shorter);
    return (longer.length - editDistance) / longer.length;
  },

  /**
   * Levenshtein distance algorithm for string similarity
   */
  levenshteinDistance(s1: string, s2: string): number {
    const costs: number[] = [];

    for (let i = 0; i <= s1.length; i++) {
      let lastValue = i;
      for (let j = 0; j <= s2.length; j++) {
        if (i === 0) {
          costs[j] = j;
        } else if (j > 0) {
          let newValue = costs[j - 1];
          if (s1.charAt(i - 1) !== s2.charAt(j - 1)) {
            newValue = Math.min(Math.min(newValue, lastValue), costs[j]) + 1;
          }
          costs[j - 1] = lastValue;
          lastValue = newValue;
        }
      }
      if (i > 0) costs[s2.length] = lastValue;
    }

    return costs[s2.length];
  },

  /**
   * Filter messages by minimum length and quality
   */
  filterQualityMessages(messages: string[], minLength: number = 5): string[] {
    return messages.filter((msg) => {
      // Must be at least minLength characters
      if (msg.length < minLength) return false;

      // Must have at least one letter
      if (!/[a-zA-Z]/i.test(msg)) return false;

      // Remove messages that are all caps (likely titles/headers)
      if (msg === msg.toUpperCase() && msg.length > 10) return false;

      return true;
    });
  },

  /**
   * Get most recent and most frequent messages (best training samples)
   */
  selectBestSamples(messages: string[], count: number = 10): string[] {
    // Sort by length (longer messages = more training data)
    const sorted = [...messages].sort((a, b) => b.length - a.length);

    // Take top N
    return sorted.slice(0, count);
  }
};
