import re

with open('/opt/verdis-wallet/lib/core/security/wallet_crypto.dart', 'r') as f:
    content = f.read()

# The Python scalecodec library uses a different SS58 prefix encoding:
# first = ((prefix >> 2) & 0x3F) | 0x40
# second = (prefix >> 8) | ((prefix & 0x03) << 6)
# For 909: [0x63, 0x43] - matches all on-chain addresses

# Replace the _encodeNetworkId method
old_encode = """  static Uint8List _encodeNetworkId(int id) {
    if (id < 64) {
      return Uint8List.fromList([id]);
    } else {
      // Correct SS58 multi-byte encoding for prefix >= 64
      final first = 0x40 | ((id >> 8) & 0x3F);
      final second = id & 0xFF;
      return Uint8List.fromList([first, second]);
    }
  }"""

new_encode = """  static Uint8List _encodeNetworkId(int id) {
    if (id < 64) {
      return Uint8List.fromList([id]);
    } else {
      // Python scalecodec SS58 encoding (matches on-chain addresses)
      // first = ((prefix >> 2) & 0x3F) | 0x40
      // second = (prefix >> 8) | ((prefix & 0x03) << 6)
      final first = ((id >> 2) & 0x3F) | 0x40;
      final second = (id >> 8) | ((id & 0x03) << 6);
      return Uint8List.fromList([first, second]);
    }
  }"""

content = content.replace(old_encode, new_encode)

with open('/opt/verdis-wallet/lib/core/security/wallet_crypto.dart', 'w') as f:
    f.write(content)
print('Fixed _encodeNetworkId to match Python scalecodec encoding')
print('For 909: first=0x%02x second=0x%02x' % ((((909 >> 2) & 0x3F) | 0x40), ((909 >> 8) | ((909 & 0x03) << 6))))
