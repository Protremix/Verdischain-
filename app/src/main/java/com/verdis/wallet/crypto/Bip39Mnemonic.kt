package com.verdis.wallet.crypto

import android.content.Context
import java.security.MessageDigest
import java.security.SecureRandom

/**
 * BIP39 mnemonic phrase generator — 12 words from 128 bits of entropy.
 * Uses the official BIP39 English wordlist (2048 words).
 */
object Bip39Mnemonic {

    private const val ENTROPY_BITS = 128  // 16 bytes -> 12 words
    private const val WORD_COUNT = 12

    private lateinit var wordList: List<String>

    fun init(context: Context) {
        val raw = context.resources.openRawResource(
            context.resources.getIdentifier("bip39_wordlist", "raw", context.packageName)
        )
        wordList = raw.bufferedReader().readLines().filter { it.isNotBlank() }
        require(wordList.size == 2048) { "BIP39 wordlist must have 2048 words, got ${wordList.size}" }
    }

    fun isInitialized(): Boolean = ::wordList.isInitialized

    /**
     * Generates a 12-word BIP39 mnemonic from 128 bits of cryptographically secure entropy.
     * Returns the mnemonic as a space-separated string.
     */
    fun generate(): String {
        ensureInitialized()
        val entropy = ByteArray(ENTROPY_BITS / 8)  // 16 bytes
        SecureRandom().nextBytes(entropy)

        // Compute checksum: first 4 bits of SHA-256(entropy)
        val sha256 = MessageDigest.getInstance("SHA-256").digest(entropy)
        val checksumByte = sha256[0]
        val checksumBits = ((checksumByte.toInt() and 0xFF) shr 4) and 0x0F  // top 4 bits

        // Combine entropy (128 bits) + checksum (4 bits) = 132 bits = 12 * 11-bit words
        val words = mutableListOf<String>()
        for (i in 0 until WORD_COUNT) {
            // Extract 11 bits for each word
            val bitStart = i * 11
            var value = 0
            for (j in 0 until 11) {
                val bitIndex = bitStart + j
                val bit = if (bitIndex < ENTROPY_BITS) {
                    val byteIndex = bitIndex / 8
                    val bitOffset = 7 - (bitIndex % 8)
                    ((entropy[byteIndex].toInt() and 0xFF) shr bitOffset) and 1
                } else {
                    // Checksum bits (only 4 bits at positions 128-131)
                    val checkBitIndex = bitIndex - ENTROPY_BITS
                    ((checksumBits shr (3 - checkBitIndex)) and 1)
                }
                value = (value shl 1) or bit
            }
            words.add(wordList[value])
        }

        return words.joinToString(" ")
    }

    /**
     * Validates a mnemonic phrase by checking word count, word validity, and checksum.
     */
    fun isValid(mnemonic: String): Boolean {
        ensureInitialized()
        val words = mnemonic.trim().lowercase().split(Regex("\\s+"))
        if (words.size != WORD_COUNT) return false

        // Convert words back to entropy + checksum
        val bits = StringBuilder()
        for (word in words) {
            val index = wordList.indexOf(word)
            if (index < 0) return false
            bits.append(index.toString(2).padStart(11, '0'))
        }

        // Extract entropy (first 128 bits) and checksum (last 4 bits)
        val entropyBits = bits.substring(0, ENTROPY_BITS)
        val checksumBits = bits.substring(ENTROPY_BITS, 132)

        // Reconstruct entropy bytes
        val entropy = ByteArray(16)
        for (i in 0 until 16) {
            val byteBits = entropyBits.substring(i * 8, (i + 1) * 8)
            entropy[i] = byteBits.toInt(2).toByte()
        }

        // Verify checksum
        val sha256 = MessageDigest.getInstance("SHA-256").digest(entropy)
        val expectedChecksum = ((sha256[0].toInt() and 0xFF) shr 4).toString(2).padStart(4, '0')
        return checksumBits == expectedChecksum
    }

    /**
     * Derives a 32-byte seed from a mnemonic using SHA-256.
     * Used for Ed25519 key generation (simplified — not BIP32/BIP39-KDF).
     */
    fun mnemonicToSeed(mnemonic: String): ByteArray {
        val normalized = mnemonic.trim().lowercase()
        return MessageDigest.getInstance("SHA-256").digest(normalized.toByteArray(Charsets.UTF_8))
    }

    private fun ensureInitialized() {
        if (!isInitialized()) {
            throw IllegalStateException("Bip39Mnemonic not initialized. Call init(context) first.")
        }
    }
}
