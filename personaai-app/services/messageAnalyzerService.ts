/**
 * MessageAnalyzerService
 * Extracts individual messages from scraped WhatsApp text
 * Separates sender messages (us) from replies (them) based on common patterns
 */

export const messageAnalyzerService = {
  parseScrapedPayload(
    rawPayload: string,
    allowedGroups: string[]
  ): {
    chatTitle: string;
    matchedGroup: string | null;
    allMessages: string[];
    incomingMessages: string[];
    outgoingMessages: string[];
    capturedAt: string;
  } | null {
    const parsed = this.parseRawPayload(rawPayload);
    if (parsed.nodes.length === 0) return null;

    const meaningfulNodes = parsed.nodes.filter((node) => this.isMeaningfulText(node.text));
    if (meaningfulNodes.length === 0) return null;

    const chatTitle = this.extractChatTitle(meaningfulNodes, allowedGroups);
    const matchedGroup = this.matchAllowedGroup(meaningfulNodes.map((node) => node.text), allowedGroups);
    const messageNodes = meaningfulNodes.filter((node) => {
      if (!this.isMessageLike(node.text)) return false;
      if (chatTitle && node.text.trim().toLowerCase() === chatTitle.trim().toLowerCase()) return false;
      return node.top === undefined || node.top > 140;
    });

    const dedupedMessages = this.deduplicateMessages(messageNodes.map((node) => node.text.trim()));
    const screenWidth = parsed.screenWidth ?? 0;
    const outgoingMessages =
      screenWidth > 0
        ? this.deduplicateMessages(
            messageNodes
              .filter((node) => typeof node.left === "number" && node.left >= screenWidth * 0.45)
              .map((node) => node.text.trim())
          )
        : [];
    const incomingMessages =
      screenWidth > 0
        ? this.deduplicateMessages(
            messageNodes
              .filter((node) => typeof node.left === "number" && node.left <= screenWidth * 0.35)
              .map((node) => node.text.trim())
          )
        : dedupedMessages;

    return {
      chatTitle,
      matchedGroup,
      allMessages: dedupedMessages,
      incomingMessages,
      outgoingMessages,
      capturedAt: parsed.capturedAt,
    };
  },

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
  },

  parseRawPayload(rawPayload: string): {
    nodes: Array<{ text: string; left?: number; top?: number }>;
    screenWidth?: number;
    capturedAt: string;
  } {
    try {
      const parsed = JSON.parse(rawPayload) as {
        nodes?: Array<{ text?: string; left?: number; top?: number }>;
        screenWidth?: number;
        capturedAt?: string | number;
      };
      return {
        nodes: Array.isArray(parsed.nodes)
          ? parsed.nodes
              .filter((node): node is { text: string; left?: number; top?: number } => typeof node?.text === "string")
              .map((node) => ({
                text: node.text,
                left: typeof node.left === "number" ? node.left : undefined,
                top: typeof node.top === "number" ? node.top : undefined,
              }))
          : [],
        screenWidth: typeof parsed.screenWidth === "number" ? parsed.screenWidth : undefined,
        capturedAt: new Date(parsed.capturedAt ?? Date.now()).toISOString(),
      };
    } catch {
      return {
        nodes: rawPayload.split(" || ").map((text) => ({ text })),
        capturedAt: new Date().toISOString(),
      };
    }
  },

  matchAllowedGroup(candidates: string[], allowedGroups: string[]): string | null {
    const normalizedCandidates = candidates.map((candidate) => candidate.trim().toLowerCase()).filter(Boolean);
    for (const group of allowedGroups) {
      const normalizedGroup = group.trim().toLowerCase();
      if (!normalizedGroup) continue;
      if (normalizedCandidates.some((candidate) => candidate === normalizedGroup || candidate.includes(normalizedGroup))) {
        return group;
      }
    }

    return null;
  },

  extractChatTitle(
    nodes: Array<{ text: string; top?: number }>,
    allowedGroups: string[]
  ): string {
    const allowedMatch = this.matchAllowedGroup(
      nodes.map((node) => node.text),
      allowedGroups
    );
    if (allowedMatch) {
      return allowedMatch;
    }

    const headerCandidate = nodes
      .filter((node) => (node.top ?? 9999) < 220)
      .map((node) => node.text.trim())
      .find((text) => this.isLikelyChatTitle(text));

    return headerCandidate ?? "WhatsApp Chat";
  },

  isMeaningfulText(text: string): boolean {
    const normalized = text.trim();
    if (!normalized) return false;
    if (/^\d{1,2}:\d{2}(?:\s?[AP]M)?$/i.test(normalized)) return false;
    if (/^\d+$/.test(normalized)) return false;
    if (/^(search|back|more options|voice call|video call|attach|camera|emoji|type a message)$/i.test(normalized)) {
      return false;
    }
    if (/messages? and calls are end-to-end encrypted/i.test(normalized)) return false;
    return true;
  },

  isMessageLike(text: string): boolean {
    const normalized = text.trim();
    if (!this.isMeaningfulText(normalized)) return false;
    if (normalized.length < 2) return false;
    if (/^(online|typing…|typing\.\.\.|last seen.*)$/i.test(normalized)) return false;
    return /[a-zA-Z]/.test(normalized);
  },

  isLikelyChatTitle(text: string): boolean {
    const normalized = text.trim();
    if (!normalized) return false;
    if (!/[a-zA-Z]/.test(normalized)) return false;
    if (normalized.length > 60) return false;
    if (/^(today|yesterday|you)$/i.test(normalized)) return false;
    return true;
  }
};
