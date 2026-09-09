# Verdis Chain — Genesis Ceremony Plan

**Version:** 1.0
**Date:** 2026-08-11
**Status:** Draft — Pending Review

## Overview

This document describes the validator key generation ceremony for Verdis Chain mainnet genesis. The ceremony produces the deterministic, reproducible set of validator session keys that are embedded in the mainnet chain specification.

## Principles

1. **Determinism** — The genesis spec must be reproducible from the same set of inputs.
2. **Transparency** — All steps are documented and auditable.
3. **Key Isolation** — Private keys are generated on air-gapped hardware and never transmitted over networks.
4. **No Custody** — The protocol never stores or transmits validator private keys. Each validator operator holds their own keys.

## Participants

| Role | Responsibility |
|------|---------------|
| Ceremony Coordinator (Rojs) | Oversees ceremony, collects public keys, builds chain spec |
| Validator Operators (21) | Generate keypairs on air-gapped hardware, submit public keys |
| Independent Observer | Witnesses ceremony, verifies reproducibility |

## Pre-Ceremony Requirements

### Hardware
- Air-gapped machine (no network connectivity) for key generation
- USB drive for transferring public keys (formatted fresh, used only for this ceremony)
- Hardware wallet (Ledger/Trezor) for seed backup (optional but recommended)

### Software
- `verdis-keygen` tool (built from `node/keygen`) or Substrate `subkey` tool
- SHA-256 checksum tool (`sha256sum`)

### Documentation
- This ceremony plan
- Mainnet chain spec template (`chain-spec-mainnet-raw.json`)
- Validator registration form (public key, name, contact)

## Ceremony Steps

### Step 1: Key Generation (Each Validator Operator, Air-Gapped)

Each of the 21 validator operators performs this step independently on an air-gapped machine:

```bash
# Generate sr25519 BABE/Grandpa session key
subkey generate --scheme sr25519 --output-session-keys

# Output:
# Secret phrase: <12-24 word mnemonic>
# Public key (hex): 0x...
# SS58 address: 5...
```

**Rules:**
- The mnemonic is written down on paper and stored in a physical safe. It is NEVER stored electronically.
- The public key (hex) and SS58 address are recorded for submission.
- The USB drive is used ONLY to transfer the public key file.

### Step 2: Public Key Submission

Each validator operator submits to the Ceremony Coordinator:
- BABE/Grandpa public key (hex, 64 bytes)
- ImOnline public key (hex, 32 bytes)
- Authority discovery public key (hex, 32 bytes)
- SS58 address
- Validator name (for display purposes only)
- Signed statement of key ownership

**Submission method:** Public keys are transmitted via encrypted email or in-person. Private keys NEVER leave the air-gapped machine.

### Step 3: Key Verification (Coordinator)

The coordinator verifies each submitted public key:
1. Check that the SS58 address matches the public key
2. Check that the key is unique (no duplicates)
3. Check that the key is not already in use on testnet
4. Record the key in the validator registry

### Step 4: Chain Spec Construction (Coordinator)

The coordinator builds the mainnet chain spec:

```bash
# Build the raw chain spec with all 21 validator keys
./verdis build-spec --chain mainnet --raw > chain-spec-mainnet-raw.json
```

The chain spec includes:
- 21 validator session keys (BABE, GRANDPA, ImOnline, AuthorityDiscovery)
- Genesis token allocation (100B VRDX, 9 decimals)
- DPoS configuration (ActiveValidatorCount=21)
- DEX initial pools
- Eco initial state
- Treasury configuration

### Step 5: Spec Verification (All Participants)

All participants verify the chain spec:
1. Download `chain-spec-mainnet-raw.json`
2. Verify SHA-256 checksum matches the announced checksum
3. Verify their own validator key is present in the spec
4. Verify all 21 validator keys are present and unique
5. Sign off on the spec

### Step 6: Spec Publication

The coordinator publishes:
- `chain-spec-mainnet-raw.json` (the final genesis spec)
- SHA-256 checksum
- List of 21 validator SS58 addresses
- Ceremony log (timestamps, participants, verification results)

### Step 7: Validator Node Setup (Each Operator)

Each validator operator:
1. Downloads the published chain spec
2. Verifies the SHA-256 checksum
3. Starts their node with their private key (loaded from air-gapped backup)
4. Connects to the bootnodes specified in the chain spec

## Security Controls

1. **Air-gapped key generation** — Private keys never touch networked machines
2. **Physical mnemonic backup** — Paper backup in physical safe, no electronic storage
3. **USB drive one-time use** — Fresh USB drive used only for public key transfer
4. **Public key verification** — All participants verify the spec contains their key
5. **Reproducibility** — Same inputs always produce same chain spec
6. **No server-side custody** — The protocol never stores private keys

## Post-Ceremony

1. All participants confirm their node is producing blocks
2. Block #1 is verified to contain all 21 validators
3. Ceremony log is archived and published
4. USB drives are physically destroyed
5. Air-gapped machines are wiped

## Timeline

| Step | Duration | Participants |
|------|----------|-------------|
| Pre-ceremony setup | 1 day | Coordinator |
| Key generation | 1 day per operator | Each operator |
| Key submission | 1 day | All operators |
| Spec construction | 1 day | Coordinator |
| Spec verification | 2 days | All participants |
| Spec publication | 1 day | Coordinator |
| Node setup | 1 day | Each operator |
| **Total** | **~7 days** | |

## Contingencies

- **Validator dropout:** If a validator operator drops out, their key is removed and a backup operator is substituted. The chain spec is rebuilt.
- **Key compromise:** If a private key is compromised, the operator generates a new keypair and the ceremony is restarted from Step 4.
- **Spec disagreement:** If any participant disagrees with the spec, the coordinator must resolve the issue before publication.

## Audit Trail

The following records are permanently archived:
1. This ceremony plan
2. All validator public key submissions
3. The final chain spec (with SHA-256 checksum)
4. All participant sign-offs
5. Ceremony log (timestamps, actions, participants)
6. Post-ceremony verification results
