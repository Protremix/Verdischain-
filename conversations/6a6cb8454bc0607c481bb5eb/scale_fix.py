#!/usr/bin/env python3
"""Replace manual SCALE encoding with polkadart_scale_codec library."""

f = '/opt/verdis-wallet/lib/features/transactions/data/transaction_repository_impl.dart'
with open(f, 'r') as fh:
    content = fh.read()

changes = []

# 1. Add import for polkadart_scale_codec
if 'polkadart_scale_codec' not in content:
    # Find the last import line and add after it
    import_line = "import 'package:http/http.dart' as http;"
    if import_line in content:
        content = content.replace(
            import_line,
            import_line + "\nimport 'package:polkadart_scale_codec/polkadart_scale_codec.dart';"
        )
        changes.append('Added polkadart_scale_codec import')

# 2. Replace _encodeCompactBigInt with library version
old_compact = """  List<int> _encodeCompactBigInt(BigInt v) {
    if (v < BigInt.from(64)) return [(v.toInt() << 2)];
    if (v < BigInt.from(16384)) {
      final n = v.toInt();
      return [(n << 2 | 1) & 0xFF, (n << 2 | 1) >> 8];
    }
    if (v < BigInt.from(1073741824)) {
      final n = v.toInt();
      return [(n << 2 | 2) & 0xFF, (n << 2 | 2) >> 8 & 0xFF, (n << 2 | 2) >> 16 & 0xFF, (n << 2 | 2) >> 24 & 0xFF];
    }
    final bytes = _bigIntToBytes(v);
    return [(bytes.length - 4) << 2 | 3, ...bytes];
  }

  List<int> _encodeCompactInt(int v) => _encodeCompactBigInt(BigInt.from(v));

  List<int> _encodeU32(int v) => [v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF, (v >> 24) & 0xFF];

  List<int> _bigIntToBytes(BigInt v) {
    final bytes = <int>[];
    var n = v;
    while (n > BigInt.zero) { bytes.add((n & BigInt.from(255)).toInt()); n = n >> 8; }
    return bytes.reversed.toList();
  }"""

new_compact = """  /// SCALE compact encoding using audited polkadart_scale_codec library
  List<int> _encodeCompactBigInt(BigInt v) {
    final output = ByteOutput();
    CompactBigIntCodec.codec.encodeTo(v, output);
    return output.toBytes();
  }

  List<int> _encodeCompactInt(int v) => _encodeCompactBigInt(BigInt.from(v));

  /// SCALE u32 encoding using audited polkadart_scale_codec library
  List<int> _encodeU32(int v) {
    final output = ByteOutput();
    U32Codec.codec.encodeTo(v, output);
    return output.toBytes();
  }"""

if old_compact in content:
    content = content.replace(old_compact, new_compact)
    changes.append('Replaced manual SCALE encoding with polkadart_scale_codec')
else:
    changes.append('ERROR: Could not find manual SCALE encoding block')

with open(f, 'w') as fh:
    fh.write(content)

for c in changes:
    print(c)
