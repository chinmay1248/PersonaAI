package com.anonymous.personaai

import android.accessibilityservice.AccessibilityService
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import android.util.Log
import com.facebook.react.modules.core.DeviceEventManagerModule
import com.facebook.react.ReactApplication

class WhatsAppReaderService : AccessibilityService() {

    private val TAG = "WhatsAppReader"

    private var overlayManager: OverlayManager? = null

    override fun onServiceConnected() {
        super.onServiceConnected()
        overlayManager = OverlayManager(this)
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        if (event == null || event.packageName != "com.whatsapp") {
            overlayManager?.hideOverlay()
            return
        }

        overlayManager?.showOverlay()

        val rootNode = rootInActiveWindow ?: return

        // Simple scraper: grab all visible text
        val texts = mutableListOf<String>()
        extractText(rootNode, texts)

        if (texts.isNotEmpty()) {
            val combinedText = texts.joinToString(" || ")
            Log.d(TAG, "Scraped Text: $combinedText")
            
            // Securely transmit to PersonaAIModule Bridge via Broadcast
            val intent = android.content.Intent("com.anonymous.personaai.WHATSAPP_SCRAPED")
            intent.putExtra("textPayload", combinedText)
            sendBroadcast(intent)
        }
    }

    private fun extractText(node: AccessibilityNodeInfo?, list: MutableList<String>) {
        if (node == null) return
        if (node.text != null && node.text.isNotEmpty()) {
            list.add(node.text.toString())
        }
        for (i in 0 until node.childCount) {
            extractText(node.getChild(i), list)
        }
    }

    override fun onInterrupt() {
        Log.d(TAG, "Service interrupted")
    }
}
