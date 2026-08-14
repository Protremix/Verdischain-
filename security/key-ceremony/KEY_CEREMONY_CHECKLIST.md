# Verdis Chain - Air-Gapped Key Ceremony Operational Checklist

**Document ID:** VC-CEREMONY-CHK-2026-V1  
**Target Chain:** Verdis Chain Mainnet (SS58 Network Prefix 909)  
**Ceremonial Officer:** Rojs  
**Facility Location:** Air-Gapped Secure Facility (Vault Alpha)  
**Execution Date:** 2026-08-14  

---

## Instructions for Participants
- Every step must be executed in strict numerical sequence without exception.
- Every checklist item requires an explicit checkmark `[X]`, the printed name of the Responsible Person, and the signature/verification of Witness 1 or Witness 2.
- Any discrepancy, hardware fault, unexpected system message, or physical seal failure halts the ceremony immediately for investigation.

---

## Participant Attendance & Verification Register

| Role | Name | Organization / Entity | ID Document Verified | Signature |
|------|------|-----------------------|----------------------|-----------|
| **Ceremonial Officer** | Rojs | Verdis Chain Foundation | Passport / Gov ID [X] | ____________________ |
| **Key Generator** | [Technician Name] | Core Security Operations | Passport / Gov ID [X] | ____________________ |
| **Witness 1** | [Auditor Name] | Independent Audit Firm | Passport / Gov ID [X] | ____________________ |
| **Witness 2** | [Engineering Lead] | Core Protocol Engineering | Passport / Gov ID [X] | ____________________ |
| **Security Observer** | [Security Lead] | Physical Vault Operations | Passport / Gov ID [X] | ____________________ |

---

## Equipment & Media Serial Number Registry

| Equipment Identifier | Description / Model | Factory Serial Number | Inspection Status |
|----------------------|---------------------|-----------------------|-------------------|
| **Workstation WS-01** | Air-Gapped Workstation (No Wireless) | <SERIAL_WS_01> | Verified Clean [ ] |
| **USB Drive A** | Clean Boot Live OS (16GB) | <SERIAL_USB_A> | Sealed / Verified [ ] |
| **USB Drive B** | Public Key Export (16GB) | <SERIAL_USB_B> | Sealed / Verified [ ] |
| **USB Drive C** | Primary Encrypted Vault (32GB) | <SERIAL_USB_C> | Sealed / Verified [ ] |
| **USB Drive D** | Offsite Encrypted Vault (32GB) | <SERIAL_USB_D> | Sealed / Verified [ ] |
| **Printer PR-01** | USB Thermal / Laser Offline Printer | <SERIAL_PRNT_01> | Sealed / Verified [ ] |
| **Safe SF-01** | Dual-Lock Fireproof Vault (UL 350) | <SERIAL_SAFE_01> | Lock Verified [ ] |
| **Tamper Bag VC-001** | Primary Vault Security Bag | VC-KEY-BAG-001 | Seal Intact [ ] |
| **Tamper Bag VC-002** | Secondary Offsite Security Bag | VC-KEY-BAG-002 | Seal Intact [ ] |

---

## 1. Pre-Ceremony Checklist (Facility, Hardware & Software Verification)

| # | Item Description | Responsible Person | Witness Verification | Status |
|---|------------------|--------------------|----------------------|--------|
| **1.1** | Verify physical perimeter of secure room (Faraday cage / windowless enclosure) | Security Observer | Witness 1: __________________ | [ ] |
| **1.2** | Perform RF spectrum sweep (10MHz - 10GHz) to confirm zero wireless/cellular signals | Security Observer | Witness 2: __________________ | [ ] |
| **1.3** | Confirm all room entrance doors are locked and physical access logging is active | Security Observer | Witness 1: __________________ | [ ] |
| **1.4** | Surrender all personal electronic devices (phones, smartwatches, trackers) into RF locker | Ceremonial Officer (Rojs) | Witness 2: __________________ | [ ] |
| **1.5** | Confirm Faraday RF storage locker is locked and key retained by Security Observer | Security Observer | Witness 1: __________________ | [ ] |
| **1.6** | Inspect air-gapped workstation packaging for factory seal integrity | Key Generator | Witness 2: __________________ | [ ] |
| **1.7** | Verify workstation motherboard has no internal Wi-Fi/Bluetooth cards installed | Key Generator | Witness 1: __________________ | [ ] |
| **1.8** | Verify Ethernet RJ-45 port is disabled or physically blocked with tamper plug | Key Generator | Witness 2: __________________ | [ ] |
| **1.9** | Inspect 4x USB flash drives packaging (Drive A, B, C, D) for serial number matching | Key Generator | Witness 1: __________________ | [ ] |
| **1.10** | Log serial numbers of USB Drive A, Drive B, Drive C, and Drive D into registry | Key Generator | Witness 2: __________________ | [ ] |
| **1.11** | Inspect offline printer packaging and verify zero wireless antenna / Bluetooth chipset | Key Generator | Witness 1: __________________ | [ ] |
| **1.12** | Load clean, unprinted paper stock into offline USB thermal printer | Key Generator | Witness 2: __________________ | [ ] |
| **1.13** | Inspect sequentially numbered tamper-evident bags (#VC-KEY-001 through #VC-KEY-008) | Security Observer | Witness 1: __________________ | [ ] |
| **1.14** | Verify Fireproof Safe (UL Class 350) dual-combination lock mechanisms operating | Security Observer | Witness 2: __________________ | [ ] |
| **1.15** | Inspect casino-grade 20-sided dice set for balance and physical integrity | Ceremonial Officer (Rojs) | Witness 1: __________________ | [ ] |
| **1.16** | Mount USB Drive A (Clean Live OS) on air-gapped workstation | Key Generator | Witness 2: __________________ | [ ] |
| **1.17** | Power on air-gapped workstation and enter BIOS setup | Key Generator | Witness 1: __________________ | [ ] |
| **1.18** | Confirm BIOS wireless, Bluetooth, camera, and network boot features are disabled | Key Generator | Witness 2: __________________ | [ ] |
| **1.19** | Boot Ubuntu 24.04 LTS Live OS with network driver blacklist parameters | Key Generator | Witness 1: __________________ | [ ] |
| **1.20** | Execute `ip link show` and confirm only loopback interface `lo` exists | Key Generator | Witness 2: __________________ | [ ] |
| **1.21** | Execute `rfkill list all` and confirm soft/hard block on all wireless states | Key Generator | Witness 1: __________________ | [ ] |
| **1.22** | Mount tool binary directory on USB Drive A in read-only mode (`ro`) | Key Generator | Witness 2: __________________ | [ ] |
| **1.23** | Compute SHA-256 hash of `/usr/local/bin/subkey` binary | Key Generator | Witness 1: __________________ | [ ] |
| **1.24** | Verify `subkey` SHA-256 hash matches official Verdis release manifest | Witness 1 | Witness 2: __________________ | [ ] |
| **1.25** | Compute SHA-256 hash of `verdis-keytool` CLI utility | Key Generator | Witness 1: __________________ | [ ] |
| **1.26** | Verify `verdis-keytool` hash matches official Verdis release manifest | Witness 1 | Witness 2: __________________ | [ ] |
| **1.27** | Compute SHA-256 hash of `qrencode` utility | Key Generator | Witness 1: __________________ | [ ] |
| **1.28** | Connect offline thermal printer directly via USB cable to workstation | Key Generator | Witness 2: __________________ | [ ] |
| **1.29** | Print test diagnostic page and confirm zero network connection headers | Key Generator | Witness 1: __________________ | [ ] |
| **1.30** | Verify presence of all required participants: Rojs, Key Gen, Witness 1, Witness 2, Security | Ceremonial Officer (Rojs) | Witness 2: __________________ | [ ] |
| **1.31** | Conduct mandatory pre-ceremony briefing and review safety rules | Ceremonial Officer (Rojs) | Witness 1: __________________ | [ ] |
| **1.32** | Formal sign-off on Pre-Ceremony Readiness by Ceremonial Officer Rojs | Ceremonial Officer (Rojs) | Witness 2: __________________ | [ ] |

---

## 2. During Ceremony Checklist (Step-by-Step Execution)

| # | Execution Step | Responsible Person | Witness Verification | Status |
|---|----------------|--------------------|----------------------|--------|
| **2.1** | Confirm workstation is booted in clean RAM-only Live environment | Key Generator | Witness 1: __________________ | [ ] |
| **2.2** | Re-verify network interface down status (`ifconfig -a`) | Key Generator | Witness 2: __________________ | [ ] |
| **2.3** | Seed kernel entropy pool with 50 physical casino dice rolls | Key Generator | Witness 1: __________________ | [ ] |
| **2.4** | Generate Validator 01 Keypair (Stash, Controller, BABE sr25519, GRANDPA ed25519, Session) | Key Generator | Witness 2: __________________ | [ ] |
| **2.5** | Generate Validator 02 Keypair (Stash, Controller, BABE sr25519, GRANDPA ed25519, Session) | Key Generator | Witness 1: __________________ | [ ] |
| **2.6** | Generate Validator 03 Keypair (Stash, Controller, BABE sr25519, GRANDPA ed25519, Session) | Key Generator | Witness 2: __________________ | [ ] |
| **2.7** | Generate Validator 04 Keypair (Stash, Controller, BABE sr25519, GRANDPA ed25519, Session) | Key Generator | Witness 1: __________________ | [ ] |
| **2.8** | Generate Validator 05 Keypair (Stash, Controller, BABE sr25519, GRANDPA ed25519, Session) | Key Generator | Witness 2: __________________ | [ ] |
| **2.9** | Generate Validator 06 Keypair (Stash, Controller, BABE sr25519, GRANDPA ed25519, Session) | Key Generator | Witness 1: __________________ | [ ] |
| **2.10**| Generate Validator 07 Keypair (Stash, Controller, BABE sr25519, GRANDPA ed25519, Session) | Key Generator | Witness 2: __________________ | [ ] |
| **2.11**| Generate Validator 08 Keypair (Stash, Controller, BABE sr25519, GRANDPA ed25519, Session) | Key Generator | Witness 1: __________________ | [ ] |
| **2.12**| Generate Validator 09 Keypair (Stash, Controller, BABE sr25519, GRANDPA ed25519, Session) | Key Generator | Witness 2: __________________ | [ ] |
| **2.13**| Generate Validator 10 Keypair (Stash, Controller, BABE sr25519, GRANDPA ed25519, Session) | Key Generator | Witness 1: __________________ | [ ] |
| **2.14**| Generate Validator 11 Keypair (Stash, Controller, BABE sr25519, GRANDPA ed25519, Session) | Key Generator | Witness 2: __________________ | [ ] |
| **2.15**| Generate Validator 12 Keypair (Stash, Controller, BABE sr25519, GRANDPA ed25519, Session) | Key Generator | Witness 1: __________________ | [ ] |
| **2.16**| Generate Validator 13 Keypair (Stash, Controller, BABE sr25519, GRANDPA ed25519, Session) | Key Generator | Witness 2: __________________ | [ ] |
| **2.17**| Generate Validator 14 Keypair (Stash, Controller, BABE sr25519, GRANDPA ed25519, Session) | Key Generator | Witness 1: __________________ | [ ] |
| **2.18**| Generate Validator 15 Keypair (Stash, Controller, BABE sr25519, GRANDPA ed25519, Session) | Key Generator | Witness 2: __________________ | [ ] |
| **2.19**| Generate Validator 16 Keypair (Stash, Controller, BABE sr25519, GRANDPA ed25519, Session) | Key Generator | Witness 1: __________________ | [ ] |
| **2.20**| Generate Validator 17 Keypair (Stash, Controller, BABE sr25519, GRANDPA ed25519, Session) | Key Generator | Witness 2: __________________ | [ ] |
| **2.21**| Generate Validator 18 Keypair (Stash, Controller, BABE sr25519, GRANDPA ed25519, Session) | Key Generator | Witness 1: __________________ | [ ] |
| **2.22**| Generate Validator 19 Keypair (Stash, Controller, BABE sr25519, GRANDPA ed25519, Session) | Key Generator | Witness 2: __________________ | [ ] |
| **2.23**| Generate Validator 20 Keypair (Stash, Controller, BABE sr25519, GRANDPA ed25519, Session) | Key Generator | Witness 1: __________________ | [ ] |
| **2.24**| Generate Validator 21 Keypair (Stash, Controller, BABE sr25519, GRANDPA ed25519, Session) | Key Generator | Witness 2: __________________ | [ ] |
| **2.25**| Generate Treasury Signatory Key 01 (sr25519, SS58 prefix 909) | Key Generator | Witness 1: __________________ | [ ] |
| **2.26**| Generate Treasury Signatory Key 02 (sr25519, SS58 prefix 909) | Key Generator | Witness 2: __________________ | [ ] |
| **2.27**| Generate Treasury Signatory Key 03 (sr25519, SS58 prefix 909) | Key Generator | Witness 1: __________________ | [ ] |
| **2.28**| Generate Treasury Signatory Key 04 (sr25519, SS58 prefix 909) | Key Generator | Witness 2: __________________ | [ ] |
| **2.29**| Generate Treasury Signatory Key 05 (sr25519, SS58 prefix 909) | Key Generator | Witness 1: __________________ | [ ] |
| **2.30**| Derive 3-of-5 Treasury Multisig SS58 Account Address | Key Generator | Witness 2: __________________ | [ ] |
| **2.31**| Mount USB Drive B and export unencrypted Public Key Manifest (`public_keys.json`) | Key Generator | Witness 1: __________________ | [ ] |
| **2.32**| Encrypt Private Key archive using AES-256-GCM with custodian split passphrases | Key Generator | Witness 2: __________________ | [ ] |
| **2.33**| Copy encrypted Private Key archive (`private_keys.enc`) to USB Drive C (Primary) | Key Generator | Witness 1: __________________ | [ ] |
| **2.34**| Copy encrypted Private Key archive (`private_keys.enc`) to USB Drive D (Secondary) | Key Generator | Witness 2: __________________ | [ ] |
| **2.35**| Print paper backup sheets (Public Addresses + Encrypted Seed QR Codes) | Key Generator | Witness 1: __________________ | [ ] |
| **2.36**| Calculate SHA-256 checksums of USB Drive B, C, D exports and display on screen | Key Generator | Witness 2: __________________ | [ ] |
| **2.37**| Print physical ceremony execution log and cryptographic checksum manifest | Key Generator | Witness 1: __________________ | [ ] |
| **2.38**| Perform test signature and verification using `subkey sign` and `subkey verify` | Key Generator | Witness 2: __________________ | [ ] |
| **2.39**| Witness 1 and Witness 2 verify test signature return code: VALID | Witness 1 & 2 | Witness 1: __________________ | [ ] |
| **2.40**| Seal USB Drive C and Primary Paper Backups in Tamper Bag #VC-KEY-001 | Security Observer | Witness 2: __________________ | [ ] |
| **2.41**| Seal USB Drive D and Secondary Paper Backups in Tamper Bag #VC-KEY-002 | Security Observer | Witness 1: __________________ | [ ] |
| **2.42**| All participants sign across seal flaps on Tamper Bags #VC-KEY-001 and #VC-KEY-002 | All Participants | Witness 2: __________________ | [ ] |
| **2.43**| Store Tamper Bag #VC-KEY-001 inside Primary Fireproof Safe | Security Observer | Witness 1: __________________ | [ ] |
| **2.44**| Zeroize RAM and wipe temporary storage on air-gapped workstation (`shred -u`) | Key Generator | Witness 2: __________________ | [ ] |
| **2.45**| Power off air-gapped workstation and disconnect offline printer | Key Generator | Witness 1: __________________ | [ ] |

---

## 3. Post-Ceremony Checklist (Verification, Storage & Chain Genesis)

| # | Action Item | Responsible Person | Witness Verification | Status |
|---|-------------|--------------------|----------------------|--------|
| **3.1** | Remove USB Drive B (Public Keys) from secure facility for genesis integration | Key Generator | Witness 1: __________________ | [ ] |
| **3.2** | Verify USB Drive B SHA-256 hash on staging machine matches ceremony log | Key Generator | Witness 2: __________________ | [ ] |
| **3.3** | Import 21 Validator session public keys into Verdis Chain `chain_spec.json` | Core Engineer | Witness 1: __________________ | [ ] |
| **3.4** | Configure 3-of-5 Treasury Multisig address as genesis treasury owner | Core Engineer | Witness 2: __________________ | [ ] |
| **3.5** | Inject session keys into 21 validator node keystores via secure local RPC | Infrastructure Lead | Witness 1: __________________ | [ ] |
| **3.6** | Verify validator session keystore file permissions (`0400` root-only access) | Security Observer | Witness 2: __________________ | [ ] |
| **3.7** | Transport Tamper Bag #VC-KEY-002 to Offsite Bank Vault under dual-custody transport | Security Observer | Witness 1: __________________ | [ ] |
| **3.8** | Confirm receipt and vault logging of Bag #VC-KEY-002 by Offsite Custodian | Security Observer | Witness 2: __________________ | [ ] |
| **3.9** | Publish Public Key Manifest (`public_keys.json`) to official GitHub repository | Core Engineer | Witness 1: __________________ | [ ] |
| **3.10**| Launch Verdis Chain Genesis Block and verify BABE slot production | Core Engineer | Witness 2: __________________ | [ ] |
| **3.11**| Verify GRANDPA block finality voting by 21 active validators on-chain | Core Engineer | Witness 1: __________________ | [ ] |
| **3.12**| Verify 3-of-5 Treasury Multisig on-chain account status and threshold | Core Engineer | Witness 2: __________________ | [ ] |
| **3.13**| File complete physical signed ceremony log in Vault Alpha archival safe | Ceremonial Officer (Rojs) | Witness 1: __________________ | [ ] |
| **3.14**| Publish official Ceremony Attestation Statement signed by Rojs and Witnesses | Ceremonial Officer (Rojs) | Witness 2: __________________ | [ ] |

---

## 4. Final Ceremony Sign-Off & Attestation

We, the undersigned participants, hereby certify under penalty of perjury and protocol breach that the air-gapped key ceremony for Verdis Chain was executed in absolute compliance with the specification above. We confirm that no private key material was exposed to network connectivity, unapproved recording equipment, or unencrypted media.

**Ceremonial Officer (Rojs):**  
Signature: ____________________________________ Date: 2026-08-14 Time: _________ UTC  

**Key Generator:**  
Signature: ____________________________________ Date: 2026-08-14 Time: _________ UTC  

**Witness 1 (Auditor):**  
Signature: ____________________________________ Date: 2026-08-14 Time: _________ UTC  

**Witness 2 (Engineering Lead):**  
Signature: ____________________________________ Date: 2026-08-14 Time: _________ UTC  

**Security Observer:**  
Signature: ____________________________________ Date: 2026-08-14 Time: _________ UTC  

---
*End of Operational Checklist - Verdis Chain Key Ceremony Protocol*
