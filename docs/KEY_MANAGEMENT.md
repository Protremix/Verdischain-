# VERDIS CHAIN — KEY MANAGEMENT & CEREMONY PROCEDURES

**Document Version:** 1.0.0  
**Effective Date:** August 2026  
**Status:** APPROVED & OPERATIONAL  
**Project:** Verdis Chain (Substrate DPoS, Runtime v14)  
**Reference Scripts:** `verdis-chain/scripts/air-gapped-key-ceremony.sh`  
**Reference Specs:** `docs/TREASURY_SECURITY_SPEC.md`, `verdis-chain/docs/validator-key-ceremony.md`  

---

## 1. OVERVIEW & SCOPE

Key management is the foundation of cryptographic trust for Verdis Chain. This document establishes standard operating procedures for key generation, storage, usage, rotation, custody, and emergency recovery across all operational key tiers:

1. **Validator Consensus Keys** (BABE sr25519 & GRANDPA ed25519)
2. **Session Keys** (`author_rotateKeys` RPC rotation)
3. **Treasury Cold-Storage Multisig Keys** (3-of-5 threshold sr25519)
4. **Administrative / Governance Keys** (Emergency Root / Council origin)

---

## 2. KEY ARCHITECTURE MATRIX

| Key Type | Cryptographic Scheme | Purpose / Role | Target Storage Medium | Rotation Frequency |
|---|---|---|---|---|
| **BABE Session Key** | `sr25519` (Schnorrkel) | Slot authorship & block signing | Local node keystore (`/chains/verdis/keystore`) | Every 30 days or on compromise |
| **GRANDPA Session Key** | `ed25519` (Edwards-25519) | Finality voting & voter commitment | Local node keystore (`/chains/verdis/keystore`) | Every 30 days or on compromise |
| **Validator Staking Key** | `sr25519` | Holds validator bond & receives rewards | Cold storage / Ledger hardware wallet | Yearly / Governance change |
| **Treasury Multisig Keys** | `sr25519` (5 Keys) | Controls 20B VRDX Treasury (3-of-5 threshold) | Air-gapped physical paper backups / HSM | Per security policy (or custodian departure) |
| **Node Identity Key** | `ed25519` (libp2p) | P2P network identity & LibP2P handshakes | Node host filesystem (protected by file permissions) | Per node infrastructure migration |

---

## 3. AIR-GAPPED KEY CEREMONY PROCEDURE

All mainnet genesis keys—including 21 production validator keypairs and 5 cold-storage Treasury multisig keys—are generated using the official air-gapped ceremony script (`verdis-chain/scripts/air-gapped-key-ceremony.sh`).

```
+-------------------------------------------------------------------------+
|                      AIR-GAPPED CEREMONY FLOW                           |
+-------------------------------------------------------------------------+
| 1. Environment Verification  --> Ensure 0 active network interfaces      |
| 2. Exec subkey / verdis-node --> Generate 21 Validator keypairs         |
| 3. Exec subkey / verdis-node --> Generate 5 Cold-Storage Multisig keys   |
| 4. Compute 3-of-5 Address    --> blake2_256(threshold ++ signatories)   |
| 5. Export Public JSON        --> Save public keys & checksums to USB     |
| 6. Mnemonic Physical Backup  --> Write mnemonics on physical paper      |
+-------------------------------------------------------------------------+
```

### 3.1 Pre-Ceremony Hardware & Environmental Requirements
1. **Dedicated Air-Gapped Machine:** Formatted laptop running clean Linux OS with all network hardware (WiFi, Bluetooth, Ethernet) physically disabled or removed.
2. **Substrate Cryptographic Tooling:** `subkey` utility or compiled `verdis-node key` binary pre-loaded via read-only USB media.
3. **Physical Storage:** Secure paper ledger cards for mnemonic phrase storage.
4. **USB Drives:** Two brand-new, factory-sealed USB drives (one for script input, one for public JSON export).

### 3.2 Executing the Key Ceremony Script
On the air-gapped machine, execute:
```bash
chmod +x verdis-chain/scripts/air-gapped-key-ceremony.sh
./verdis-chain/scripts/air-gapped-key-ceremony.sh
```

**Outputs Produced:**
- `output/validator-keys.json`: 21 public key records (`sr25519` & `ed25519` addresses, hex public keys — **NO SECRETS**).
- `output/multisig-keys.json`: 5 Treasury cold-storage public keys and calculated 3-of-5 address.
- `output/ceremony-checksums.txt`: SHA-256 hashes of generated public JSON files.
- `output/ceremony-log.txt`: Audit log recording step timestamps.

### 3.3 Custody Assignments & Physical Storage Rules
1. **5 Treasury Signers:**
   - 5 independent key custodians are assigned.
   - Each custodian receives exactly **one** 12/24-word seed phrase written on tamper-evident paper storage cards.
   - No single person may hold or access more than 1 seed phrase.
   - Seed phrases are stored in fireproof, waterproof safes in distinct physical locations across different geographic jurisdictions.
2. **Zero Cloud / Electronic Backups:** Private keys and seed phrases derived from the ceremony must **NEVER** be photographed, typed into networked devices, stored on cloud drives, or transmitted over network channels.

---

## 4. VALIDATOR SESSION KEY MANAGEMENT & ROTATION

Active validators (21 nodes on testnet/mainnet) operate hot session keys inside their Substrate node keystores.

```
       [ Validator Operator Node ]
                   │
                   ▼ RPC: author_rotateKeys
   [ Keystore generates new sr25519/ed25519 ]
                   │
                   ▼ Returns Hex Output
 [ Extrinsic: session.setKeys(keys, proof) ]
                   │
                   ▼ Epoch Rotation
     [ Consensus activates new keys ]
```

### 4.1 Initial Session Key Injection
Validator operators inject hot session keys into their running node keystore via the local JSON-RPC endpoint (bound strictly to `127.0.0.1`):

```bash
curl -H "Content-Type: application/json" \
  -d '{"id":1, "jsonrpc":"2.0", "method":"author_rotateKeys", "params":[]}' \
  http://127.0.0.1:9944
```

The RPC call returns a concatenated hexadecimal string representing the public keys for BABE and GRANDPA.

### 4.2 Binding Session Keys On-Chain
Using their cold/controller account, the validator submits the `session.setKeys` extrinsic:
```rust
// Extrinsic call structure:
pallet_session::Call::set_keys {
    keys: SessionKeys {
        babe: BabeKeyId,
        grandpa: GrandpaKeyId,
    },
    proof: vec![],
}
```
The new session keys take effect at the start of the next epoch boundary.

### 4.3 Scheduled Session Key Rotation Protocol
1. **Frequency:** Validator session keys must be rotated every 30 days.
2. **Procedure:**
   - Step 1: Issue `author_rotateKeys` on the validator node.
   - Step 2: Submit `session.setKeys` extrinsic at least 1 epoch prior to planned rotation window.
   - Step 3: Verify new keys are registered in `Session::Validators` state via storage query.
   - Step 4: Archive or securely purge old keystore files from node filesystem `/chains/verdis/keystore`.

---

## 5. TREASURY 3-OF-5 MULTISIG KEY OPERATIONS

The 20 Billion VRDX Treasury account is governed by a **3-of-5 multisignature scheme** implemented via `pallet_multisig`.

### 5.1 Address Derivation
The 3-of-5 multisig SS58 address is derived deterministically from the 5 cold-storage public keys generated during the key ceremony:
```bash
verdis-node key multisig \
  --threshold 3 \
  --signatories <ADDR_1> <ADDR_2> <ADDR_3> <ADDR_4> <ADDR_5>
```

### 5.2 Transaction Authorization Workflow
```
[ Treasury Proposal Created ] ──> [ Signer 1 Approves (as_multi) ]
                                             │
                                             ▼
[ Transfer Executed ] <── [ Signer 3 Approves ] <── [ Signer 2 Approves ]
```

1. **Proposal Submission:** Any authorized entity or council origin submits a spending proposal.
2. **First Approval (`as_multi` call):** Signer 1 initiates the multisig call on-chain, creating a pending multisig record in `pallet_multisig`.
3. **Second & Third Approvals:** Signers 2 and 3 review the call hash independently on air-gapped signing hardware and broadcast their approvals.
4. **Execution:** On receipt of the 3rd valid signature, `pallet_multisig` automatically dispatches the underlying Treasury transaction.

---

## 6. KEY COMPROMISE & EMERGENCY RESPONSE PROCEDURES

### 6.1 Validator Key Compromise Action Plan
If a validator node's hot keystore is suspected of being compromised:
1. **Immediate Session Rotation:** Operator immediately calls `author_rotateKeys` on a fresh node instance and broadcasts `session.setKeys` to switch signing authority.
2. **Node Isolation:** Shut down the compromised server instance to prevent double-signing/equivocation.
3. **Keystore Purge:** Securely erase the old keystore directory using `shred -u /chains/verdis/keystore/*`.

### 6.2 Treasury Cold Key Compromise Action Plan
If 1 or 2 Treasury cold keys are lost or compromised:
1. The remaining 3 or 4 secure signers immediately construct a multisig transaction to execute a **Multisig Migration Call**.
2. Perform a mini key ceremony to generate replacement cold keypairs for affected custodians.
3. Update the `pallet_multisig` signatory set on-chain to register the new 3-of-5 signatory list.
4. If 3 or more keys are compromised simultaneously, emergency governance origin must be invoked per Constitution Article 16 to freeze Treasury interactions until clean state is restored.
