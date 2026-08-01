package com.verdis.wallet

import android.content.Context
import android.content.SharedPreferences
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.MasterKey
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKeys
import com.google.gson.Gson

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
            val masterKey = MasterKey.Builder(context)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build()
            EncryptedSharedPreferences.create(
                context,
                PREFS_NAME,
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
        } catch (e: Exception) {
            // Fallback to regular prefs
            context.getSharedPreferences("verdis_wallet_fallback", Context.MODE_PRIVATE)
        }
    }

    fun createWallet(context: Context): Wallet {
        val privKey = CryptoUtils.generatePrivateKey()
        val privHex = "0x" + CryptoUtils.toHex(privKey)
        val pubKey = CryptoUtils.derivePublicKey(privKey)
        val pubHex = "0x" + CryptoUtils.toHex(pubKey)
        val address = CryptoUtils.deriveAddress(pubKey)
        val seed = generateSeedPhrase()

        val wallet = Wallet(privHex, pubHex, address, seed)
        saveWallet(context, wallet)
        return wallet
    }

    fun importWallet(context: Context, keyOrSeed: String): Wallet {
        val privHex = if (keyOrSeed.contains(" ")) {
            // Seed phrase → derive private key via SHA-256
            val hash = CryptoUtils.sha256(keyOrSeed.toByteArray())
            "0x" + CryptoUtils.toHex(hash)
        } else if (keyOrSeed.startsWith("0x")) {
            keyOrSeed
        } else {
            "0x$keyOrSeed"
        }

        val privKey = CryptoUtils.privateKeyFromHex(privHex)
        val pubKey = CryptoUtils.derivePublicKey(privKey)
        val pubHex = "0x" + CryptoUtils.toHex(pubKey)
        val address = CryptoUtils.deriveAddress(pubKey)

        val wallet = Wallet(privHex, pubHex, address, if (keyOrSeed.contains(" ")) keyOrSeed else null)
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
        val addr = prefs.getString(KEY_ADDRESS, "") ?: ""
        val seed = prefs.getString(KEY_SEED, null)
        return Wallet(priv, pub, addr, seed)
    }

    fun clearWallet(context: Context) {
        getEncryptedPrefs(context).edit().clear().apply()
    }

    fun signTransaction(wallet: Wallet, to: String, amount: Double, fee: Double, nonce: Long): String {
        // Build transaction data and sign
        val txData = "${wallet.address}$to$amount$fee$nonce"
        val privKey = CryptoUtils.privateKeyFromHex(wallet.privateKey)
        val signature = CryptoUtils.sign(privKey, txData.toByteArray(Charsets.UTF_8))
        return "0x" + CryptoUtils.toHex(signature)
    }

    private val bip39Words = listOf(
        "abandon","ability","able","about","above","absent","absorb","abstract","absurd","abuse","access","accident",
        "account","accuse","achieve","acid","acoustic","acquire","across","action","actor","actual","adapt","addict",
        "address","adjust","admit","adult","advance","advice","aerobic","affair","afford","afraid","again","agent",
        "agree","ahead","aim","air","airport","aisle","alarm","album","alcohol","alert","alien","allergy",
        "allow","almost","alone","alpha","already","also","alter","always","amateur","amazing","among","amount",
        "amused","analyst","anchor","ancient","anger","angle","angry","animal","ankle","announce","annual","another",
        "answer","antenna","antique","anxiety","apart","apology","appear","apple","approve","april","arch","arctic",
        "area","arena","argue","arm","armed","armor","army","around","arrange","arrest","arrive","arrow",
        "art","artefact","artist","artwork","ask","aspect","assault","asset","assist","assume","asthma","athlete",
        "atom","attack","attend","attitude","attract","auction","audit","august","aunt","author","auto","autumn",
        "avenue","average","avoid","awake","aware","away","awesome","awful","awkward","axis","baby","bachelor",
        "bacon","badge","bag","balance","balcony","ball","bamboo","banana","banner","bar","barely","bargain",
        "barrel","base","basic","basket","battle","beach","bean","beauty","because","become","beef","before"
    )

    private fun generateSeedPhrase(): String {
        return (1..12).map { bip39Words.random() }.joinToString(" ")
    }
}
