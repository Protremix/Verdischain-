package com.verdis.wallet.crypto

import android.content.Context
import android.content.SharedPreferences
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import java.security.KeyFactory
import java.security.KeyStore
import java.security.MessageDigest
import java.security.PrivateKey
import java.security.PublicKey
import java.security.SecureRandom
import java.security.Signature
import java.security.spec.PKCS8EncodedKeySpec
import java.security.spec.X509EncodedKeySpec
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.GCMParameterSpec
import javax.crypto.spec.PBEKeySpec
import javax.crypto.spec.SecretKeySpec

/**
 * Key Manager for Ed25519 accounts on Substrate networks.
 * Uses Android Keystore for hardware-backed key encryption (P0 fix).
 * Uses PBKDF2WithHmacSHA256 for PIN derivation (P1 fix).
 */
class KeyManager(private val context: Context? = null) {

    private val prefs: SharedPreferences? by lazy {
        context?.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    }

    init {
        context?.let { Bip39Mnemonic.init(it) }
        ensureKeystoreKey()
    }

    companion object {
        const val PREFS_NAME = "verdis_wallet_keys"
        private const val KEY_ACCOUNT_LIST = "accounts_list"
        private const val KEY_MNEMONIC_PREFIX = "account_mnemonic_"
        private const val ANDROID_KEYSTORE = "AndroidKeyStore"
        private const val KEY_ALIAS = "verdis_wallet_master"
        private const val GCM_IV_LENGTH = 12
        private const val PBKDF2_ITERATIONS = 200_000 // P1 fix: doubled for brute force resistance
        private const val PBKDF2_KEY_LENGTH = 256
        private const val SALT_LENGTH = 16

        val ED25519_PUBKEY_HEADER = byteArrayOf(
            0x30.toByte(), 0x2a.toByte(), 0x30.toByte(), 0x05.toByte(),
            0x06.toByte(), 0x03.toByte(), 0x2b.toByte(), 0x65.toByte(),
            0x70.toByte(), 0x03.toByte(), 0x21.toByte(), 0x00.toByte()
        )

        val ED25519_PRIVKEY_HEADER = byteArrayOf(
            0x30.toByte(), 0x2e.toByte(), 0x02.toByte(), 0x01.toByte(),
            0x00.toByte(), 0x30.toByte(), 0x05.toByte(), 0x06.toByte(),
            0x03.toByte(), 0x2b.toByte(), 0x65.toByte(), 0x70.toByte(),
            0x04.toByte(), 0x22.toByte(), 0x04.toByte(), 0x20.toByte()
        )

        fun privKeyFromSeed(seed32Bytes: ByteArray): PrivateKey {
            require(seed32Bytes.size == 32) { "Seed must be exactly 32 bytes" }
            val pkcs8 = ED25519_PRIVKEY_HEADER + seed32Bytes
            // P1 fix: Validate PKCS8 format size (16-byte header + 32-byte seed = 48 bytes)
            require(pkcs8.size == 48) { "Invalid private key format: expected 48 bytes, got ${'$'}{pkcs8.size}" }
            val keyFactory = KeyFactory.getInstance("Ed25519")
            return keyFactory.generatePrivate(PKCS8EncodedKeySpec(pkcs8))
        }

        fun pubKeyFromBytes(pubKey32Bytes: ByteArray): PublicKey {
            require(pubKey32Bytes.size == 32) { "Public key must be exactly 32 bytes" }
            val x509 = ED25519_PUBKEY_HEADER + pubKey32Bytes
            val keyFactory = KeyFactory.getInstance("Ed25519")
            return keyFactory.generatePublic(X509EncodedKeySpec(x509))
        }
    }

    // === Android Keystore-backed encryption ===

    private var keystoreSecretKey: SecretKey? = null

    /**
     * Initializes the Android Keystore master key for AES-GCM encryption.
     * Hardware-backed on supported devices (TEE/StrongBox).
     */
    private fun ensureKeystoreKey() {
        try {
            val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE).apply { load(null) }
            if (keyStore.containsAlias(KEY_ALIAS)) {
                keystoreSecretKey = keyStore.getKey(KEY_ALIAS, null) as SecretKey
            } else {
                val keyGenerator = KeyGenerator.getInstance(
                    KeyProperties.KEY_ALGORITHM_AES, ANDROID_KEYSTORE
                )
                val spec = KeyGenParameterSpec.Builder(
                    KEY_ALIAS,
                    KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
                )
                    .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                    .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                    .setKeySize(256)
                    .setUserAuthenticationRequired(false) // PIN gate handles auth
                    .build()
                keyGenerator.init(spec)
                keystoreSecretKey = keyGenerator.generateKey()
            }
        } catch (e: Exception) {
            // P0 fix: Keystore unavailable — log warning and use PBKDF2 fallback
            android.util.Log.w("KeyManager", "Android Keystore unavailable, using PBKDF2 fallback: ${'$'}{e.message}")
            keystoreSecretKey = null
        }
    }

    /**
     * Encrypts data using Android Keystore AES-GCM (P0 fix).
     * Falls back to PBKDF2-derived key if Keystore is unavailable.
     */
    fun encrypt(data: ByteArray, pin: String): ByteArray {
        val iv = ByteArray(GCM_IV_LENGTH).apply { SecureRandom().nextBytes(this) }

        val cipher = Cipher.getInstance("AES/GCM/NoPadding")

        keystoreSecretKey?.let { key ->
            cipher.init(Cipher.ENCRYPT_MODE, key, GCMParameterSpec(128, iv))
            val encrypted = cipher.doFinal(data)
            // Format: [iv(12)] [encrypted_with_gcm_tag]
            return iv + encrypted
        }

        // Fallback: PBKDF2-derived key from PIN + random salt
        val salt = ByteArray(SALT_LENGTH).apply { SecureRandom().nextBytes(this) }
        val secretKey = derivePinKey(pin, salt)
        cipher.init(Cipher.ENCRYPT_MODE, secretKey, GCMParameterSpec(128, iv))
        val encrypted = cipher.doFinal(data)
        // Format: [salt(16)] [iv(12)] [encrypted_with_gcm_tag]
        return salt + iv + encrypted
    }

    /**
     * Decrypts data encrypted by encrypt(). Auto-detects format (Keystore vs fallback).
     */
    fun decrypt(data: ByteArray, pin: String): ByteArray {
        require(data.size > GCM_IV_LENGTH) { "Invalid encrypted data length" }

        // Try Keystore format first: [iv(12)] [encrypted]
        keystoreSecretKey?.let { key ->
            if (data.size > GCM_IV_LENGTH + 16) { // minimum meaningful ciphertext
                try {
                    val iv = data.copyOfRange(0, GCM_IV_LENGTH)
                    val encrypted = data.copyOfRange(GCM_IV_LENGTH, data.size)
                    val cipher = Cipher.getInstance("AES/GCM/NoPadding")
                    cipher.init(Cipher.DECRYPT_MODE, key, GCMParameterSpec(128, iv))
                    return cipher.doFinal(encrypted)
                } catch (e: Exception) {
                    // Might be old format, fall through to PBKDF2
                }
            }
        }

        // PBKDF2 format: [salt(16)] [iv(12)] [encrypted]
        require(data.size > SALT_LENGTH + GCM_IV_LENGTH) { "Invalid encrypted data length" }
        val salt = data.copyOfRange(0, SALT_LENGTH)
        val iv = data.copyOfRange(SALT_LENGTH, SALT_LENGTH + GCM_IV_LENGTH)
        val encrypted = data.copyOfRange(SALT_LENGTH + GCM_IV_LENGTH, data.size)

        val secretKey = derivePinKey(pin, salt)
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        cipher.init(Cipher.DECRYPT_MODE, secretKey, GCMParameterSpec(128, iv))
        return cipher.doFinal(encrypted)
    }

    /**
     * Derives an AES key from PIN using PBKDF2WithHmacSHA256 (P1 fix).
     * 200,000 iterations with 16-byte random salt.
     */
    private fun derivePinKey(pin: String, salt: ByteArray): SecretKey {
        val spec = PBEKeySpec(pin.toCharArray(), salt, PBKDF2_ITERATIONS, PBKDF2_KEY_LENGTH)
        val factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256")
        val keyBytes = factory.generateSecret(spec).encoded
        spec.clearPassword()
        // P0 fix: Return SecretKeySpec but note keyBytes array still lives in JVM heap.
        // SecretKeySpec copies the array internally, so we can safely zero the original.
        val keySpec = SecretKeySpec(keyBytes, "AES")
        keyBytes.fill(0) // Zero out the raw key bytes
        return keySpec
    }

    // === Account Management ===

    fun generateAccountWithMnemonic(accountName: String, pin: String): Pair<String, String> {
        val mnemonic = Bip39Mnemonic.generate()
        val privKeySeed = Bip39Mnemonic.mnemonicToSeed(mnemonic)
        val pubKeyBytes = Ed25519Derivation.derivePublicKey(privKeySeed)

        saveAccountData(accountName, pubKeyBytes, privKeySeed, pin)
        saveEncryptedMnemonic(accountName, mnemonic, pin)

        val address = getAddress(accountName)
        return Pair(mnemonic, address)
    }

    fun generateAccount(accountName: String, pin: String): String {
        val (mnemonic, address) = generateAccountWithMnemonic(accountName, pin)
        return address
    }

    fun importFromMnemonic(accountName: String, mnemonic: String, pin: String): String {
        val trimmed = mnemonic.trim()
        if (!Bip39Mnemonic.isValid(trimmed)) {
            throw IllegalArgumentException("Invalid BIP39 mnemonic phrase")
        }

        val privKeySeed = Bip39Mnemonic.mnemonicToSeed(trimmed)
        val pubKeyBytes = Ed25519Derivation.derivePublicKey(privKeySeed)

        saveAccountData(accountName, pubKeyBytes, privKeySeed, pin)
        saveEncryptedMnemonic(accountName, trimmed, pin)

        return getAddress(accountName)
    }

    fun importFromSeedHex(accountName: String, seedHex: String, pin: String): String {
        val privKeySeed = seedHex.chunked(2).map { it.toInt(16).toByte() }.toByteArray()
        require(privKeySeed.size == 32) { "Private key seed must be 32 bytes (64 hex chars)" }

        val pubKeyBytes = Ed25519Derivation.derivePublicKey(privKeySeed)
        saveAccountData(accountName, pubKeyBytes, privKeySeed, pin)

        return getAddress(accountName)
    }

    fun importAccount(accountName: String, seedPhraseOrHex: String, pin: String): String {
        val trimmed = seedPhraseOrHex.trim()
        val wordCount = trimmed.split(Regex("\\s+")).size

        return if (wordCount == 12 && !trimmed.startsWith("0x") && !trimmed.matches(Regex("^[0-9a-fA-F]{64}$"))) {
            importFromMnemonic(accountName, trimmed, pin)
        } else if (trimmed.matches(Regex("^[0-9a-fA-F]{64}$"))) {
            importFromSeedHex(accountName, trimmed, pin)
        } else {
            throw IllegalArgumentException("Input must be a 12-word mnemonic or 64-char hex private key")
        }
    }

    fun getAccounts(): List<String> {
        val rawList = getString(KEY_ACCOUNT_LIST) ?: return emptyList()
        return rawList.split(",").filter { it.isNotBlank() }
    }

    fun getPublicKey(accountName: String): ByteArray {
        val encoded = getString("account_${accountName}_pubkey")
            ?: throw IllegalArgumentException("Account '$accountName' not found")
        return base64Decode(encoded)
    }

    fun getAddress(accountName: String, prefix: Int = Ss58Codec.DEFAULT_PREFIX): String {
        val pubKey = getPublicKey(accountName)
        return Ss58Codec.encode(pubKey, prefix)
    }

    fun sign(accountName: String, pin: String, message: ByteArray): ByteArray {
        val privKeySeed = exportPrivateKey(accountName, pin)
        val privateKey = privKeyFromSeed(privKeySeed)

        val signer = Signature.getInstance("Ed25519")
        signer.initSign(privateKey)
        signer.update(message)
        val signature = signer.sign()

        // Clear sensitive data from memory (P0 fix: memory safety)
        privKeySeed.fill(0)

        return signature
    }

    fun signRaw(privKeySeed: ByteArray, message: ByteArray): ByteArray {
        val privateKey = privKeyFromSeed(privKeySeed)
        val signer = Signature.getInstance("Ed25519")
        signer.initSign(privateKey)
        signer.update(message)
        return signer.sign()
    }

    fun exportPrivateKey(accountName: String, pin: String): ByteArray {
        val encryptedBase64 = getString("account_${accountName}_privkey")
            ?: throw IllegalArgumentException("Account '$accountName' not found")
        val encryptedData = base64Decode(encryptedBase64)
        val key = decrypt(encryptedData, pin)
        val keyCopy = key.copyOf()
        key.fill(0)
        return keyCopy
    }

    fun exportMnemonic(accountName: String, pin: String): String {
        val encryptedBase64 = getString("${KEY_MNEMONIC_PREFIX}${accountName}")
            ?: throw IllegalArgumentException("No mnemonic stored for '$accountName'")
        val encryptedData = base64Decode(encryptedBase64)
        return decrypt(encryptedData, pin).toString(Charsets.UTF_8)
    }

    fun deleteAccount(accountName: String) {
        val accounts = getAccounts().toMutableList()
        accounts.remove(accountName)
        saveString(KEY_ACCOUNT_LIST, accounts.joinToString(","))
        removeKey("account_${accountName}_pubkey")
        removeKey("account_${accountName}_privkey")
        removeKey("${KEY_MNEMONIC_PREFIX}${accountName}")
    }

    fun hasAccount(): Boolean = getAccounts().isNotEmpty()

    private fun saveAccountData(
        accountName: String,
        pubKeyBytes: ByteArray,
        privKeySeed: ByteArray,
        pin: String
    ) {
        val encryptedPrivKey = encrypt(privKeySeed, pin)

        saveString("account_${accountName}_pubkey", base64Encode(pubKeyBytes))
        saveString("account_${accountName}_privkey", base64Encode(encryptedPrivKey))

        val accounts = getAccounts().toMutableList()
        if (!accounts.contains(accountName)) {
            accounts.add(accountName)
            saveString(KEY_ACCOUNT_LIST, accounts.joinToString(","))
        }

        // Clear sensitive data (P0 fix: memory safety)
        privKeySeed.fill(0)
    }

    private fun saveEncryptedMnemonic(accountName: String, mnemonic: String, pin: String) {
        val mnemonicBytes = mnemonic.toByteArray(Charsets.UTF_8)
        val encrypted = encrypt(mnemonicBytes, pin)
        saveString("${KEY_MNEMONIC_PREFIX}${accountName}", base64Encode(encrypted))

        // Clear sensitive data (P0 fix: memory safety)
        mnemonicBytes.fill(0)
    }

    // === Storage helpers ===

    private fun getString(key: String): String? = prefs?.getString(key, null)

    private fun saveString(key: String, value: String) {
        prefs?.edit()?.putString(key, value)?.apply()
    }

    private fun removeKey(key: String) {
        prefs?.edit()?.remove(key)?.apply()
    }

    private fun base64Encode(data: ByteArray): String =
        android.util.Base64.encodeToString(data, android.util.Base64.NO_WRAP)

    private fun base64Decode(data: String): ByteArray =
        android.util.Base64.decode(data, android.util.Base64.DEFAULT)
}
