# VERDIS CHAIN — COMPREHENSIVE THREAT MODEL

**Document Version:** 1.0.0  
**Effective Date:** August 2026  
**Status:** APPROVED  
**Project:** Verdis Chain (Substrate DPoS, BABE/GRANDPA, Runtime v14)  
**Native Token:** VRDX (100 Billion Total Supply, 9 Decimals)  
**Scope:** Core Runtime (16 Pallets), Infrastructure, P2P Consensus, Cryptoeconomics, Key Infrastructure  

---

## 1. EXECUTIVE SUMMARY & METHODOLOGY

This Threat Model utilizes the STRIDE framework (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) tailored specifically for the Substrate-based Verdis Chain architecture. It identifies core protocol assets, potential adversary profiles, specific attack vectors, deployed mitigations, and residual risks.

---

## 2. SYSTEM ARCHITECTURE & ASSET IDENTIFICATION

Verdis Chain manages critical high-value state across 16 core pallets and network infrastructure:

```
+-----------------------------------------------------------------------+
|                         VERDIS CHAIN ASSETS                           |
+------------------------------------+----------------------------------+
| 1. Consensus & Block Finality      | BABE slot election & GRANDPA     |
| 2. Token Supply Invariant          | 100B VRDX max issuance           |
| 3. Treasury Pool                   | 20B VRDX (3-of-5 Multisig)       |
| 4. Validator Set & Staking Pool    | 21 active validators             |
| 5. DEX Liquidity Pools             | 6 active pools (AMM-DEX)          |
| 6. User Escrow & Vesting Accounts  | Presale & team vesting pallets   |
+------------------------------------+----------------------------------+
```

### 2.1 Critical Asset Catalog

| Asset | Description | Impact of Compromise |
|---|---|---|
| **Consensus & Finality** | BABE slot allocation and GRANDPA voter chain finalization. | Chain split, finality stall, re-orgs, double-spending. |
| **100B Token Supply Invariant** | Total supply cap of 100,000,000,000 VRDX (9 decimals). | Hyperinflation, complete token devaluation, loss of economic trust. |
| **Treasury Pool (20B VRDX)** | On-chain reserve held for ecosystem growth and security. | Complete drain of project reserves ($20\text{B VRDX}$). |
| **DEX Liquidity Pools** | Reserves across 6 AMM pools (VRDX pair tokens). | Liquidity drain, impermanent loss exploit, pool bricking. |
| **Validator Staking Balances** | Stake deposited by validators (10M VRDX active threshold) & delegators. | Sybil takeover, un-slashed double-signing, economic theft. |
| **User Funds & Smart Contracts** | Individual non-custodial user balances and WASM contract state. | Direct theft of user assets, smart contract state corruption. |

---

## 3. THREAT ACTOR PROFILES

Verdis Chain models four primary threat actor profiles based on capability, resources, and motivation:

| Threat Actor Profile | Capabilities & Motivation | Target Vector |
|---|---|---|
| **1. Malicious / Colluding Validator** | Controls 1 or more of the 21 active validator nodes. Seeks maximum MEV, double-signing rewards, or consensus disruption. | BABE equivocation, GRANDPA double-voting, censorship, front-running. |
| **2. Well-Funded Stake Attacker** | Acquires substantial VRDX tokens to gain >33% or >67% effective stake weight. | DPoS stake manipulation, finality block, governance proposal takeover. |
| **3. Network / Infrastructure Attacker** | Controls botnets or ISP-level transit routing. Seeks service disruption or eclipse attacks. | DDoS against bootnode `91.98.160.145`, P2P eclipse attack, RPC flooding. |
| **4. Supply Chain / Code Contributor Attacker** | Attempts malicious code injection via dependencies, PRs, or build pipeline. | Dependency backdoor (Cargo crates), malicious WASM runtime injection. |

---

## 4. ATTACK VECTORS, STRIDE ANALYSIS & MITIGATIONS

### 4.1 Consensus & Finality Attack Vectors

#### AV-01: BABE Equivocation / GRANDPA Double-Signing
- **STRIDE Category:** Spoofing / Tampering
- **Mechanics:** A malicious validator signs two conflicting blocks in the same BABE slot or signs two distinct GRANDPA finality votes at the same round height.
- **Mitigation:**
  - Implemented `pallet_offences` and Substrate `EquivocationReportEquivocation`.
  - Automatic 100% slash of validator stake and immediate removal from active set on proven equivocation.
  - GRANDPA voter set enforces strict 2/3 majority requirement ($15 / 21$ votes).
- **Residual Risk:** Low. Requires collusion of >14 validators to force an un-slashed fork.

---

### 4.2 Economic & Token Supply Vectors

#### AV-02: Inflationary Minting / Supply Invariant Violation
- **STRIDE Category:** Elevation of Privilege / Tampering
- **Mechanics:** An attacker exploits an unauthenticated or logic-flawed dispatchable to mint VRDX tokens out of thin air, exceeding the 100B cap.
- **Mitigation:**
  - Strict audit of `pallets/fungible-tokens` and `pallets/eco`.
  - Fixed `SEC-P0-03` (`mint_carbon_credit` root authorization).
  - Runtime invariant checks in `sp_runtime::traits::TotalIssuance` enforcing 100B hard cap.
- **Residual Risk:** Negligible. Verified via automated test suite.

---

### 4.3 AMM-DEX & Financial Vectors

#### AV-03: Front-Running & MEV Exploitation in AMM Swaps
- **STRIDE Category:** Tampering / Information Disclosure
- **Mechanics:** Malicious block producers inspect transaction pool (`gulf-stream` / transaction pool) and re-order or insert sandwich trades before user DEX swaps execute.
- **Mitigation:**
  - `pallets/amm-dex` enforces slippage protection parameters (`min_amount_out`) provided by users.
  - Implemented `pallets/circuit-breaker` to trip on abnormal price impact or multi-million token slippage spikes.
- **Residual Risk:** Medium. Standard MEV inherent in public mempools; mitigated by tight slippage bounds.

#### AV-04: Integer Overflow / Underflow in Liquidity Shares
- **STRIDE Category:** Elevation of Privilege / Tampering
- **Mechanics:** Attacker deposits high-decimal token values, triggering arithmetic overflow during LP share division or multiplication.
- **Mitigation:**
  - Fixed `SEC-P0-01` (division by zero) and `SEC-P0-04` (LP share calculation overflow).
  - Replaced all intermediate math in `pallets/amm-dex` with `U256` checked operations (`checked_mul`, `checked_div`).
- **Residual Risk:** Low. Covered by 28 specific DEX security regression tests.

---

### 4.4 Key Management & Administrative Vectors

#### AV-05: Treasury / Team Key Compromise
- **STRIDE Category:** Spoofing / Elevation of Privilege
- **Mechanics:** Attacker steals private keys governing the 20B VRDX Treasury account.
- **Mitigation:**
  - Replaced single-key control with **3-of-5 air-gapped cold-storage multisig** (`docs/TREASURY_SECURITY_SPEC.md`).
  - Keys generated on network-isolated hardware via `scripts/air-gapped-key-ceremony.sh`.
  - Spend proposals require dual-layer approval: Council 2/3 majority + 3-of-5 Multisig sign-off.
- **Residual Risk:** Low. Requires compromising 3 independent physical key custodians across separate geographical locations.

---

### 4.5 Infrastructure & Network Vectors

#### AV-06: Bootnode Eclipse / DDoS Attack (`91.98.160.145`)
- **STRIDE Category:** Denial of Service
- **Mechanics:** Attacker floods bootnode `91.98.160.145` with UDP/TCP traffic or malicious P2P handshakes to isolate new nodes joining the testnet/mainnet.
- **Mitigation:**
  - Hetzner Enterprise DDoS mitigation enabled at hardware perimeter.
  - Rate limiting via Substrate P2P connection limits (`--in-peers 50`, `--out-peers 50`).
  - Planned expansion to multi-region distributed bootnode architecture (Hetzner + AWS + OVH) for mainnet release.
- **Residual Risk:** Medium until additional bootnodes are deployed prior to mainnet launch.

---

### 4.6 Cross-Chain Bridge Vectors

#### AV-07: Bridge Escrow Replay / Signature Forgery (`VerdisBridge.sol`)
- **STRIDE Category:** Spoofing / Tampering
- **Mechanics:** Attacker replays cross-chain minting messages from EVM bridge contract (`VerdisBridge.sol` / `WVRS_BSC.sol`) to mint unbacked synthetic assets on Verdis Chain.
- **Mitigation:**
  - Nonce-based replay protection built into cross-chain payload verification.
  - Multi-relayer threshold signature requirement prior to emitting token mint events.
- **Residual Risk:** Medium. External bridge audits scheduled alongside core runtime external audit.

---

## 5. SUMMARY OF MITIGATIONS & RISK MATRIX

```
+---------------------------------------------------------------------------+
|                          RESIDUAL RISK SUMMARY                            |
+---------------------+-------------------+------------------+--------------+
| Attack Vector       | Likelihood        | Impact           | Residual Risk|
+---------------------+-------------------+------------------+--------------+
| BABE Equivocation   | Low               | High             | LOW          |
| Supply Inflation    | Very Low          | Critical         | LOW          |
| DEX Math Overflow   | Very Low          | High             | NEGLIGIBLE   |
| Treasury Compromise | Very Low          | Critical         | LOW          |
| Bootnode DDoS       | Medium            | Medium           | MEDIUM       |
| MEV / Front-run     | High              | Low              | MEDIUM       |
+---------------------+-------------------+------------------+--------------+
```

---

## 6. THREAT MODEL MAINTENANCE & REVIEW CYCLE

This Threat Model must be re-evaluated:
1. Prior to mainnet genesis deployment.
2. Following any major WASM runtime upgrade modifying core pallets.
3. Annually or following any SEV-0 / SEV-1 incident.
