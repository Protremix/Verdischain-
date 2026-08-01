package com.verdis.wallet

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKeys

/**
 * Manages app-level security: PIN and biometric authentication.
 * PIN is stored as a salted hash in encrypted preferences — never plaintext.
 */
object SecurityManager {

    private const val SECURE_PREFS = "verdis_security_encrypted"
    private const val KEY_PIN_HASH = "pin_hash"
    private const val KEY_PIN_SALT = "pin_salt"
    private const val KEY_BIOMETRIC_ENABLED = "biometric_enabled"
    private const val KEY_PIN_ENABLED = "pin_enabled"
    private const val KEY_APP_LOCK_ENABLED = "app_lock_enabled"

    data class SecurityState(
        val pinEnabled: Boolean,
        val biometricEnabled: Boolean,
        val appLockEnabled: Boolean,
        val hasPin: Boolean
    )

    private fun getSecurePrefs(context: Context): SharedPreferences {
        return try {
            val masterKeyAlias = MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC)
            EncryptedSharedPreferences.create(
                SECURE_PREFS,
                masterKeyAlias,
                context,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
        } catch (e: Exception) {
            context.getSharedPreferences("verdis_security_fallback", Context.MODE_PRIVATE)
        }
    }

    fun getState(context: Context): SecurityState {
        val prefs = getSecurePrefs(context)
        return SecurityState(
            pinEnabled = prefs.getBoolean(KEY_PIN_ENABLED, false),
            biometricEnabled = prefs.getBoolean(KEY_BIOMETRIC_ENABLED, false),
            appLockEnabled = prefs.getBoolean(KEY_APP_LOCK_ENABLED, false),
            hasPin = prefs.getString(KEY_PIN_HASH, null) != null
        )
    }

    fun isSecurityEnabled(context: Context): Boolean {
        val state = getState(context)
        return state.appLockEnabled && (state.pinEnabled || state.biometricEnabled)
    }

    // --- PIN Management ---

    fun setPin(context: Context, pin: String): Boolean {
        if (pin.length < 4 || pin.length > 8 || !pin.all { it.isDigit() }) return false
        val salt = CryptoUtils.toHex(ByteArray(16).also { java.security.SecureRandom().nextBytes(it) })
        val hash = hashPin(pin, salt)
        val prefs = getSecurePrefs(context)
        prefs.edit()
            .putString(KEY_PIN_HASH, hash)
            .putString(KEY_PIN_SALT, salt)
            .putBoolean(KEY_PIN_ENABLED, true)
            .putBoolean(KEY_APP_LOCK_ENABLED, true)
            .apply()
        return true
    }

    fun verifyPin(context: Context, pin: String): Boolean {
        val prefs = getSecurePrefs(context)
        val storedHash = prefs.getString(KEY_PIN_HASH, null) ?: return false
        val salt = prefs.getString(KEY_PIN_SALT, null) ?: return false
        return hashPin(pin, salt) == storedHash
    }

    fun removePin(context: Context) {
        val prefs = getSecurePrefs(context)
        prefs.edit()
            .remove(KEY_PIN_HASH)
            .remove(KEY_PIN_SALT)
            .putBoolean(KEY_PIN_ENABLED, false)
            .apply()
        // If biometric also off, disable app lock
        if (!prefs.getBoolean(KEY_BIOMETRIC_ENABLED, false)) {
            prefs.edit().putBoolean(KEY_APP_LOCK_ENABLED, false).apply()
        }
    }

    private fun hashPin(pin: String, salt: String): String {
        val combined = pin + salt
        val digest = java.security.MessageDigest.getInstance("SHA-256")
        val hashBytes = digest.digest(combined.toByteArray())
        return CryptoUtils.toHex(hashBytes)
    }

    // --- Biometric Management ---

    fun setBiometricEnabled(context: Context, enabled: Boolean) {
        val prefs = getSecurePrefs(context)
        prefs.edit().putBoolean(KEY_BIOMETRIC_ENABLED, enabled).apply()
        if (enabled) {
            prefs.edit().putBoolean(KEY_APP_LOCK_ENABLED, true).apply()
        } else if (!prefs.getBoolean(KEY_PIN_ENABLED, false)) {
            prefs.edit().putBoolean(KEY_APP_LOCK_ENABLED, false).apply()
        }
    }

    fun isBiometricEnabled(context: Context): Boolean {
        return getSecurePrefs(context).getBoolean(KEY_BIOMETRIC_ENABLED, false)
    }

    // --- App Lock ---

    fun setAppLockEnabled(context: Context, enabled: Boolean) {
        getSecurePrefs(context).edit().putBoolean(KEY_APP_LOCK_ENABLED, enabled).apply()
    }

    fun shouldLockOnResume(context: Context): Boolean {
        return isSecurityEnabled(context)
    }
}
