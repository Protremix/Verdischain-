# Verdis Chain — Validator Key Generation Ceremony

## Overview

This document defines the secure key generation ceremony for the 21 genesis validators of the Verdis Chain mainnet.

**Status:** DRAFT — Pending Rojs approval
**Prerequisite:** All code security fixes applied, governance configured, 446 tests passing.

---

## 1. Roles

| Role | Count | Responsibility |
|------|-------|----------------|
| Ceremony Coordinator | 1 | Rojs Gordons — oversees, does NOT touch keys |
| Key Generator | 1 per validator | Each validator operator generates their own keys |
| Witness | 2 | Independent witnesses verify the ceremony integrity |
| Auditor | 1 | External security auditor (optional but recommended) |

---

## 2. Key Types Required Per Validator

Each validator needs:

1. **Sr25519 keypair** — for DPoS validator identity and extrinsic signing
2. **Babe keypair** — for block production (sr25519)
3. **Grandpa keypair** — for finality (ed25519)
4. **Session keys** — combined Babe + Grandpa keys submitted via `session.setKeys()`

---

## 3. Ceremony Environment Requirements

### Air-Gapped Machine (per validator)
- **Hardware:** Dedicated laptop, no network (WiFi/Bluetooth disabled)
- **OS:** Ubuntu 22.04 LTS (minimal install, no network packages)
- **Software:** `subkey` tool (Substrate key utility)
- **Storage:** 2x USB drives (one for keys, one for backup)
- **Physical:** Tamper-evident seals on all equipment

### Verification Machine (shared)
- **Hardware:** Online laptop for verification only
- **Software:** `subkey`, `substrate-interface` (Python)
- **Network:** Access to GitHub for verification against genesis spec

---

## 4. Ceremony Steps

### Phase 1: Preparation (T-7 days)

1. **Rojs** distributes this document to all 21 validator operators
2. Each operator confirms participation and signs a commitment letter
3. Ceremony date, time, and location confirmed
4. Air-gapped machines prepared and verified (no network, no cameras)

### Phase 2: Key Generation (T-0, air-gapped)

For each validator (1-21):

```
Step 1: Generate sr25519 controller key
  $ subkey generate --scheme sr25519 --output validator-N-controller.json
  → Record: SS58 address, public key, mnemonic (SEALED envelope)

Step 2: Generate Babe key (sr25519)
  $ subkey generate --scheme sr25519 --output validator-N-babe.json
  → Record: Public key

Step 3: Generate Grandpa key (ed25519)
  $ subkey generate --scheme ed25519 --output validator-N-grandpa.json
  → Record: Public key

Step 4: Compose session keys
  SessionKeys = (babe_pubkey, grandpa_pubkey)
  → Record: Combined session key hex

Step 5: Export public keys to USB
  → Copy ONLY public keys (NOT private keys/mnemonics) to USB drive
  → Label: "Validator-N Public Keys"

Step 6: Seal private keys
  → Copy private keys/mnemonics to SECOND USB drive
  → Seal in tamper-evident envelope
  → Label: "Validator-N Private Keys — CUSTODY"
  → Sign across the seal
```

### Phase 3: Verification (T+1, online)

1. **Coordinator** collects all 21 USB drives with public keys
2. Verification machine validates each key:
   - Format: 32-byte public keys (64 hex chars)
   - Uniqueness: No duplicate keys
   - Address: SS58 format with prefix 909
3. All 21 sets of public keys are combined into a genesis update
4. Genesis hash is computed and published

### Phase 4: Genesis Finalization (T+2)

1. Update `mainnet_genesis()` in `node/src/chain_spec.rs`:
   - Replace placeholder URIs with real validator public keys
   - Update session keys for all 21 validators
   - Update Babe/Grandpa authorities (first 6 active)
2. Generate mainnet raw chain spec:
   ```
   $ cargo run --release -- build-spec --chain mainnet --raw > chain-specs/mainnet-raw.json
   ```
3. Verify genesis hash is deterministic:
   ```
   $ cargo run --release -- build-spec --chain mainnet --raw > /tmp/mainnet-raw-2.json
   $ diff chain-specs/mainnet-raw.json /tmp/mainnet-raw-2.json
   # Must be identical
   ```
4. **Rojs** signs the genesis hash (PGP or hardware wallet)
5. Genesis hash published publicly

### Phase 5: Validator Setup (T+3)

Each validator operator:

1. Recovers their controller key from their sealed USB:
   ```
   $ subkey inspect "<mnemonic>"
   ```
2. Inserts session keys into their node keystore:
   ```
   $ ./verdis key insert --chain mainnet --scheme sr25519 --suri "<babe-mnemonic>" --key-type babe
   $ ./verdis key insert --chain mainnet --scheme ed25519 --suri "<grandpa-mnemonic>" --key-type gran
   ```
3. Starts their node:
   ```
   $ ./verdis --chain mainnet-raw.json --validator --name "Validator-N" \
     --base-path /data/validator-N \
     --port 30333 --rpc-port 9933 --rpc-methods Safe
   ```
4. Submits session keys to the chain:
   ```
   # Via polkadot.js/apps or substrate-interface
   session.setKeys(session_keys, proof=empty)
   ```

---

## 5. Security Rules

1. **Never transmit private keys over any network**
2. **Never store private keys on the verification machine**
3. **Mnemonics are written on paper, sealed, and physically custody**
4. **Two-person rule:** No single person handles both key generation and genesis update
5. **Audit trail:** Every step is logged, timed, and witnessed
6. **No cameras** in the ceremony room
7. **Air-gapped machines** are destroyed or wiped after ceremony
8. **Backup keys** are stored in a physically separate, secure location

---

## 6. Validator Allocation

| Validator # | Role | Stake | Key Custody |
|-------------|------|------|-------------|
| 1-6 | Active (Babe+Grandpa) | 10M VRDX each | Operator HSM/YubiKey |
| 7-21 | Standby | 1M VRDX each | Operator HSM/YubiKey |

Total: 6 × 10M + 15 × 1M = 75M VRDX staked at genesis

---

## 7. Post-Ceremony Validation

- [ ] All 21 validator addresses verified on-chain
- [ ] All 21 session keys submitted
- [ ] All 21 validators producing/finalizing blocks (active 6)
- [ ] No placeholder keys remain in genesis
- [ ] Genesis hash signed and published
- [ ] Backup keys stored in geographically separate location
- [ ] Air-gapped machines wiped/destroyed
- [ ] Ceremony log archived

---

## 8. Emergency Key Recovery

If a validator loses their key:

1. **Controller key lost:** Use recovery mnemonic (sealed backup)
2. **Session key lost:** Generate new Babe/Grandpa keys, submit `session.setKeys()`
3. **Complete loss:** Validator is slashed, stake confiscated, replaced by standby

---

## Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Project Owner | Rojs Gordons | ________________ | _________ |
| Ceremony Coordinator | ________________ | ________________ | _________ |
| Witness 1 | ________________ | ________________ | _________ |
| Witness 2 | ________________ | ________________ | _________ |
