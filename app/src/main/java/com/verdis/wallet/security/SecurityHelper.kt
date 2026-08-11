package com.verdis.wallet.security

import android.content.Context
import android.content.SharedPreferences
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity
import java.security.SecureRandom
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.PBEKeySpec

/**
 * Security helper managing PIN authentication, Biometric authentication,
 * and 60-second inactivity auto-lock functionality.
 *
 * P1 fix: PIN now hashed with PBKDF2WithHmacSHA256 + random salt (200k iterations).
 * P1 fix: Brute force protection with max 5 attempts + exponential backoff.
 */
class SecurityHelper(private val context: Context) {

    companion object {
        private const val PREFS_NAME = "verdis_security_prefs"
        private const val KEY_PIN_HASH = "pin_hash"
        private const val KEY_PIN_SALT = "pin_salt"
        private const val KEY_BIOMETRIC_ENABLED = "biometric_enabled"
        private const val KEY_LAST_ACTIVITY = "last_activity_time"
        private const val KEY_FAILED_ATTEMPTS = "failed_attempts"
        private const val KEY_LOCK_UNTIL = "lock_until"
        // P1 fix: Configurable inactivity timeout (default 60s, can be set to 30s/60s/120s/300s)
        var inactivityLockTimeoutMs: Long = 60_000L
            private set

        fun setInactivityTimeout(seconds: Int) {
            inactivityLockTimeoutMs = when {
                seconds <= 0 -> 30_000L  // minimum 30s
                seconds > 600 -> 600_000L  // maximum 10 minutes
                else -> seconds * 1000L
            }
        }
        private const val PBKDF2_ITERATIONS = 200_000 // P1 fix: doubled for stronger brute force resistance
        private const val PBKDF2_KEY_LENGTH = 256
        private const val SALT_LENGTH = 32
        private const val MAX_FAILED_ATTEMPTS = 5
    }

    private val prefs: SharedPreferences =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun setPin(pin: String): Boolean {
        if (pin.length != 6 || !pin.all { it.isDigit() }) {
            return false
        }

        // P1 fix: Generate random salt for each PIN
        val salt = ByteArray(SALT_LENGTH).apply { SecureRandom().nextBytes(this) }
        val hash = hashPinSecure(pin, salt)

        prefs.edit()
            .putString(KEY_PIN_HASH, hash)
            .putString(KEY_PIN_SALT, salt.toHex())
            .putLong(KEY_LAST_ACTIVITY, System.currentTimeMillis())
            .putInt(KEY_FAILED_ATTEMPTS, 0)
            .putLong(KEY_LOCK_UNTIL, 0L)
            .apply()
        return true
    }

    fun verifyPin(pin: String): Boolean {
        if (!isPinSet()) return false

        // P1 fix: Brute force protection
        val lockUntil = prefs.getLong(KEY_LOCK_UNTIL, 0L)
        if (lockUntil > 0 && System.currentTimeMillis() < lockUntil) {
            val remainingSec = (lockUntil - System.currentTimeMillis()) / 1000
            return false // Locked — caller should check isLocked() for UX
        }

        val storedHash = prefs.getString(KEY_PIN_HASH, null) ?: return false
        val storedSaltHex = prefs.getString(KEY_PIN_SALT, null) ?: return false
        val salt = storedSaltHex.hexToBytes()

        val inputHash = hashPinSecure(pin, salt)
        val isValid = storedHash.equals(inputHash, ignoreCase = true)

        if (isValid) {
            // Reset failed attempts on success
            prefs.edit()
                .putInt(KEY_FAILED_ATTEMPTS, 0)
                .putLong(KEY_LOCK_UNTIL, 0L)
                .putLong(KEY_LAST_ACTIVITY, System.currentTimeMillis())
                .apply()
        } else {
            // P1 fix: Track failed attempts and lock after MAX_FAILED_ATTEMPTS
            val attempts = prefs.getInt(KEY_FAILED_ATTEMPTS, 0) + 1
            if (attempts >= MAX_FAILED_ATTEMPTS) {
                // P1 fix: Exponential backoff starting at 60s: 60s, 120s, 240s, 480s...
                val backoffMs = (60_000L * (1L shl (attempts - MAX_FAILED_ATTEMPTS).coerceAtMost(5)))
                prefs.edit()
                    .putInt(KEY_FAILED_ATTEMPTS, attempts)
                    .putLong(KEY_LOCK_UNTIL, System.currentTimeMillis() + backoffMs)
                    .apply()
            } else {
                prefs.edit().putInt(KEY_FAILED_ATTEMPTS, attempts).apply()
            }
        }

        return isValid
    }

    /**
     * Check if the app is currently locked due to too many failed attempts.
     */
    fun isLocked(): Boolean {
        val lockUntil = prefs.getLong(KEY_LOCK_UNTIL, 0L)
        return lockUntil > 0 && System.currentTimeMillis() < lockUntil
    }

    /**
     * Get remaining lock time in seconds (0 if not locked).
     */
    fun getLockRemainingSeconds(): Long {
        val lockUntil = prefs.getLong(KEY_LOCK_UNTIL, 0L)
        if (lockUntil == 0L) return 0
        return maxOf(0, (lockUntil - System.currentTimeMillis()) / 1000)
    }

    fun getFailedAttempts(): Int = prefs.getInt(KEY_FAILED_ATTEMPTS, 0)

    fun isPinSet(): Boolean = !prefs.getString(KEY_PIN_HASH, null).isNullOrEmpty()

    fun isBiometricEnabled(): Boolean = prefs.getBoolean(KEY_BIOMETRIC_ENABLED, false)

    fun setBiometricEnabled(enabled: Boolean) {
        prefs.edit().putBoolean(KEY_BIOMETRIC_ENABLED, enabled).apply()
    }

    fun isBiometricHardwareAvailable(): Boolean {
        val biometricManager = BiometricManager.from(context)
        val result = biometricManager.canAuthenticate(
            BiometricManager.Authenticators.BIOMETRIC_STRONG or
                    BiometricManager.Authenticators.BIOMETRIC_WEAK
        )
        return result == BiometricManager.BIOMETRIC_SUCCESS
    }

    fun shouldLock(): Boolean {
        if (!isPinSet()) return false
        val lastActivity = prefs.getLong(KEY_LAST_ACTIVITY, 0L)
        if (lastActivity == 0L) return true
        val elapsedTime = System.currentTimeMillis() - lastActivity
        return elapsedTime >= inactivityLockTimeoutMs
    }

    fun updateLastActivity() {
        prefs.edit().putLong(KEY_LAST_ACTIVITY, System.currentTimeMillis()).apply()
    }

    fun clearSecurity() {
        prefs.edit().clear().apply()
    }

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

    /**
     * P1 fix: PBKDF2WithHmacSHA256 PIN hashing with salt.
     * 100,000 iterations, 256-bit output.
     */
    private fun hashPinSecure(pin: String, salt: ByteArray): String {
        val spec = PBEKeySpec(pin.toCharArray(), salt, PBKDF2_ITERATIONS, PBKDF2_KEY_LENGTH)
        val factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
        val hashBytes = factory.generateSecret(spec).encoded
        spec.clearPassword()
        return hashBytes.toHex()
    }

    private fun ByteArray.toHex(): String = joinToString("") { "%02x".format(it) }
    private fun String.hexToBytes(): ByteArray = chunked(2).map { it.toInt(16).toByte() }.toByteArray()
}
