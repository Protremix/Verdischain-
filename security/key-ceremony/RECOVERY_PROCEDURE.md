# Verdis Chain - Key Recovery & Key Rotation Procedure

**Document Version:** 1.0.0  
**Target Infrastructure:** Verdis Chain Mainnet (SS58 Network Prefix 909)  
**Governance Scope:** Validator Session Keys, Stash/Controller Accounts, 3-of-5 Treasury Multisig  
**Ceremonial Officer:** Rojs  
**Classification:** STRICTLY CONFIDENTIAL - OPERATIONAL STANDARD OPERATING PROCEDURE (SOP)  

---

## 1. Scope & Recovery Triggers

This document establishes the official standard operating procedure (SOP) for key recovery, session key rotation, and custodian replacement across the Verdis Chain network. 

Key recovery procedures are activated under four explicit operational conditions:
1. **Lost Key / Media Corruption**: Physical destruction, unreadable memory sectors, or missing encrypted USB storage media holding session or stash backing data.
2. **Suspected or Confirmed Key Compromise**: Unauthorized access, malware detection on node host, physical security breach of a custodian vault, or anomalous signing behavior.
3. **Custodian Unavailability**: Permanent incapacity, resignation, protocol removal, or prolonged unreachability of an assigned Key Custodian or Treasury Multisig signatory.
4. **Scheduled Key Hygiene / Key Rotation Policy**: Routine maintenance protocol mandating periodic rotation of active validator session keys (BABE/GRANDPA/ImOnline) every 90 days.

---

## 2. Required Participants & Authorization Matrix

Key recovery operations require strict quorum attendance based on the criticality of the affected key level:

| Recovery Level | Key Type Affected | Required Quorum | Authorized Lead |
|----------------|-------------------|-----------------|-----------------|
| **Level 1 (Routine)** | Validator Session Key (BABE/GRANDPA) | Node Operator + 1 Witness | Infrastructure Lead |
| **Level 2 (Urgent)** | Validator Stash / Controller Key | Affected Custodian + Rojs + 2 Witnesses | Ceremonial Officer (Rojs) |
| **Level 3 (Routine MSIG)** | Single Treasury Signatory (1 of 5) | 3 Remaining Signatories + Rojs | Ceremonial Officer (Rojs) |
| **Level 4 (Catastrophic)** | Multiple Treasury Signatories (≥3 of 5) | Technical Council Quorum + Rojs + 3 Witnesses | Technical Council / Rojs |

---

## 3. Validator Key Recovery & Rotation Mechanics

Substrate architecture cleanly separates long-term staking identity (Stash/Controller) from short-term consensus block-signing keys (Session Keys). This separation enables non-disruptive, rapid key rotation without unbonding staked funds.

```
+-------------------------------------------------------------------+
|                        STASH ACCOUNT (Offline)                    |
|                        Key Scheme: sr25519                        |
+----------------------------------+--------------------------------+
                                   |
                         staking.set_controller
                                   |
                                   v
+-------------------------------------------------------------------+
|                     CONTROLLER ACCOUNT (Online)                   |
|                        Key Scheme: sr25519                        |
+----------------------------------+--------------------------------+
                                   |
                           session.set_keys
                                   |
                                   v
+-------------------------------------------------------------------+
|                       ACTIVE SESSION KEYS                         |
|   BABE (sr25519) | GRANDPA (ed25519) | ImOnline (sr25519)            |
+-------------------------------------------------------------------+
```

### 3.1 Session Key Rotation (Routine & Emergency)
Session keys consist of four cryptographic components loaded into the Substrate validator node's local keystore:
- **BABE Key (`sr25519`)**: Block authoring slot allocation.
- **GRANDPA Key (`ed25519`)**: Chain finality gadget voter.
- **ImOnline Key (`sr25519`)**: Heartbeat uptime reporting to prevent offline slashes.
- **Authority Discovery Key (`sr25519`)**: DHT network address lookup.

#### Session Key Rotation Protocol (Step-by-Step):
1. **Generate New Session Keys on Validator Node**:
   Access the secure local RPC interface on the target validator node (port 9944, loopback only):
   ```bash
   curl -H "Content-Type: application/json" \
        -d '{"id":1, "jsonrpc":"2.0", "method":"author_rotateKeys", "params":[]}' \
        http://127.0.0.1:9944
   ```
   The node generates new session keys directly in memory, stores them in the secure keystore (`/var/lib/verdis/data/chains/verdis_mainnet/keystore`), and returns the combined public key hex string payload (`0x...`).

2. **Register New Session Keys On-Chain**:
   From the Controller account (or via Stash proxy), submit the `session.setKeys(keys, proof)` extrinsic to the Verdis Chain runtime:
   - `keys`: The combined hex payload returned by `author_rotateKeys`.
   - `proof`: Hex payload proof (0x00 for standard session key binding).

3. **Session Activation Latency**:
   The new session keys do NOT take effect instantly. In Substrate, session key updates take effect at the start of **Session N + 2** (2 session eras, approximately 4 hours on Verdis Mainnet). The validator must keep the old node keystore active until the era transition completes.

4. **Re-Registration & Verification**:
   Verify session key registration on-chain using the Verdis Chain RPC:
   ```bash
   curl -H "Content-Type: application/json" \
        -d '{"id":1, "jsonrpc":"2.0", "method":"session_validators", "params":[]}' \
        http://127.0.0.1:9944
   ```
   Confirm the validator SS58 address is active in the upcoming validator set.

---

### 3.2 Validator Stash / Controller Key Recovery
If a validator Controller key is compromised or lost, the offline Stash key is used to re-point control to a newly generated Controller account:

1. Perform air-gapped key ceremony to generate a new Controller keypair (`sr25519`, SS58 network 909).
2. From the air-gapped Stash account, submit `staking.set_controller(new_controller_ss58)`.
3. The new Controller immediately assumes operational control over validator staking and session key registration.
4. If the Stash key itself is lost or compromised, the validator must execute `staking.unbond` (subject to unbonding period) and migrate stake to a newly generated Stash key pair.

---

## 4. Treasury Multisig Key Recovery Procedures

Verdis Chain Mainnet Treasury is secured by a **3-of-5 Threshold Multisig Account** (`sr25519`, SS58 prefix 909) comprising 5 distinct Key Custodians.

```
       [ Treasury Signatory 1 ] -----       [ Treasury Signatory 2 ] ------       [ Treasury Signatory 3 ] -------+---> [ 3-of-5 Multisig Account ] ---> Verdis Treasury Vault
       [ Treasury Signatory 4 ] ------/
       [ Treasury Signatory 5 ] -----/
```

### 4.1 Scenario A: Single Signatory Key Lost or Compromised (Threshold Intact)
If 1 or 2 signatories are lost or compromised, the threshold of **3 valid signatories remains intact**. The remaining operational signatories can execute an on-chain key replacement without chain downtime or hard forks.

#### Execution Steps (Step-by-Step):
1. **Convene Emergency Custodian Session**: Ceremonial Officer Rojs convenes the remaining valid signatories (at least 3 active custodians required).
2. **Generate Replacement Signatory Key**:
   Execute a mini air-gapped key ceremony following `KEY_CEREMONY_SPEC.md` to derive a new Treasury Signatory keypair (`sr25519`, prefix 909).
3. **Construct Multisig Rotation Extrinsic**:
   The active 3 signatories construct a Substrate batch transaction:
   ```rust
   // Pseudo-code representation of Substrate multisig migration call
   multisig.as_multi(
       threshold: 3,
       other_signatories: [Signatory_2, Signatory_3, Signatory_4, Signatory_5],
       call: system.remark("Replace Signatory 1 with New_Signatory_1")
   );
   ```
4. **Deploy Updated Multisig Identity**:
   - Register the new 5-member account set: `[New_Signatory_1, Signatory_2, Signatory_3, Signatory_4, Signatory_5]`.
   - Transfer Treasury ownership balance and proxy rights to the updated 3-of-5 Multisig SS58 address.
5. **Revoke Old Signatory Key**: Update physical key inventory (`KEY_INVENTORY_TEMPLATE.csv`) marking the old signatory key as `REVOKED_COMPROMISED`.

---

### 4.2 Scenario B: Catastrophic Loss (3 or More Signatories Lost)
If 3 or more Treasury signatories become permanently unavailable or compromised, the 3-of-5 threshold cannot be met through standard multisig calls.

#### Catastrophic Emergency Protocol:
1. **Technical Council Emergency Motion**:
   The Verdis Chain Technical Council convenes an emergency governance session under Section 5 of `EMERGENCY_PROCEDURE.md`.
2. **Fast-Track Democracy Motion**:
   A fast-track referendum is submitted (`democracy.fast_track`) to dispatch a `sudo` / `system.set_code` runtime upgrade or direct treasury state patch.
3. **State Patch Execution**:
   The runtime state modification updates the storage key for `pallet_treasury` owner address to point to the newly derived 3-of-5 Multisig account created during an emergency air-gapped recovery ceremony led by Rojs.

---

## 5. Offsite Backup Access & Custodian Handover Protocol

To access encrypted USB Drive D or physical paper backups stored in the offsite bank vault:

1. **Dual-Custody Authorization**: Minimum 2 authorized custodians (including Ceremonial Officer Rojs) must present physical photo identification at the bank vault facility.
2. **Tamper Bag Seal Audit**: Inspect Tamper Bag #VC-KEY-002 serial number and seal flap prior to opening. Record seal condition in the physical vault log.
3. **Custodian Deprovisioning Procedure**:
   - When a key custodian resigns or is replaced, their AES-256 passphrase share is rendered invalid by rotating the master encryption container during the next scheduled recovery ceremony.
   - All physical paper backup copies associated with the departing custodian are shredded using a DIN 66399 Level P-7 high-security shredder.

---

## 6. Classification of Recovery Execution Workflows

Recovery procedures are divided into two distinct operational timelines:

### 6.1 Time-Sensitive Emergency Recovery (0 - 4 Hours)
*Trigger:* Confirmed session key theft, active validator double-signing threat, or active security exploit.

1. **T+00:00**: Incident Commander or Rojs issues **Red Alert**.
2. **T+00:15**: Affected validator operator immediately chills validator node (`staking.chill`) to exit active validator set and prevent slashes.
3. **T+00:30**: Execute emergency session key rotation (`author_rotateKeys`) on backup air-gapped host.
4. **T+01:00**: Submit `session.setKeys` on-chain.
5. **T+04:00**: Verify session activation at era boundary and un-chill validator.

### 6.2 Non-Urgent Scheduled Recovery / Custodian Migration (1 - 7 Days)
*Trigger:* Personnel departure, routine key hygiene rotation, hardware upgrade.

1. **Day 1**: Formal notice submitted to Ceremonial Officer Rojs; schedule air-gapped ceremony.
2. **Day 2**: Pre-ceremony checklist verification and physical vault preparation.
3. **Day 3**: Air-gapped generation of replacement keys and USB Drive C/D update.
4. **Day 4**: On-chain rotation call execution and witness attestation logging.
5. **Day 7**: Post-recovery audit report filed and inventory manifest updated.

---

## 7. Audit & Documentation Requirements

Every recovery event must produce a complete, cryptographically verifiable audit trail including:

1. **Recovery Incident Log (RIL)**: Documenting trigger cause, affected key IDs, timestamps (UTC), and participants.
2. **Cryptographic Checksum Manifest**: SHA-256 hashes of all updated public key JSON files.
3. **Witness Attestation Form**: Physical signatures of Ceremonial Officer Rojs, Key Custodians, and independent Witnesses.
4. **Updated Key Inventory File**: Check-in of updated `KEY_INVENTORY_TEMPLATE.csv` into secure vault archive.

### Recovery Execution Log Sheet

| Recovery Field | Operational Data |
|----------------|------------------|
| **Recovery Event ID** | REC-2026-XXXX |
| **Recovery Type** | Session Rotation [ ] / Stash Repoint [ ] / Treasury MSIG [ ] |
| **Affected Key Identifier** | <KEY_ID> |
| **Lead Operator** | [Operator Name] |
| **Authorizing Officer** | Rojs |
| **Witness 1 Signature** | _______________________ |
| **Witness 2 Signature** | _______________________ |
| **Status After Recovery** | ROTATION_VERIFIED_ACTIVE |

---
*End of Key Recovery & Rotation Procedure - Verdis Chain Foundation*
