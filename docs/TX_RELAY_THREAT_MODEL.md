# TX Relay v3 — Cryptographic Threat Model (ARCH-039)

**Component:** Transaction Relay Service (tx-relay)
**Version:** v3 (AES-GCM encrypted)
**Status:** Testnet only — must not be used for mainnet without independent review

---

## 1. Component Overview

The TX Relay is a server-side service that allows users to submit transactions without running a full node. It accepts a signed payload from the user's wallet, optionally encrypts sensitive fields using AES-GCM, and submits the extrinsic to the Verdis Chain node via RPC.

## 2. Trust Assumptions

| Assumption | Risk Level | Mitigation |
|-----------|-----------|------------|
| User private key never leaves the user's device | CRITICAL | Keys generated client-side via @noble/secp256k1, signing happens in browser/app |
| TX Relay cannot forge transactions | CRITICAL | Relay only forwards pre-signed extrinsics; no signing authority |
| AES-GCM encryption protects relay transit | MEDIUM | AES-256-GCM with random nonce; key derived per session |
| Relay cannot modify transaction content | HIGH | Extrinsic is SCALE-encoded and signed before relay receives it; any modification invalidates signature |
| Relay availability is not consensus-critical | LOW | Users can submit directly via their own node or any RPC endpoint |

## 3. Attack Surface

### 3.1 Man-in-the-Middle (MITM)
- **Vector:** Attacker intercepts traffic between wallet and relay
- **Mitigation:** HTTPS (TLS 1.3), HSTS headers, CSP policy
- **Residual risk:** Low (TLS provides confidentiality and integrity)

### 3.2 Relay Compromise
- **Vector:** Attacker gains control of relay server
- **Impact:** Can observe transaction metadata (sender, method, params) but NOT private keys
- **Can attacker forge transactions?** No — relay has no signing keys
- **Can attacker drop transactions?** Yes — availability issue, not security
- **Mitigation:** Users can bypass relay and submit directly to any node RPC

### 3.3 Key Extraction from Browser
- **Vector:** XSS attack extracts private key from wallet page
- **Impact:** Full key compromise — attacker can sign any transaction
- **Mitigation:** CSP headers, no inline scripts, input sanitization
- **Residual risk:** Medium (depends on CSP effectiveness)

### 3.4 AES-GCM Nonce Reuse
- **Vector:** If nonce is reused with same key, confidentiality is broken
- **Mitigation:** Random 96-bit nonce per encryption operation
- **Residual risk:** Low (2^32 messages before collision probability becomes significant)

### 3.5 Replay Attacks
- **Vector:** Attacker replays a previously submitted transaction
- **Mitigation:** Substrate transactions include era + nonce; stale transactions are rejected by the runtime
- **Residual risk:** Very Low

## 4. Threats NOT Mitigated by TX Relay

- **Key loss:** If user loses their mnemonic, funds are irrecoverable
- **Phishing:** Attacker tricks user into signing a malicious transaction
- **Smart contract bugs:** If user interacts with a buggy contract, relay cannot prevent it
- **Network consensus failures:** Relay is not involved in consensus

## 5. Recommendations for Mainnet

1. **Independent review:** AES-GCM implementation must be reviewed by a third-party cryptographer
2. **Key management:** Relay server must never store user keys (already enforced)
3. **Rate limiting:** Add per-IP and per-account rate limits to prevent spam
4. **Monitoring:** Log all relay transactions for audit trail
5. **Fallback:** Users must always have the option to submit via their own node
6. **Deprecation plan:** TX Relay should be optional, not required, for mainnet

## 6. Cryptographic Primitives

| Primitive | Implementation | Standard |
|-----------|---------------|-----------|
| Key generation | @noble/secp256k1 v2.0.0 | RFC 6979 deterministic ECDSA |
| Hashing | @noble/hashes (BLAKE2b) | RFC 7693 |
| Address format | SS58 with prefix 909 | Substrate SS58 |
| Mnemonic | BIP39 2048-word list | BIP39 standard |
| Transit encryption | AES-256-GCM | NIST SP 800-38D |
| Transaction encoding | SCALE codec | Substrate SCALE |

## 7. Open Questions for Independent Audit

1. Is the AES-GCM key derivation function adequate? (Currently per-session)
2. Are there side-channel risks in the browser-based signing implementation?
3. Can the relay be used to correlate transactions to IP addresses? (Privacy concern)
4. What is the impact of relay downtime on user experience?
