package com.verdis.wallet

import android.content.Context
import android.util.Base64
import org.bouncycastle.crypto.params.ECPrivateKeyParameters
import org.bouncycastle.crypto.params.ECPublicKeyParameters
import org.bouncycastle.crypto.signers.ECDSASigner
import org.bouncycastle.crypto.generators.ECKeyPairGenerator
import org.bouncycastle.crypto.params.ECKeyGenerationParameters
import org.bouncycastle.crypto.ec.CustomNamedCurves
import org.bouncycastle.crypto.digests.KeccakDigest
import org.bouncycastle.crypto.digests.SHA256Digest
import org.bouncycastle.math.ec.ECPoint
import org.bouncycastle.util.BigIntegers
import java.math.BigInteger
import java.security.SecureRandom
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.SecretKeySpec
import javax.crypto.spec.IvParameterSpec

object CryptoUtils {
    private val secp256k1Params = CustomNamedCurves.getByName("secp256k1")
    private val domainParams = org.bouncycastle.crypto.params.ECDomainParameters(
        secp256k1Params.curve, secp256k1Params.g, secp256k1Params.n, secp256k1Params.h
    )

    fun generatePrivateKey(): ByteArray {
        val gen = ECKeyPairGenerator()
        val secureRandom = SecureRandom()
        gen.init(ECKeyGenerationParameters(domainParams, secureRandom))
        val keyPair = gen.generateKeyPair()
        return (keyPair.private as ECPrivateKeyParameters).d.toByteArray().let {
            if (it.size == 33 && it[0] == 0.toByte()) it.copyOfRange(1, 33) else it
        }
    }

    fun privateKeyFromHex(hex: String): ByteArray {
        val clean = if (hex.startsWith("0x")) hex.substring(2) else hex
        return ByteArray(clean.length / 2) { i ->
            ((clean[i * 2].digitValueOrNull() ?: 0) * 16 + (clean[i * 2 + 1].digitValueOrNull() ?: 0)).toByte()
        }
    }

    fun toHex(bytes: ByteArray): String {
        return bytes.joinToString("") { "%02x".format(it) }
    }

    fun derivePublicKey(privateKeyBytes: ByteArray): ByteArray {
        val privKey = BigInteger(1, privateKeyBytes)
        val pubPoint: ECPoint = domainParams.g.multiply(privKey)
        return pubPoint.getEncoded(false) // uncompressed point
    }

    fun deriveAddress(publicKeyBytes: ByteArray): String {
        // For uncompressed: first byte is 0x04, skip it
        val xy = if (publicKeyBytes[0] == 4.toByte()) publicKeyBytes.copyOfRange(1, publicKeyBytes.size) else publicKeyBytes
        
        // Keccak-256 hash
        val digest = KeccakDigest(256)
        digest.update(xy, 0, xy.size)
        val hash = ByteArray(32)
        digest.doFinal(hash, 0)
        
        // Last 20 bytes = address
        val addressBytes = hash.copyOfRange(12, 32)
        return "0x" + toHex(addressBytes)
    }

    fun keccak256(data: ByteArray): ByteArray {
        val digest = KeccakDigest(256)
        digest.update(data, 0, data.size)
        val out = ByteArray(32)
        digest.doFinal(out, 0)
        return out
    }

    fun sha256(data: ByteArray): ByteArray {
        val digest = SHA256Digest()
        digest.update(data, 0, data.size)
        val out = ByteArray(32)
        digest.doFinal(out, 0)
        return out
    }

    fun sign(privateKeyBytes: ByteArray, data: ByteArray): ByteArray {
        val privKey = BigInteger(1, privateKeyBytes)
        val signer = ECDSASigner()
        signer.init(true, ECPrivateKeyParameters(privKey, domainParams))
        val hash = keccak256(data)
        val sig = signer.generateSignature(hash)
        val r = sig[0] as BigInteger
        val s = sig[1] as BigInteger
        // Normalize s to low-S
        val n = domainParams.n
        val sNorm = if (s > n.divide(BigInteger.valueOf(2))) n.subtract(s) else s
        // Encode as r || s (64 bytes)
        val rBytes = BigIntegers.asUnsignedByteArray(32, r)
        val sBytes = BigIntegers.asUnsignedByteArray(32, sNorm)
        return rBytes + sBytes
    }
}

// Extension for hex char to int
private fun Char.digitValueOrNull(): Int? = when (this) {
    in '0'..'9' -> this - '0'
    in 'a'..'f' -> this - 'a' + 10
    in 'A'..'F' -> this - 'A' + 10
    else -> null
}
