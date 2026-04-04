package com.anonymous.personaai

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.provider.Settings
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.ReactContextBaseJavaModule
import com.facebook.react.bridge.ReactMethod
import com.facebook.react.modules.core.DeviceEventManagerModule

class PersonaAIModule(reactContext: ReactApplicationContext) : ReactContextBaseJavaModule(reactContext) {

    private val ACTION_WHATSAPP_SCRAPED = "com.anonymous.personaai.WHATSAPP_SCRAPED"

    // Broadcast receiver securely listens to the Accessibility Service regardless of Thread
    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            if (intent?.action == ACTION_WHATSAPP_SCRAPED) {
                val scrapedText = intent.getStringExtra("textPayload")
                if (!scrapedText.isNullOrEmpty()) {
                    sendEventToJS("OnWhatsAppMessagesScraped", scrapedText)
                }
            }
        }
    }

    init {
        // Register the receiver dynamically when React initialization kicks in
        reactApplicationContext.registerReceiver(
            receiver, 
            IntentFilter(ACTION_WHATSAPP_SCRAPED),
            Context.RECEIVER_EXPORTED
        )
    }

    override fun getName(): String {
        return "PersonaAIModule"
    }

    @ReactMethod
    fun requestAccessibilityPermission() {
        val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
        reactApplicationContext.startActivity(intent)
    }

    private fun sendEventToJS(eventName: String, payload: String) {
        if (reactApplicationContext.hasActiveReactInstance()) {
            reactApplicationContext
                .getJSModule(DeviceEventManagerModule.RCTDeviceEventEmitter::class.java)
                .emit(eventName, payload)
        }
    }
}
