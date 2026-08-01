package com.verdis.wallet

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKeys

object WalletManager {
    private const val TAG = "VerdisWallet"
    private const val PREFS_NAME = "verdis_wallet_encrypted"
    private const val FALLBACK_PREFS = "verdis_wallet_plain"
    private const val KEY_PRIVATE = "private_key"
    private const val KEY_PUBLIC = "public_key"
    private const val KEY_ADDRESS = "address"
    private const val KEY_SEED = "seed_phrase"

    data class Wallet(
        val privateKey: String,
        val publicKey: String,
        val address: String,
        val seedPhrase: String?
    )

    /**
     * Returns EncryptedSharedPreferences with a fallback to plaintext if the KeyStore
     * is in a broken state (common on Samsung Android 12+ after factory reset or
     * after the app is force-stopped while the KeyStore is mid-write).
     */
    private fun getPrefs(context: Context): SharedPreferences {
        return try {
            val masterKeyAlias = MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC)
            EncryptedSharedPreferences.create(
                PREFS_NAME,
                masterKeyAlias,
                context.applicationContext,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
        } catch (e: Exception) {
            Log.w(TAG, "EncryptedSharedPreferences unavailable, using fallback: ${e.message}")
            // Delete corrupted encrypted prefs file so next launch can recreate it
            runCatching {
                context.applicationContext.deleteSharedPreferences(PREFS_NAME)
            }
            context.applicationContext.getSharedPreferences(FALLBACK_PREFS, Context.MODE_PRIVATE)
        }
    }

    fun createWallet(context: Context): Wallet {
        val seedPhrase = CryptoUtils.generateSeedPhrase()
        val privKeyBytes = CryptoUtils.seedToPrivateKey(seedPhrase)
        val privHex = "0x" + CryptoUtils.toHex(privKeyBytes)
        val pubKeyBytes = CryptoUtils.derivePublicKey(privKeyBytes)
        val pubHex = "0x" + CryptoUtils.toHex(pubKeyBytes)
        val address = CryptoUtils.deriveAddress(pubKeyBytes)

        val wallet = Wallet(
            privateKey = privHex,
            publicKey = pubHex,
            address = address,
            seedPhrase = seedPhrase
        )
        saveWallet(context, wallet)
        return wallet
    }

    fun importWallet(context: Context, keyOrSeed: String): Wallet {
        val cleaned = keyOrSeed.trim()
        val isSeed = cleaned.contains(" ")

        val (privKeyBytes, seedPhrase) = if (isSeed) {
            CryptoUtils.seedToPrivateKey(cleaned) to cleaned
        } else {
            CryptoUtils.privateKeyFromHex(cleaned) to null
        }

        val privHex = "0x" + CryptoUtils.toHex(privKeyBytes)
        val pubKeyBytes = CryptoUtils.derivePublicKey(privKeyBytes)
        val pubHex = "0x" + CryptoUtils.toHex(pubKeyBytes)
        val address = CryptoUtils.deriveAddress(pubKeyBytes)

        val wallet = Wallet(
            privateKey = privHex,
            publicKey = pubHex,
            address = address,
            seedPhrase = seedPhrase
        )
        saveWallet(context, wallet)
        return wallet
    }

    fun saveWallet(context: Context, wallet: Wallet) {
        try {
            getPrefs(context).edit()
                .putString(KEY_PRIVATE, wallet.privateKey)
                .putString(KEY_PUBLIC, wallet.publicKey)
                .putString(KEY_ADDRESS, wallet.address)
                .putString(KEY_SEED, wallet.seedPhrase)
                .apply()
        } catch (e: Exception) {
            Log.e(TAG, "saveWallet failed: ${e.message}")
        }
    }

    fun loadWallet(context: Context): Wallet? {
        return try {
            val prefs = getPrefs(context)
            val priv = prefs.getString(KEY_PRIVATE, null) ?: return null
            val pub = prefs.getString(KEY_PUBLIC, "") ?: ""
            val address = prefs.getString(KEY_ADDRESS, "") ?: ""
            val seed = prefs.getString(KEY_SEED, null)
            Wallet(privateKey = priv, publicKey = pub, address = address, seedPhrase = seed)
        } catch (e: Exception) {
            Log.e(TAG, "loadWallet failed: ${e.message}")
            null
        }
    }

    fun clearWallet(context: Context) {
        try {
            getPrefs(context).edit().clear().apply()
        } catch (e: Exception) {
            Log.e(TAG, "clearWallet failed: ${e.message}")
        }
    }

    fun signTransaction(
        wallet: Wallet,
        to: String,
        amount: Double,
        fee: Double,
        nonce: Long,
        data: String? = null
    ): String {
        val dataStr = data ?: ""
        val payload = "${wallet.address}:$to:$amount:$fee:$nonce:$dataStr"
        val privKeyBytes = CryptoUtils.privateKeyFromHex(wallet.privateKey)
        return CryptoUtils.signMessage(privKeyBytes, payload)
    }

    fun buildTransaction(
        wallet: Wallet,
        to: String,
        amount: Double,
        fee: Double,
        nonce: Long,
        data: String? = null
    ): Map<String, Any> {
        val privKeyBytes = CryptoUtils.privateKeyFromHex(wallet.privateKey)
        return CryptoUtils.buildSignedTransaction(
            privateKey = privKeyBytes,
            publicKey = wallet.publicKey,
            from = wallet.address,
            to = to,
            amount = amount,
            fee = fee,
            nonce = nonce,
            data = data
        )
    }
}
