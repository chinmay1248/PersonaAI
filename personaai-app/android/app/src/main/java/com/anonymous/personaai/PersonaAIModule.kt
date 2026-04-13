package com.anonymous.personaai

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.Build
import android.provider.Settings
import android.net.Uri
import com.facebook.react.bridge.ReactApplicationContext
import com.facebook.react.bridge.ReactContextBaseJavaModule
import com.facebook.react.bridge.ReactMethod
import com.facebook.react.modules.core.DeviceEventManagerModule

class PersonaAIModule(reactContext: ReactApplicationContext) : ReactContextBaseJavaModule(reactContext) {

    private val ACTION_WHATSAPP_SCRAPED = "com.anonymous.personaai.WHATSAPP_SCRAPED"

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
        try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                reactApplicationContext.registerReceiver(
                    receiver,
                    IntentFilter(ACTION_WHATSAPP_SCRAPED),
                    Context.RECEIVER_EXPORTED
                )
            } else {
                @Suppress("UnspecifiedRegisterReceiverFlag")
                reactApplicationContext.registerReceiver(
                    receiver,
                    IntentFilter(ACTION_WHATSAPP_SCRAPED)
                )
            }
        } catch (e: Exception) {
            // Gracefully handle if receiver registration fails
            android.util.Log.w("PersonaAIModule", "Failed to register broadcast receiver: ${e.message}")
        }
    }

    override fun getName(): String {
        return "PersonaAIModule"
    }

    @ReactMethod
    fun requestAccessibilityPermission() {
        try {
            val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
            reactApplicationContext.startActivity(intent)
        } catch (e: Exception) {
            android.util.Log.w("PersonaAIModule", "Failed to open accessibility settings: ${e.message}")
        }
    }

    @ReactMethod
    fun requestOverlayPermission() {
        try {
            val intent = Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:${reactApplicationContext.packageName}")
            )
            intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
            reactApplicationContext.startActivity(intent)
        } catch (e: Exception) {
            android.util.Log.w("PersonaAIModule", "Failed to open overlay settings: ${e.message}")
        }
    }

    @ReactMethod
    fun addListener(eventName: String) {
        // Required for NativeEventEmitter on Android.
    }

    @ReactMethod
    fun removeListeners(count: Int) {
        // Required for NativeEventEmitter on Android.
    }

    private fun sendEventToJS(eventName: String, payload: String) {
        try {
            if (reactApplicationContext.hasActiveReactInstance()) {
                reactApplicationContext
                    .getJSModule(DeviceEventManagerModule.RCTDeviceEventEmitter::class.java)
                    .emit(eventName, payload)
            }
        } catch (e: Exception) {
            android.util.Log.w("PersonaAIModule", "Failed to send event to JS: ${e.message}")
        }
    }
}
