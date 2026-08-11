import re

path = "/opt/verdis-wallet/mobile/assets/verdis_signer.html"
with open(path) as f:
    content = f.read()

old_encode = """  function ss58Encode(publicKey) {
    if (publicKey.length !== 32) throw new Error('Public key must be 32 bytes');

    // Prefix 909 as 2 bytes LE: 0x8D, 0x03
    const prefixBytes = new Uint8Array([SS58_PREFIX & 0xff, (SS58_PREFIX >> 8) & 0xff]);"""

new_encode = """  function ss58Encode(publicKey) {
    if (publicKey.length !== 32) throw new Error('Public key must be 32 bytes');

    // Substrate canonical 2-byte prefix encoding (prefix >= 64)
    // See sp-core crypto.rs to_ss58check_with_version()
    const ident = SS58_PREFIX & 0b0011111111111111;
    const first = (((ident & 0b0000000011111100) >> 2) | 0b01000000) & 0xff;
    const second = ((ident >> 8) | ((ident & 0b0000000000000011) << 6)) & 0xff;
    const prefixBytes = new Uint8Array([first, second]);"""

assert old_encode in content, "OLD ENCODE PATTERN NOT FOUND"
content = content.replace(old_encode, new_encode)
print("ss58Encode patched OK")

with open(path, "w") as f:
    f.write(content)
