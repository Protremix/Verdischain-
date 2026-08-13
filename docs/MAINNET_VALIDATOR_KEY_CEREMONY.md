# Mainnet Validator Key Ceremony Procedure

## Overview

This document describes the air-gapped key generation ceremony for Verdis Chain mainnet validators. All validator keys MUST be generated on air-gapped hardware. No private keys, seeds, mnemonics, or secret URIs should ever touch a network-connected device.

## Prerequisites

- Air-gapped machine (no WiFi/Bluetooth/Ethernet, physically removed network cards)
- USB drive for transferring public keys and chain spec modifications
- Verified `subkey` binary (Substrate key generation tool) on the air-gapped machine
- Verdis Chain chain spec file (`mainnet-plain.json`)
- At least 3 ceremony witnesses (for 3-of-5 multisig cold storage)

## Key Types

Each validator requires FOUR key pairs:

| Key Type | Crypto | Purpose | Stored In |
|----------|--------|---------|-----------|
| **BABE** | sr25519 | Block production (VRF) | `keystore/babe` |
| **GRANDPA** | ed25519 | Block finality (BFT voting) | `keystore/grandpa` |
| **Account** | sr25519 | Validator account (staking, rewards) | Wallet |
| **Session Controller** | sr25519 | Session key management | `keystore/controller` |

## Ceremony Steps

### Step 1: Prepare Air-Gapped Environment

1. Boot air-gapped machine from verified read-only USB (Ubuntu Live or Tails).
2. Verify no network interfaces are active: `ip link show` should show only `lo`.
3. Install `subkey` from verified binary on USB drive.
4. Generate a new BIP39 mnemonic for each validator: `subkey generate-node-key`
5. Record each mnemonic on paper (NOT digital storage). Store in tamper-evident envelope.

### Step 2: Generate Validator Keys (per validator)

```bash
# On air-gapped machine, for each validator (1-21):

# 1. Generate BABE key (sr25519)
subkey generate --scheme sr25519 --output babe_key.json
# Record: public key, SS58 address, seed phrase

# 2. Generate GRANDPA key (ed25519)
subkey generate --scheme ed25519 --output grandpa_key.json
# Record: public key, SS58 address, seed phrase

# 3. Generate Account key (sr25519)
subkey generate --scheme sr25519 --output account_key.json
# Record: SS58 address, seed phrase (this is the validator's staking account)

# 4. Generate Controller key (sr25519)
subkey generate --scheme sr25519 --output controller_key.json
# Record: SS58 address, seed phrase
```

### Step 3: Export Public Keys

For each validator, export ONLY the public keys to the USB drive:

```json
{
  "validatorId": 1,
  "account": "5X...SS58...",
  "controller": "5X...SS58...",
  "babe": "5X...SS58...",
  "grandpa": "5X...SS58...",
  "babePublicKey": "0x...hex...",
  "grandpaPublicKey": "0x...hex..."
}
```

**NEVER export private keys, seeds, or mnemonics to USB.**

### Step 4: Update Chain Spec

1. Transfer the public keys JSON file to the build machine.
2. For each validator, add to the chain spec:
   - `balances.balances`: fund each validator account with at least 100M VRDX (MinValidatorStake)
   - `session.keys`: add `[account, controller, {babe, grandpa}]` entry
   - `babe.authorities`: add `[babe_public_key, 1]`
   - `grandpa.authorities`: add `[grandpa_public_key, 1]`
   - `dpos.validatorNames`: add `[account, name_bytes]`

3. Verify:
   - 21 session key entries
   - 21 BABE authorities
   - 21 GRANDPA authorities
   - Total genesis balance = exactly 100B VRDX

### Step 5: Generate Raw Chain Spec

```bash
./target/release/verdis-node build-spec --chain=mainnet-plain --raw --disable-default-bootnode > mainnet-raw.json
```

### Step 6: Verify Chain Spec Integrity

```bash
# Verify no dev keys exist
grep -E "//Alice|//Bob|//Charlie|//Dave|//Eve|//Ferdie|MAINNET_VALIDATOR_" mainnet-plain.json
# Should return nothing

# Verify total supply
python3 -c "
import json
with open('mainnet-plain.json') as f:
    spec = json.load(f)
balances = spec['genesis']['runtimeGenesis']['patch']['balances']['balances']
total = sum(b for _, b in balances)
assert total == 100_000_000_000 * 10**9, f'MISMATCH: {total}'
print(f'Total supply: {total / 10**9} VRDX OK')
"

# Verify authority counts
python3 -c "
import json
with open('mainnet-plain.json') as f:
    spec = json.load(f)
patch = spec['genesis']['runtimeGenesis']['patch']
babe = len(patch['babe']['authorities'])
grandpa = len(patch['grandpa']['authorities'])
session = len(patch['session']['keys'])
print(f'BABE: {babe}, GRANDPA: {grandpa}, Session: {session}')
assert babe == grandpa == session == 21
print('All counts = 21 OK')
"
```

### Step 7: Key Custody

1. **Hot keys** (BABE, GRANDPA): Loaded onto validator node keystore. Encrypted at rest with node-specific password.
2. **Controller keys**: Stored in cold storage (hardware wallet, HSM, or air-gapped USB in safe).
3. **Account keys**: Stored in cold storage. Used only for staking operations via controller.
4. **Mnemonic/seed phrases**: Written on paper, stored in tamper-evident envelopes in physical safe. 2-of-3 shamir secret sharing for backup.

### Step 8: Key Rotation

- Session keys (BABE/GRANDPA) can be rotated via `session.set_keys()` extrinsic.
- Controller keys can be changed via `staking.set_controller()` equivalent.
- Account keys CANNOT be rotated — new validator registration required.
- Rotation frequency: every 90 days minimum, immediately on suspected compromise.

### Step 9: Secure Deletion

After the ceremony:
1. Wipe all temporary files from the air-gapped machine: `shred -vfz -n 3 /tmp/*key*`
2. Destroy USB drive used for public key transfer (physical destruction).
3. Reformat air-gapped machine storage.
4. All ceremony participants sign a document confirming:
   - Keys were generated on air-gapped hardware
   - No private keys were transmitted electronically
   - Public keys were accurately recorded in the chain spec
   - Seeds/mnemonics are stored in physical safe

## Multi-Person Control

- **3-of-5 multisig** for cold storage of team allocation (5B VRDX)
- **2-of-3 witness signatures** required for chain spec finalization
- **Individual validator operators** control their own keys
- No single person has access to all validator keys

## Validation Checklist

- [ ] All 21 validators have unique key pairs (no shared keys)
- [ ] No dev keys (//Alice, //Bob, etc.) in mainnet spec
- [ ] Total genesis supply = 100B VRDX
- [ ] 21 BABE authorities populated
- [ ] 21 GRANDPA authorities populated
- [ ] 21 session key entries
- [ ] Each validator funded with >= 100M VRDX (MinValidatorStake)
- [ ] BlockReward in genesis matches runtime (342 VRDX)
- [ ] Raw chain spec generated and verified
- [ ] All seeds/mnemonics in physical safe
- [ ] Ceremony witnesses signed off
