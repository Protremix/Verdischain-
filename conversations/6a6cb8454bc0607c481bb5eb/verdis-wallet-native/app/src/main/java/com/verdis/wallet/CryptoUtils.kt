package com.verdis.wallet

import org.bouncycastle.crypto.digests.KeccakDigest
import org.bouncycastle.crypto.digests.SHA256Digest
import org.bouncycastle.crypto.ec.CustomNamedCurves
import org.bouncycastle.crypto.params.ECDomainParameters
import org.bouncycastle.crypto.params.ECPrivateKeyParameters
import org.bouncycastle.crypto.params.ECPublicKeyParameters
import org.bouncycastle.crypto.signers.ECDSASigner
import org.bouncycastle.crypto.signers.HMacDSAKCalculator
import org.bouncycastle.math.ec.ECPoint
import org.bouncycastle.util.BigIntegers
import java.math.BigInteger
import java.security.SecureRandom

object CryptoUtils {

    private val secp256k1Params = CustomNamedCurves.getByName("secp256k1")
    private val domainParams = ECDomainParameters(
        secp256k1Params.curve,
        secp256k1Params.g,
        secp256k1Params.n,
        secp256k1Params.h
    )

    val bip39Words = listOf(
        "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract",
        "absurd", "abuse", "access", "accident", "account", "accuse", "achieve", "acid",
        "acoustic", "acquire", "across", "action", "actor", "actual", "adapt", "addict",
        "address", "adjust", "admit", "adult", "advance", "advice", "aerobic", "affair",
        "afford", "afraid", "again", "agent", "agree", "ahead", "aim", "air",
        "airport", "aisle", "alarm", "album", "alcohol", "alert", "alien", "allergy",
        "allow", "almost", "alone", "alpha", "already", "also", "alter", "always",
        "amateur", "amazing", "among", "amount", "amused", "analyst", "anchor", "ancient",
        "anger", "angle", "angry", "animal", "ankle", "announce", "annual", "another",
        "answer", "antenna", "antique", "anxiety", "apart", "apology", "appear", "apple",
        "approve", "april", "arch", "arctic", "area", "arena", "argue", "arm",
        "armed", "armor", "army", "around", "arrange", "arrest", "arrive", "arrow",
        "art", "artefact", "artist", "artwork", "ask", "aspect", "assault", "asset",
        "assist", "assume", "asthma", "athlete", "atom", "attack", "attend", "attitude",
        "attract", "auction", "audit", "august", "aunt", "author", "auto", "autumn",
        "avenue", "average", "avoid", "awake", "aware", "away", "awesome", "awful",
        "awkward", "axis", "baby", "bachelor", "bacon", "badge", "bag", "balance",
        "balcony", "ball", "bamboo", "banana", "banner", "bar", "barely", "bargain",
        "barrel", "base", "basic", "basket", "battle", "beach", "bean", "beauty",
        "because", "become", "beef", "before", "begin", "behave", "behind", "believe",
        "below", "belt", "bench", "benefit", "best", "betray", "better", "between",
        "beyond", "bicycle", "bid", "bike", "bind", "biology", "bird", "birth",
        "bitter", "black", "blade", "blame", "blanket", "blast", "bleak", "bless",
        "blind", "blood", "blossom", "blouse", "blue", "blur", "blush", "board",
        "boat", "body", "boil", "bomb", "bone", "bonus", "book", "boost",
        "border", "boring", "borrow", "boss", "bottom", "bounce", "box", "boy",
        "bracket", "brain", "brand", "brass", "brave", "bread", "breeze", "brick",
        "bridge", "brief", "bright", "bring", "brisk", "broccoli", "broken", "bronze",
        "broom", "brother", "brown", "brush", "bubble", "buddy", "budget", "buffalo",
        "build", "bulb", "bulk", "bullet", "bundle", "bunker", "burden", "burger",
        "burst", "bus", "business", "busy", "butter", "buyer", "buzz", "cabbage",
        "cabin", "cable", "cactus", "cage", "cake", "call", "calm", "camera",
        "camp", "can", "canal", "cancel", "candy", "cannon", "canoe", "canvas"
    )

    fun generatePrivateKey(): ByteArray {
        val secureRandom = SecureRandom()
        val n = domainParams.n
        var privKey: BigInteger
        do {
            val bytes = ByteArray(32)
            secureRandom.nextBytes(bytes)
            privKey = BigInteger(1, bytes)
        } while (privKey <= BigInteger.ZERO || privKey >= n)
        return BigIntegers.asUnsignedByteArray(32, privKey)
    }

    fun derivePublicKey(privateKey: ByteArray): ByteArray {
        val privKey = BigInteger(1, privateKey)
        val pubPoint: ECPoint = domainParams.g.multiply(privKey).normalize()
        return pubPoint.getEncoded(false) // 65 bytes uncompressed: 0x04 + 32-byte X + 32-byte Y
    }

    fun deriveAddress(publicKey: ByteArray): String {
        val pubKeyNoPrefix = if (publicKey.size == 65 && publicKey[0] == 4.toByte()) {
            publicKey.copyOfRange(1, 65)
        } else {
            publicKey
        }

        val hash = keccak256(pubKeyNoPrefix)
        val addressBytes = hash.copyOfRange(12, 32)
        val rawAddressHex = toHex(addressBytes)

        val hashOfAddress = keccak256(rawAddressHex.toByteArray(Charsets.US_ASCII))
        val result = StringBuilder(40)

        for (i in 0 until 40) {
            val c = rawAddressHex[i]
            if (c in 'a'..'f') {
                val byteVal = hashOfAddress[i / 2].toInt() and 0xFF
                val nibble = if (i % 2 == 0) (byteVal ushr 4) else (byteVal and 0x0F)
                if (nibble >= 8) {
                    result.append(c.uppercaseChar())
                } else {
                    result.append(c)
                }
            } else {
                result.append(c)
            }
        }

        return "0x$result"
    }

    fun toHex(bytes: ByteArray): String {
        val sb = StringBuilder(bytes.size * 2)
        for (b in bytes) {
            sb.append(String.format("%02x", b.toInt() and 0xFF))
        }
        return sb.toString()
    }

    fun hexToBytes(hex: String): ByteArray {
        val clean = hex.removePrefix("0x").removePrefix("0X")
        val formatted = if (clean.length % 2 != 0) "0$clean" else clean
        val len = formatted.length
        val data = ByteArray(len / 2)
        var i = 0
        while (i < len) {
            data[i / 2] = ((Character.digit(formatted[i], 16) shl 4) +
                    Character.digit(formatted[i + 1], 16)).toByte()
            i += 2
        }
        return data
    }

    fun privateKeyFromHex(hex: String): ByteArray {
        val clean = hex.removePrefix("0x").removePrefix("0X").padStart(64, '0')
        val bytes = hexToBytes(clean)
        return if (bytes.size > 32) bytes.copyOfRange(bytes.size - 32, bytes.size) else bytes
    }

    fun sha256(data: ByteArray): ByteArray {
        val digest = SHA256Digest()
        digest.update(data, 0, data.size)
        val out = ByteArray(digest.digestSize)
        digest.doFinal(out, 0)
        return out
    }

    fun keccak256(data: ByteArray): ByteArray {
        val digest = KeccakDigest(256)
        digest.update(data, 0, data.size)
        val out = ByteArray(digest.digestSize)
        digest.doFinal(out, 0)
        return out
    }

    fun sign(privateKey: ByteArray, data: ByteArray): ByteArray {
        val privKey = BigInteger(1, privateKey)
        val signer = ECDSASigner(HMacDSAKCalculator(SHA256Digest()))
        signer.init(true, ECPrivateKeyParameters(privKey, domainParams))

        val hash = keccak256(data)
        val components = signer.generateSignature(hash)
        val r = components[0]
        var s = components[1]

        val halfN = domainParams.n.shiftRight(1)
        if (s > halfN) {
            s = domainParams.n.subtract(s)
        }

        val rBytes = BigIntegers.asUnsignedByteArray(32, r)
        val sBytes = BigIntegers.asUnsignedByteArray(32, s)
        return rBytes + sBytes
    }

    fun signMessage(privateKey: ByteArray, message: String): String {
        val sig = sign(privateKey, message.toByteArray(Charsets.UTF_8))
        return "0x" + toHex(sig)
    }

    fun verifySignature(publicKey: ByteArray, signature: ByteArray, data: ByteArray): Boolean {
        if (signature.size != 64) return false
        return try {
            val r = BigInteger(1, signature.copyOfRange(0, 32))
            val s = BigInteger(1, signature.copyOfRange(32, 64))

            val pubKeyBytes = when {
                publicKey.size == 64 -> byteArrayOf(0x04.toByte()) + publicKey
                else -> publicKey
            }

            val point = domainParams.curve.decodePoint(pubKeyBytes)
            val pubKeyParams = ECPublicKeyParameters(point, domainParams)

            val signer = ECDSASigner()
            signer.init(false, pubKeyParams)

            val hash = keccak256(data)
            signer.verifySignature(hash, r, s)
        } catch (e: Exception) {
            false
        }
    }

    fun generateSeedPhrase(): String {
        val random = SecureRandom()
        val words = mutableListOf<String>()
        for (i in 0 until 12) {
            val index = random.nextInt(bip39Words.size)
            words.add(bip39Words[index])
        }
        return words.joinToString(" ")
    }

    fun seedToPrivateKey(seed: String): ByteArray {
        val normalized = seed.trim().lowercase().replace("\\s+".toRegex(), " ")
        return sha256(normalized.toByteArray(Charsets.UTF_8))
    }
}
