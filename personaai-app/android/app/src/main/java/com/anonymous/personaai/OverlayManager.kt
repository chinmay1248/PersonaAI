package com.anonymous.personaai

import android.content.Context
import android.graphics.PixelFormat
import android.os.Build
import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.WindowManager
import android.widget.Button
import android.widget.Toast

class OverlayManager(private val context: Context) {
    private var windowManager: WindowManager? = null
    private var overlayView: View? = null

    fun showOverlay() {
        if (overlayView != null) return

        windowManager = context.getSystemService(Context.WINDOW_SERVICE) as WindowManager

        val layoutParams = WindowManager.LayoutParams(
            WindowManager.LayoutParams.WRAP_CONTENT,
            WindowManager.LayoutParams.WRAP_CONTENT,
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O)
                WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
            else
                WindowManager.LayoutParams.TYPE_PHONE,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        )

        layoutParams.gravity = Gravity.CENTER_VERTICAL or Gravity.RIGHT
        layoutParams.x = 0
        layoutParams.y = 100

        // Create a simple programmatic button instead of XML to avoid layout issues in eject mode
        val button = Button(context).apply {
            text = "AI"
            setBackgroundColor(0xFF6366F1.toInt()) // Indigo
            setTextColor(0xFFFFFFFF.toInt())
            setOnClickListener {
                Toast.makeText(context, "Fetching PersonaAI Suggestions...", Toast.LENGTH_SHORT).show()
                // Here we would call the React Native UI or the API bridge
            }
        }

        overlayView = button
        windowManager?.addView(overlayView, layoutParams)
    }

    fun hideOverlay() {
        if (overlayView != null) {
            windowManager?.removeView(overlayView)
            overlayView = null
        }
    }
}
