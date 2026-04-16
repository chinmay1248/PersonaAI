package com.anonymous.personaai

import android.content.Context
import android.graphics.Color
import android.graphics.PixelFormat
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Build
import android.provider.Settings
import android.util.TypedValue
import android.view.Gravity
import android.view.MotionEvent
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.widget.Button
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.ScrollView
import android.widget.TextView
import android.widget.Toast

/**
 * Manages the floating overlay shown on top of WhatsApp.
 *
 * Two states:
 * 1. **Collapsed** — small circular "AI" button on the right edge.
 * 2. **Expanded** — dark card with 3 reply suggestions and a close button.
 *
 * When the user taps a suggestion it is delivered back via [onSuggestionSelected]
 * so the accessibility service can paste it into WhatsApp's input field.
 */
class OverlayManager(private val context: Context) {

    private var windowManager: WindowManager? = null

    // Collapsed state views
    private var fabView: View? = null
    private var fabLayoutParams: WindowManager.LayoutParams? = null

    // Expanded state views
    private var panelView: View? = null

    // Callback for when a suggestion is tapped
    var onSuggestionSelected: ((String) -> Unit)? = null

    // Latest scraped messages (set by WhatsAppReaderService)
    var latestIncomingMessages: List<String> = emptyList()
    var latestAllMessages: List<String> = emptyList()

    // Colors matching the PersonaAI theme
    private val COLOR_PRIMARY = 0xFF0F766E.toInt()      // Teal
    private val COLOR_PANEL_BG = 0xFF1A1A2E.toInt()      // Dark blue-black
    private val COLOR_CARD_BG = 0xFF16213E.toInt()       // Slightly lighter
    private val COLOR_TEXT_PRIMARY = 0xFFFFFFFF.toInt()
    private val COLOR_TEXT_SECONDARY = 0xFFA0AEC0.toInt()
    private val COLOR_ACCENT = 0xFFC96C50.toInt()        // Warm accent

    private fun dp(value: Int): Int =
        TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, value.toFloat(), context.resources.displayMetrics).toInt()

    private fun overlayType(): Int =
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O)
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
        else
            @Suppress("DEPRECATION")
            WindowManager.LayoutParams.TYPE_PHONE

    private fun canDrawOverlay(): Boolean =
        Build.VERSION.SDK_INT < Build.VERSION_CODES.M || Settings.canDrawOverlays(context)

    // ─── PUBLIC API ───────────────────────────────────────────────

    fun showOverlay() {
        if (fabView != null) return
        if (!canDrawOverlay()) return

        windowManager = context.getSystemService(Context.WINDOW_SERVICE) as WindowManager
        showFab()
    }

    fun hideOverlay() {
        dismissPanel()
        dismissFab()
    }

    // ─── FAB (COLLAPSED STATE) ────────────────────────────────────

    private fun showFab() {
        if (fabView != null) return

        val size = dp(48)
        val fabBg = GradientDrawable().apply {
            shape = GradientDrawable.OVAL
            setColor(COLOR_PRIMARY)
        }

        val button = TextView(context).apply {
            text = "AI"
            setTextColor(Color.WHITE)
            textSize = 14f
            typeface = Typeface.DEFAULT_BOLD
            gravity = Gravity.CENTER
            background = fabBg
            elevation = dp(6).toFloat()
        }

        val params = WindowManager.LayoutParams(
            size, size,
            overlayType(),
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.TOP or Gravity.START
            x = context.resources.displayMetrics.widthPixels - size - dp(8)
            y = context.resources.displayMetrics.heightPixels / 3
        }

        // Make FAB draggable + tappable
        var initialX = 0; var initialY = 0
        var initialTouchX = 0f; var initialTouchY = 0f
        var moved = false

        button.setOnTouchListener { _, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> {
                    initialX = params.x; initialY = params.y
                    initialTouchX = event.rawX; initialTouchY = event.rawY
                    moved = false
                    true
                }
                MotionEvent.ACTION_MOVE -> {
                    val dx = (event.rawX - initialTouchX).toInt()
                    val dy = (event.rawY - initialTouchY).toInt()
                    if (Math.abs(dx) > dp(5) || Math.abs(dy) > dp(5)) moved = true
                    params.x = initialX + dx
                    params.y = initialY + dy
                    try { windowManager?.updateViewLayout(button, params) } catch (_: Exception) {}
                    true
                }
                MotionEvent.ACTION_UP -> {
                    if (!moved) onFabTapped()
                    true
                }
                else -> false
            }
        }

        fabView = button
        fabLayoutParams = params
        try {
            windowManager?.addView(button, params)
        } catch (e: SecurityException) {
            fabView = null
        }
    }

    private fun dismissFab() {
        fabView?.let {
            try { windowManager?.removeView(it) } catch (_: Exception) {}
        }
        fabView = null
    }

    // ─── FAB TAP → GENERATE REPLIES ──────────────────────────────

    private fun onFabTapped() {
        if (panelView != null) {
            dismissPanel()
            return
        }

        val messages = latestIncomingMessages.ifEmpty { latestAllMessages }
        if (messages.isEmpty()) {
            Toast.makeText(context, "No messages captured yet. Chat a bit first!", Toast.LENGTH_SHORT).show()
            return
        }

        showPanel(loading = true, suggestions = emptyList(), mood = "")

        OverlayApiClient.generateReplies(
            context = context,
            incomingMessages = messages.takeLast(5),
            conversationHistory = latestAllMessages.takeLast(5),
            callback = object : OverlayApiClient.Callback {
                override fun onSuccess(result: OverlayApiClient.ReplyResult) {
                    dismissPanel()
                    showPanel(loading = false, suggestions = result.suggestions, mood = result.mood)
                }

                override fun onError(message: String) {
                    dismissPanel()
                    Toast.makeText(context, "PersonaAI: $message", Toast.LENGTH_SHORT).show()
                }
            }
        )
    }

    // ─── PANEL (EXPANDED STATE) ──────────────────────────────────

    private fun showPanel(loading: Boolean, suggestions: List<OverlayApiClient.ReplySuggestion>, mood: String) {
        if (panelView != null) return

        val screenWidth = context.resources.displayMetrics.widthPixels
        val panelWidth = screenWidth - dp(32)

        val panelBg = GradientDrawable().apply {
            setColor(COLOR_PANEL_BG)
            cornerRadius = dp(20).toFloat()
        }

        val container = LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            background = panelBg
            setPadding(dp(16), dp(16), dp(16), dp(16))
            elevation = dp(12).toFloat()
        }

        // Header row
        val header = FrameLayout(context)
        val title = TextView(context).apply {
            text = if (loading) "Generating replies..." else "PersonaAI Suggestions"
            setTextColor(COLOR_TEXT_PRIMARY)
            textSize = 16f
            typeface = Typeface.DEFAULT_BOLD
        }
        header.addView(title, FrameLayout.LayoutParams(
            ViewGroup.LayoutParams.WRAP_CONTENT,
            ViewGroup.LayoutParams.WRAP_CONTENT,
            Gravity.START or Gravity.CENTER_VERTICAL
        ))

        val closeBtn = TextView(context).apply {
            text = "✕"
            setTextColor(COLOR_TEXT_SECONDARY)
            textSize = 18f
            setPadding(dp(8), dp(4), dp(8), dp(4))
            setOnClickListener { dismissPanel() }
        }
        header.addView(closeBtn, FrameLayout.LayoutParams(
            ViewGroup.LayoutParams.WRAP_CONTENT,
            ViewGroup.LayoutParams.WRAP_CONTENT,
            Gravity.END or Gravity.CENTER_VERTICAL
        ))
        container.addView(header, LinearLayout.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.WRAP_CONTENT
        ).apply { bottomMargin = dp(12) })

        if (loading) {
            // Show loading spinner
            val progress = ProgressBar(context).apply {
                isIndeterminate = true
            }
            container.addView(progress, LinearLayout.LayoutParams(
                dp(36), dp(36)
            ).apply {
                gravity = Gravity.CENTER_HORIZONTAL
                topMargin = dp(16)
                bottomMargin = dp(16)
            })

            val loadingText = TextView(context).apply {
                text = "Analyzing your style and crafting replies..."
                setTextColor(COLOR_TEXT_SECONDARY)
                textSize = 13f
                gravity = Gravity.CENTER
            }
            container.addView(loadingText)
        } else {
            // Mood badge
            if (mood.isNotBlank()) {
                val moodBadgeBg = GradientDrawable().apply {
                    setColor(0xFF2D3748.toInt())
                    cornerRadius = dp(12).toFloat()
                }
                val moodBadge = TextView(context).apply {
                    text = "Mood: $mood"
                    setTextColor(COLOR_PRIMARY)
                    textSize = 12f
                    typeface = Typeface.DEFAULT_BOLD
                    background = moodBadgeBg
                    setPadding(dp(10), dp(4), dp(10), dp(4))
                }
                container.addView(moodBadge, LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.WRAP_CONTENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT
                ).apply { bottomMargin = dp(10) })
            }

            // Scrollable suggestion cards
            val scroll = ScrollView(context).apply {
                isVerticalScrollBarEnabled = false
            }
            val cardsContainer = LinearLayout(context).apply {
                orientation = LinearLayout.VERTICAL
            }

            for (suggestion in suggestions) {
                val cardBg = GradientDrawable().apply {
                    setColor(COLOR_CARD_BG)
                    cornerRadius = dp(14).toFloat()
                    setStroke(1, 0xFF2D3748.toInt())
                }
                val card = LinearLayout(context).apply {
                    orientation = LinearLayout.VERTICAL
                    background = cardBg
                    setPadding(dp(14), dp(12), dp(14), dp(12))
                    isClickable = true
                    isFocusable = true

                    setOnClickListener {
                        onSuggestionSelected?.invoke(suggestion.text)
                        dismissPanel()
                        Toast.makeText(context, "Reply pasted! ✓", Toast.LENGTH_SHORT).show()
                    }
                }

                val rankLabel = TextView(context).apply {
                    text = "Option ${suggestion.rank}"
                    setTextColor(COLOR_PRIMARY)
                    textSize = 11f
                    typeface = Typeface.DEFAULT_BOLD
                }
                card.addView(rankLabel)

                val replyText = TextView(context).apply {
                    text = suggestion.text
                    setTextColor(COLOR_TEXT_PRIMARY)
                    textSize = 14f
                    setLineSpacing(dp(4).toFloat(), 1f)
                }
                card.addView(replyText, LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT
                ).apply { topMargin = dp(4) })

                val tapHint = TextView(context).apply {
                    text = "Tap to paste"
                    setTextColor(COLOR_TEXT_SECONDARY)
                    textSize = 10f
                }
                card.addView(tapHint, LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.WRAP_CONTENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT
                ).apply { topMargin = dp(6) })

                cardsContainer.addView(card, LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    ViewGroup.LayoutParams.WRAP_CONTENT
                ).apply { bottomMargin = dp(8) })
            }

            scroll.addView(cardsContainer)
            container.addView(scroll, LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.WRAP_CONTENT
            ).apply {
                // Cap max height at ~50% of screen
                height = minOf(dp(300), context.resources.displayMetrics.heightPixels / 2)
            })
        }

        // Create the window params
        val params = WindowManager.LayoutParams(
            panelWidth,
            ViewGroup.LayoutParams.WRAP_CONTENT,
            overlayType(),
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.CENTER
        }

        panelView = container
        try {
            windowManager?.addView(container, params)
        } catch (e: SecurityException) {
            panelView = null
        }
    }

    private fun dismissPanel() {
        panelView?.let {
            try { windowManager?.removeView(it) } catch (_: Exception) {}
        }
        panelView = null
    }
}
