path = '/opt/verdis/app/dist/crypto.js'
with open(path) as f:
    code = f.read()

changes = 0

# 1. Fix getPublicKeyFromPrivateKey — strip 0x prefix before Buffer.from
old_gpk = """function getPublicKeyFromPrivateKey(privateKey) {
    try {
        const privBytes = Buffer.from(privateKey, 'hex');
        const pubBytes = secp256k1.getPublicKey(privBytes, true);
        return Buffer.from(pubBytes).toString('hex');
    }
    catch {
        return `pub_${privateKey.slice(0, 16)}`;
    }
}"""

new_gpk = """function getPublicKeyFromPrivateKey(privateKey) {
    try {
        const cleanKey = privateKey.startsWith('0x') ? privateKey.slice(2) : privateKey;
        const privBytes = Buffer.from(cleanKey, 'hex');
        const pubBytes = secp256k1.getPublicKey(privBytes, true);
        return Buffer.from(pubBytes).toString('hex');
    }
    catch {
        return `pub_${privateKey.slice(0, 16)}`;
    }
}"""

if old_gpk in code:
    code = code.replace(old_gpk, new_gpk)
    changes += 1
    print('1. Fixed getPublicKeyFromPrivateKey — strips 0x prefix')
else:
    print('1. ERROR: getPublicKeyFromPrivateKey pattern not found')

# 2. Fix sign — strip 0x prefix before passing to secp256k1.sign
old_sign = """function sign(data, privateKey) {
    try {
        const messageHash = sha256(data);
        const sig = secp256k1.sign(messageHash, privateKey);
        const hex = typeof sig.toCompactHex === 'function' ? sig.toCompactHex() : Buffer.from(sig).toString('hex');
        return {
            signature: hex,
            recovery: sig.recovery ?? 0,
        };
    }
    catch {
        return {
            signature: `sig_${privateKey.slice(0, 8)}`,
            recovery: 0,
        };
    }
}"""

new_sign = """function sign(data, privateKey) {
    try {
        const cleanKey = privateKey.startsWith('0x') ? privateKey.slice(2) : privateKey;
        const messageHash = sha256(data);
        const sig = secp256k1.sign(messageHash, cleanKey);
        const hex = typeof sig.toCompactHex === 'function' ? sig.toCompactHex() : Buffer.from(sig).toString('hex');
        return {
            signature: hex,
            recovery: sig.recovery ?? 0,
        };
    }
    catch {
        return {
            signature: `sig_${privateKey.slice(0, 8)}`,
            recovery: 0,
        };
    }
}"""

if old_sign in code:
    code = code.replace(old_sign, new_sign)
    changes += 1
    print('2. Fixed sign — strips 0x prefix')
else:
    print('2. ERROR: sign pattern not found')

# 3. Fix signTransaction — always re-derive publicKey from privateKey (don't trust override)
old_st = """function signTransaction(privateKey, to, amount, fee, nonce, data = null, publicKeyOverride) {
    const publicKey = publicKeyOverride || getPublicKeyFromPrivateKey(privateKey);
    const senderAddress = getAddressFromPublicKey(publicKey);"""

new_st = """function signTransaction(privateKey, to, amount, fee, nonce, data = null, publicKeyOverride) {
    // Always re-derive from private key to ensure consistency (override may be stale/fake)
    const publicKey = getPublicKeyFromPrivateKey(privateKey);
    const senderAddress = getAddressFromPublicKey(publicKey);"""

if old_st in code:
    code = code.replace(old_st, new_st)
    changes += 1
    print('3. Fixed signTransaction — always re-derives publicKey from privateKey')
else:
    print('3. ERROR: signTransaction pattern not found')

# 4. Also fix getAddressFromPublicKey to handle 0x-prefixed public keys properly
# (shouldn't happen now, but just in case)
old_addr = """function getAddressFromPublicKey(publicKey) {
    if (!publicKey)
        return '';
    if (publicKey.startsWith('0x') || publicKey.startsWith('RJ')) {
        return publicKey;
    }"""
new_addr = """function getAddressFromPublicKey(publicKey) {
    if (!publicKey)
        return '';
    // Only return as-is if it's already a valid address (0x + 40 hex chars), not a raw public key
    if (publicKey.startsWith('0x') && publicKey.length === 42) {
        return publicKey;
    }
    if (publicKey.startsWith('RJ')) {
        return publicKey;
    }"""

if old_addr in code:
    code = code.replace(old_addr, new_addr)
    changes += 1
    print('4. Fixed getAddressFromPublicKey — only returns as-is for valid addresses')
else:
    print('4. ERROR: getAddressFromPublicKey pattern not found')

with open(path, 'w') as f:
    f.write(code)

print(f'\n{changes} fixes applied to crypto.js')
