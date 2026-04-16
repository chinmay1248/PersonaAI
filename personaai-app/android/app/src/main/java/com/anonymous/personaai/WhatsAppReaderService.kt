package com.anonymous.personaai

import android.accessibilityservice.AccessibilityService
import android.graphics.Rect
import android.content.Intent
import android.os.Bundle
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import android.util.Log
import org.json.JSONArray
import org.json.JSONObject

class WhatsAppReaderService : AccessibilityService() {

    private val TAG = "WhatsAppReader"

    private var overlayManager: OverlayManager? = null

    // Debounce: avoid re-processing the exact same screen content repeatedly
    private var lastPayloadHash: Int = 0

    // Noise filter: exclude common WhatsApp chrome / UI labels
    private val NOISE_PATTERNS = setOf(
        "type a message",
        "search...",
        "online",
        "last seen",
        "tap to add",
        "disappearing messages",
        "end-to-end encrypted",
        "new chat",
        "chats",
        "status",
        "calls",
        "communities",
        "message",
        "photo",
        "video",
        "voice message",
        "camera",
        "gallery",
        "audio",
        "document",
        "location",
        "contact",
        "pay",
        "today",
        "yesterday"
    )

    // Time-stamp pattern (e.g. "10:45 AM", "3:15 pm", "22:10")
    private val TIMESTAMP_REGEX = Regex(
        "^\\d{1,2}:\\d{2}(\\s*[AaPp][Mm])?\$"
    )

    // Date header pattern (e.g. "4/15/2026", "15/04/2026", "April 15, 2026", "Today", "Yesterday")
    private val DATE_REGEX = Regex(
        "^(\\d{1,2}[/\\-]\\d{1,2}[/\\-]\\d{2,4}|" +
        "[A-Za-z]+\\s+\\d{1,2},?\\s+\\d{4}|" +
        "today|yesterday)\$",
        RegexOption.IGNORE_CASE
    )

    override fun onServiceConnected() {
        super.onServiceConnected()
        Log.i(TAG, "Accessibility service connected")
        overlayManager = OverlayManager(this)

        // Wire up the paste-back callback
        overlayManager?.onSuggestionSelected = { selectedReply ->
            pasteIntoWhatsApp(selectedReply)
        }
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        val sourcePackage = event?.packageName?.toString()
        if (event == null || (sourcePackage != "com.whatsapp" && sourcePackage != "com.whatsapp.w4b")) {
            overlayManager?.hideOverlay()
            return
        }

        overlayManager?.showOverlay()

        val rootNode = rootInActiveWindow ?: return

        // ─── Step 1: Extract all visible text nodes with screen coordinates ───
        val rawNodes = mutableListOf<ScrapedNode>()
        extractNodes(rootNode, rawNodes)

        if (rawNodes.isEmpty()) return

        // ─── Step 2: Compute a quick hash to debounce identical events ───
        val contentHash = rawNodes.map { it.text }.hashCode()
        if (contentHash == lastPayloadHash) return
        lastPayloadHash = contentHash

        // ─── Step 3: Filter out noise (timestamps, UI labels, etc.) ───
        val screenWidth = resources.displayMetrics.widthPixels
        val messageBubbles = rawNodes.filter { node ->
            isLikelyMessageBubble(node, screenWidth)
        }

        if (messageBubbles.isEmpty()) return

        // ─── Step 4: Classify incoming vs outgoing using horizontal position ───
        // WhatsApp incoming bubbles are left-aligned; outgoing are right-aligned.
        // Heuristic: if the bubble's center-X is in the left 55% of screen → incoming
        val centerThreshold = screenWidth * 0.55
        val incomingMessages = mutableListOf<String>()
        val allMessages = mutableListOf<String>()

        for (node in messageBubbles) {
            val centerX = (node.left + node.right) / 2.0
            allMessages.add(node.text)
            if (centerX < centerThreshold) {
                incomingMessages.add(node.text)
            }
        }

        // ─── Step 5: Feed the overlay with parsed message lists ───
        overlayManager?.latestAllMessages = allMessages
        overlayManager?.latestIncomingMessages = incomingMessages

        Log.d(TAG, "Parsed ${allMessages.size} msgs (${incomingMessages.size} incoming)")

        // ─── Step 6: Also broadcast to the React Native bridge (for app-side usage) ───
        val nodesJson = JSONArray()
        for (node in rawNodes) {
            nodesJson.put(JSONObject().apply {
                put("text", node.text)
                put("left", node.left)
                put("right", node.right)
                put("top", node.top)
                put("bottom", node.bottom)
            })
        }
        val payload = JSONObject().apply {
            put("packageName", sourcePackage)
            put("screenWidth", screenWidth)
            put("capturedAt", System.currentTimeMillis())
            put("incomingCount", incomingMessages.size)
            put("totalCount", allMessages.size)
            put("nodes", nodesJson)
        }.toString()

        val intent = Intent("com.anonymous.personaai.WHATSAPP_SCRAPED")
        intent.putExtra("textPayload", payload)
        sendBroadcast(intent)
    }

    // ─── PASTE BACK INTO WHATSAPP ────────────────────────────────────

    /**
     * Finds WhatsApp's text input field and injects the selected reply text.
     * Uses ACTION_SET_TEXT which sets the content of an editable field directly.
     */
    private fun pasteIntoWhatsApp(text: String) {
        val rootNode = rootInActiveWindow
        if (rootNode == null) {
            Log.w(TAG, "Cannot paste: rootInActiveWindow is null")
            return
        }

        val editText = findEditableNode(rootNode)
        if (editText != null) {
            val args = Bundle().apply {
                putCharSequence(
                    AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,
                    text
                )
            }
            val success = editText.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)
            Log.i(TAG, "Paste into WhatsApp input: success=$success")
        } else {
            // Fallback: try clipboard-based paste
            Log.w(TAG, "No editable node found; attempting clipboard fallback")
            pasteViaClipboard(rootNode, text)
        }
    }

    /**
     * Recursively searches the accessibility node tree for an editable text field.
     * WhatsApp uses an EditText (or a subclass) for the message input.
     */
    private fun findEditableNode(node: AccessibilityNodeInfo?): AccessibilityNodeInfo? {
        if (node == null) return null

        // Check if this node is editable
        if (node.isEditable) {
            return node
        }

        // Check by class name as a fallback
        val className = node.className?.toString() ?: ""
        if (className.contains("EditText") || className.contains("edit", ignoreCase = true)) {
            return node
        }

        // Recurse into children
        for (i in 0 until node.childCount) {
            val child = node.getChild(i) ?: continue
            val result = findEditableNode(child)
            if (result != null) return result
        }

        return null
    }

    /**
     * Clipboard-based fallback for devices/situations where ACTION_SET_TEXT
     * does not work. Copies text to clipboard, then dispatches ACTION_PASTE.
     */
    private fun pasteViaClipboard(rootNode: AccessibilityNodeInfo, text: String) {
        try {
            val clipboardManager = getSystemService(CLIPBOARD_SERVICE) as android.content.ClipboardManager
            val clip = android.content.ClipData.newPlainText("PersonaAI Reply", text)
            clipboardManager.setPrimaryClip(clip)

            val editText = findEditableNode(rootNode)
            if (editText != null) {
                // Focus the node first
                editText.performAction(AccessibilityNodeInfo.ACTION_FOCUS)
                // Then paste
                editText.performAction(AccessibilityNodeInfo.ACTION_PASTE)
                Log.i(TAG, "Clipboard paste performed successfully")
            } else {
                Log.w(TAG, "Clipboard fallback: still no editable node found to paste into")
            }
        } catch (e: Exception) {
            Log.e(TAG, "Clipboard paste failed", e)
        }
    }

    // ─── NODE EXTRACTION & FILTERING ─────────────────────────────────

    /**
     * Simple data class holding a scraped text node and its screen bounds.
     */
    data class ScrapedNode(
        val text: String,
        val left: Int,
        val right: Int,
        val top: Int,
        val bottom: Int
    )

    /**
     * Recursively walks the accessibility tree and extracts all nodes
     * that have non-blank text or content descriptions.
     */
    private fun extractNodes(node: AccessibilityNodeInfo?, list: MutableList<ScrapedNode>) {
        if (node == null) return

        val value = node.text?.toString() ?: node.contentDescription?.toString()
        if (!value.isNullOrBlank()) {
            val bounds = Rect()
            node.getBoundsInScreen(bounds)
            list.add(ScrapedNode(value, bounds.left, bounds.right, bounds.top, bounds.bottom))
        }

        for (i in 0 until node.childCount) {
            extractNodes(node.getChild(i), list)
        }
    }

    /**
     * Determines whether a scraped node is likely an actual chat message
     * (as opposed to UI chrome like timestamps, headers, or button labels).
     *
     * Heuristic rules:
     * 1. Text must be > 1 character (skip single emoji-button labels)
     * 2. Text must not match a known noise pattern
     * 3. Text must not be purely a timestamp
     * 4. Text must not be a date header
     * 5. Node must have reasonable width (actual bubble, not a tiny icon label)
     */
    private fun isLikelyMessageBubble(node: ScrapedNode, screenWidth: Int): Boolean {
        val txt = node.text.trim()

        // Too short — likely a button label or icon
        if (txt.length < 2) return false

        // Exact match with known noise words (case-insensitive)
        if (NOISE_PATTERNS.any { txt.equals(it, ignoreCase = true) }) return false

        // Pure timestamp
        if (TIMESTAMP_REGEX.matches(txt)) return false

        // Date header
        if (DATE_REGEX.matches(txt)) return false

        // Very narrow node — likely a label, not a message bubble
        val nodeWidth = node.right - node.left
        if (nodeWidth < screenWidth * 0.15) return false

        // Very wide node that covers the full screen — likely a header/toolbar
        if (nodeWidth > screenWidth * 0.98 && txt.length < 30) return false

        return true
    }

    override fun onInterrupt() {
        Log.d(TAG, "Service interrupted")
    }

    override fun onDestroy() {
        super.onDestroy()
        overlayManager?.hideOverlay()
        Log.i(TAG, "Accessibility service destroyed")
    }
}
