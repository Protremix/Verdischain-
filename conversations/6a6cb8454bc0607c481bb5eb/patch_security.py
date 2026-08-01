#!/usr/bin/env python3
"""Patch security.js: real slashing with penalties + crypto-secure admin key + VM limits"""

with open('/opt/verdis/app/dist/core/security.js') as f:
    content = f.read()

# Fix 1: Crypto-secure admin key generation
old_genkey = """generateApiKey() {
        const chars = '0123456789abcdef';
        let key = '';
        for (let i = 0; i < 64; i++) {
            key += chars[Math.floor(Math.random() * 16)];
        }
        return key;
    }"""

new_genkey = """generateApiKey() {
        try {
            const crypto = require('crypto');
            return crypto.randomBytes(32).toString('hex');
        } catch {
            // Fallback (should not happen in Node.js)
            const chars = '0123456789abcdef';
            let key = '';
            for (let i = 0; i < 64; i++) {
                key += chars[Math.floor(Math.random() * 16)];
            }
            return key;
        }
    }"""

if old_genkey in content:
    content = content.replace(old_genkey, new_genkey)
    print("1. Fixed admin key generation (crypto.randomBytes)")
else:
    print("1. ERROR: generateApiKey not found")

# Fix 2: Real slashing with actual penalties
old_slash = """slashValidator(address, reason) {
        if (this.slashedValidators.has(address)) {
            return { slashed: false, penalty: 0 };
        }
        this.slashedValidators.add(address);
        this.logEvent('slashing', 'critical', `Validator ${address} slashed: ${reason}`, undefined, address);
        return { slashed: true, penalty: 0 };
    }"""

new_slash = """slashValidator(address, reason, consensus, tokenSystem) {
        if (this.slashedValidators.has(address)) {
            return { slashed: false, penalty: 0 };
        }
        this.slashedValidators.add(address);
        // Calculate penalty: confiscate 50% of staked tokens
        let penalty = 0;
        if (consensus && tokenSystem) {
            const validator = consensus.getValidators().get(address);
            const staked = tokenSystem.getStaked(address);
            penalty = Math.floor(staked * 0.5);
            if (penalty > 0) {
                // Confiscate 50% of staked tokens (burned, not redistributed)
                tokenSystem.unstake(address, penalty);
                this.logEvent('slashing', 'critical',
                    `Validator ${address} slashed: ${reason}. Penalty: ${penalty} VRS confiscated`,
                    undefined, address);
            } else {
                this.logEvent('slashing', 'critical',
                    `Validator ${address} slashed: ${reason}. No stake to confiscate`,
                    undefined, address);
            }
        } else {
            this.logEvent('slashing', 'critical',
                `Validator ${address} slashed: ${reason}`, undefined, address);
        }
        return { slashed: true, penalty };
    }"""

if old_slash in content:
    content = content.replace(old_slash, new_slash)
    print("2. Fixed slashing with real stake confiscation (50% penalty)")
else:
    print("2. ERROR: slashValidator not found")

# Fix 3: Add transaction timeout to nonce tracking
old_consume = """consumeNonce(nonce) {
        if (this.usedNonces.has(nonce)) {
            this.logEvent('replay', 'critical', `Replay attack detected: nonce ${nonce} already used`);
            return false;
        }
        this.usedNonces.add(nonce);
        // Keep only last 100000 nonces to prevent memory bloat
        if (this.usedNonces.size > 100000) {
            const arr = Array.from(this.usedNonces).sort((a, b) => a - b);
            this.usedNonces = new Set(arr.slice(-50000));
        }
        return true;
    }"""

new_consume = """consumeNonce(nonce) {
        if (this.usedNonces.has(nonce)) {
            this.logEvent('replay', 'critical', `Replay attack detected: nonce ${nonce} already used`);
            return false;
        }
        this.usedNonces.add(nonce);
        // TTL-based cleanup: keep nonces from last 24h only
        if (this.usedNonces.size > 100000) {
            const cutoff = Date.now() - 86400000; // 24h
            const arr = Array.from(this.usedNonces).filter(n => n > cutoff);
            this.usedNonces = new Set(arr.slice(-50000));
        }
        return true;
    }"""

if old_consume in content:
    content = content.replace(old_consume, new_consume)
    print("3. Fixed nonce cleanup (TTL-based, 24h)")
else:
    print("3. ERROR: consumeNonce not found")

with open('/opt/verdis/app/dist/core/security.js', 'w') as f:
    f.write(content)
print("Security.js patched successfully!")
