package com.verdis.wallet

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKeys

object WalletManager {

    private const val PREFS_NAME = "verdis_wallet_encrypted"
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

    private fun getEncryptedPrefs(context: Context): SharedPreferences {
        return try {
            val masterKeyAlias = MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC)
            EncryptedSharedPreferences.create(
                PREFS_NAME,
                masterKeyAlias,
                context,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
        } catch (e: Exception) {
            context.getSharedPreferences("verdis_wallet_fallback", Context.MODE_PRIVATE)
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
        val prefs = getEncryptedPrefs(context)
        prefs.edit()
            .putString(KEY_PRIVATE, wallet.privateKey)
            .putString(KEY_PUBLIC, wallet.publicKey)
            .putString(KEY_ADDRESS, wallet.address)
            .putString(KEY_SEED, wallet.seedPhrase)
            .apply()
    }

    fun loadWallet(context: Context): Wallet? {
        val prefs = getEncryptedPrefs(context)
        val priv = prefs.getString(KEY_PRIVATE, null) ?: return null
        val pub = prefs.getString(KEY_PUBLIC, "") ?: ""
        val address = prefs.getString(KEY_ADDRESS, "") ?: ""
        val seed = prefs.getString(KEY_SEED, null)

        return Wallet(
            privateKey = priv,
            publicKey = pub,
            address = address,
            seedPhrase = seed
        )
    }

    fun clearWallet(context: Context) {
        val prefs = getEncryptedPrefs(context)
        prefs.edit().clear().apply()
    }

    fun signTransaction(wallet: Wallet, to: String, amount: Double, fee: Double, nonce: Long): String {
        val txData = "${wallet.address}$to$amount$fee$nonce"
        val privKeyBytes = CryptoUtils.privateKeyFromHex(wallet.privateKey)
        return CryptoUtils.signMessage(privKeyBytes, txData)
    }
}
