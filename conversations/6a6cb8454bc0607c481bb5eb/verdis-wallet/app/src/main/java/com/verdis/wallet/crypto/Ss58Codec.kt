package com.verdis.wallet.crypto

import java.math.BigInteger
import java.security.MessageDigest
import java.security.NoSuchAlgorithmException

/**
 * SS58 address codec for Substrate networks (default network prefix 909).
 */
object Ss58Codec {
    const val DEFAULT_PREFIX = 909
    private val SS58_PREFIX_BYTES = "SS58PRE".toByteArray(Charsets.UTF_8)

    // Bitcoin Base58 alphabet
    private const val BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    private val BASE58_INDEXES = IntArray(128) { -1 }.apply {
        for (i in BASE58_ALPHABET.indices) {
            this[BASE58_ALPHABET[i].code] = i
        }
    }

    /**
     * Encodes a 32-byte public key to an SS58 address string.
     * Default network prefix is 909 (Verdis).
     */
    fun encode(publicKey: ByteArray, prefix: Int = DEFAULT_PREFIX): String {
        require(publicKey.size == 32) { "Public key must be exactly 32 bytes" }

        val prefixBytes = getPrefixBytes(prefix)
        val checksum = computeChecksum(prefixBytes, publicKey)

        val fullPayload = ByteArray(prefixBytes.size + publicKey.size + checksum.size)
        System.arraycopy(prefixBytes, 0, fullPayload, 0, prefixBytes.size)
        System.arraycopy(publicKey, 0, fullPayload, prefixBytes.size, publicKey.size)
        System.arraycopy(checksum, 0, fullPayload, prefixBytes.size + publicKey.size, checksum.size)

        return base58Encode(fullPayload)
    }

    /**
     * Decodes an SS58 address string back to the 32-byte public key.
     */
    fun decode(address: String): ByteArray {
        val decoded = base58Decode(address)
        require(decoded.size >= 36) { "Invalid SS58 address length: ${decoded.size}" }

        val prefixSize = decoded.size - 34 // Prefix size (2 bytes for prefix 909)
        require(prefixSize > 0) { "Invalid SS58 payload prefix structure" }

        val prefixBytes = decoded.copyOfRange(0, prefixSize)
        val publicKey = decoded.copyOfRange(prefixSize, decoded.size - 2)
        val checksum = decoded.copyOfRange(decoded.size - 2, decoded.size)

        require(publicKey.size == 32) { "Extracted public key must be 32 bytes" }

        val expectedChecksum = computeChecksum(prefixBytes, publicKey)
        require(checksum.contentEquals(expectedChecksum)) { "Invalid SS58 checksum" }

        return publicKey
    }

    /**
     * Formats network prefix as 2 bytes Little Endian (for prefix 909).
     */
    fun getPrefixBytes(prefix: Int): ByteArray {
        return byteArrayOf(
            (prefix and 0xFF).toByte(),
            ((prefix ushr 8) and 0xFF).toByte()
        )
    }

    /**
     * Computes 2-byte checksum using BLAKE2b-256 (if available in java.security)
     * or SHA-256 fallback taking first 2 bytes.
     */
    fun computeChecksum(prefixBytes: ByteArray, publicKey: ByteArray): ByteArray {
        return try {
            val digest = MessageDigest.getInstance("BLAKE2b-256")
            digest.update(SS58_PREFIX_BYTES)
            digest.update(prefixBytes)
            digest.update(publicKey)
            val hash = digest.digest()
            hash.copyOfRange(0, 2)
        } catch (e: NoSuchAlgorithmException) {
            val digest = MessageDigest.getInstance("SHA-256")
            digest.update(prefixBytes)
            digest.update(publicKey)
            val hash = digest.digest()
            hash.copyOfRange(0, 2)
        }
    }

    /**
     * Base58 encoding (Bitcoin-style, BigInteger numeric conversion without leading zeros).
     */
    fun base58Encode(input: ByteArray): String {
        if (input.isEmpty()) return ""
        var num = BigInteger(1, input)
        val base = BigInteger.valueOf(58)
        val sb = StringBuilder()
        while (num > BigInteger.ZERO) {
            val remainder = (num % base).toInt()
            sb.append(BASE58_ALPHABET[remainder])
            num /= base
        }
        return sb.reverse().toString()
    }

    /**
     * Base58 decoding back to ByteArray.
     */
    fun base58Decode(input: String): ByteArray {
        if (input.isEmpty()) return ByteArray(0)
        var num = BigInteger.ZERO
        val base = BigInteger.valueOf(58)
        for (ch in input) {
            val idx = if (ch.code < 128) BASE58_INDEXES[ch.code] else -1
            require(idx >= 0) { "Invalid Base58 character: '$ch'" }
            num = num * base + BigInteger.valueOf(idx.toLong())
        }
        var bytes = num.toByteArray()
        if (bytes.size > 1 && bytes[0] == 0.toByte()) {
            bytes = bytes.copyOfRange(1, bytes.size)
        }
        return bytes
    }
}
