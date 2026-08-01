// Migration script v2: fix wallets with fake public keys
// Handles invalid keys gracefully

const fs = require('fs');
const secp256k1 = require('@noble/secp256k1');
const { sha256 } = require('@noble/hashes/sha256');
const { hmac } = require('@noble/hashes/hmac');

secp256k1.etc.hmacSha256Sync = (key, ...msgs) => {
    return hmac(sha256, key, secp256k1.etc.concatBytes(...msgs));
};

function sha256Hex(data) {
    const bytes = typeof data === 'string' ? Buffer.from(data, 'utf-8') : data;
    return Buffer.from(sha256(bytes)).toString('hex');
}

function tryDeriveRealAddress(privateKey) {
    try {
        const cleanKey = privateKey.startsWith('0x') ? privateKey.slice(2) : privateKey;
        // Check if it's a valid 32-byte (64 hex char) key
        if (cleanKey.length !== 64 || !/^[0-9a-fA-F]+$/.test(cleanKey)) {
            return null; // Not a valid secp256k1 private key
        }
        const privBytes = new Uint8Array(Buffer.from(cleanKey, 'hex'));
        const pubBytes = secp256k1.getPublicKey(privBytes, true);
        const publicKey = Buffer.from(pubBytes).toString('hex');
        const pubBytesForAddr = Buffer.from(publicKey, 'utf-8');
        const hash = sha256(pubBytesForAddr);
        const address = '0x' + Buffer.from(hash).subarray(0, 20).toString('hex');
        return { publicKey, address };
    } catch (e) {
        return null;
    }
}

// Load state
const statePath = '/opt/verdis/blobs/verdis-state.json';
const state = JSON.parse(fs.readFileSync(statePath, 'utf8'));

const balances = state.balances || {};
const wallets = state.wallets || [];
let migrated = 0;
let skipped = 0;
let invalid = 0;

console.log('=== Wallet Migration v2 ===\n');

for (const wallet of wallets) {
    const isFake = (wallet.publicKey || '').startsWith('pub_');
    if (!isFake) {
        skipped++;
        continue;
    }

    const derived = tryDeriveRealAddress(wallet.privateKey);
    if (!derived) {
        // Invalid private key — can't migrate
        console.log(`INVALID wallet: ${wallet.address}`);
        console.log(`  privateKey length: ${wallet.privateKey.length} (need 66 chars with 0x)`);
        console.log(`  Skipping — this wallet was created with an invalid/short key`);
        invalid++;
        console.log('');
        continue;
    }

    const oldAddress = wallet.address;
    const newAddress = derived.address;
    const oldBalance = balances[oldAddress] || 0;

    if (oldAddress === newAddress) {
        console.log(`OK (same address): ${oldAddress}`);
        // Still update the public key
        wallet.publicKey = derived.publicKey;
        migrated++;
        continue;
    }

    console.log(`Migrating: ${oldAddress} -> ${newAddress}`);
    console.log(`  Balance: ${oldBalance} VCO`);
    console.log(`  Old pubkey: ${wallet.publicKey.substring(0, 30)}...`);
    console.log(`  New pubkey: ${derived.publicKey.substring(0, 30)}...`);

    // Update wallet
    wallet.publicKey = derived.publicKey;
    wallet.address = newAddress;

    // Migrate balance
    if (oldBalance > 0) {
        balances[newAddress] = (balances[newAddress] || 0) + oldBalance;
        delete balances[oldAddress];
        console.log(`  Migrated ${oldBalance} VCO`);
    }

    migrated++;
    console.log('');
}

console.log(`=== Summary ===`);
console.log(`Migrated: ${migrated}`);
console.log(`Already valid (skipped): ${skipped}`);
console.log(`Invalid keys (can't migrate): ${invalid}`);
console.log(`Total wallets: ${wallets.length}`);

// Save state
fs.writeFileSync(statePath, JSON.stringify(state, null, 2));
console.log('\nState file saved.');
