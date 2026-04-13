package com.anonymous.personaai

import android.accessibilityservice.AccessibilityService
import android.graphics.Rect
import android.content.Intent
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import android.util.Log
import org.json.JSONArray
import org.json.JSONObject

class WhatsAppReaderService : AccessibilityService() {

    private val TAG = "WhatsAppReader"

    private var overlayManager: OverlayManager? = null

    override fun onServiceConnected() {
        super.onServiceConnected()
        overlayManager = OverlayManager(this)
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        val sourcePackage = event?.packageName?.toString()
        if (event == null || (sourcePackage != "com.whatsapp" && sourcePackage != "com.whatsapp.w4b")) {
            overlayManager?.hideOverlay()
            return
        }

        overlayManager?.showOverlay()

        val rootNode = rootInActiveWindow ?: return

        // Simple scraper: grab all visible text
        val nodes = JSONArray()
        extractText(rootNode, nodes)

        if (nodes.length() > 0) {
            val payload = JSONObject().apply {
                put("packageName", sourcePackage)
                put("screenWidth", resources.displayMetrics.widthPixels)
                put("capturedAt", System.currentTimeMillis())
                put("nodes", nodes)
            }.toString()
            Log.d(TAG, "Scraped payload size: ${nodes.length()}")
            
            // Securely transmit to PersonaAIModule Bridge via Broadcast
            val intent = Intent("com.anonymous.personaai.WHATSAPP_SCRAPED")
            intent.putExtra("textPayload", payload)
            sendBroadcast(intent)
        }
    }

    private fun extractText(node: AccessibilityNodeInfo?, list: JSONArray) {
        if (node == null) return
        val value = node.text?.toString() ?: node.contentDescription?.toString()
        if (!value.isNullOrBlank()) {
            val bounds = Rect()
            node.getBoundsInScreen(bounds)
            list.put(JSONObject().apply {
                put("text", value)
                put("left", bounds.left)
                put("right", bounds.right)
                put("top", bounds.top)
                put("bottom", bounds.bottom)
            })
        }
        for (i in 0 until node.childCount) {
            extractText(node.getChild(i), list)
        }
    }

    override fun onInterrupt() {
        Log.d(TAG, "Service interrupted")
    }
}
