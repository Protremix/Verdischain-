path = "/var/www/verdiscan/wallet/index.html"
with open(path) as f:
    content = f.read()

old_ss58 = """function ss58Encode(publicKey, prefix) {
  const prefixBytes = prefix < 64 ? [prefix] : [
    (prefix & 0b00111111) | 0b01000000,
    (prefix >> 6) & 0xff
  ];
  // Use compressed public key (33 bytes)
  const pkBytes = publicKey.length === 33 ? Array.from(publicKey) : Array.from(publicKey).slice(0, 32);
  const data = [...prefixBytes, ...pkBytes];
  // Checksum: blake2b-512 of data, take first 2 bytes
  const checksumInput = new Uint8Array(data);
  const hash = blake2b(checksumInput, { dkLen: 64 });
  const checksum = Array.from(hash).slice(0, 2);
  return base58Encode([...data, ...checksum]);
}"""

new_ss58 = """function ss58Encode(publicKey, prefix) {
  // Substrate canonical SS58 encoding (sp-core crypto.rs)
  const SS58PRE = new TextEncoder().encode('SS58PRE');
  const prefixBytes = prefix < 64 ? [prefix] : [
    ((prefix & 0b11111100) >> 2) | 0b01000000,
    (prefix >> 8) | ((prefix & 0b00000011) << 6)
  ];
  // Use compressed public key (33 bytes)
  const pkBytes = publicKey.length === 33 ? Array.from(publicKey) : Array.from(publicKey).slice(0, 32);
  const data = [...prefixBytes, ...pkBytes];
  // Checksum: blake2b-512("SS58PRE" + data), take first 2 bytes
  const checksumInput = new Uint8Array([...SS58PRE, ...data]);
  const hash = blake2b(checksumInput, { dkLen: 64 });
  const checksum = Array.from(hash).slice(0, 2);
  return base58Encode([...data, ...checksum]);
}"""

assert old_ss58 in content, "OLD SS58 PATTERN NOT FOUND"
content = content.replace(old_ss58, new_ss58)

with open(path, "w") as f:
    f.write(content)
print("Web wallet ss58Encode patched OK")
