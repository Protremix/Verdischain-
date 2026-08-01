package com.verdis.wallet

import android.content.Context
import android.util.Log
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import com.google.gson.Gson

object WalletManager {
    data class Wallet(
        val address: String,
        val privateKey: String,
        val publicKey: String,
        val seedPhrase: String? = null
    )

    private fun prefs(ctx: Context) = try {
        val masterKey = MasterKey.Builder(ctx).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build()
        EncryptedSharedPreferences.create(
            ctx, "verdis_wallet_v3", masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    } catch (e: Throwable) {
        Log.w("VerdisWallet", "Falling back to plain prefs: ${e.message}")
        ctx.getSharedPreferences("verdis_wallet_v3_fallback", Context.MODE_PRIVATE)
    }

    fun loadWallet(ctx: Context): Wallet? {
        return try {
            val json = prefs(ctx).getString("wallet", null) ?: return null
            Gson().fromJson(json, Wallet::class.java)
        } catch (e: Throwable) {
            Log.e("VerdisWallet", "loadWallet error: ${e.message}", e)
            null
        }
    }

    fun saveWallet(ctx: Context, wallet: Wallet) {
        try {
            prefs(ctx).edit().putString("wallet", Gson().toJson(wallet)).apply()
        } catch (e: Throwable) {
            Log.e("VerdisWallet", "saveWallet error: ${e.message}", e)
        }
    }

    fun clearWallet(ctx: Context) {
        try { prefs(ctx).edit().clear().apply() }
        catch (e: Throwable) {}
    }

    fun createWallet(ctx: Context): Wallet {
        val privKey = CryptoUtils.generatePrivateKey()
        val pubKey = CryptoUtils.derivePublicKey(privKey)
        val address = CryptoUtils.deriveAddress(pubKey)
        val seed = CryptoUtils.generateSeedPhrase()
        val wallet = Wallet(address, CryptoUtils.toHex(privKey), CryptoUtils.toHex(pubKey), seed)
        saveWallet(ctx, wallet)
        return wallet
    }

    fun importWallet(ctx: Context, key: String): Wallet {
        val privHex = if (key.startsWith("0x")) key.substring(2) else key
        val privKey = CryptoUtils.privateKeyFromHex(privHex)
        val pubKey = CryptoUtils.derivePublicKey(privKey)
        val address = CryptoUtils.deriveAddress(pubKey)
        val wallet = Wallet(address, CryptoUtils.toHex(privKey), CryptoUtils.toHex(pubKey), null)
        saveWallet(ctx, wallet)
        return wallet
    }
}
