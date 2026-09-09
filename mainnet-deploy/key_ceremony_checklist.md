# Verdis Chain Mainnet Key Ceremony Checklist

This checklist documents the complete, air-gapped security procedure for generating, backing up, and validating initial session keys (BABE & GRANDPA) and Council multisig administrative keys for the Verdis Chain Mainnet release.

---

## 📋 Pre-Ceremony Preparation

### 1. Roles & Personnel
- [ ] **Ceremony Master**: Leads execution and manages step transitions.
- [ ] **Key Custodians (3 Minimum)**: Hold hardware backup shares / M-of-N key components.
- [ ] **Security Auditor**: Observes compliance, verifies checksums, and signs off on destruction.

### 2. Air-Gapped Hardware & Environment
- [ ] **Air-Gapped Laptop**: Compute node with networking physical hardware disabled (WiFi/Bluetooth/Ethernet cards removed or physically disconnected).
- [ ] **Faraday Enclosure / Shielded Room**: Secure location with no cameras, active cell phones, or wireless transmitters.
- [ ] **Clean Bootable OS Media**: Live USB running Tails OS or Ubuntu Server 22.04 LTS built from verified ISO SHA256 checksums.
- [ ] **Storage Media**: 3x Factory-new, USB drives (Format: FAT32/EXT4) for key exports and public spec storage.
- [ ] **Metal Backup Storage**: Stainless steel seed storage plates and laser engraver/punch tools.
- [ ] **Pre-compiled Tools**: `subkey` binary pre-compiled from Substrate source and placed on the live USB.

---

## 🔒 Execution Phase: Air-Gapped Key Generation

### Phase 1: Environment Initialization & Verification
1. [ ] Boot air-gapped laptop from live OS USB.
2. [ ] Verify networking status:
   ```bash
   ip a # Ensure no active network interfaces (loopback lo only)
   rfkill list # Ensure all wireless devices are blocked
   ```
3. [ ] Verify `subkey` tool checksum:
   ```bash
   ./subkey --version
   sha256sum ./subkey
   ```

### Phase 2: Council 2/3 AdminOrigin & Treasury Multisig Key Generation
*Note: Sudo pallet is REMOVED for mainnet. AdminOrigin for tokenomics, presale, and upgrades is controlled by Council 2/3 threshold.*

1. [ ] Generate Council Member 1 Keypair:
   ```bash
   ./subkey generate --scheme sr25519 > council-member-1.txt
   ```
2. [ ] Generate Council Member 2 Keypair:
   ```bash
   ./subkey generate --scheme sr25519 > council-member-2.txt
   ```
3. [ ] Generate Council Member 3 Keypair:
   ```bash
   ./subkey generate --scheme sr25519 > council-member-3.txt
   ```
4. [ ] Record public SS58 addresses for Council 2/3 configuration.
5. [ ] Punch/Engrave seed phrases (24 words) onto metal backup plates for each Council member.
6. [ ] Store metal plates in separate secure physical vaults across 3 geographic zones.

### Phase 3: Generation of 21 Validator Session Keys (sr25519 BABE + sr25519 GRANDPA)
*Note: Verdis Chain validators require sr25519 keys for BABE block production and sr25519 keys for GRANDPA finality consensus.*

For each Validator Index $i \in \{0 \dots 20\}$:

#### Validator Instance #$i$ Setup
1. [ ] Generate Master Staking/Account Seed:
   ```bash
   ./subkey generate --scheme sr25519 > val_${i}_master.txt
   ```
2. [ ] Derive BABE Session Key (sr25519):
   ```bash
   ./subkey inspect --scheme sr25519 "//verdis//validator//${i}//babe" > val_${i}_babe.txt
   ```
3. [ ] Derive GRANDPA Session Key (sr25519):
   ```bash
   ./subkey inspect --scheme sr25519 "//verdis//validator//${i}//grandpa" > val_${i}_grandpa.txt
   ```
4. [ ] Format JSON public session key entry:
   ```json
   {
     "index": i,
     "moniker": "verdis-val-${LOCATION}-${i}",
     "babe": "<PUBLIC_KEY_HEX_BABE>",
     "grandpa": "<PUBLIC_KEY_HEX_GRANDPA>",
     "combined_session_key": "<CONCATENATED_HEX_OR_ROTATE_KEYS_OUTPUT>"
   }
   ```
5. [ ] Store public keys in `verdis_mainnet_genesis_keys.json`.

---

## 🛠 Genesis Specification Injection

1. [ ] Mount USB Drive #1 (Public Key Collection).
2. [ ] Copy `verdis_mainnet_genesis_keys.json` and Council public keys to USB Drive #1.
3. [ ] Transfer `verdis_mainnet_genesis_keys.json` to build workstation.
4. [ ] Update `node/src/chain_spec.rs` (or `chain-specs/mainnet.json`):
   - Set 21 Genesis Validator Accounts & Session Keys.
   - Inject Council 2/3 Threshold Members.
   - Set Total Supply: `100,000,000,000 VRDX` (100B supply with 9 decimals = `100,000,000,000,000,000,000` base units).
   - Verify `MaxMissedEpochs = 50000` and `ReactivationCooldown = 100`.
   - Confirm Sudo pallet initialization block is **completely omitted**.
5. [ ] Compile raw chain spec:
   ```bash
   verdis-chain build-spec --chain=chain-specs/mainnet.json --raw > chain-specs/mainnet-raw.json
   ```

---

## 🧹 Post-Ceremony Sanitization & Destruction

1. [ ] Unmount and remove USB Drive #1 (Contains **ONLY** public keys and chain spec).
2. [ ] Secure USB Drive #2 & #3 containing encrypted key backups in physical safes.
3. [ ] Perform RAM Wipe on Air-Gapped Laptop:
   ```bash
   # Overwrite working directory RAM
   shred -u -z -n 3 *.txt
   # Perform system reboot & memory wipe
   sync && echo 3 > /proc/sys/vm/drop_caches
   poweroff
   ```
4. [ ] Remove battery and power cable from air-gapped laptop.
5. [ ] Complete Ceremony Log Sign-off:
   - [ ] Ceremony Master Signature: ___________________________ Date: ____________
   - [ ] Key Custodian 1 Signature: ___________________________ Date: ____________
   - [ ] Key Custodian 2 Signature: ___________________________ Date: ____________
   - [ ] Key Custodian 3 Signature: ___________________________ Date: ____________
   - [ ] Security Auditor Signature: ___________________________ Date: ____________
