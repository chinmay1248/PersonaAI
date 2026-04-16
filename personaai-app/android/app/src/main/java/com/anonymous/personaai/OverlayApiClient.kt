package com.anonymous.personaai

import android.content.Context
import android.os.Handler
import android.os.Looper
import android.util.Log
import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

/**
 * Lightweight HTTP client that calls the PersonaAI backend directly from
 * the native Android layer.  Uses HttpURLConnection so we don't need to
 * add OkHttp or any extra dependency.
 */
object OverlayApiClient {

    private const val TAG = "OverlayApiClient"
    private const val TIMEOUT_MS = 15_000

    data class ReplySuggestion(val id: String, val rank: Int, val text: String)
    data class ReplyResult(val mood: String, val suggestions: List<ReplySuggestion>)

    interface Callback {
        fun onSuccess(result: ReplyResult)
        fun onError(message: String)
    }

    /**
     * Calls POST /ai/generate-reply in a background thread and delivers
     * the result on the main thread via [callback].
     */
    fun generateReplies(
        context: Context,
        incomingMessages: List<String>,
        conversationHistory: List<String>,
        callback: Callback
    ) {
        Thread {
            try {
                val token = SharedPrefsHelper.getAccessToken(context)
                if (token.isNullOrBlank()) {
                    postError(callback, "Not signed in. Open PersonaAI app and login first.")
                    return@Thread
                }

                val apiUrl = SharedPrefsHelper.getApiUrl(context)
                val chatConfigId = SharedPrefsHelper.getChatConfigId(context)

                // Build the request body
                val history = JSONArray()
                for (msg in conversationHistory.takeLast(5)) {
                    history.put(JSONObject().apply {
                        put("role", "them")
                        put("text", msg)
                    })
                }

                val body = JSONObject().apply {
                    if (!chatConfigId.isNullOrBlank()) {
                        put("chat_config_id", chatConfigId)
                    }
                    put("incoming_messages", JSONArray(incomingMessages))
                    put("conversation_history", history)
                    put("count", 3)
                }

                // Make the HTTP call
                val url = URL("$apiUrl/ai/generate-reply")
                val conn = (url.openConnection() as HttpURLConnection).apply {
                    requestMethod = "POST"
                    setRequestProperty("Content-Type", "application/json")
                    setRequestProperty("Authorization", "Bearer $token")
                    connectTimeout = TIMEOUT_MS
                    readTimeout = TIMEOUT_MS
                    doOutput = true
                }

                OutputStreamWriter(conn.outputStream, "UTF-8").use { writer ->
                    writer.write(body.toString())
                    writer.flush()
                }

                val responseCode = conn.responseCode
                if (responseCode !in 200..299) {
                    val errorStream = conn.errorStream ?: conn.inputStream
                    val errorBody = BufferedReader(InputStreamReader(errorStream)).use { it.readText() }
                    Log.w(TAG, "API error $responseCode: $errorBody")
                    postError(callback, "API returned $responseCode")
                    return@Thread
                }

                val responseBody = BufferedReader(InputStreamReader(conn.inputStream)).use { it.readText() }
                val json = JSONObject(responseBody)

                val mood = json.optString("detected_mood", "neutral")
                val suggestionsArray = json.getJSONArray("suggestions")
                val suggestions = mutableListOf<ReplySuggestion>()
                for (i in 0 until suggestionsArray.length()) {
                    val s = suggestionsArray.getJSONObject(i)
                    suggestions.add(
                        ReplySuggestion(
                            id = s.optString("id", "$i"),
                            rank = s.optInt("rank", i + 1),
                            text = s.getString("text")
                        )
                    )
                }

                Handler(Looper.getMainLooper()).post {
                    callback.onSuccess(ReplyResult(mood, suggestions))
                }
            } catch (e: Exception) {
                Log.e(TAG, "generateReplies failed", e)
                postError(callback, e.message ?: "Unknown error")
            }
        }.start()
    }

    private fun postError(callback: Callback, message: String) {
        Handler(Looper.getMainLooper()).post {
            callback.onError(message)
        }
    }
}
