package com.verdis.wallet.security

import android.content.Context
import android.content.SharedPreferences
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity
import java.security.MessageDigest

/**
 * Security helper managing PIN authentication, Biometric authentication,
 * and 60-second inactivity auto-lock functionality.
 */
class SecurityHelper(private val context: Context) {

    companion object {
        private const val PREFS_NAME = "verdis_security_prefs"
        private const val KEY_PIN_HASH = "pin_hash"
        private const val KEY_BIOMETRIC_ENABLED = "biometric_enabled"
        private const val KEY_LAST_ACTIVITY = "last_activity_time"
        private const val INACTIVITY_LOCK_TIMEOUT_MS = 60_000L // 60 seconds
    }

    private val prefs: SharedPreferences =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    /**
     * Set a new 6-digit PIN. Hashes PIN using SHA-256 and saves to SharedPreferences.
     *
     * @param pin 6-digit PIN string
     * @return true if PIN set successfully, false if invalid PIN format
     */
    fun setPin(pin: String): Boolean {
        if (pin.length != 6 || !pin.all { it.isDigit() }) {
            return false
        }
        val hash = hashPin(pin)
        prefs.edit()
            .putString(KEY_PIN_HASH, hash)
            .putLong(KEY_LAST_ACTIVITY, System.currentTimeMillis())
            .apply()
        return true
    }

    /**
     * Verify the entered PIN against stored SHA-256 hash.
     * Updates last activity timestamp upon successful verification.
     *
     * @param pin 6-digit PIN string to verify
     * @return true if PIN is correct
     */
    fun verifyPin(pin: String): Boolean {
        if (!isPinSet()) return false
        val storedHash = prefs.getString(KEY_PIN_HASH, null) ?: return false
        val inputHash = hashPin(pin)
        val isValid = storedHash.equals(inputHash, ignoreCase = true)
        if (isValid) {
            updateLastActivity()
        }
        return isValid
    }

    /**
     * Check if a security PIN has been created.
     */
    fun isPinSet(): Boolean {
        return !prefs.getString(KEY_PIN_HASH, null).isNullOrEmpty()
    }

    /**
     * Check if user has enabled biometric authentication.
     */
    fun isBiometricEnabled(): Boolean {
        return prefs.getBoolean(KEY_BIOMETRIC_ENABLED, false)
    }

    /**
     * Enable or disable biometric authentication preference.
     */
    fun setBiometricEnabled(enabled: Boolean) {
        prefs.edit().putBoolean(KEY_BIOMETRIC_ENABLED, enabled).apply()
    }

    /**
     * Check if device hardware supports biometric authentication.
     */
    fun isBiometricHardwareAvailable(): Boolean {
        val biometricManager = BiometricManager.from(context)
        val result = biometricManager.canAuthenticate(
            BiometricManager.Authenticators.BIOMETRIC_STRONG or
                    BiometricManager.Authenticators.BIOMETRIC_WEAK
        )
        return result == BiometricManager.BIOMETRIC_SUCCESS
    }

    /**
     * Check whether the app should lock due to 60-second inactivity.
     *
     * @return true if PIN is set and last activity was >= 60 seconds ago
     */
    fun shouldLock(): Boolean {
        if (!isPinSet()) return false
        val lastActivity = prefs.getLong(KEY_LAST_ACTIVITY, 0L)
        if (lastActivity == 0L) return true
        val elapsedTime = System.currentTimeMillis() - lastActivity
        return elapsedTime >= INACTIVITY_LOCK_TIMEOUT_MS
    }

    /**
     * Update the last active timestamp to current System time.
     */
    fun updateLastActivity() {
        prefs.edit().putLong(KEY_LAST_ACTIVITY, System.currentTimeMillis()).apply()
    }

    /**
     * Clear stored PIN and biometric settings.
     */
    fun clearSecurity() {
        prefs.edit().clear().apply()
    }

    /**
     * Trigger AndroidX BiometricPrompt for user authentication.
     *
     * @param activity Hosting FragmentActivity
     * @param title Title displayed on biometric dialog
     * @param subtitle Subtitle displayed on biometric dialog
     * @param negativeButtonText Text for fallback button (e.g. "Use PIN")
     * @param onSuccess Callback invoked on biometric verification success
     * @param onError Callback invoked on biometric error or cancellation
     */
    fun authenticateBiometric(
        activity: FragmentActivity,
        title: String = "Biometric Authentication",
        subtitle: String = "Verify your identity to proceed",
        negativeButtonText: String = "Use PIN",
        onSuccess: () -> Unit,
        onError: (String) -> Unit
    ) {
        val executor = ContextCompat.getMainExecutor(activity)
        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle(title)
            .setSubtitle(subtitle)
            .setNegativeButtonText(negativeButtonText)
            .setAllowedAuthenticators(
                BiometricManager.Authenticators.BIOMETRIC_STRONG or
                        BiometricManager.Authenticators.BIOMETRIC_WEAK
            )
            .build()

        val biometricPrompt = BiometricPrompt(
            activity,
            executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    super.onAuthenticationSucceeded(result)
                    updateLastActivity()
                    onSuccess()
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    super.onAuthenticationError(errorCode, errString)
                    onError(errString.toString())
                }

                override fun onAuthenticationFailed() {
                    super.onAuthenticationFailed()
                    onError("Biometric authentication failed")
                }
            }
        )

        biometricPrompt.authenticate(promptInfo)
    }

    private fun hashPin(pin: String): String {
        val digest = MessageDigest.getInstance("SHA-256")
        val hashBytes = digest.digest(pin.toByteArray(Charsets.UTF_8))
        return hashBytes.joinToString("") { "%02x".format(it) }
    }
}
