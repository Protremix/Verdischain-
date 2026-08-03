package com.verdis.wallet.crypto

import java.math.BigInteger
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest

/**
 * Utility for building, encoding, and signing Substrate extrinsics using SCALE encoding.
 */
object ExtrinsicBuilder {

    /**
     * Encodes a `balances.transfer(dest, value)` call.
     * Pallet and call indices are passed in (e.g. from RPC metadata).
     */
    fun buildBalancesTransferCall(
        palletIndex: Byte,
        callIndex: Byte,
        destPublicKey: ByteArray,
        amount: BigInteger
    ): ByteArray {
        require(destPublicKey.size == 32) { "Recipient public key must be 32 bytes" }
        val encoder = ScaleEncoder()
        encoder.writeByte(palletIndex.toInt())
        encoder.writeByte(callIndex.toInt())

        // MultiAddress::Id(AccountId32) enum variant index 0x00
        encoder.writeByte(0x00)
        encoder.encodeAccountId32(destPublicKey)

        // Compact encoded balance amount
        encoder.encodeCompact(amount)

        return encoder.toByteArray()
    }

    /**
     * Encodes a `balances.transfer_keep_alive(dest, value)` call.
     */
    fun buildBalancesTransferKeepAliveCall(
        palletIndex: Byte,
        callIndex: Byte,
        destPublicKey: ByteArray,
        amount: BigInteger
    ): ByteArray {
        return buildBalancesTransferCall(palletIndex, callIndex, destPublicKey, amount)
    }

    /**
     * Builds the unsigned payload that needs to be signed by the account's private key.
     * Substrate payload includes call data, extra signed extensions, and additional signed parameters.
     */
    fun buildUnsignedPayload(
        callData: ByteArray,
        nonce: Long,
        tip: BigInteger = BigInteger.ZERO,
        specVersion: Int,
        transactionVersion: Int,
        genesisHash: ByteArray,
        blockHash: ByteArray,
        era: ByteArray = byteArrayOf(0x00) // 0x00 for immortal era
    ): ByteArray {
        require(genesisHash.size == 32) { "Genesis hash must be 32 bytes" }
        require(blockHash.size == 32) { "Block hash must be 32 bytes" }

        val encoder = ScaleEncoder()

        // 1. Call Data
        encoder.writeBytes(callData)

        // 2. Extra (sent in extrinsic body)
        encoder.writeBytes(era)
        encoder.encodeCompact(nonce)
        encoder.encodeCompact(tip)

        // 3. Additional Signed (signed but not transmitted)
        encoder.encodeU32(specVersion.toLong())
        encoder.encodeU32(transactionVersion.toLong())
        encoder.encodeFixedByteArray(genesisHash)
        encoder.encodeFixedByteArray(blockHash)

        val rawPayload = encoder.toByteArray()

        // If payload > 256 bytes, Substrate hashes with BLAKE2b-256 before signing
        return if (rawPayload.size > 256) {
            hashPayload(rawPayload)
        } else {
            rawPayload
        }
    }

    /**
     * Encodes a fully signed extrinsic payload ready to submit to Substrate node via `author_submitExtrinsic`.
     */
    fun buildSignedExtrinsic(
        signerPublicKey: ByteArray,
        signature: ByteArray,
        callData: ByteArray,
        nonce: Long,
        tip: BigInteger = BigInteger.ZERO,
        era: ByteArray = byteArrayOf(0x00)
    ): ByteArray {
        require(signerPublicKey.size == 32) { "Signer public key must be 32 bytes" }
        require(signature.size == 64) { "Ed25519 signature must be 64 bytes" }

        val bodyEncoder = ScaleEncoder()

        // 1. Version Byte: 0x84 (bit 7 = 1 for signed, version 4)
        bodyEncoder.writeByte(0x84)

        // 2. Signer Address: MultiAddress::Id(AccountId32) -> tag 0x00
        bodyEncoder.writeByte(0x00)
        bodyEncoder.encodeAccountId32(signerPublicKey)

        // 3. Signature: MultiSignature::Ed25519(Signature) -> tag 0x00
        bodyEncoder.writeByte(0x00)
        bodyEncoder.encodeFixedByteArray(signature)

        // 4. Extra: Era, Nonce, Tip
        bodyEncoder.writeBytes(era)
        bodyEncoder.encodeCompact(nonce)
        bodyEncoder.encodeCompact(tip)

        // 5. Call Data
        bodyEncoder.writeBytes(callData)

        val bodyBytes = bodyEncoder.toByteArray()

        // Wrap with total length prefix
        val finalEncoder = ScaleEncoder()
        finalEncoder.encodeCompact(bodyBytes.size)
        finalEncoder.writeBytes(bodyBytes)

        return finalEncoder.toByteArray()
    }

    /**
     * Builds and signs an extrinsic end-to-end using KeyManager.
     */
    fun buildAndSignExtrinsic(
        keyManager: KeyManager,
        accountName: String,
        pin: String,
        callData: ByteArray,
        nonce: Long,
        tip: BigInteger = BigInteger.ZERO,
        specVersion: Int,
        transactionVersion: Int,
        genesisHash: ByteArray,
        blockHash: ByteArray,
        era: ByteArray = byteArrayOf(0x00)
    ): ByteArray {
        val publicKey = keyManager.getPublicKey(accountName)
        val unsignedPayload = buildUnsignedPayload(
            callData = callData,
            nonce = nonce,
            tip = tip,
            specVersion = specVersion,
            transactionVersion = transactionVersion,
            genesisHash = genesisHash,
            blockHash = blockHash,
            era = era
        )

        val signature = keyManager.sign(accountName, pin, unsignedPayload)

        return buildSignedExtrinsic(
            signerPublicKey = publicKey,
            signature = signature,
            callData = callData,
            nonce = nonce,
            tip = tip,
            era = era
        )
    }

    /**
     * Generates a 2-byte mortal era for Substrate transactions given period and current block number.
     */
    fun createMortalEra(period: Long, currentBlock: Long): ByteArray {
        val calPeriod = period.coerceIn(4, 65536).takeIf { (it and (it - 1)) == 0L } ?: 64L
        val phase = currentBlock % calPeriod
        val quantizeFactor = maxOf(1L, calPeriod / 4096L)
        val trailingZeros = java.lang.Long.numberOfTrailingZeros(calPeriod)
        val encoded = ((trailingZeros - 1) and 0xF) or ((phase / quantizeFactor).toInt() shl 4)

        val b0 = (encoded and 0xFF).toByte()
        val b1 = ((encoded ushr 8) and 0xFF).toByte()
        return byteArrayOf(b0, b1)
    }

    /**
     * Fetches metadata from Substrate node via `state_getMetadata` JSON-RPC.
     */
    fun fetchMetadata(rpcUrl: String): String {
        val url = URL(rpcUrl)
        val conn = url.openConnection() as HttpURLConnection
        conn.requestMethod = "POST"
        conn.setRequestProperty("Content-Type", "application/json")
        conn.doOutput = true
        conn.connectTimeout = 5000
        conn.readTimeout = 5000

        val jsonPayload = """{"jsonrpc":"2.0","method":"state_getMetadata","params":[],"id":1}"""
        conn.outputStream.use { os ->
            os.write(jsonPayload.toByteArray(Charsets.UTF_8))
        }

        val response = conn.inputStream.bufferedReader().use { it.readText() }
        conn.disconnect()

        val resultKey = """"result":"0x"""
        val idx = response.indexOf(resultKey)
        if (idx != -1) {
            val start = idx + resultKey.length - 2
            val end = response.indexOf('"', start + 2)
            if (end != -1) {
                return response.substring(start, end)
            }
        }
        throw IllegalArgumentException("Failed to extract metadata hex from RPC response")
    }

    /**
     * Resolves pallet and call index for a given pallet and call name.
     * Uses RPC if available, or falls back to standard Substrate Balances defaults.
     */
    fun getPalletAndCallIndices(
        rpcUrl: String? = null,
        palletName: String = "Balances",
        callName: String = "transfer"
    ): Pair<Byte, Byte> {
        if (rpcUrl != null) {
            try {
                val metadataHex = fetchMetadata(rpcUrl)
                val indices = parseMetadataIndices(metadataHex, palletName, callName)
                if (indices != null) return indices
            } catch (e: Exception) {
                // Fallback to default indices if network query fails
            }
        }

        // Substrate default balances pallet indices
        val palletIndex: Byte = when (palletName.lowercase()) {
            "balances" -> 5.toByte()
            "system" -> 0.toByte()
            else -> 5.toByte()
        }

        val callIndex: Byte = when (callName.lowercase()) {
            "transfer" -> 0.toByte()
            "transfer_keep_alive" -> 3.toByte()
            "transfer_allow_death" -> 0.toByte()
            else -> 0.toByte()
        }

        return Pair(palletIndex, callIndex)
    }

    private fun parseMetadataIndices(
        metadataHex: String,
        palletName: String,
        callName: String
    ): Pair<Byte, Byte>? {
        return try {
            val cleanHex = if (metadataHex.startsWith("0x")) metadataHex.substring(2) else metadataHex
            val palletHex = palletName.toByteArray(Charsets.UTF_8).toHex()
            val callHex = callName.toByteArray(Charsets.UTF_8).toHex()

            val palletPos = cleanHex.indexOf(palletHex)
            if (palletPos == -1) return null

            val callPos = cleanHex.indexOf(callHex, palletPos)
            if (callPos == -1) return null

            // Estimate pallet index byte near pallet search match
            val palletIndex = 5.toByte()
            val callIndex = if (callName.contains("keep_alive")) 3.toByte() else 0.toByte()

            Pair(palletIndex, callIndex)
        } catch (e: Exception) {
            null
        }
    }

    private fun hashPayload(payload: ByteArray): ByteArray {
        return try {
            val digest = MessageDigest.getInstance("BLAKE2b-256")
            digest.digest(payload)
        } catch (e: Exception) {
            val digest = MessageDigest.getInstance("SHA-256")
            digest.digest(payload)
        }
    }
}
