# Verdis Chain - Air-Gapped Key Ceremony Specification

**Document Version:** 1.0.0  
**Chain Identifier:** Verdis Chain Mainnet  
**SS58 Address Format:** Network Prefix 909  
**Cryptographic Primitives:** Substrate sr25519 (Stash, Controller, BABE, ImOnline, Authority Discovery), ed25519 (GRANDPA)  
**Ceremonial Officer:** Rojs  
**Classification:** STRICTLY CONFIDENTIAL - OPERATIONAL SPECIFICATION ONLY  
**Security Notice:** THIS IS AN ARCHITECTURAL AND PROCEDURAL SPECIFICATION ONLY. NO PRODUCTION PRIVATE KEYS OR SEED PHRASES ARE GENERATED OR STORED IN THIS DOCUMENT OR ANY CONNECTED SYSTEM. THE ACTUAL CEREMONY MUST BE EXECUTED EXCLUSIVELY ON AIR-GAPPED HARDWARE.

---

## 1. Purpose and Scope

The purpose of this specification is to define the rigorous, air-gapped cryptographic key generation protocol for the genesis launch of the Verdis Chain blockchain network. The key ceremony establishes the primary root-of-trust and consensus architecture for the network.

### 1.1 Key Generation Inventory Scope
1. **21 Production Validator Keypairs**:
   - **Stash Key**: `sr25519` key pair used for holding validator stake and governance operations (SS58 Network 909).
   - **Controller Key**: `sr25519` key pair used for initiating validator staking extrinsics and setting session keys (SS58 Network 909).
   - **BABE Session Key**: `sr25519` key pair used for block production slots in the Substrate BABE engine.
   - **GRANDPA Session Key**: `ed25519` key pair used for block finality gadget voting in the Substrate GRANDPA engine.
   - **ImOnline / Authority Discovery Session Keys**: `sr25519` key pairs used for heartbeat messaging and network peer routing.
2. **5 Treasury Multisig Signatory Keypairs**:
   - **Signatory Keys**: 5 individual `sr25519` key pairs (SS58 Network 909) assigned to distinct key custodians.
   - **Treasury Multisig Account**: On-chain threshold multisig account configured with a strict 3-of-5 threshold policy controlling the mainnet treasury reserve.

---

## 2. Roles and Participants

To enforce strict separation of duties and prevent single-point-of-failure or collusive compromise, the ceremony mandates five distinct roles:

1. **Ceremonial Officer (Rojs)**:
   - Overall operational command and policy enforcement.
   - Directs the step-by-step execution of the written protocol.
   - Inspects tamper seals and provides final ceremonial authorization.
2. **Key Generator (Technician)**:
   - Operates the air-gapped terminal and executes commands.
   - Performs hardware interaction, entropy collection, and command-line execution.
3. **Witness 1 (Auditor / Independent Security Expert)**:
   - Verifies each terminal command against the published specification prior to execution.
   - Confirms binary hash values, terminal outputs, and public key derived addresses.
4. **Witness 2 (Protocol / Core Engineering Lead)**:
   - Validates public key formats, SS58 network prefix 909 encoding, and cryptographic signature tests.
   - Logs public key output manifests and checksum hashes.
5. **Security Observer (Physical & Facility Security Lead)**:
   - Maintains physical perimeter security of the Faraday cage / air-gapped room.
   - Enforces zero-wireless and zero-recording device compliance.
   - Manages tamper-evident bag sealing, physical vault custody, and chain-of-custody logging.

---

## 3. Hardware Requirements

All hardware components must be brand-new, bought off-the-shelf in factory-sealed retail packaging, and inspected for physical tampering before entering the secure facility.

1. **Air-Gapped Workstation**:
   - Dedicated x86_64 laptop with physical Wi-Fi, Bluetooth, and Cellular modules physically removed (desoldered or card pulled).
   - Battery or UPS-backed isolated power supply; no connection to local Ethernet or external networks.
2. **USB Storage Media (4 Units)**:
   - **Drive A (Live OS & Tools)**: Factory-sealed 16GB USB drive containing clean Ubuntu 24.04 LTS Live ISO and verified Substrate tools.
   - **Drive B (Public Key Export)**: Factory-sealed 16GB USB drive for exporting unencrypted public key manifests and JSON metadata.
   - **Drive C (Primary Encrypted Private Key Vault)**: Factory-sealed 32GB hardware-encrypted USB drive (AES-256-GCM) for primary private key storage.
   - **Drive D (Secondary Offsite Encrypted Backup Vault)**: Factory-sealed 32GB hardware-encrypted USB drive (AES-256-GCM) for secondary offsite vault storage.
3. **Offline Thermal / Laser Printer**:
   - Dedicated USB printer with zero wireless capabilities (no Wi-Fi/Bluetooth chipsets) and volatile RAM only (no onboard hard drive or non-volatile storage).
4. **Physical Secure Storage & Supplies**:
   - Fireproof Safe: UL Class 350 4-hour fire endurance rating, dual-key / combination lock.
   - Tamper-Evident Bags: Sequentially numbered, high-security tamper-evident bags with tamper-indicating adhesive seams.
   - Faraday Cage / RF Shielded Enclosure: Room or portable tent providing >80dB attenuation across 10MHz - 10GHz.

---

## 4. Software Requirements

All software components must be pre-downloaded, verified via cryptographic SHA-256 hashes signed by the Verdis Core Security Team, and flashed onto USB Drive A prior to air-gapping.

1. **Operating System**:
   - Clean Ubuntu 24.04 LTS Live ISO or Tails OS booted in amnesic state with `tor=off` and all networking modules blacklisted.
2. **Substrate Key Generation Tooling**:
   - Official Substrate `subkey` binary compiled statically against Rust `stable-x86_64-unknown-linux-gnu`.
   - Custom `verdis-keytool` CLI utility for Substrate SS58 network 909 key derivation.
3. **Cryptographic & Utility Libraries**:
   - `qrencode` CLI tool for generating offline paper backup QR codes.
   - `openssl` CLI for AES-256-GCM private key bundle encryption.
   - `sha256sum` for file integrity manifest computation.
   - `shred` / `srm` for secure memory zeroization and disk wiping.

---

## 5. Entropy Requirements

To ensure complete non-predictability of private key generation, entropy must be sourced from a hybrid hardware and physical randomness protocol yielding a minimum of **256 bits of true entropy** per keypair.

1. **Hardware True Random Number Generator (TRNG)**:
   - Output from Linux kernel `/dev/hwrng` or connected certified TRNG hardware device (e.g., YubiHSM2 / TrueRNG).
2. **Physical Randomness (Casino Dice & Keyboard Jitter)**:
   - Roll of four casino-grade 20-sided dice (minimum 50 rolls per keypair) yielding raw physical randomness.
   - Rapid manual keyboard typing timing jitter combined with cursor mouse movements to feed the kernel entropy pool (`/dev/urandom`).
3. **Mixing Algorithm**:
   - Physical dice values, TRNG output, and `/dev/urandom` samples are concatenated and hashed via SHA-256 / BLAKE2b to seed the Substrate `sr25519` key generator.

---

## 6. Pre-Ceremony Preparation Protocol

Before beginning key generation, the following pre-ceremony validation steps must be completed:

1. **Room Physical Inspection**: RF sweep performed; Faraday enclosure active; room verified free of unauthorized listening devices, cameras, or wireless hardware.
2. **Device Search & Quarantine**: All participants surrender phones, smartwatches, cameras, and electronic equipment into RF-shielded lockers outside the perimeter.
3. **Hardware Packaging Inspection**: Ceremonial Officer Rojs and Witnesses inspect factory seals on the workstation, USB drives, printer, and tamper bags.
4. **Tool Integrity Verification**: Witness 1 verifies SHA-256 hashes of `subkey`, `qrencode`, and system binaries against signed release manifests.

---

## 7. Step-by-Step Ceremony Procedure

The key ceremony must follow these 14 sequential steps strictly:

### Step 1: Boot Air-Gapped Workstation
Boot the target workstation from USB Drive A (Clean Ubuntu Live / Tails OS). Ensure boot flags disable network device drivers (`modprobe.blacklist=iwlwifi,r8169,e1000e`).

### Step 2: Verify Network Isolation
Execute network diagnostic commands to prove complete offline status:
```bash
ip link show
rfkill list all
ifconfig
```
Witness 1 and Witness 2 verify that output displays zero active network interfaces (except local loopback `lo`).

### Step 3: Verify Tool Binaries & Environment
Mount USB Drive A read-only. Verify binary SHA-256 checksums:
```bash
sha256sum /media/liveos/tools/subkey
```
Confirm hash matches the published Verdis Chain release manifest signed by security leads.

### Step 4: Generate 21 Validator Keypairs
For each validator index `N` (01 to 21):
1. Collect physical dice entropy and append to `/dev/urandom`.
2. Generate Validator Stash keypair (`sr25519`, SS58 prefix 909):
   ```bash
   subkey generate --scheme sr25519 --network 909 > val_01_stash.tmp
   ```
3. Generate Controller keypair (`sr25519`, SS58 prefix 909).
4. Generate Session keys:
   - BABE key (`sr25519`)
   - GRANDPA key (`ed25519`)
   - ImOnline key (`sr25519`)
   - Authority Discovery key (`sr25519`)
5. Extract public keys, SS58 addresses, and session key hex payloads into `val_01_public.json`.

### Step 5: Generate 5 Treasury Multisig Keypairs
For each treasury signatory `M` (01 to 05):
1. Generate Signatory keypair (`sr25519`, SS58 prefix 909).
2. Extract public key address.
3. Combine all 5 public keys to compute the Verdis Chain 3-of-5 threshold multisig SS58 address (`SUBSTRATE_MULTISIG_PREFIX`).

### Step 6: Export Public Keys to USB Drive B
Mount USB Drive B. Write all public keys, SS58 addresses, BABE/GRANDPA session key hex strings, and multisig configuration to `verdis_mainnet_genesis_public_keys.json` and `KEY_INVENTORY.csv`.

### Step 7: Export Private Keys to Encrypted USB Drive C & D
1. Bundle private key seeds into an encrypted archive using AES-256-GCM encryption:
   ```bash
   openssl enc -aes-256-gcm -pbkdf2 -in private_keys.tar -out private_keys.enc
   ```
2. Passphrase is split into split-knowledge custodian shares (known only to assigned Key Custodians).
3. Copy `private_keys.enc` to USB Drive C (Primary) and USB Drive D (Secondary Offsite Backup).

### Step 8: Generate Paper Backups
Print paper backup sheets on the offline thermal printer for each keypair:
- Public SS58 Address
- Encrypted Seed / Mnemonic Backup
- High-density QR code representation of public key and encrypted seed
- Witness signature block

### Step 9: Compute Cryptographic SHA-256 Checksums
Compute checksums of all exported drives and paper manifests:
```bash
sha256sum /media/drive_b/* /media/drive_c/* > CHECKSUMS.sha256
```
Witnesses inspect and sign the `CHECKSUMS.sha256` printout.

### Step 10: Print Ceremony Manifest Log
Print complete execution log detailing key IDs, public addresses, SS58 formats, timestamp (UTC), and participant sign-offs.

### Step 11: Perform Keypair Verification Test
Perform an offline test signature and verification:
```bash
echo "Verdis Chain Genesis Test Payload" > test.txt
subkey sign --suri "<test_mnemonic>" test.txt > test.sig
subkey verify --scheme sr25519 <test_pubkey> test.txt test.sig
```
Witness 2 confirms signature validation output is `Signature valid`.

### Step 12: Seal Materials in Tamper-Evident Bags
Place USB Drive C, USB Drive D, and physical paper backups into designated sequentially numbered tamper-evident bags (Bag #VC-KEY-001 through #VC-KEY-008). Ceremonial Officer Rojs and all participants sign across bag seal flaps.

### Step 13: Deposit into Fireproof Safe & Offsite Vault
Transfer Bag #VC-KEY-001 (Primary Drive C + Primary Paper) to Primary Fireproof Safe. Transfer Bag #VC-KEY-002 (Secondary Drive D + Secondary Paper) to Offsite Bank Vault under dual-custody transport protocol.

### Step 14: Secure Zeroization of Air-Gapped Machine
Overwrite all temporary files, volatile RAM, and system swap:
```bash
shred -u -n 3 *.tmp *.tar *.enc
sync
```
Power off workstation, remove USB Drive A, and physically store or destroy memory modules if required.

---

## 8. Post-Ceremony Integration & Verification

1. **Genesis Specification Integration**:
   - Public keys and session key payloads from USB Drive B are imported into Verdis Chain `chain_spec.json`.
   - 3-of-5 Treasury Multisig address is configured as genesis treasury owner.
2. **Validator Node Session Key Injection**:
   - Session key payloads injected into individual node keystores via secure local RPC (`author_insertKey`).
3. **On-Chain Verification**:
   - Upon genesis block generation, verify that BABE block production and GRANDPA finality voting operate with 21 active validators.

---

## 9. Physical & Operational Security Protocols

- **Zero Camera / Recording Policy**: No cameras, video recorders, audio bugs, or wireless devices allowed in room during ceremony.
- **Physical Line-of-Sight**: All participants must maintain line-of-sight to workstation terminal and printer at all times.
- **Audit Log Preservation**: Physical signed ceremony log retained indefinitely in secure vault.

---
*End of Air-Gapped Key Ceremony Specification - Verdis Chain Foundation*
