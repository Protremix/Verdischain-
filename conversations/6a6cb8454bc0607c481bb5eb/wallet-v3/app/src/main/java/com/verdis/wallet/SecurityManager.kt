package com.verdis.wallet

import android.content.Context
import android.util.Log
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import java.security.SecureRandom

object SecurityManager {
    data class SecurityState(val pinEnabled: Boolean, val biometricEnabled: Boolean)

    private fun prefs(ctx: Context) = try {
        val masterKey = MasterKey.Builder(ctx).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build()
        EncryptedSharedPreferences.create(
            ctx, "verdis_sec_v3", masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    } catch (e: Throwable) {
        ctx.getSharedPreferences("verdis_sec_v3_fb", Context.MODE_PRIVATE)
    }

    fun getState(ctx: Context): SecurityState {
        return try {
            SecurityState(
                pinEnabled = prefs(ctx).getString("pin_hash", null) != null,
                biometricEnabled = prefs(ctx).getBoolean("bio_enabled", false)
            )
        } catch (e: Throwable) { SecurityState(false, false) }
    }

    fun shouldLock(ctx: Context): Boolean {
        return try {
            val state = getState(ctx)
            state.pinEnabled || state.biometricEnabled
        } catch (e: Throwable) { false }
    }

    fun hasPin(ctx: Context): Boolean {
        return try { prefs(ctx).getString("pin_hash", null) != null }
        catch (e: Throwable) { false }
    }

    fun setPin(ctx: Context, pin: String) {
        try {
            // SHA-256 with salt for proper PIN hashing
            val salt = ByteArray(16)
            SecureRandom().nextBytes(salt)
            val hashInput = salt + pin.toByteArray(Charsets.UTF_8)
            val hash = CryptoUtils.sha256(hashInput)
            val stored = CryptoUtils.toHex(salt) + ":" + CryptoUtils.toHex(hash)
            prefs(ctx).edit().putString("pin_hash", stored).apply()
            prefs(ctx).edit().putBoolean("lock_enabled", true).apply()
        } catch (e: Throwable) { Log.e("VerdisSec", "setPin: ${e.message}") }
    }

    fun verifyPin(ctx: Context, pin: String): Boolean {
        return try {
            val stored = prefs(ctx).getString("pin_hash", null) ?: return false
            val parts = stored.split(":")
            if (parts.size != 2) return false
            val salt = parts[0].chunked(2).map { it.toInt(16).toByte() }.toByteArray()
            val expectedHash = parts[1]
            val hashInput = salt + pin.toByteArray(Charsets.UTF_8)
            val actualHash = CryptoUtils.toHex(CryptoUtils.sha256(hashInput))
            actualHash == expectedHash
        } catch (e: Throwable) { false }
    }

    fun clearPin(ctx: Context) {
        try { prefs(ctx).edit().remove("pin_hash").remove("lock_enabled").apply() }
        catch (e: Throwable) {}
    }

    fun isBiometric(ctx: Context): Boolean {
        return try { prefs(ctx).getBoolean("bio_enabled", false) }
        catch (e: Throwable) { false }
    }

    fun setBiometric(ctx: Context, enabled: Boolean) {
        try {
            prefs(ctx).edit().putBoolean("bio_enabled", enabled).apply()
            if (enabled) prefs(ctx).edit().putBoolean("lock_enabled", true).apply()
        } catch (e: Throwable) {}
    }
}
