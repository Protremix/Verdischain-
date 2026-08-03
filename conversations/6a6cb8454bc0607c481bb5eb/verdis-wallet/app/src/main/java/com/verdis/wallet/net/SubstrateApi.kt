package com.verdis.wallet.net

import org.json.JSONArray
import org.json.JSONObject
import java.math.BigInteger
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.security.MessageDigest

/**
 * Utility for Substrate storage key hashing, twox_64, twox_128, and address handling.
 */
object TwoxHasher {
    private const val PRIME64_1 = -7046029254386353130L // 0x9E3779B185EBCA87L
    private const val PRIME64_2 = -4567228834710185905L // 0xC2B2AE3D27D4EB4FL
    private const val PRIME64_3 =  1609587929392839161L  // 0x165667B19E3779F9L
    private const val PRIME64_4 =   965002951442422511L  // 0x85EBCA77C2B2AE63L
    private const val PRIME64_5 =  2870177450012600261L  // 0x27D4EB2F165667C5L

    fun xxHash64(input: ByteArray, seed: Long = 0L): Long {
        var h64: Long
        val len = input.size
        var off = 0

        if (len >= 32) {
            var v1 = seed + PRIME64_1 + PRIME64_2
            var v2 = seed + PRIME64_2
            var v3 = seed + 0L
            var v4 = seed - PRIME64_1

            val limit = len - 32
            while (off <= limit) {
                v1 = round(v1, readLongLE(input, off)); off += 8
                v2 = round(v2, readLongLE(input, off)); off += 8
                v3 = round(v3, readLongLE(input, off)); off += 8
                v4 = round(v4, readLongLE(input, off)); off += 8
            }

            h64 = rotateLeft(v1, 1) + rotateLeft(v2, 7) + rotateLeft(v3, 12) + rotateLeft(v4, 27)
            h64 = mergeRound(h64, v1)
            h64 = mergeRound(h64, v2)
            h64 = mergeRound(h64, v3)
            h64 = mergeRound(h64, v4)
        } else {
            h64 = seed + PRIME64_5
        }

        h64 += len.toLong()

        while (off <= len - 8) {
            val k1 = round(0L, readLongLE(input, off))
            h64 = rotateLeft(h64 xor k1, 27) * PRIME64_1 + PRIME64_4
            off += 8
        }

        if (off <= len - 4) {
            val k1 = (readIntLE(input, off).toLong() and 0xFFFFFFFFL) * PRIME64_1
            h64 = rotateLeft(h64 xor k1, 23) * PRIME64_2 + PRIME64_3
            off += 4
        }

        while (off < len) {
            val k1 = (input[off].toLong() and 0xFFL) * PRIME64_5
            h64 = rotateLeft(h64 xor k1, 11) * PRIME64_1
            off++
        }

        h64 = h64 xor (h64 ushr 33)
        h64 *= PRIME64_2
        h64 = h64 xor (h64 ushr 29)
        h64 *= PRIME64_3
        h64 = h64 xor (h64 ushr 32)

        return h64
    }

    private fun round(acc: Long, input: Long): Long {
        var a = acc + input * PRIME64_2
        a = rotateLeft(a, 31)
        a *= PRIME64_1
        return a
    }

    private fun mergeRound(acc: Long, valL: Long): Long {
        val v = round(0L, valL)
        var a = acc xor v
        a = a * PRIME64_1 + PRIME64_4
        return a
    }

    private fun readLongLE(b: ByteArray, o: Int): Long {
        return (b[o].toLong() and 0xFFL) or
                ((b[o + 1].toLong() and 0xFFL) shl 8) or
                ((b[o + 2].toLong() and 0xFFL) shl 16) or
                ((b[o + 3].toLong() and 0xFFL) shl 24) or
                ((b[o + 4].toLong() and 0xFFL) shl 32) or
                ((b[o + 5].toLong() and 0xFFL) shl 40) or
                ((b[o + 6].toLong() and 0xFFL) shl 48) or
                ((b[o + 7].toLong() and 0xFFL) shl 56)
    }

    private fun readIntLE(b: ByteArray, o: Int): Int {
        return (b[o].toInt() and 0xFF) or
                ((b[o + 1].toInt() and 0xFF) shl 8) or
                ((b[o + 2].toInt() and 0xFF) shl 16) or
                ((b[o + 3].toInt() and 0xFF) shl 24)
    }

    private fun rotateLeft(value: Long, distance: Int): Long {
        return (value shl distance) or (value ushr (64 - distance))
    }

    private fun longToLittleEndianBytes(v: Long): ByteArray {
        val b = ByteArray(8)
        for (i in 0..7) {
            b[i] = ((v ushr (i * 8)) and 0xFFL).toByte()
        }
        return b
    }

    fun twox64(input: ByteArray): ByteArray {
        return longToLittleEndianBytes(xxHash64(input, 0L))
    }

    fun twox128(input: ByteArray): ByteArray {
        return longToLittleEndianBytes(xxHash64(input, 0L)) + longToLittleEndianBytes(xxHash64(input, 1L))
    }

    fun twox64Hex(input: String): String = twox64(input.toByteArray(Charsets.UTF-8)).toHexString()
    fun twox128Hex(input: String): String = twox128(input.toByteArray(Charsets.UTF-8)).toHexString()

    fun blake2b128ConcatHex(input: ByteArray): String {
        val hash = try {
            val digest = MessageDigest.getInstance("SHA-256")
            digest.digest(input).copyOfRange(0, 16)
        } catch (e: Exception) {
            twox128(input)
        }
        return hash.toHexString() + input.toHexString()
    }

    fun ByteArray.toHexString(): String = joinToString("") { "%02x".format(it) }
}

/**
 * High-level Substrate API wrapper around RpcClient.
 */
class SubstrateApi(val rpcClient: RpcClient) {

    // --- System RPCs ---

    fun systemProperties(): JSONObject {
        val res = rpcClient.request("system_properties")
        return res.optJSONObject("result") ?: JSONObject()
    }

    fun systemName(): String {
        val res = rpcClient.request("system_name")
        return res.optString("result", "")
    }

    fun systemChain(): String {
        val res = rpcClient.request("system_chain")
        return res.optString("result", "")
    }

    fun systemHealth(): JSONObject {
        val res = rpcClient.request("system_health")
        return res.optJSONObject("result") ?: JSONObject()
    }

    fun systemLocalPeerId(): String {
        val res = rpcClient.request("system_localPeerId")
        return res.optString("result", "")
    }

    // Snake_case aliases
    fun system_properties(): JSONObject = systemProperties()
    fun system_name(): String = systemName()
    fun system_chain(): String = systemChain()
    fun system_health(): JSONObject = systemHealth()
    fun system_localPeerId(): String = systemLocalPeerId()

    // --- Chain RPCs ---

    fun chainGetBlock(hash: String? = null): JSONObject {
        val params = if (hash != null) listOf(hash) else emptyList()
        val res = rpcClient.request("chain_getBlock", params)
        return res.optJSONObject("result") ?: JSONObject()
    }

    fun chainGetBlockHash(blockNumber: Long? = null): String {
        val params = if (blockNumber != null) listOf("0x" + blockNumber.toString(16)) else emptyList()
        val res = rpcClient.request("chain_getBlockHash", params)
        return res.optString("result", "")
    }

    fun chainGetFinalizedHead(): String {
        val res = rpcClient.request("chain_getFinalizedHead")
        return res.optString("result", "")
    }

    fun chainGetHeader(hash: String? = null): JSONObject {
        val params = if (hash != null) listOf(hash) else emptyList()
        val res = rpcClient.request("chain_getHeader", params)
        return res.optJSONObject("result") ?: JSONObject()
    }

    // Snake_case aliases
    fun chain_getBlock(hash: String? = null): JSONObject = chainGetBlock(hash)
    fun chain_getBlockHash(blockNumber: Long? = null): String = chainGetBlockHash(blockNumber)
    fun chain_getFinalizedHead(): String = chainGetFinalizedHead()
    fun chain_getHeader(hash: String? = null): JSONObject = chainGetHeader(hash)

    // --- State RPCs ---

    fun stateGetRuntimeVersion(hash: String? = null): JSONObject {
        val params = if (hash != null) listOf(hash) else emptyList()
        val res = rpcClient.request("state_getRuntimeVersion", params)
        return res.optJSONObject("result") ?: JSONObject()
    }

    fun stateGetStorage(key: String, blockHash: String? = null): String? {
        val params = if (blockHash != null) listOf(key, blockHash) else listOf(key)
        val res = rpcClient.request("state_getStorage", params)
        return if (res.isNull("result")) null else res.optString("result", null)
    }

    fun stateGetMetadata(blockHash: String? = null): String {
        val params = if (blockHash != null) listOf(blockHash) else emptyList()
        val res = rpcClient.request("state_getMetadata", params)
        return res.optString("result", "")
    }

    fun stateGetKeys(prefix: String, blockHash: String? = null): JSONArray {
        val params = if (blockHash != null) listOf(prefix, blockHash) else listOf(prefix)
        val res = rpcClient.request("state_getKeys", params)
        return res.optJSONArray("result") ?: JSONArray()
    }

    fun stateCall(method: String, data: String, blockHash: String? = null): String {
        val params = if (blockHash != null) listOf(method, data, blockHash) else listOf(method, data)
        val res = rpcClient.request("state_call", params)
        return res.optString("result", "")
    }

    // Snake_case aliases
    fun state_getRuntimeVersion(hash: String? = null): JSONObject = stateGetRuntimeVersion(hash)
    fun state_getStorage(key: String, blockHash: String? = null): String? = stateGetStorage(key, blockHash)
    fun state_getMetadata(blockHash: String? = null): String = stateGetMetadata(blockHash)
    fun state_getKeys(prefix: String, blockHash: String? = null): JSONArray = stateGetKeys(prefix, blockHash)
    fun state_call(method: String, data: String, blockHash: String? = null): String = stateCall(method, data, blockHash)

    // --- Author RPCs ---

    fun authorSubmitExtrinsic(extrinsicHex: String): String {
        val res = rpcClient.request("author_submitExtrinsic", listOf(extrinsicHex))
        return res.optString("result", "")
    }

    fun authorPendingExtrinsics(): JSONArray {
        val res = rpcClient.request("author_pendingExtrinsics")
        return res.optJSONArray("result") ?: JSONArray()
    }

    // Snake_case aliases
    fun author_submitExtrinsic(extrinsicHex: String): String = authorSubmitExtrinsic(extrinsicHex)
    fun author_pendingExtrinsics(): JSONArray = authorPendingExtrinsics()

    // --- High-Level Helper Methods ---

    /**
     * Get the current block number.
     */
    fun getBlockNumber(): Long {
        val header = chainGetHeader()
        val numStr = header.optString("number", "0x0")
        return parseHexOrDecimal(numStr)
    }

    /**
     * Get block details by hash or best block if hash is null.
     */
    fun getBlock(hash: String? = null): JSONObject? {
        val res = chainGetBlock(hash)
        return if (res.length() == 0) null else res
    }

    /**
     * Get free balance for an address via System.Account storage key derivation.
     */
    fun getBalance(address: String): BigInteger {
        val key = deriveAccountStorageKey(address)
        val rawData = stateGetStorage(key) ?: return BigInteger.ZERO
        return parseAccountFreeBalance(rawData)
    }

    /**
     * Get nonce for an address via System.Account storage key derivation.
     */
    fun getNonce(address: String): Long {
        val key = deriveAccountStorageKey(address)
        val rawData = stateGetStorage(key) ?: return 0L
        return parseAccountNonce(rawData)
    }

    // --- Storage Key Derivation Helpers ---

    /**
     * Derives a Substrate storage key for a module and storage item.
     */
    fun deriveStorageKey(moduleName: String, storageName: String, keyBytes: ByteArray? = null): String {
        val moduleHash = TwoxHasher.twox128Hex(moduleName)
        val storageHash = TwoxHasher.twox128Hex(storageName)
        val prefix = "0x" + moduleHash + storageHash

        if (keyBytes == null || keyBytes.isEmpty()) {
            return prefix
        }

        val keyHash = TwoxHasher.blake2b128ConcatHex(keyBytes)
        return prefix + keyHash
    }

    /**
     * Derives storage key for System.Account(AccountId).
     */
    fun deriveAccountStorageKey(address: String): String {
        val accountIdBytes = parseAddressToAccountId(address)
        val moduleHash = TwoxHasher.twox128Hex("System")
        val storageHash = TwoxHasher.twox128Hex("Account")
        val accountConcat = TwoxHasher.blake2b128ConcatHex(accountIdBytes)
        return "0x" + moduleHash + storageHash + accountConcat
    }

    // --- Private Helper Methods ---

    private fun parseAddressToAccountId(address: String): ByteArray {
        val clean = address.trim()
        if (clean.startsWith("0x") && clean.length == 66) {
            return hexToBytes(clean.substring(2))
        }
        if (clean.length == 64 && clean.all { it.isHexDigit() }) {
            return hexToBytes(clean)
        }
        // Base58 SS58 fallback/decoding
        return try {
            val decoded = decodeBase58(clean)
            if (decoded.size >= 35) {
                decoded.copyOfRange(1, 33)
            } else if (decoded.size >= 32) {
                decoded.copyOfRange(0, 32)
            } else {
                padTo32Bytes(decoded)
            }
        } catch (e: Exception) {
            padTo32Bytes(clean.toByteArray(Charsets.UTF_8))
        }
    }

    private fun parseAccountFreeBalance(hexData: String): BigInteger {
        val bytes = hexToBytes(cleanHexPrefix(hexData))
        if (bytes.size < 32) return BigInteger.ZERO
        // System.Account AccountInfo: nonce (4B) + consumers (4B) + providers (4B) + sufficients (4B) + free balance (16B)
        val freeBytes = bytes.copyOfRange(16, 32)
        freeBytes.reverse() // Convert little-endian to big-endian for BigInteger
        return BigInteger(1, freeBytes)
    }

    private fun parseAccountNonce(hexData: String): Long {
        val bytes = hexToBytes(cleanHexPrefix(hexData))
        if (bytes.size < 4) return 0L
        return ByteBuffer.wrap(bytes, 0, 4).order(ByteOrder.LITTLE_ENDIAN).int.toLong() and 0xFFFFFFFFL
    }

    private fun parseHexOrDecimal(str: String): Long {
        val clean = str.trim()
        return if (clean.startsWith("0x") || clean.startsWith("0X")) {
            java.lang.Long.parseUnsignedLong(clean.substring(2), 16)
        } else {
            clean.toLongOrNull() ?: 0L
        }
    }

    private fun cleanHexPrefix(hex: String): String {
        return if (hex.startsWith("0x") || hex.startsWith("0X")) hex.substring(2) else hex
    }

    private fun hexToBytes(hex: String): ByteArray {
        val len = hex.length
        val result = ByteArray(len / 2)
        for (i in 0 until len step 2) {
            val firstDigit = Character.digit(hex[i], 16)
            val secondDigit = Character.digit(hex[i + 1], 16)
            if (firstDigit != -1 && secondDigit != -1) {
                result[i / 2] = ((firstDigit shl 4) + secondDigit).toByte()
            }
        }
        return result
    }

    private fun padTo32Bytes(input: ByteArray): ByteArray {
        val result = ByteArray(32)
        val copyLen = minOf(input.size, 32)
        System.arraycopy(input, 0, result, 0, copyLen)
        return result
    }

    private fun decodeBase58(input: String): ByteArray {
        val ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        var bi = BigInteger.ZERO
        for (char in input) {
            val alphaIndex = ALPHABET.indexOf(char)
            if (alphaIndex != -1) {
                bi = bi.multiply(BigInteger.valueOf(58)).add(BigInteger.valueOf(alphaIndex.toLong()))
            }
        }
        var bytes = bi.toByteArray()
        if (bytes.isNotEmpty() && bytes[0] == 0.toByte()) {
            bytes = bytes.copyOfRange(1, bytes.size)
        }
        var leadingZeros = 0
        for (char in input) {
            if (char == '1') leadingZeros++ else break
        }
        val result = ByteArray(leadingZeros + bytes.size)
        System.arraycopy(bytes, 0, result, leadingZeros, bytes.size)
        return result
    }

    private fun Char.isHexDigit(): Boolean {
        return this in '0'..'9' || this in 'a'..'f' || this in 'A'..'F'
    }
}
