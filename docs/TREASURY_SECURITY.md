# VERDIS CHAIN — TREASURY SECURITY SPECIFICATION & AUDIT POLICY

**Document Version:** 1.0.0  
**Effective Date:** August 2026  
**Status:** APPROVED SPECIFICATION (Implementation Pending Key Ceremony)  
**Project:** Verdis Chain (Substrate DPoS, Runtime v14)  
**Treasury Allocation:** 20,000,000,000 VRDX (20% of 100B Total Supply, 9 Decimals)  
**References:** `verdis-chain/docs/TREASURY_SECURITY_SPEC.md`, `verdis-chain/docs/TREASURY_POLICY.md`  

---

## 1. EXECUTIVE SUMMARY & ALLOCATION OVERVIEW

The Verdis Chain Treasury holds **20,000,000,000 VRDX** tokens (20 Billion units with 9 decimals = $20,000,000,000,000,000,000$ base plancks). It is designed to fund ecosystem growth, validator security incentives, research, developer grants, and emergency response operations over a multi-decade horizon.

Because of the critical magnitude of these funds, single-key control or single-governance authority over the Treasury is strictly prohibited. Control is governed by a dual-layer cryptographic and protocol mechanism: **Council 2/3 Governance Approval + 3-of-5 Air-Gapped Cold-Storage Multisignature Authorization**.

---

## 2. CURRENT STATE VS. MAINNET TARGET STATE

| Dimension | Current Testnet State (Block #29400+) | Mainnet Target State |
|---|---|---|
| **Treasury Account ID** | `PalletId(*b"verdist0")` (Pallet-controlled) | `PalletId(*b"verdist0")` (Unchanged) |
| **Team / Admin Control** | `PalletId(*b"verdistm")` (**Placeholder**) | **Real 3-of-5 Multisig Address** (derived from key ceremony) |
| **Multisig Pallet** | `pallet_multisig` (Instance 38) | `pallet_multisig` configured in genesis with 5 signatories |
| **Spend Origin** | Governance Council 2/3 (`EnsureCouncilSpend`) | Dual Origin: Council 2/3 + 3-of-5 Multisig Approval |
| **Signer Threshold** | Governance Vote | **3 of 5 independent signers required** |
| **Key Generation** | Local CLI Keyring | Air-gapped cold key ceremony (`scripts/air-gapped-key-ceremony.sh`) |

---

## 3. ARCHITECTURE & MULTISIG SPECIFICATIONS

```
+-----------------------------------------------------------------------+
|                    TREASURY SPEND APPROVAL PIPELINE                   |
+-----------------------------------------------------------------------+
| 1. Grant / Spend Proposal Submitted on-chain                          |
| 2. Governance Council Review -> Requires 2/3 Majority Approval         |
| 3. 3-of-5 Multisig Review    -> 5 Independent Signers Review Hash     |
| 4. Signatures Collected      -> Minimum 3 Independent Signatures       |
| 5. On-Chain Execution        -> pallet_multisig releases funds        |
+-----------------------------------------------------------------------+
```

### 3.1 Mathematical Address Derivation
The target 3-of-5 Treasury multisig account is constructed deterministically using Substrate's standard `pallet_multisig` address calculation formula:

$$\text{MultisigAddress} = \text{AccountId32}\Big(\text{blake2\_256}\big(\text{Threshold} \mathbin{\Vert} \text{SortedSignatories}\big)\Big)$$

Where:
- $\text{Threshold} = 3$
- $\text{SortedSignatories} = [\text{Signer}_1, \text{Signer}_2, \text{Signer}_3, \text{Signer}_4, \text{Signer}_5]$ (sorted lexicographically by public key bytes).

### 3.2 Key Ceremony Dependency
Replacing `PalletId(*b"verdistm")` with the computed multisig address requires executing `verdis-chain/scripts/air-gapped-key-ceremony.sh` and invoking `scripts/import-mainnet-keys.py` to patch `node/src/chain_spec.rs:mainnet_genesis()`.

---

## 4. SECURITY CONTROLS & GUARANTEES

### 4.1 Replay Protection
All multisig transaction calls in Substrate incorporate strict replay protection:
1. **Call Hash Verification:** Signers approve an explicit 32-byte `call_hash` rather than arbitrary byte payloads.
2. **Timepoint Binding:** Every pending multisig approval is bound to a specific block height and extrinsic index (`Timepoint { height, index }`). Replaying an old signature on a subsequent block is rejected by `pallet_multisig`.
3. **Chain ID Verification:** Cryptographic signatures include `sp_core::crypto::Header` and unique `genesis_hash` payload binding.

### 4.2 Spending Limits & Velocity Controls
To prevent rapid depletion of Treasury reserves in the event of compromised governance or multisig keys:
- **Spend Period:** Enforced spend period of 600 blocks (~1 hour on 6-second slot time).
- **Per-Period Ceiling:** Maximum Treasury spend per period is capped at **1% of total Treasury balance** (200,000,000 VRDX).
- **Large-Proposal Time Lock:** Proposals exceeding 50,000,000 VRDX require a **7-day enactment delay** on-chain, allowing community and security taskforce intervention if malicious intent is detected.

### 4.3 Prohibited Uses & Invariant Safeguards
- **No Token Burn:** Treasury burn rate is set to **0%** to preserve the strict 100 Billion VRDX total supply invariant.
- **No Team Enrichment:** Direct transfers from `verdist0` to team allocation vesting accounts are blocked at runtime.
- **No Unapproved Loans:** Collateralized lending of Treasury reserves to third-party protocols is forbidden.

---

## 5. SIGNER CUSTODY, ROTATION & RECOVERY

### 5.1 Physical Custody Matrix
- **5 Independent Custodians:** 5 distinct security officers across 5 separate geographical regions.
- **Air-Gapped Hardware:** Each signer uses a dedicated, air-gapped signing hardware device or air-gapped Linux machine.
- **Zero Network Exposure:** Seed phrases are never entered on internet-connected hosts.

### 5.2 Signer Key Rotation Procedure
Signers must be rotated if a custodian leaves the project or key compromise is suspected:
1. Generate a new keypair for the replacement custodian via the air-gapped key ceremony protocol.
2. The current 3-of-5 multisig executes an on-chain extrinsic invoking `pallet_multisig` to register the new 5-signatory array and re-derive the multisig address.
3. Migrate remaining Treasury balance from the old multisig address to the newly derived address via an atomic spend proposal.

### 5.3 Emergency Recovery & Threshold Resilience
- The 3-of-5 threshold provides **fault tolerance for up to 2 key losses**:
  - If 1 custodian loses access: The remaining 4 signers can safely execute a rotation proposal.
  - If 2 custodians lose access: The remaining 3 signers can still achieve threshold and execute a rotation proposal.
  - If $\ge 3$ custodians lose access: Treasury transfers are locked. Recovery requires invocation of the Emergency Governance Origin (Constitution Article 16) to execute a runtime patch.

---

## 6. ON-CHAIN AUDIT TRAIL & TRANSPARENCY

1. Every Treasury proposal, approval, rejection, and disbursement emits native Substrate runtime events:
   - `pallet_treasury::Event::Proposed { proposal_index }`
   - `pallet_treasury::Event::Awarded { proposal_index, award, beneficiary }`
   - `pallet_multisig::Event::NewMultisig { approving, multisig, call_hash }`
   - `pallet_multisig::Event::MultisigExecuted { approving, multisig, call_hash, result }`
2. All events are indexed in real-time by the Verdis Explorer (`91.98.160.145`) and made publicly verifiable.
