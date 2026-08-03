package com.verdis.wallet.crypto

import java.io.ByteArrayOutputStream
import java.math.BigInteger

/**
 * Result representation for SCALE codec decoding.
 */
sealed class ScaleResult<out T, out E> {
    data class Ok<out T>(val value: T) : ScaleResult<T, Nothing>()
    data class Err<out E>(val value: E) : ScaleResult<Nothing, E>()

    val isOk: Boolean get() = this is Ok
    val isErr: Boolean get() = this is Err

    fun getOrNull(): T? = (this as? Ok)?.value
    fun errorOrNull(): E? = (this as? Err)?.value
}

/**
 * 4-element tuple for SCALE codec.
 */
data class ScaleTuple4<A, B, C, D>(
    val first: A,
    val second: B,
    val third: C,
    val fourth: D
)

/**
 * SCALE Encoder for Substrate data types.
 */
class ScaleEncoder {
    private val outputStream = ByteArrayOutputStream()

    fun writeByte(b: Int) {
        outputStream.write(b and 0xFF)
    }

    fun writeBytes(bytes: ByteArray) {
        outputStream.write(bytes)
    }

    fun encodeBoolean(value: Boolean) {
        writeByte(if (value) 1 else 0)
    }

    fun encodeCompact(value: Long) {
        encodeCompact(BigInteger.valueOf(value))
    }

    fun encodeCompact(value: Int) {
        encodeCompact(BigInteger.valueOf(value.toLong()))
    }

    fun encodeCompact(value: BigInteger) {
        require(value >= BigInteger.ZERO) { "Compact integer must be non-negative" }
        if (value < BigInteger.valueOf(64)) {
            writeByte((value.toInt() shl 2) or 0b00)
        } else if (value < BigInteger.valueOf(16384)) {
            val v = (value.toInt() shl 2) or 0b01
            writeByte(v and 0xFF)
            writeByte((v ushr 8) and 0xFF)
        } else if (value < BigInteger.valueOf(1073741824)) { // 2^30
            val v = (value.toLong() shl 2) or 0b10
            writeByte((v and 0xFF).toInt())
            writeByte(((v ushr 8) and 0xFF).toInt())
            writeByte(((v ushr 16) and 0xFF).toInt())
            writeByte(((v ushr 24) and 0xFF).toInt())
        } else {
            var bytes = value.toByteArray()
            if (bytes.size > 1 && bytes[0] == 0.toByte()) {
                bytes = bytes.copyOfRange(1, bytes.size)
            }
            val leBytes = bytes.reversedArray()
            val numBytes = leBytes.size
            require(numBytes >= 4) { "BigInteger byte count must be at least 4" }
            val header = ((numBytes - 4) shl 2) or 0b11
            writeByte(header)
            writeBytes(leBytes)
        }
    }

    fun encodeU8(value: Int) {
        writeByte(value)
    }

    fun encodeU16(value: Int) {
        writeByte(value and 0xFF)
        writeByte((value ushr 8) and 0xFF)
    }

    fun encodeU32(value: Long) {
        writeByte((value and 0xFF).toInt())
        writeByte(((value ushr 8) and 0xFF).toInt())
        writeByte(((value ushr 16) and 0xFF).toInt())
        writeByte(((value ushr 24) and 0xFF).toInt())
    }

    fun encodeU64(value: BigInteger) {
        val bytes = valueToFixedLittleEndian(value, 8)
        writeBytes(bytes)
    }

    fun encodeU64(value: Long) {
        for (i in 0 until 8) {
            writeByte(((value ushr (i * 8)) and 0xFF).toInt())
        }
    }

    fun encodeU128(value: BigInteger) {
        val bytes = valueToFixedLittleEndian(value, 16)
        writeBytes(bytes)
    }

    fun encodeByteArray(bytes: ByteArray) {
        encodeCompact(bytes.size)
        writeBytes(bytes)
    }

    fun encodeFixedByteArray(bytes: ByteArray) {
        writeBytes(bytes)
    }

    fun encodeString(value: String) {
        encodeByteArray(value.toByteArray(Charsets.UTF_8))
    }

    fun <T> encodeOption(value: T?, encoder: (ScaleEncoder, T) -> Unit) {
        if (value == null) {
            writeByte(0x00)
        } else {
            writeByte(0x01)
            encoder(this, value)
        }
    }

    fun <T, E> encodeResult(
        result: ScaleResult<T, E>,
        okEncoder: (ScaleEncoder, T) -> Unit,
        errEncoder: (ScaleEncoder, E) -> Unit
    ) {
        when (result) {
            is ScaleResult.Ok -> {
                writeByte(0x00)
                okEncoder(this, result.value)
            }
            is ScaleResult.Err -> {
                writeByte(0x01)
                errEncoder(this, result.value)
            }
        }
    }

    fun <T> encodeList(list: List<T>, encoder: (ScaleEncoder, T) -> Unit) {
        encodeCompact(list.size)
        for (item in list) {
            encoder(this, item)
        }
    }

    fun <A, B> encodeTuple2(
        tuple: Pair<A, B>,
        encA: (ScaleEncoder, A) -> Unit,
        encB: (ScaleEncoder, B) -> Unit
    ) {
        encA(this, tuple.first)
        encB(this, tuple.second)
    }

    fun <A, B, C> encodeTuple3(
        tuple: Triple<A, B, C>,
        encA: (ScaleEncoder, A) -> Unit,
        encB: (ScaleEncoder, B) -> Unit,
        encC: (ScaleEncoder, C) -> Unit
    ) {
        encA(this, tuple.first)
        encB(this, tuple.second)
        encC(this, tuple.third)
    }

    fun <A, B, C, D> encodeTuple4(
        tuple: ScaleTuple4<A, B, C, D>,
        encA: (ScaleEncoder, A) -> Unit,
        encB: (ScaleEncoder, B) -> Unit,
        encC: (ScaleEncoder, C) -> Unit,
        encD: (ScaleEncoder, D) -> Unit
    ) {
        encA(this, tuple.first)
        encB(this, tuple.second)
        encC(this, tuple.third)
        encD(this, tuple.fourth)
    }

    fun encodeEnum(index: Int) {
        require(index in 0..255) { "Enum index must fit in u8 (0..255)" }
        encodeU8(index)
    }

    fun encodeAccountId32(accountId: ByteArray) {
        require(accountId.size == 32) { "AccountId32 must be exactly 32 bytes" }
        writeBytes(accountId)
    }

    fun toByteArray(): ByteArray = outputStream.toByteArray()

    private fun valueToFixedLittleEndian(value: BigInteger, size: Int): ByteArray {
        var bytes = value.toByteArray()
        if (bytes.size > 1 && bytes[0] == 0.toByte()) {
            bytes = bytes.copyOfRange(1, bytes.size)
        }
        val le = bytes.reversedArray()
        val res = ByteArray(size)
        val copyLen = minOf(le.size, size)
        System.arraycopy(le, 0, res, 0, copyLen)
        return res
    }
}

/**
 * SCALE Reader/Decoder for Substrate data types.
 */
class ScaleReader(private val bytes: ByteArray) {
    var position: Int = 0
        private set

    fun hasMore(): Boolean = position < bytes.size

    fun readByte(): Int {
        if (position >= bytes.size) {
            throw IndexOutOfBoundsException("Unexpected end of SCALE input at index $position")
        }
        return bytes[position++].toInt() and 0xFF
    }

    fun readBytes(count: Int): ByteArray {
        if (position + count > bytes.size) {
            throw IndexOutOfBoundsException("Cannot read $count bytes from position $position, total bytes: ${bytes.size}")
        }
        val result = bytes.copyOfRange(position, position + count)
        position += count
        return result
    }

    fun decodeBoolean(): Boolean {
        return readByte() != 0
    }

    fun decodeCompactBigInteger(): BigInteger {
        val b0 = readByte()
        val mode = b0 and 0b11
        return when (mode) {
            0b00 -> (b0 ushr 2).toBigInteger()
            0b01 -> {
                val b1 = readByte()
                ((b0 or (b1 shl 8)) ushr 2).toBigInteger()
            }
            0b10 -> {
                val b1 = readByte()
                val b2 = readByte()
                val b3 = readByte()
                val valLong = (b0.toLong() or (b1.toLong() shl 8) or (b2.toLong() shl 16) or (b3.toLong() shl 24)) ushr 2
                valLong.toBigInteger()
            }
            0b11 -> {
                val numBytes = (b0 ushr 2) + 4
                val rawBytes = readBytes(numBytes)
                BigInteger(1, rawBytes.reversedArray())
            }
            else -> throw IllegalStateException("Invalid compact mode: $mode")
        }
    }

    fun decodeCompactInt(): Int = decodeCompactBigInteger().toInt()

    fun decodeCompactLong(): Long = decodeCompactBigInteger().toLong()

    fun decodeU8(): Int = readByte()

    fun decodeU16(): Int {
        val b0 = readByte()
        val b1 = readByte()
        return b0 or (b1 shl 8)
    }

    fun decodeU32(): Long {
        val b0 = readByte().toLong()
        val b1 = readByte().toLong()
        val b2 = readByte().toLong()
        val b3 = readByte().toLong()
        return b0 or (b1 shl 8) or (b2 shl 16) or (b3 shl 24)
    }

    fun decodeU64(): BigInteger {
        val raw = readBytes(8)
        return BigInteger(1, raw.reversedArray())
    }

    fun decodeU128(): BigInteger {
        val raw = readBytes(16)
        return BigInteger(1, raw.reversedArray())
    }

    fun decodeByteArray(): ByteArray {
        val len = decodeCompactInt()
        return readBytes(len)
    }

    fun decodeFixedByteArray(count: Int): ByteArray = readBytes(count)

    fun decodeString(): String {
        return String(decodeByteArray(), Charsets.UTF_8)
    }

    fun <T> decodeOption(decoder: (ScaleReader) -> T): T? {
        val flag = readByte()
        return if (flag == 0) null else decoder(this)
    }

    fun <T, E> decodeResult(
        okDecoder: (ScaleReader) -> T,
        errDecoder: (ScaleReader) -> E
    ): ScaleResult<T, E> {
        val flag = readByte()
        return if (flag == 0) {
            ScaleResult.Ok(okDecoder(this))
        } else {
            ScaleResult.Err(errDecoder(this))
        }
    }

    fun <T> decodeList(decoder: (ScaleReader) -> T): List<T> {
        val len = decodeCompactInt()
        val list = ArrayList<T>(len)
        for (i in 0 until len) {
            list.add(decoder(this))
        }
        return list
    }

    fun <A, B> decodeTuple2(
        decA: (ScaleReader) -> A,
        decB: (ScaleReader) -> B
    ): Pair<A, B> {
        val a = decA(this)
        val b = decB(this)
        return Pair(a, b)
    }

    fun <A, B, C> decodeTuple3(
        decA: (ScaleReader) -> A,
        decB: (ScaleReader) -> B,
        decC: (ScaleReader) -> C
    ): Triple<A, B, C> {
        val a = decA(this)
        val b = decB(this)
        val c = decC(this)
        return Triple(a, b, c)
    }

    fun <A, B, C, D> decodeTuple4(
        decA: (ScaleReader) -> A,
        decB: (ScaleReader) -> B,
        decC: (ScaleReader) -> C,
        decD: (ScaleReader) -> D
    ): ScaleTuple4<A, B, C, D> {
        val a = decA(this)
        val b = decB(this)
        val c = decC(this)
        val d = decD(this)
        return ScaleTuple4(a, b, c, d)
    }

    fun decodeEnum(): Int = decodeU8()

    fun decodeAccountId32(): ByteArray = readBytes(32)
}

/**
 * Extension helper functions for ByteArray and String.
 */
fun ByteArray.toHex(): String {
    val sb = StringBuilder(size * 2)
    for (b in this) {
        sb.append(String.format("%02x", b.toInt() and 0xFF))
    }
    return sb.toString()
}

fun ByteArray.toHexString(): String = "0x${toHex()}"

fun String.hexToByteArray(): ByteArray {
    val cleanHex = if (startsWith("0x", ignoreCase = true)) substring(2) else this
    if (cleanHex.isEmpty()) return ByteArray(0)
    val len = cleanHex.length
    require(len % 2 == 0) { "Hex string length must be even" }
    val result = ByteArray(len / 2)
    for (i in 0 until len step 2) {
        result[i / 2] = cleanHex.substring(i, i + 2).toInt(16).toByte()
    }
    return result
}

fun ByteArray.toScaleReader(): ScaleReader = ScaleReader(this)
