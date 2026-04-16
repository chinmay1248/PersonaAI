package com.anonymous.personaai

import android.content.Context
import android.content.SharedPreferences

/**
 * Shared preferences helper that enables the Accessibility Service
 * (which runs outside of React Native) to read the JWT token and API URL.
 */
object SharedPrefsHelper {

    private const val PREFS_NAME = "PersonaAIPrefs"
    private const val KEY_ACCESS_TOKEN = "accessToken"
    private const val KEY_API_URL = "apiUrl"
    private const val KEY_CHAT_CONFIG_ID = "activeChatConfigId"
    private const val DEFAULT_API_URL = "https://personaai-backend-production-4490.up.railway.app/v1"

    private fun prefs(context: Context): SharedPreferences =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun saveCredentials(context: Context, token: String, apiUrl: String, chatConfigId: String?) {
        prefs(context).edit()
            .putString(KEY_ACCESS_TOKEN, token)
            .putString(KEY_API_URL, apiUrl.ifBlank { DEFAULT_API_URL })
            .putString(KEY_CHAT_CONFIG_ID, chatConfigId ?: "")
            .apply()
    }

    fun getAccessToken(context: Context): String? =
        prefs(context).getString(KEY_ACCESS_TOKEN, null)

    fun getApiUrl(context: Context): String =
        prefs(context).getString(KEY_API_URL, DEFAULT_API_URL) ?: DEFAULT_API_URL

    fun getChatConfigId(context: Context): String? {
        val id = prefs(context).getString(KEY_CHAT_CONFIG_ID, null)
        return if (id.isNullOrBlank()) null else id
    }
}
