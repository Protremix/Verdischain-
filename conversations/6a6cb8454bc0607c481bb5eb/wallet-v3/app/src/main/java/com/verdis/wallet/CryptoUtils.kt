package com.verdis.wallet

import org.bouncycastle.crypto.digests.KeccakDigest
import org.bouncycastle.crypto.params.ECDomainParameters
import org.bouncycastle.crypto.params.ECPrivateKeyParameters
import org.bouncycastle.crypto.params.ECPublicKeyParameters
import org.bouncycastle.crypto.signers.ECDSASigner
import org.bouncycastle.crypto.ec.CustomNamedCurves
import org.bouncycastle.math.ec.ECPoint
import java.math.BigInteger
import java.security.MessageDigest
import java.security.SecureRandom

object CryptoUtils {
    private val random = SecureRandom()
    private val curve by lazy { CustomNamedCurves.getByName("secp256k1") }
    private val domain by lazy { ECDomainParameters(curve.curve, curve.g, curve.n, curve.h) }

    fun generatePrivateKey(): ByteArray {
        val n = domain.n
        var k: BigInteger
        do {
            val b = ByteArray(32)
            random.nextBytes(b)
            k = BigInteger(1, b)
        } while (k <= BigInteger.ZERO || k >= n)
        val bytes = k.toByteArray()
        return if (bytes.size > 32) bytes.copyOfRange(bytes.size - 32, bytes.size) else bytes
    }

    fun derivePublicKey(privKey: ByteArray): ByteArray {
        val k = BigInteger(1, privKey)
        val pt: ECPoint = domain.g.multiply(k).normalize()
        return pt.getEncoded(false)
    }

    fun deriveAddress(pubKey: ByteArray): String {
        val raw = if (pubKey.size == 65 && pubKey[0] == 4.toByte()) pubKey.copyOfRange(1, 65) else pubKey
        val hash = keccak256(raw)
        val addr = toHex(hash.copyOfRange(12, 32))
        return "0x" + checksumAddress(addr)
    }

    private fun checksumAddress(addr: String): String {
        val hashHex = toHex(keccak256(addr.toByteArray(Charsets.US_ASCII)))
        val sb = StringBuilder(40)
        for (i in 0 until 40) {
            val c = addr[i]
            if (c in 'a'..'f') {
                val byteVal = Character.digit(hashHex[i / 2], 16) and 0xFF
                val nibble = if (i % 2 == 0) (byteVal ushr 4) else (byteVal and 0x0F)
                sb.append(if (nibble >= 8) c.uppercaseChar() else c)
            } else {
                sb.append(c)
            }
        }
        return sb.toString()
    }

    fun keccak256(input: ByteArray): ByteArray {
        val digest = KeccakDigest(256)
        digest.update(input, 0, input.size)
        val out = ByteArray(32)
        digest.doFinal(out, 0)
        return out
    }

    fun sha256(input: ByteArray): ByteArray {
        return MessageDigest.getInstance("SHA-256").digest(input)
    }

    fun toHex(bytes: ByteArray): String = bytes.joinToString("") { "%02x".format(it) }
    fun privateKeyFromHex(hex: String): ByteArray = BigInteger(hex, 16).toByteArray().let { if (it.size > 32) it.copyOfRange(it.size - 32, it.size) else it }

    fun generateSeedPhrase(): String {
        val words = listOf("green", "forest", "carbon", "leaf", "earth", "ocean", "solar", "wind", "rain", "tree", "seed", "bloom", "spring", "river", "mountain", "valley", "harvest", "meadow", "energy", "clean", "future", "nature", "planet", "growth")
        val sb = StringBuilder()
        for (i in 0 until 12) {
            if (i > 0) sb.append(" ")
            val idx = BigInteger(32, random).mod(BigInteger(words.size.toString())).toInt()
            sb.append(words[idx])
        }
        return sb.toString()
    }

    fun signMessage(privateKey: ByteArray, message: ByteArray): ByteArray {
        val hash = keccak256(message)
        val signer = ECDSASigner()
        signer.init(true, ECPrivateKeyParameters(BigInteger(1, privateKey), domain))
        val sig = signer.generateSignature(hash)
        val r = sig[0].toByteArray()
        val s = sig[1].toByteArray()
        val rBytes = if (r.size > 32) r.copyOfRange(r.size - 32, r.size) else ByteArray(32 - r.size) + r
        val sBytes = if (s.size > 32) s.copyOfRange(s.size - 32, s.size) else ByteArray(32 - s.size) + s
        return rBytes + sBytes
    }
}
