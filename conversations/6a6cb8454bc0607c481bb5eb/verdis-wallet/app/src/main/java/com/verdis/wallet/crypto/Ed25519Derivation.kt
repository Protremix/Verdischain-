package com.verdis.wallet.crypto

import java.math.BigInteger
import java.security.MessageDigest

/**
 * Minimal Ed25519 implementation for public key derivation from a 32-byte seed.
 * Uses the standard Ed25519 curve (Curve25519 / Edwards form).
 */
object Ed25519Derivation {

    // Field prime: p = 2^255 - 19
    private val P = BigInteger("57896044618658097711785492504343953926634992332820282019728792003956563505853")

    // Group order: L = 2^252 + 27742317777372353535851937790883648493
    private val L = BigInteger("7237005577332262213973186563042994240857116359379907606001950938285454250989")

    // d = -121665 / 121666 mod p
    private val D: BigInteger

    // Base point B (y-coordinate first, then x-coordinate for Edwards form)
    // B_y = 4/5 mod p
    private val B_Y: BigInteger
    private val B_X: BigInteger

    // I = sqrt(-1) mod p
    private val I: BigInteger

    init {
        // d = -121665 * inverse(121666) mod p
        D = BigInteger.valueOf(-121665).multiply(BigInteger.valueOf(121666).modInverse(P)).mod(P)

        // B_y = 4 * inverse(5) mod p
        B_Y = BigInteger.valueOf(4).multiply(BigInteger.valueOf(5).modInverse(P)).mod(P)

        // B_x = recover_x(B_y, sign_bit=0)
        B_X = recoverX(B_Y, false)

        // I = sqrt(-1) mod p
        // p ≡ 5 (mod 8), so sqrt(-1) = 2^((p-1)/4) mod p
        I = BigInteger.valueOf(2).modPow(P.subtract(BigInteger.ONE).divide(BigInteger.valueOf(4)), P)
    }

    /**
     * Derives the 32-byte Ed25519 public key from a 32-byte seed.
     */
    fun derivePublicKey(seed: ByteArray): ByteArray {
        require(seed.size == 32) { "Seed must be 32 bytes" }

        // 1. h = SHA-512(seed)
        val h = MessageDigest.getInstance("SHA-512").digest(seed)

        // 2. Clamp the lower 32 bytes to get scalar a
        val aBytes = h.copyOfRange(0, 32)
        aBytes[0] = (aBytes[0] and 0xF8.toByte()) // clear bits 0,1,2
        aBytes[31] = (aBytes[31] and 0x7F.toByte()) // clear bit 255
        aBytes[31] = (aBytes[31] or 0x40.toByte())  // set bit 254

        // Convert to BigInteger (little-endian)
        val a = leBytesToBigInteger(aBytes)

        // 3. Compute A = a * B (scalar multiplication of base point)
        val pointA = scalarMult(a, B_X, B_Y)

        // 4. Encode the point as the public key (compressed)
        return encodePoint(pointA.first, pointA.second)
    }

    // --- Ed25519 Curve Arithmetic ---

    /**
     * Point addition on the Edwards curve: x3 = (x1y2 + x2y1)/(1 + d x1x2y1y2)
     * y3 = (y1y2 + x1x2)/(1 - d x1x2y1y2)
     */
    private fun edwardsAdd(
        x1: BigInteger, y1: BigInteger,
        x2: BigInteger, y2: BigInteger
    ): Pair<BigInteger, BigInteger> {
        val x1y2 = x1.multiply(y2).mod(P)
        val x2y1 = x2.multiply(y1).mod(P)
        val y1y2 = y1.multiply(y2).mod(P)
        val x1x2 = x1.multiply(x2).mod(P)

        val dProduct = D.multiply(x1x2).multiply(y1y2).mod(P)

        val x3Num = x1y2.add(x2y1).mod(P)
        val x3Den = BigInteger.ONE.add(dProduct).mod(P)
        val x3 = x3Num.multiply(x3Den.modInverse(P)).mod(P)

        val y3Num = y1y2.add(x1x2).mod(P)
        val y3Den = BigInteger.ONE.subtract(dProduct).mod(P)
        val y3 = y3Num.multiply(y3Den.modInverse(P)).mod(P)

        return Pair(x3, y)
    }

    /**
     * Scalar multiplication using double-and-add.
     */
    private fun scalarMult(
        scalar: BigInteger,
        px: BigInteger, py: BigInteger
    ): Pair<BigInteger, BigInteger> {
        var resultX = BigInteger.ZERO
        var resultY = BigInteger.ONE // Identity point (0, 1)
        var addendX = px
        var addendY = py

        var s = scalar
        while (s > BigInteger.ZERO) {
            if (s.testBit(0)) {
                val (nx, ny) = edwardsAdd(resultX, resultY, addendX, addendY)
                resultX = nx
                resultY = ny
            }
            val (dx, dy) = edwardsAdd(addendX, addendY, addendX, addendY)
            addendX = dx
            addendY = dy
            s = s.shiftRight(1)
        }

        return Pair(resultX, resultY)
    }

    /**
     * Encodes a point (x, y) as the 32-byte compressed Ed25519 public key.
     * Format: little-endian y-coordinate with the high bit of the last byte set to the sign of x.
     */
    private fun encodePoint(x: BigInteger, y: BigInteger): ByteArray {
        val yBytes = bigIntegerToLeBytes(y, 32)
        // Set the sign bit (bit 255) based on the parity of x
        val xParity = x.and(BigInteger.ONE).toInt()
        if (xParity != 0) {
            yBytes[31] = (yBytes[31].toInt() or 0x80).toByte()
        }
        return yBytes
    }

    /**
     * Recovers the x-coordinate from y and the sign bit.
     * x^2 = (y^2 - 1) / (d * y^2 + 1) mod p
     */
    private fun recoverX(y: BigInteger, signBit: Boolean): BigInteger {
        val y2 = y.multiply(y).mod(P)
        val num = y2.subtract(BigInteger.ONE).mod(P)
        val den = D.multiply(y2).add(BigInteger.ONE).mod(P)

        // x^2 = num / den = num * den^((p-3)/4) mod p (since p ≡ 5 mod 8)
        val exp = P.subtract(BigInteger.valueOf(3)).divide(BigInteger.valueOf(4))
        var x = num.multiply(den.modPow(exp, P)).mod(P)

        // Check: x^2 should equal num/den
        if (!x.multiply(x).mod(P).equals(num.multiply(den.modInverse(P)).mod(P))) {
            // Try multiplying by I (sqrt(-1))
            x = x.multiply(I).mod(P)
        }

        // Adjust sign
        val desiredParity = if (signBit) 1 else 0
        if (x.and(BigInteger.ONE).toInt() != desiredParity) {
            x = P.subtract(x).mod(P)
        }

        return x
    }

    // --- Byte conversion helpers ---

    private fun leBytesToBigInteger(bytes: ByteArray): BigInteger {
        // Little-endian to BigInteger
        val reversed = bytes.reversedArray()
        return BigInteger(1, reversed)
    }

    private fun bigIntegerToLeBytes(value: BigInteger, length: Int): ByteArray {
        // BigInteger to little-endian bytes of fixed length
        val bigEndian = value.toByteArray()
        // Remove leading zero if present
        val trimmed = if (bigEndian.size > length && bigEndian[0] == 0.toByte()) {
            bigEndian.copyOfRange(1, bigEndian.size)
        } else {
            bigEndian
        }
        val result = ByteArray(length)
        val reversed = trimmed.reversedArray()
        val copyLen = minOf(reversed.size, length)
        System.arraycopy(reversed, 0, result, 0, copyLen)
        return result
    }
}
