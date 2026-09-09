// Pure Dart Blake2b-256 implementation for Substrate SS58 checksums
// Based on RFC 7693 (BLAKE2) specification
// Only implements the 256-bit (32-byte) output variant needed for SS58

import 'dart:typed_data';

class Blake2b {
  // Blake2b constants
  static const List<int> _iv = [
    0x6a09e667f3bcc908, 0xbb67ae8584caa73b,
    0x3c6ef372fe94f82b, 0xa54ff53a5f1d36f1,
    0x510e527fade682d1, 0x9b05688c2b3e6c1f,
    0x1f83d9abfb41bd6b, 0x5be0cd19137e2179,
  ];

  static const List<List<int>> _sigma = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    [14, 10, 4, 8, 9, 15, 13, 6, 1, 12, 0, 2, 11, 7, 5, 3],
    [11, 8, 12, 0, 5, 2, 15, 13, 10, 14, 3, 6, 7, 1, 9, 4],
    [7, 9, 3, 1, 13, 12, 11, 14, 2, 6, 5, 10, 4, 0, 15, 8],
    [9, 0, 5, 7, 2, 4, 10, 15, 14, 6, 8, 11, 1, 12, 3, 13],
    [2, 12, 6, 10, 0, 11, 8, 3, 4, 13, 7, 5, 15, 14, 1, 9],
    [12, 5, 1, 15, 14, 13, 4, 10, 0, 7, 6, 3, 9, 2, 8, 11],
    [13, 11, 7, 14, 12, 1, 3, 9, 5, 0, 15, 4, 8, 6, 2, 10],
    [6, 15, 14, 9, 11, 3, 0, 8, 12, 2, 13, 7, 1, 4, 10, 5],
    [10, 2, 8, 4, 7, 6, 1, 5, 15, 11, 9, 14, 3, 12, 13, 0],
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    [14, 10, 4, 8, 9, 15, 13, 6, 1, 12, 0, 2, 11, 7, 5, 3],
  ];

  int _h0, _h1, _h2, _h3, _h4, _h5, _h6, _h7;
  int _t0 = 0, _t1 = 0;
  int _f0 = 0, _f1 = 0;
  final int _outputLength;
  final List<int> _buffer = List.filled(128, 0);
  int _bufferLen = 0;

  Blake2b._internal(this._outputLength)
      : _h0 = _iv[0] ^ 0x01010000, // digest_length | key_length | fanout | depth
        _h1 = _iv[1],
        _h2 = _iv[2],
        _h3 = _iv[3],
        _h4 = _iv[4],
        _h5 = _iv[5],
        _h6 = _iv[6],
        _h7 = _iv[7];

  factory Blake2b({int digestLength = 32}) {
    return Blake2b._internal(digestLength);
  }

  static Blake2b newDigest() => Blake2b._internal(32);

  void update(Uint8List data) {
    for (int i = 0; i < data.length; i++) {
      if (_bufferLen == 128) {
        _t0 += 128;
        if (_t0 == 0) _t1++;
        _compress();
        _bufferLen = 0;
      }
      _buffer[_bufferLen++] = data[i];
    }
  }

  Uint8List digest() {
    _t0 += _bufferLen;
    if (_t0 < 0 && _bufferLen > 0) _t1++;
    // Set last block flag
    _f0 = 0xFFFFFFFFFFFFFFFF;
    // Pad remaining buffer with zeros
    for (int i = _bufferLen; i < 128; i++) {
      _buffer[i] = 0;
    }
    _compress();

    final result = Uint8List(_outputLength);
    _writeU64(result, 0, _h0);
    if (_outputLength > 8) _writeU64(result, 8, _h1);
    if (_outputLength > 16) _writeU64(result, 16, _h2);
    if (_outputLength > 24) _writeU64(result, 24, _h3);
    return result;
  }

  Uint8List get bytes => digest();

  void _compress() {
    final m = List<int>.filled(16, 0);
    final v = List<int>.filled(16, 0);

    for (int i = 0; i < 16; i++) {
      m[i] = _readU64(_buffer, i * 8);
    }

    v[0] = _h0; v[1] = _h1; v[2] = _h2; v[3] = _h3;
    v[4] = _h4; v[5] = _h5; v[6] = _h6; v[7] = _h7;
    v[8] = _iv[0]; v[9] = _iv[1]; v[10] = _iv[2]; v[11] = _iv[3];
    v[12] = _iv[4] ^ _t0;
    v[13] = _iv[5] ^ _t1;
    v[14] = _iv[6] ^ _f0;
    v[15] = _iv[7] ^ _f1;

    for (int r = 0; r < 12; r++) {
      final s = _sigma[r];
      _mixing(v, 0, 4, 8, 12, m[s[0]], m[s[1]]);
      _mixing(v, 1, 5, 9, 13, m[s[2]], m[s[3]]);
      _mixing(v, 2, 6, 10, 14, m[s[4]], m[s[5]]);
      _mixing(v, 3, 7, 11, 15, m[s[6]], m[s[7]]);
      _mixing(v, 0, 5, 10, 15, m[s[8]], m[s[9]]);
      _mixing(v, 1, 6, 11, 12, m[s[10]], m[s[11]]);
      _mixing(v, 2, 7, 8, 13, m[s[12]], m[s[13]]);
      _mixing(v, 3, 4, 9, 14, m[s[14]], m[s[15]]);
    }

    _h0 ^= v[0] ^ v[8];
    _h1 ^= v[1] ^ v[9];
    _h2 ^= v[2] ^ v[10];
    _h3 ^= v[3] ^ v[11];
    _h4 ^= v[4] ^ v[12];
    _h5 ^= v[5] ^ v[13];
    _h6 ^= v[6] ^ v[14];
    _h7 ^= v[7] ^ v[15];
  }

  static void _mixing(List<int> v, int a, int b, int c, int d, int x, int y) {
    v[a] = _add64(v[a], v[b]) + x;
    v[d] = _rotr64(_xor64(v[d], v[a]), 32);
    v[c] = _add64(v[c], v[d]);
    v[b] = _rotr64(_xor64(v[b], v[c]), 24);
    v[a] = _add64(v[a], v[b]) + y;
    v[d] = _rotr64(_xor64(v[d], v[a]), 16);
    v[c] = _add64(v[c], v[d]);
    v[b] = _rotr64(_xor64(v[b], v[c]), 63);
  }

  static int _add64(int a, int b) {
    return (a + b) & 0xFFFFFFFFFFFFFFFF;
  }

  static int _xor64(int a, int b) {
    return a ^ b;
  }

  static int _rotr64(int x, int n) {
    return ((x >> n) | (x << (64 - n))) & 0xFFFFFFFFFFFFFFFF;
  }

  static int _readU64(List<int> buf, int offset) {
    return buf[offset] |
        (buf[offset + 1] << 8) |
        (buf[offset + 2] << 16) |
        (buf[offset + 3] << 24) |
        (buf[offset + 4] << 32) |
        (buf[offset + 5] << 40) |
        (buf[offset + 6] << 48) |
        (buf[offset + 7] << 56);
  }

  static void _writeU64(List<int> buf, int offset, int value) {
    buf[offset] = value & 0xFF;
    buf[offset + 1] = (value >> 8) & 0xFF;
    buf[offset + 2] = (value >> 16) & 0xFF;
    buf[offset + 3] = (value >> 24) & 0xFF;
    buf[offset + 4] = (value >> 32) & 0xFF;
    buf[offset + 5] = (value >> 40) & 0xFF;
    buf[offset + 6] = (value >> 48) & 0xFF;
    buf[offset + 7] = (value >> 56) & 0xFF;
  }
}

// Convenience function: Blake2b-256 hash of input bytes
Uint8List blake2b256(Uint8List input) {
  final b = Blake2b.newDigest();
  b.update(input);
  return b.digest();
}
