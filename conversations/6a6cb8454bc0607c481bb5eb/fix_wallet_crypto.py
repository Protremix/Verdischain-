import re

with open('/opt/verdis-wallet/lib/core/security/wallet_crypto.dart', 'r') as f:
    content = f.read()

# Fix the ss58Address method to use correct checksum (blake2b512 with SS58PRE)
old_method = """  static String ss58Address(Uint8List publicKey) {
    const int networkId = 909;
    final prefix = _encodeNetworkId(networkId);
    final input = Uint8List.fromList([...prefix, ...publicKey]);
    // Substrate SS58 uses Blake2b-256 for checksums (NOT SHA-256)
    final hash1 = blake2b256(input);
    final hash2 = blake2b256(hash1);
    final checksum = hash2.sublist(0, 2);
    final address = Uint8List.fromList([...prefix, ...publicKey, ...checksum]);
    return base58.encode(address);
  }"""

new_method = """  static String ss58Address(Uint8List publicKey) {
    const int networkId = 909;
    final prefix = _encodeNetworkId(networkId);
    final body = Uint8List.fromList([...prefix, ...publicKey]);
    // SS58 checksum: blake2b-512("SS58PRE" + body), take first 2 bytes
    final ss58pre = Uint8List.fromList('SS58PRE'.codeUnits);
    final hashInput = Uint8List.fromList([...ss58pre, ...body]);
    final hash = blake2b512(hashInput);
    final checksum = hash.sublist(0, 2);
    final address = Uint8List.fromList([...body, ...checksum]);
    return base58.encode(address);
  }"""

content = content.replace(old_method, new_method)

# Fix the prefix encoding: 0xC0 -> 0x40
content = content.replace(
    'final first = 0xC0 | ((id >> 8) & 0x3F);',
    'final first = 0x40 | ((id >> 8) & 0x3F);'
)

with open('/opt/verdis-wallet/lib/core/security/wallet_crypto.dart', 'w') as f:
    f.write(content)
print('wallet_crypto.dart fixed.')
